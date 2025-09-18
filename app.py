"""
Legacy app.py - Use app/__init__.py for new application factory pattern.
This file is kept for backwards compatibility.
"""
from app import create_app

# Create default app instance for backwards compatibility
app = create_app()
