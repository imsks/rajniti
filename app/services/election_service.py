"""
Service layer for election-related business logic.
"""
from typing import List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

from app.models import Election, State
from app.services.base_service import BaseService
from app.core.exceptions import ValidationError, NotFoundError
from app.schemas.election import ElectionFilterSchema


class ElectionService(BaseService[Election]):
    """Service for election-related operations."""
    
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, Election)
    
    def create_election(self, data: Dict[str, Any]) -> Election:
        """
        Create a new election with validation.
        
        Args:
            data: Election data dictionary
            
        Returns:
            Created election instance
            
        Raises:
            ValidationError: If state doesn't exist
        """
        # Validate that state exists
        state = State.query.get(data['state_id'])
        if not state:
            raise ValidationError(f"State with ID '{data['state_id']}' does not exist", field="state_id")
        
        return self.create(data)
    
    def get_elections_by_filter(self, filters: ElectionFilterSchema) -> List[Election]:
        """
        Get elections filtered by provided criteria.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List of filtered elections
        """
        try:
            query = Election.query
            
            if filters.state_id:
                query = query.filter(Election.state_id == filters.state_id)
            
            if filters.year:
                query = query.filter(Election.year == filters.year)
            
            if filters.type:
                query = query.filter(Election.type == filters.type.value)
            
            return query.all()
            
        except Exception as e:
            self.logger.log_error(
                operation="get_elections_by_filter",
                table=self.model_class.__tablename__,
                error=str(e),
                filters=filters.dict()
            )
            raise
    
    def get_elections_by_state(self, state_id: str) -> List[Election]:
        """
        Get all elections for a specific state.
        
        Args:
            state_id: State identifier
            
        Returns:
            List of elections for the state
        """
        try:
            return Election.query.filter(Election.state_id == state_id).all()
        except Exception as e:
            self.logger.log_error(
                operation="get_elections_by_state",
                table=self.model_class.__tablename__,
                error=str(e),
                state_id=state_id
            )
            raise
    
    def get_elections_by_year(self, year: int) -> List[Election]:
        """
        Get all elections for a specific year.
        
        Args:
            year: Election year
            
        Returns:
            List of elections for the year
        """
        try:
            return Election.query.filter(Election.year == year).all()
        except Exception as e:
            self.logger.log_error(
                operation="get_elections_by_year",
                table=self.model_class.__tablename__,
                error=str(e),
                year=year
            )
            raise
    
    def check_election_exists(self, state_id: str, year: int, election_type: str) -> bool:
        """
        Check if an election already exists for given parameters.
        
        Args:
            state_id: State identifier
            year: Election year
            election_type: Type of election
            
        Returns:
            True if election exists, False otherwise
        """
        try:
            existing = Election.query.filter(
                Election.state_id == state_id,
                Election.year == year,
                Election.type == election_type
            ).first()
            
            return existing is not None
            
        except Exception as e:
            self.logger.log_error(
                operation="check_election_exists",
                table=self.model_class.__tablename__,
                error=str(e),
                state_id=state_id,
                year=year,
                election_type=election_type
            )
            raise
