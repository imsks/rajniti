"""
Output Manager for handling dual persistence modes (JSON and Database).
Supports writing scraped data to both JSON files and database tables.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValidationError, DatabaseError
from app.core.logging_config import get_logger


class OutputManager:
    """Manages dual output modes for scraped election data."""
    
    def __init__(self, data_root: str = "app/data"):
        """
        Initialize the output manager.
        
        Args:
            data_root: Root directory for JSON data storage
        """
        self.data_root = Path(data_root)
        self.logger = get_logger("rajniti.output_manager")
    
    def persist_output(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        election_type: Literal["lok_sabha", "vidhan_sabha"],
        dataset_name: str,
        output_mode: Literal["json", "db", "both"] = "json",
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Persist scraped data using the specified output mode.
        
        Args:
            data: The data to persist
            election_type: Type of election (lok_sabha or vidhan_sabha)
            dataset_name: Name of the dataset (e.g., "candidates-2024")
            output_mode: Where to save the data ("json", "db", or "both")
            meta: Optional metadata for the dataset
            
        Returns:
            Dictionary with persistence results
        """
        results = {
            "election_type": election_type,
            "dataset_name": dataset_name,
            "output_mode": output_mode,
            "timestamp": datetime.utcnow().isoformat(),
            "success": False,
            "json_result": None,
            "db_result": None,
            "errors": []
        }
        
        try:
            # Persist to JSON
            if output_mode in ["json", "both"]:
                json_result = self._persist_to_json(data, election_type, dataset_name, meta)
                results["json_result"] = json_result
                self.logger.info(
                    "Data persisted to JSON", 
                    election_type=election_type,
                    dataset_name=dataset_name,
                    records_count=len(data) if isinstance(data, list) else 1
                )
            
            # Persist to Database
            if output_mode in ["db", "both"]:
                db_result = self._persist_to_database(data, election_type, dataset_name)
                results["db_result"] = db_result
                self.logger.info(
                    "Data persisted to database", 
                    election_type=election_type,
                    dataset_name=dataset_name,
                    records_count=db_result.get("records_inserted", 0)
                )
            
            results["success"] = True
            
        except Exception as e:
            error_msg = f"Failed to persist data: {str(e)}"
            results["errors"].append(error_msg)
            self.logger.error(
                "Data persistence failed",
                election_type=election_type,
                dataset_name=dataset_name,
                error=str(e)
            )
            
        return results
    
    def _persist_to_json(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        election_type: str,
        dataset_name: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Persist data to JSON files."""
        
        # Create directory structure
        dataset_dir = self.data_root / election_type / dataset_name
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        # Save main data
        data_file = dataset_dir / "data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Generate and save metadata
        if not meta:
            meta = self._generate_metadata(data, election_type, dataset_name)
        
        meta_file = dataset_dir / "meta.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)
        
        # Generate and save schema
        schema = self._generate_schema(data, election_type)
        schema_file = dataset_dir / "schema.json"
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        return {
            "data_file": str(data_file),
            "meta_file": str(meta_file),
            "schema_file": str(schema_file),
            "records_count": len(data) if isinstance(data, list) else 1
        }
    
    def _persist_to_database(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        election_type: str,
        dataset_name: str
    ) -> Dict[str, Any]:
        """Persist data to database tables using the optional database manager."""
        
        # Check if we have access to the Flask app and database manager
        if not current_app or not hasattr(current_app, 'db_manager'):
            return {
                "records_inserted": 0,
                "records_skipped": 0,
                "errors": ["Database manager not available"]
            }
        
        db_manager = current_app.db_manager
        
        if not db_manager.is_available():
            return {
                "records_inserted": 0,
                "records_skipped": 0,
                "errors": ["Database functionality is disabled"]
            }
        
        if not isinstance(data, list):
            data = [data]
        
        results = {
            "records_inserted": 0,
            "records_skipped": 0,
            "errors": []
        }
        
        try:
            # Determine data type and insert accordingly
            if "candidate" in dataset_name.lower():
                results = db_manager.insert_candidates(data)
            elif "constituency" in dataset_name.lower() or "constituencies" in dataset_name.lower():
                results = db_manager.insert_constituencies(data)
            elif "party" in dataset_name.lower() or "parties" in dataset_name.lower():
                results = db_manager.insert_parties(data)
            else:
                # For other data types, just return success without insertion
                results = {
                    "records_inserted": 0,
                    "records_skipped": len(data),
                    "errors": [f"Data type '{dataset_name}' not supported for database insertion"]
                }
            
        except Exception as e:
            results["errors"].append(str(e))
            self.logger.error("Database persistence failed", error=str(e))
        
        return results
    
    
    def _generate_metadata(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        election_type: str,
        dataset_name: str
    ) -> Dict[str, Any]:
        """Generate metadata for the dataset."""
        
        record_count = len(data) if isinstance(data, list) else 1
        
        return {
            "dataset_name": dataset_name,
            "election_type": election_type,
            "title": f"{dataset_name.replace('-', ' ').title()} - {election_type.replace('_', ' ').title()}",
            "description": f"Auto-generated dataset for {dataset_name}",
            "source": "Election Commission of India (ECI)",
            "source_url": "https://results.eci.gov.in",
            "last_updated": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "format": "JSON",
            "encoding": "UTF-8",
            "total_records": record_count,
            "generated_by": "Rajniti Output Manager",
            "license": "Public Domain"
        }
    
    def _generate_schema(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        election_type: str
    ) -> Dict[str, Any]:
        """Generate JSON schema based on data structure."""
        
        if isinstance(data, list) and data:
            sample_record = data[0]
        else:
            sample_record = data if isinstance(data, dict) else {}
        
        properties = {}
        for key, value in sample_record.items():
            if isinstance(value, str):
                properties[key] = {"type": "string"}
            elif isinstance(value, int):
                properties[key] = {"type": "integer"}
            elif isinstance(value, float):
                properties[key] = {"type": "number"}
            elif isinstance(value, bool):
                properties[key] = {"type": "boolean"}
            elif value is None:
                properties[key] = {"type": ["string", "null"]}
            else:
                properties[key] = {"type": "string"}
        
        return {
            "type": "array" if isinstance(data, list) else "object",
            "title": f"{election_type.replace('_', ' ').title()} Data Schema",
            "items": {
                "type": "object",
                "properties": properties,
                "additionalProperties": True
            } if isinstance(data, list) else None,
            "properties": properties if not isinstance(data, list) else None,
            "additionalProperties": True
        }
    
    
    def load_from_source(
        self, 
        election_type: Literal["lok_sabha", "vidhan_sabha"],
        dataset_name: str,
        source: Literal["json", "db"] = "json"
    ) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """
        Load data from the specified source.
        
        Args:
            election_type: Type of election
            dataset_name: Name of the dataset
            source: Where to load from ("json" or "db")
            
        Returns:
            The loaded data or None if not found
        """
        try:
            if source == "json":
                return self._load_from_json(election_type, dataset_name)
            else:
                return self._load_from_database(election_type, dataset_name)
        except Exception as e:
            self.logger.error(
                "Failed to load data",
                election_type=election_type,
                dataset_name=dataset_name,
                source=source,
                error=str(e)
            )
            return None
    
    def _load_from_json(self, election_type: str, dataset_name: str) -> Optional[Dict[str, Any]]:
        """Load data from JSON files."""
        data_file = self.data_root / election_type / dataset_name / "data.json"
        
        if not data_file.exists():
            return None
        
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_from_database(self, election_type: str, dataset_name: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from database tables."""
        # This would require more sophisticated logic to determine which tables to query
        # For now, return None - this can be implemented based on specific requirements
        self.logger.info(f"Database loading not yet implemented for {dataset_name}")
        return None
