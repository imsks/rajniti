"""
Data Services Layer

This layer abstracts data access so we can easily switch from JSON to database later.
All business logic for data retrieval and manipulation goes here.
"""

from .data_service import DataService
from .json_data_service import JsonDataService

# Create singleton instance
data_service: DataService = JsonDataService()

__all__ = ["data_service", "DataService", "JsonDataService"]
