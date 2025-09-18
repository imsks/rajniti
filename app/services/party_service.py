"""
Service layer for party-related business logic.
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

from app.models import Party
from app.services.base_service import BaseService
from app.core.exceptions import ValidationError, DatabaseError
from app.schemas.party import PartySearchSchema


class PartyService(BaseService[Party]):
    """Service for party-related operations."""
    
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, Party)
    
    def search_parties(self, search_params: PartySearchSchema) -> List[Party]:
        """
        Search parties by name.
        
        Args:
            search_params: Search parameters
            
        Returns:
            List of matching parties
        """
        try:
            query = Party.query
            
            if search_params.name:
                query = query.filter(Party.name.ilike(f"%{search_params.name}%"))
            
            return query.all()
            
        except Exception as e:
            self.logger.log_error(
                operation="search_parties",
                table=self.model_class.__tablename__,
                error=str(e),
                search_params=search_params.dict()
            )
            raise
    
    def get_party_by_name(self, name: str) -> Optional[Party]:
        """
        Get party by exact name match.
        
        Args:
            name: Party name
            
        Returns:
            Party instance if found, None otherwise
        """
        try:
            return Party.query.filter(Party.name == name).first()
        except Exception as e:
            self.logger.log_error(
                operation="get_party_by_name",
                table=self.model_class.__tablename__,
                error=str(e),
                name=name
            )
            raise
    
    def load_scraped_data(self, data_file_path: str) -> List[Dict[str, Any]]:
        """
        Load scraped party data from JSON file.
        
        Args:
            data_file_path: Path to the JSON data file
            
        Returns:
            List of party data dictionaries
            
        Raises:
            ValidationError: If file not found or invalid
        """
        try:
            file_path = Path(data_file_path)
            if not file_path.exists():
                raise ValidationError(f"Data file not found: {data_file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValidationError("Data file must contain a list of parties")
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format in data file: {str(e)}")
        except Exception as e:
            self.logger.log_error(
                operation="load_scraped_data",
                table=self.model_class.__tablename__,
                error=str(e),
                data_file_path=data_file_path
            )
            raise
    
    def import_scraped_parties(self, data_file_path: str) -> Dict[str, int]:
        """
        Import parties from scraped data file.
        
        Args:
            data_file_path: Path to the JSON data file
            
        Returns:
            Dictionary with import statistics
        """
        try:
            scraped_data = self.load_scraped_data(data_file_path)
            
            inserted = 0
            skipped = 0
            errors = 0
            
            for party_data in scraped_data:
                try:
                    # Validate required fields
                    if not party_data.get("party_name") or not party_data.get("symbol"):
                        skipped += 1
                        continue
                    
                    # Check if party already exists
                    existing = self.get_party_by_name(party_data["party_name"])
                    if existing:
                        skipped += 1
                        continue
                    
                    # Create new party
                    create_data = {
                        "name": party_data["party_name"],
                        "symbol": party_data["symbol"],
                        "total_seats": party_data.get("total_seats")
                    }
                    
                    self.create(create_data)
                    inserted += 1
                    
                except Exception as e:
                    self.logger.log_error(
                        operation="import_party",
                        table=self.model_class.__tablename__,
                        error=str(e),
                        party_data=party_data
                    )
                    errors += 1
            
            return {
                "inserted": inserted,
                "skipped": skipped,
                "errors": errors,
                "total_processed": len(scraped_data)
            }
            
        except Exception as e:
            self.logger.log_error(
                operation="import_scraped_parties",
                table=self.model_class.__tablename__,
                error=str(e),
                data_file_path=data_file_path
            )
            raise
    
    def get_parties_by_seats_range(self, min_seats: int, max_seats: Optional[int] = None) -> List[Party]:
        """
        Get parties within a specific seat range.
        
        Args:
            min_seats: Minimum number of seats
            max_seats: Maximum number of seats (optional)
            
        Returns:
            List of parties within the seat range
        """
        try:
            query = Party.query.filter(Party.total_seats >= min_seats)
            
            if max_seats is not None:
                query = query.filter(Party.total_seats <= max_seats)
            
            return query.order_by(Party.total_seats.desc()).all()
            
        except Exception as e:
            self.logger.log_error(
                operation="get_parties_by_seats_range",
                table=self.model_class.__tablename__,
                error=str(e),
                min_seats=min_seats,
                max_seats=max_seats
            )
            raise
