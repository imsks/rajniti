"""
Database configuration and setup utilities.
Handles optional database initialization and configuration.
"""
import os
from typing import Optional, Dict, Any
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from app.core.logging_config import get_logger


class DatabaseConfig:
    """Manages database configuration and optional setup."""
    
    def __init__(self):
        self.logger = get_logger("rajniti.database_config")
        self._db: Optional[SQLAlchemy] = None
        self._migrate: Optional[Migrate] = None
        self._is_enabled = False
    
    def is_enabled(self) -> bool:
        """Check if database functionality is enabled."""
        return self._is_enabled
    
    def enable_database(self, app: Flask, force: bool = False) -> bool:
        """
        Enable database functionality for the application.
        
        Args:
            app: Flask application instance
            force: Force enable even if DATABASE_URL is not set
            
        Returns:
            True if database was successfully enabled, False otherwise
        """
        try:
            # Check if database should be enabled
            database_url = app.config.get('SQLALCHEMY_DATABASE_URI')
            enable_db = app.config.get('ENABLE_DATABASE', 'false').lower() == 'true'
            
            if not enable_db and not force:
                self.logger.info("Database functionality disabled by configuration")
                return False
            
            if not database_url and not force:
                self.logger.info("No database URL configured, skipping database setup")
                return False
            
            # Import models here to avoid circular imports
            from app.models import db
            
            # Initialize database
            self._db = db
            db.init_app(app)
            
            # Initialize migrations
            self._migrate = Migrate(app, db)
            
            # Test database connection
            with app.app_context():
                try:
                    db.engine.connect()
                    self.logger.info("Database connection successful")
                    self._is_enabled = True
                    return True
                except Exception as e:
                    self.logger.warning(f"Database connection failed: {str(e)}")
                    self._is_enabled = False
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to enable database: {str(e)}")
            self._is_enabled = False
            return False
    
    def create_tables(self, app: Flask) -> bool:
        """
        Create database tables if database is enabled.
        
        Args:
            app: Flask application instance
            
        Returns:
            True if tables were created successfully, False otherwise
        """
        if not self._is_enabled or not self._db:
            self.logger.info("Database not enabled, skipping table creation")
            return False
        
        try:
            with app.app_context():
                self._db.create_all()
                self.logger.info("Database tables created successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {str(e)}")
            return False
    
    def populate_initial_data(self, app: Flask) -> bool:
        """
        Populate initial data if database is enabled.
        
        Args:
            app: Flask application instance
            
        Returns:
            True if data was populated successfully, False otherwise
        """
        if not self._is_enabled or not self._db:
            self.logger.info("Database not enabled, skipping data population")
            return False
        
        try:
            with app.app_context():
                from app.models.populate import PopulateDB
                populate = PopulateDB(self._db, app.config.get('SQLALCHEMY_DATABASE_URI'))
                populate.init_populate()
                self.logger.info("Initial data populated successfully")
                return True
        except Exception as e:
            self.logger.error(f"Failed to populate initial data: {str(e)}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about database status."""
        return {
            "enabled": self._is_enabled,
            "db_instance": self._db is not None,
            "migrate_instance": self._migrate is not None
        }
    
    @property
    def db(self) -> Optional[SQLAlchemy]:
        """Get the database instance if enabled."""
        return self._db if self._is_enabled else None
    
    @property
    def migrate(self) -> Optional[Migrate]:
        """Get the migrate instance if enabled."""
        return self._migrate if self._is_enabled else None
