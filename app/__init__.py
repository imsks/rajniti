"""
Simple Flask application factory for Rajniti Election Data API.

Clean, minimal setup without unnecessary complexity.
"""
import os

from flask import Flask
from flask_cors import CORS

from app.core.exceptions import RajnitiError
from app.core.response import error_response


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Simple configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JSON_SORT_KEYS"] = False

    # Enable CORS
    CORS(app)

    # Register routes
    _register_routes(app)

    # Register error handlers
    _register_error_handlers(app)

    return app


def _register_routes(app: Flask) -> None:
    """Register API routes"""
    from app.routes.api_routes import api_bp

    app.register_blueprint(api_bp)


def _register_error_handlers(app: Flask) -> None:
    """Register error handlers"""

    @app.errorhandler(RajnitiError)
    def handle_rajniti_error(error):
        return error_response(error.message, error.code)

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response("Endpoint not found", 404)

    @app.errorhandler(500)
    def handle_server_error(error):
        return error_response("Internal server error", 500)
