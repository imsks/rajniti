"""
Database module for optional database functionality.
Provides a clean interface for database operations while keeping them optional.
"""

from .db_manager import DatabaseManager
from .db_config import DatabaseConfig

__all__ = ['DatabaseManager', 'DatabaseConfig']
