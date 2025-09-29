"""
Development server entry point for the Rajniti application.
"""
import os
import logging
from app import create_app

def main():
    """Main entry point for the development server."""
    # Get environment
    env = os.getenv("FLASK_ENV", "development")
    
    # Create app with specified environment
    app = create_app()
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("rajniti.server")
    
    # Server configuration
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8080"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    logger.info(f"Starting Rajniti development server on {host}:{port}")
    logger.info(f"Debug mode: {debug}, Environment: {env}")
    
    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )


if __name__ == '__main__':
    main()