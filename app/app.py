from flask import Flask
from database import db  # Import database instance
from routes import register_routes  # Function to register API routes

def create_app():
    app = Flask(__name__)
    
    # Load configurations from instance folder
    app.config.from_pyfile('instance/config.py', silent=True)

    # Initialize database
    db.init_app(app)

    # Register routes
    register_routes(app)

    return app
