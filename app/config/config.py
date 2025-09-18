"""
Production-grade configuration management for Rajniti application.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BaseConfig:
    """Base configuration with common settings."""
    
    # Flask Core
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:12345678@localhost/INDIA"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_recycle": 300,
        "pool_pre_ping": True
    }
    
    # API Configuration
    API_VERSION: str = os.getenv("API_VERSION", "v1")
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Scraping Configuration
    ECI_BASE_URL: str = os.getenv("ECI_BASE_URL", "https://results.eci.gov.in")
    SCRAPER_RETRY_ATTEMPTS: int = int(os.getenv("SCRAPER_RETRY_ATTEMPTS", "3"))
    SCRAPER_RETRY_DELAY: int = int(os.getenv("SCRAPER_RETRY_DELAY", "2"))
    SCRAPER_TIMEOUT: int = int(os.getenv("SCRAPER_TIMEOUT", "30"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # File Storage
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    CACHE_DIR: str = os.getenv("CACHE_DIR", "cache")


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG: bool = True
    TESTING: bool = False
    LOG_LEVEL: str = "DEBUG"


class ProductionConfig(BaseConfig):
    """Production configuration."""
    DEBUG: bool = False
    TESTING: bool = False
    
    # Production database with connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 20,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
        "pool_timeout": 30
    }


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False


# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}


def get_config(environment: Optional[str] = None) -> BaseConfig:
    """Get configuration based on environment."""
    env = environment or os.getenv("FLASK_ENV", "development")
    return config_map.get(env, config_map["default"])