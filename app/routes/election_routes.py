"""
Election-type specific routes for Lok Sabha and Vidhan Sabha data.
Provides clean API endpoints for accessing election data by type.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from flask import Blueprint, jsonify, request, current_app
from flask.wrappers import Response

from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger
from app.core.output_manager import OutputManager
from app.scrapers import LokSabhaScraper, VidhanSabhaScraper

# Create blueprints for election routes
lok_sabha_bp = Blueprint('lok_sabha', __name__)
vidhan_sabha_bp = Blueprint('vidhan_sabha', __name__)
election_bp = Blueprint('elections', __name__)

logger = get_logger("rajniti.election_routes")


class ElectionDataManager:
    """Manages election data loading and processing."""
    
    def __init__(self, data_root: str = "app/data"):
        self.data_root = Path(data_root)
        self.output_manager = OutputManager(data_root)
        self.logger = get_logger("rajniti.election_data_manager")
    
    def get_election_index(self, election_type: str) -> Dict[str, Any]:
        """Get index information for an election type."""
        try:
            meta_file = self.data_root / election_type / "meta.json"
            data_file = self.data_root / election_type / "data.json"
            
            if not meta_file.exists() or not data_file.exists():
                raise NotFoundError("Election type", election_type)
            
            # Load metadata and structure info
            import json
            with open(meta_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get available datasets
            available_datasets = []
            election_dir = self.data_root / election_type
            
            for item in election_dir.iterdir():
                if item.is_dir() and item.name not in ['common']:
                    dataset_data_file = item / "data.json"
                    if dataset_data_file.exists():
                        available_datasets.append(item.name)
            
            return {
                "election_type": election_type,
                "metadata": meta,
                "structure": data.get("structure", {}),
                "available_datasets": sorted(available_datasets),
                "summary": data.get("summary", {})
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get election index for {election_type}", error=str(e))
            raise
    
    def get_dataset(self, election_type: str, dataset_name: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get specific dataset for an election type."""
        try:
            dataset_dir = self.data_root / election_type / dataset_name
            data_file = dataset_dir / "data.json"
            meta_file = dataset_dir / "meta.json"
            
            if not data_file.exists():
                raise NotFoundError("Dataset", f"{election_type}/{dataset_name}")
            
            # Load data
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load metadata if available
            meta = {}
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    meta = json.load(f)
            
            # Apply filters if provided
            if filters and isinstance(data, list):
                data = self._apply_filters(data, filters)
            
            return {
                "dataset_name": dataset_name,
                "election_type": election_type,
                "metadata": meta,
                "data": data,
                "count": len(data) if isinstance(data, list) else 1
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get dataset {election_type}/{dataset_name}", error=str(e))
            raise
    
    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to dataset."""
        filtered_data = data
        
        for key, value in filters.items():
            if value:
                filtered_data = [
                    item for item in filtered_data 
                    if str(item.get(key, '')).lower() == str(value).lower()
                ]
        
        return filtered_data


# Initialize data manager
data_manager = ElectionDataManager()


# LOK SABHA ROUTES
@lok_sabha_bp.route('/', methods=['GET'])
def get_lok_sabha_index():
    """Get Lok Sabha election data index."""
    try:
        index_data = data_manager.get_election_index("lok_sabha")
        return APIResponse.success(
            data=index_data,
            message="Lok Sabha election data index retrieved successfully"
        )
    except NotFoundError as e:
        return APIResponse.not_found("Lok Sabha data")
    except Exception as e:
        logger.error("Failed to get Lok Sabha index", error=str(e))
        return APIResponse.internal_error()


@lok_sabha_bp.route('/<dataset_name>', methods=['GET'])
def get_lok_sabha_dataset(dataset_name: str):
    """Get specific Lok Sabha dataset."""
    try:
        # Parse query parameters for filtering
        filters = {
            'party': request.args.get('party'),
            'constituency': request.args.get('constituency'),
            'status': request.args.get('status'),
            'year': request.args.get('year')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        dataset = data_manager.get_dataset("lok_sabha", dataset_name, filters)
        return APIResponse.success(
            data=dataset,
            message=f"Lok Sabha {dataset_name} data retrieved successfully"
        )
    except NotFoundError as e:
        return APIResponse.not_found("Dataset", f"lok_sabha/{dataset_name}")
    except Exception as e:
        logger.error(f"Failed to get Lok Sabha dataset {dataset_name}", error=str(e))
        return APIResponse.internal_error()


@lok_sabha_bp.route('/scrape', methods=['POST'])
def scrape_lok_sabha_data():
    """Trigger scraping of Lok Sabha election data."""
    try:
        # Parse request data
        data = request.get_json() or {}
        year = data.get('year', 2024)
        output_mode = data.get('output_mode', 'json')
        
        if output_mode not in ['json', 'db', 'both']:
            return APIResponse.validation_error({
                "output_mode": ["Must be one of: json, db, both"]
            })
        
        # Initialize scraper and start scraping
        scraper = LokSabhaScraper()
        try:
            results = scraper.scrape(year=year, output_mode=output_mode)
            
            return APIResponse.success(
                data={
                    "scraping_completed": True,
                    "year": year,
                    "output_mode": output_mode,
                    "candidates_scraped": len(results),
                    "message": f"Successfully scraped Lok Sabha {year} data"
                },
                message="Lok Sabha data scraping completed successfully"
            )
        finally:
            scraper.close()
            
    except ValidationError as e:
        return APIResponse.validation_error({"error": [str(e)]})
    except Exception as e:
        logger.error("Failed to scrape Lok Sabha data", error=str(e))
        return APIResponse.internal_error()


# VIDHAN SABHA ROUTES
@vidhan_sabha_bp.route('/', methods=['GET'])
def get_vidhan_sabha_index():
    """Get Vidhan Sabha election data index."""
    try:
        index_data = data_manager.get_election_index("vidhan_sabha")
        return APIResponse.success(
            data=index_data,
            message="Vidhan Sabha election data index retrieved successfully"
        )
    except NotFoundError as e:
        return APIResponse.not_found("Vidhan Sabha data")
    except Exception as e:
        logger.error("Failed to get Vidhan Sabha index", error=str(e))
        return APIResponse.internal_error()


@vidhan_sabha_bp.route('/<dataset_name>', methods=['GET'])
def get_vidhan_sabha_dataset(dataset_name: str):
    """Get specific Vidhan Sabha dataset."""
    try:
        # Parse query parameters for filtering
        filters = {
            'party': request.args.get('party'),
            'constituency_code': request.args.get('constituency_code'),
            'state': request.args.get('state'),
            'status': request.args.get('status'),
            'year': request.args.get('year')
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        dataset = data_manager.get_dataset("vidhan_sabha", dataset_name, filters)
        return APIResponse.success(
            data=dataset,
            message=f"Vidhan Sabha {dataset_name} data retrieved successfully"
        )
    except NotFoundError as e:
        return APIResponse.not_found("Dataset", f"vidhan_sabha/{dataset_name}")
    except Exception as e:
        logger.error(f"Failed to get Vidhan Sabha dataset {dataset_name}", error=str(e))
        return APIResponse.internal_error()


@vidhan_sabha_bp.route('/scrape', methods=['POST'])
def scrape_vidhan_sabha_data():
    """Trigger scraping of Vidhan Sabha election data."""
    try:
        # Parse request data
        data = request.get_json() or {}
        state = data.get('state')
        year = data.get('year', 2024)
        output_mode = data.get('output_mode', 'json')
        
        if not state:
            return APIResponse.validation_error({
                "state": ["State parameter is required for Vidhan Sabha scraping"]
            })
        
        if output_mode not in ['json', 'db', 'both']:
            return APIResponse.validation_error({
                "output_mode": ["Must be one of: json, db, both"]
            })
        
        # Initialize scraper and start scraping
        scraper = VidhanSabhaScraper()
        try:
            results = scraper.scrape(state=state, year=year, output_mode=output_mode)
            
            return APIResponse.success(
                data={
                    "scraping_completed": True,
                    "state": state,
                    "year": year,
                    "output_mode": output_mode,
                    "candidates_scraped": len(results),
                    "message": f"Successfully scraped {state.title()} Vidhan Sabha {year} data"
                },
                message="Vidhan Sabha data scraping completed successfully"
            )
        finally:
            scraper.close()
            
    except ValidationError as e:
        return APIResponse.validation_error({"error": [str(e)]})
    except Exception as e:
        logger.error("Failed to scrape Vidhan Sabha data", error=str(e))
        return APIResponse.internal_error()


# GENERAL ELECTION ROUTES
@election_bp.route('/types', methods=['GET'])
def get_election_types():
    """Get available election types."""
    try:
        election_types = []
        
        # Check for lok_sabha data
        lok_sabha_dir = data_manager.data_root / "lok_sabha"
        if lok_sabha_dir.exists():
            election_types.append({
                "type": "lok_sabha",
                "name": "Lok Sabha",
                "description": "Parliamentary (National) Elections",
                "endpoint": "/api/v1/lok_sabha"
            })
        
        # Check for vidhan_sabha data
        vidhan_sabha_dir = data_manager.data_root / "vidhan_sabha"
        if vidhan_sabha_dir.exists():
            election_types.append({
                "type": "vidhan_sabha",
                "name": "Vidhan Sabha",
                "description": "State Assembly Elections",
                "endpoint": "/api/v1/vidhan_sabha"
            })
        
        return APIResponse.success(
            data={
                "available_types": election_types,
                "total_types": len(election_types)
            },
            message="Available election types retrieved successfully"
        )
        
    except Exception as e:
        logger.error("Failed to get election types", error=str(e))
        return APIResponse.internal_error()


@election_bp.route('/search', methods=['GET'])
def search_across_elections():
    """Search across all election types."""
    try:
        query = request.args.get('q', '').strip()
        election_type = request.args.get('type')  # optional filter
        
        if not query:
            return APIResponse.validation_error({
                "q": ["Search query parameter is required"]
            })
        
        results = {
            "query": query,
            "results": [],
            "total": 0
        }
        
        # Search in Lok Sabha data
        if not election_type or election_type == 'lok_sabha':
            lok_sabha_results = _search_in_election_type("lok_sabha", query)
            results["results"].extend(lok_sabha_results)
        
        # Search in Vidhan Sabha data
        if not election_type or election_type == 'vidhan_sabha':
            vidhan_sabha_results = _search_in_election_type("vidhan_sabha", query)
            results["results"].extend(vidhan_sabha_results)
        
        results["total"] = len(results["results"])
        
        return APIResponse.success(
            data=results,
            message="Search completed successfully"
        )
        
    except Exception as e:
        logger.error("Failed to perform search", error=str(e))
        return APIResponse.internal_error()


def _search_in_election_type(election_type: str, query: str) -> List[Dict[str, Any]]:
    """Search within a specific election type."""
    results = []
    
    try:
        # Get available datasets for this election type
        election_dir = data_manager.data_root / election_type
        if not election_dir.exists():
            return results
        
        for dataset_dir in election_dir.iterdir():
            if dataset_dir.is_dir():
                data_file = dataset_dir / "data.json"
                if data_file.exists():
                    try:
                        import json
                        with open(data_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        if isinstance(data, list):
                            # Search through list items
                            for item in data:
                                if _item_matches_query(item, query):
                                    results.append({
                                        **item,
                                        "_election_type": election_type,
                                        "_dataset": dataset_dir.name
                                    })
                        elif isinstance(data, dict):
                            # Search through dict values
                            if _item_matches_query(data, query):
                                results.append({
                                    **data,
                                    "_election_type": election_type,
                                    "_dataset": dataset_dir.name
                                })
                    
                    except Exception as e:
                        logger.warning(f"Failed to search in {dataset_dir}", error=str(e))
                        continue
        
    except Exception as e:
        logger.error(f"Failed to search in {election_type}", error=str(e))
    
    return results


def _item_matches_query(item: Dict[str, Any], query: str) -> bool:
    """Check if an item matches the search query."""
    query_lower = query.lower()
    
    # Search in string values
    for value in item.values():
        if isinstance(value, str) and query_lower in value.lower():
            return True
    
    return False


@election_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for the application."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check data directory
        try:
            data_dir = data_manager.data_root
            health_status["components"]["data_storage"] = {
                "status": "healthy" if data_dir.exists() else "unhealthy",
                "path": str(data_dir)
            }
        except Exception as e:
            health_status["components"]["data_storage"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check database (if enabled)
        try:
            if hasattr(current_app, 'db_manager'):
                db_health = current_app.db_manager.health_check()
                health_status["components"]["database"] = db_health
            else:
                health_status["components"]["database"] = {
                    "status": "disabled",
                    "message": "Database manager not available"
                }
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e)
            }
        
        # Check available election types
        try:
            available_types = []
            if (data_manager.data_root / "lok_sabha").exists():
                available_types.append("lok_sabha")
            if (data_manager.data_root / "vidhan_sabha").exists():
                available_types.append("vidhan_sabha")
            
            health_status["components"]["election_types"] = {
                "status": "healthy" if available_types else "warning",
                "available": available_types,
                "count": len(available_types)
            }
        except Exception as e:
            health_status["components"]["election_types"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Determine overall status
        component_statuses = [comp.get("status", "unknown") for comp in health_status["components"].values()]
        if "unhealthy" in component_statuses or "error" in component_statuses:
            health_status["status"] = "unhealthy"
        elif "warning" in component_statuses:
            health_status["status"] = "warning"
        
        status_code = 200 if health_status["status"] == "healthy" else 503
        
        return APIResponse.success(
            data=health_status,
            message="Health check completed",
            status_code=status_code
        )
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return APIResponse.internal_error()
