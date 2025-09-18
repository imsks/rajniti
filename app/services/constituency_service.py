"""
Service layer for constituency-related business logic.
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

from app.models import Constituency, State
from app.services.base_service import BaseService
from app.core.exceptions import ValidationError
from app.schemas.constituency import ConstituencyFilterSchema


class ConstituencyService(BaseService[Constituency]):
    """Service for constituency-related operations."""
    
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, Constituency)
    
    def create_constituency(self, data: Dict[str, Any]) -> Constituency:
        """
        Create a new constituency with validation.
        
        Args:
            data: Constituency data dictionary
            
        Returns:
            Created constituency instance
            
        Raises:
            ValidationError: If state doesn't exist
        """
        # Validate state exists
        state = State.query.get(data['state_id'])
        if not state:
            raise ValidationError(f"State with ID '{data['state_id']}' does not exist", field="state_id")
        
        return self.create(data)
    
    def get_constituencies_by_filter(self, filters: ConstituencyFilterSchema) -> List[Constituency]:
        """
        Get constituencies filtered by provided criteria.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List of filtered constituencies
        """
        try:
            query = Constituency.query
            
            if filters.state_id:
                query = query.filter(Constituency.state_id == filters.state_id)
            
            return query.all()
            
        except Exception as e:
            self.logger.log_error(
                operation="get_constituencies_by_filter",
                table=self.model_class.__tablename__,
                error=str(e),
                filters=filters.dict()
            )
            raise
    
    def get_constituencies_by_state(self, state_id: str) -> List[Constituency]:
        """
        Get all constituencies for a specific state.
        
        Args:
            state_id: State identifier
            
        Returns:
            List of constituencies for the state
        """
        try:
            return Constituency.query.filter(Constituency.state_id == state_id).all()
        except Exception as e:
            self.logger.log_error(
                operation="get_constituencies_by_state",
                table=self.model_class.__tablename__,
                error=str(e),
                state_id=state_id
            )
            raise
    
    def import_scraped_constituencies(self, data_file_path: str) -> Dict[str, int]:
        """
        Import constituencies from scraped data file.
        
        Args:
            data_file_path: Path to the JSON data file
            
        Returns:
            Dictionary with import statistics
        """
        try:
            file_path = Path(data_file_path)
            if not file_path.exists():
                raise ValidationError(f"Data file not found: {data_file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            
            inserted = 0
            skipped = 0
            errors = 0
            
            for entry in scraped_data:
                try:
                    const_id = entry.get("constituency_id")
                    name = entry.get("constituency_name")
                    state_id = entry.get("state_id")
                    
                    # Validate required fields
                    if not const_id or not name or not state_id:
                        skipped += 1
                        continue
                    
                    # Check if constituency already exists
                    existing = self.get_by_id(const_id)
                    if existing:
                        skipped += 1
                        continue
                    
                    # Validate state exists
                    state = State.query.get(state_id)
                    if not state:
                        skipped += 1
                        continue
                    
                    # Create constituency
                    create_data = {
                        "id": const_id,
                        "name": name,
                        "state_id": state_id
                    }
                    
                    self.create(create_data)
                    inserted += 1
                    
                except Exception as e:
                    self.logger.log_error(
                        operation="import_constituency",
                        table=self.model_class.__tablename__,
                        error=str(e),
                        constituency_data=entry
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
                operation="import_scraped_constituencies",
                table=self.model_class.__tablename__,
                error=str(e),
                data_file_path=data_file_path
            )
            raise
