"""
Production-grade Flask application factory for the Rajniti project.
"""
from typing import Optional
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from app.config.config import get_config, BaseConfig
from app.core.logging_config import setup_logging, get_logger
from app.core.exceptions import RajnitiException
from app.core.responses import APIResponse
from app.db import DatabaseConfig, DatabaseManager


def create_app(config_name: Optional[str] = None) -> Flask:
    """
    Application factory function.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(config.LOG_LEVEL, config.LOG_FORMAT)
    logger = get_logger("rajniti.app")
    
    # Initialize extensions
    _init_extensions(app, config)
    
    # Register blueprints
    _register_blueprints(app, config)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Setup database
    _setup_database(app, config)
    
    logger.info("Rajniti application created successfully", config=config_name)
    
    return app


def _init_extensions(app: Flask, config: BaseConfig) -> None:
    """Initialize Flask extensions."""
    # Setup optional database
    db_config = DatabaseConfig()
    db_enabled = db_config.enable_database(app)
    
    # Store database configuration in app for access by other components
    app.db_config = db_config
    app.db_manager = DatabaseManager(db_config)
    
    if db_enabled:
        logger = get_logger("rajniti.app")
        logger.info("Database functionality enabled")
    else:
        logger = get_logger("rajniti.app")
        logger.info("Database functionality disabled - running in JSON-only mode")
    
    # CORS
    CORS(app, origins=config.CORS_ORIGINS)


def _register_blueprints(app: Flask, config: BaseConfig) -> None:
    """Register application blueprints."""
    # Import legacy routes
    from app.routes.party import party_bp
    from app.routes.constituency import constituency_bp
    from app.routes.candidate import candidate_bp
    from app.routes.election import election_bp
    from app.routes.data_routes import data_bp
    from app.routes.election_routes import lok_sabha_bp, vidhan_sabha_bp, election_bp as election_types_bp
    
    # Import new API v2
    from app.api import api_bp
    
    api_prefix = f"/api/{config.API_VERSION}"
    
    # Register new API v2 (primary API)
    app.register_blueprint(api_bp)
    
    # Register original CRUD routes (for backward compatibility)
    app.register_blueprint(party_bp, url_prefix=api_prefix)
    app.register_blueprint(constituency_bp, url_prefix=api_prefix)
    app.register_blueprint(candidate_bp, url_prefix=api_prefix)
    app.register_blueprint(election_bp, url_prefix=api_prefix)
    
    # Register dynamic data routes
    app.register_blueprint(data_bp, url_prefix=api_prefix)
    
    # Register new election-type specific routes
    app.register_blueprint(lok_sabha_bp, url_prefix=f"{api_prefix}/lok_sabha")
    app.register_blueprint(vidhan_sabha_bp, url_prefix=f"{api_prefix}/vidhan_sabha")
    app.register_blueprint(election_types_bp, url_prefix=f"{api_prefix}/elections")


def _register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    
    @app.errorhandler(RajnitiException)
    def handle_rajniti_exception(error: RajnitiException):
        """Handle custom Rajniti exceptions."""
        status_code_map = {
            "VALIDATION_ERROR": 422,
            "DATABASE_ERROR": 500,
            "SCRAPING_ERROR": 500,
            "NOT_FOUND": 404,
            "CONFLICT": 409,
            "AUTHENTICATION_ERROR": 401,
            "AUTHORIZATION_ERROR": 403,
            "RATE_LIMIT_ERROR": 429,
            "EXTERNAL_SERVICE_ERROR": 502
        }
        
        status_code = status_code_map.get(error.error_code, 500)
        
        return APIResponse.error(
            message=error.message,
            error_code=error.error_code,
            status_code=status_code,
            details=error.details
        )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return APIResponse.not_found("Endpoint")
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return APIResponse.error(
            message="Method not allowed",
            error_code="METHOD_NOT_ALLOWED",
            status_code=405
        )
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 errors."""
        logger = get_logger("rajniti.error")
        logger.error("Internal server error", error=str(error))
        
        return APIResponse.internal_error()


def _setup_database(app: Flask, config: BaseConfig) -> None:
    """Setup database tables and initial data if database is enabled."""
    
    @app.before_first_request
    def create_tables():
        """Create database tables and populate initial data."""
        logger = get_logger("rajniti.database")
        
        # Only setup database if it's enabled
        if not hasattr(app, 'db_config') or not app.db_config.is_enabled():
            logger.info("Database disabled, skipping table creation and data population")
            return
        
        try:
            # Create tables
            tables_created = app.db_config.create_tables(app)
            if tables_created:
                logger.info("Database tables created successfully")
            
            # Populate initial data
            data_populated = app.db_config.populate_initial_data(app)
            if data_populated:
                logger.info("Initial data populated successfully")
            
        except Exception as e:
            logger.warning("Database setup failed - continuing in JSON-only mode", error=str(e))

