"""
Development server entry point for the Rajniti application.
"""
import os
from app import create_app
from app.core.logging_config import get_logger

def main():
    """Main entry point for the development server."""
    # Get environment
    env = os.getenv("FLASK_ENV", "development")
    
    # Create app with specified environment
    app = create_app(env)
    
    # Setup logger
    logger = get_logger("rajniti.server")
    
    # Server configuration
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8080"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    logger.info(
        "Starting Rajniti development server",
        host=host,
        port=port,
        debug=debug,
        environment=env
    )
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )


if __name__ == '__main__':
    main()