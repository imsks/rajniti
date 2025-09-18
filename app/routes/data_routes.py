"""
Dynamic data routes for serving organized data from the data/ folder.
Automatically creates REST endpoints for each data category.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Blueprint, jsonify, current_app, request
from flask.wrappers import Response

from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger

# Create blueprint for data routes
data_bp = Blueprint('data', __name__)
logger = get_logger("rajniti.data_routes")


class DataManager:
    """Manages data loading and validation for the API."""
    
    def __init__(self, data_root: str = "app/data"):
        self.data_root = Path(data_root)
        self.logger = get_logger("rajniti.data_manager")
    
    def get_available_datasets(self) -> List[str]:
        """Get list of available data categories."""
        try:
            categories = []
            for item in self.data_root.iterdir():
                if item.is_dir() and item.name != "DL-Election":  # Skip old folder
                    data_file = item / "data.json"
                    if data_file.exists():
                        categories.append(item.name)
            return sorted(categories)
        except Exception as e:
            self.logger.error("Failed to get available datasets", error=str(e))
            return []
    
    def load_data(self, category: str) -> Dict[str, Any]:
        """Load data.json for a category."""
        try:
            data_file = self.data_root / category / "data.json"
            if not data_file.exists():
                raise NotFoundError("Data category", category)
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info("Data loaded successfully", category=category, records=len(data) if isinstance(data, list) else 1)
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in data file", category=category, error=str(e))
            raise ValidationError(f"Invalid JSON format in {category} data")
        except FileNotFoundError:
            raise NotFoundError("Data category", category)
        except Exception as e:
            self.logger.error("Failed to load data", category=category, error=str(e))
            raise
    
    def load_schema(self, category: str) -> Dict[str, Any]:
        """Load schema.json for a category."""
        try:
            schema_file = self.data_root / category / "schema.json"
            if not schema_file.exists():
                raise NotFoundError("Schema", f"{category}/schema")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            return schema
            
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in schema file", category=category, error=str(e))
            raise ValidationError(f"Invalid JSON format in {category} schema")
        except FileNotFoundError:
            raise NotFoundError("Schema", f"{category}/schema")
        except Exception as e:
            self.logger.error("Failed to load schema", category=category, error=str(e))
            raise
    
    def load_meta(self, category: str) -> Dict[str, Any]:
        """Load meta.json for a category."""
        try:
            meta_file = self.data_root / category / "meta.json"
            if not meta_file.exists():
                raise NotFoundError("Metadata", f"{category}/meta")
            
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            return meta
            
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON in meta file", category=category, error=str(e))
            raise ValidationError(f"Invalid JSON format in {category} metadata")
        except FileNotFoundError:
            raise NotFoundError("Metadata", f"{category}/meta")
        except Exception as e:
            self.logger.error("Failed to load metadata", category=category, error=str(e))
            raise
    
    def filter_data(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to data."""
        if not filters or not isinstance(data, list):
            return data
        
        filtered_data = data
        
        for key, value in filters.items():
            if key.startswith('_'):  # Skip internal parameters
                continue
                
            filtered_data = [
                item for item in filtered_data 
                if isinstance(item, dict) and self._matches_filter(item, key, value)
            ]
        
        return filtered_data
    
    def _matches_filter(self, item: Dict[str, Any], key: str, value: Any) -> bool:
        """Check if an item matches a filter condition."""
        if key not in item:
            return False
        
        item_value = item[key]
        
        # Exact match for strings and numbers
        if isinstance(value, (str, int, float)):
            return str(item_value).lower() == str(value).lower()
        
        # List membership
        if isinstance(value, list):
            return item_value in value
        
        return False


# Initialize data manager
data_manager = DataManager()


# ==================== DYNAMIC ROUTE GENERATORS ====================

def register_data_routes():
    """Register dynamic routes for all data categories."""
    categories = data_manager.get_available_datasets()
    
    for category in categories:
        logger.info("Registering routes for data category", category=category)
        
        # Register data route
        data_bp.add_url_rule(
            f'/{category}',
            f'get_{category}_data',
            lambda cat=category: get_data(cat),
            methods=['GET']
        )
        
        # Register schema route
        data_bp.add_url_rule(
            f'/{category}/schema',
            f'get_{category}_schema',
            lambda cat=category: get_schema(cat),
            methods=['GET']
        )
        
        # Register meta route
        data_bp.add_url_rule(
            f'/{category}/meta',
            f'get_{category}_meta',
            lambda cat=category: get_meta(cat),
            methods=['GET']
        )


# ==================== ROUTE HANDLERS ====================

@data_bp.route('/index')
def get_data_index():
    """Get index of all available data endpoints."""
    try:
        categories = data_manager.get_available_datasets()
        
        endpoints = {}
        for category in categories:
            endpoints[category] = {
                "data": f"/api/v1/{category}",
                "schema": f"/api/v1/{category}/schema", 
                "meta": f"/api/v1/{category}/meta",
                "description": f"Access {category} data, schema, and metadata"
            }
        
        index_data = {
            "title": "Rajniti Data API Index",
            "description": "Available election data endpoints",
            "version": "1.0.0",
            "total_datasets": len(categories),
            "categories": categories,
            "endpoints": endpoints,
            "usage": {
                "data": "GET /{category} - Get the actual data",
                "schema": "GET /{category}/schema - Get JSON schema for validation",
                "meta": "GET /{category}/meta - Get metadata and documentation",
                "filters": "Add query parameters to filter data (e.g., ?state_id=DL)"
            }
        }
        
        return APIResponse.success(
            data=index_data,
            message="Data index retrieved successfully"
        )
        
    except Exception as e:
        logger.error("Failed to generate data index", error=str(e))
        return APIResponse.internal_error("Failed to load data index")


def get_data(category: str) -> Response:
    """Get data for a specific category with optional filtering."""
    try:
        # Load the data
        data = data_manager.load_data(category)
        
        # Apply filters if provided
        filters = {k: v for k, v in request.args.items() if k not in ['page', 'limit']}
        if filters and isinstance(data, list):
            data = data_manager.filter_data(data, filters)
        
        # Apply pagination if requested
        page = request.args.get('page', type=int)
        limit = request.args.get('limit', type=int)
        
        if page and limit and isinstance(data, list):
            start = (page - 1) * limit
            end = start + limit
            paginated_data = data[start:end]
            
            return APIResponse.paginated(
                data=paginated_data,
                page=page,
                per_page=limit,
                total=len(data),
                message=f"{category.title()} data retrieved successfully"
            )
        
        # Prepare metadata
        meta = {
            "category": category,
            "total_records": len(data) if isinstance(data, list) else 1,
            "filters_applied": filters if filters else None
        }
        
        return APIResponse.success(
            data=data,
            message=f"{category.title()} data retrieved successfully",
            meta=meta
        )
        
    except (NotFoundError, ValidationError) as e:
        logger.warning("Data request failed", category=category, error=str(e))
        return APIResponse.error(
            message=str(e),
            error_code=e.error_code,
            status_code=404 if isinstance(e, NotFoundError) else 422
        )
    except Exception as e:
        logger.error("Failed to get data", category=category, error=str(e))
        return APIResponse.internal_error(f"Failed to load {category} data")


def get_schema(category: str) -> Response:
    """Get JSON schema for a specific category."""
    try:
        schema = data_manager.load_schema(category)
        
        return APIResponse.success(
            data=schema,
            message=f"{category.title()} schema retrieved successfully"
        )
        
    except (NotFoundError, ValidationError) as e:
        return APIResponse.error(
            message=str(e),
            error_code=e.error_code,
            status_code=404 if isinstance(e, NotFoundError) else 422
        )
    except Exception as e:
        logger.error("Failed to get schema", category=category, error=str(e))
        return APIResponse.internal_error(f"Failed to load {category} schema")


def get_meta(category: str) -> Response:
    """Get metadata for a specific category."""
    try:
        meta = data_manager.load_meta(category)
        
        return APIResponse.success(
            data=meta,
            message=f"{category.title()} metadata retrieved successfully"
        )
        
    except (NotFoundError, ValidationError) as e:
        return APIResponse.error(
            message=str(e),
            error_code=e.error_code,
            status_code=404 if isinstance(e, NotFoundError) else 422
        )
    except Exception as e:
        logger.error("Failed to get metadata", category=category, error=str(e))
        return APIResponse.internal_error(f"Failed to load {category} metadata")


# Auto-register routes when module is imported
register_data_routes()
