from flask import Flask
from flask_migrate import Migrate
from config import Config
from database.db import db, initialize_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database
    initialize_database(app)
    Migrate(app, db)
    
    # Register blueprints
    from routes.party_routes import party_bp
    from routes.constituency_routes import constituency_bp
    from routes.candidate_routes import candidate_bp
    
    app.register_blueprint(party_bp, url_prefix='/api/party')
    app.register_blueprint(constituency_bp, url_prefix='/api/constituency')
    app.register_blueprint(candidate_bp, url_prefix='/api/candidate')
    
    return app