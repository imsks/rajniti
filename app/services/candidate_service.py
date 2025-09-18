"""
Service layer for candidate-related business logic.
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy

from app.models import Candidate, Constituency, Party
from app.services.base_service import BaseService
from app.core.exceptions import ValidationError
from app.schemas.candidate import CandidateFilterSchema


class CandidateService(BaseService[Candidate]):
    """Service for candidate-related operations."""
    
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, Candidate)
    
    def create_candidate(self, data: Dict[str, Any]) -> Candidate:
        """
        Create a new candidate with validation.
        
        Args:
            data: Candidate data dictionary
            
        Returns:
            Created candidate instance
            
        Raises:
            ValidationError: If constituency or party doesn't exist
        """
        # Validate constituency exists
        constituency = Constituency.query.get(data['const_id'])
        if not constituency:
            raise ValidationError(f"Constituency with ID '{data['const_id']}' does not exist", field="const_id")
        
        # Validate party exists
        party = Party.query.get(data['party_id'])
        if not party:
            raise ValidationError(f"Party with ID '{data['party_id']}' does not exist", field="party_id")
        
        return self.create(data)
    
    def get_candidates_by_filter(self, filters: CandidateFilterSchema) -> List[Candidate]:
        """
        Get candidates filtered by provided criteria.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List of filtered candidates
        """
        try:
            query = Candidate.query
            
            if filters.const_id:
                query = query.filter(Candidate.const_id == filters.const_id)
            
            if filters.party_id:
                query = query.filter(Candidate.party_id == filters.party_id)
            
            if filters.status:
                query = query.filter(Candidate.status == filters.status.value)
            
            if filters.elec_type:
                query = query.filter(Candidate.elec_type == filters.elec_type)
            
            return query.all()
            
        except Exception as e:
            self.logger.log_error(
                operation="get_candidates_by_filter",
                table=self.model_class.__tablename__,
                error=str(e),
                filters=filters.dict()
            )
            raise
    
    def get_candidates_by_constituency(self, const_id: str) -> List[Candidate]:
        """Get all candidates for a constituency."""
        try:
            return Candidate.query.filter(Candidate.const_id == const_id).all()
        except Exception as e:
            self.logger.log_error(
                operation="get_candidates_by_constituency",
                table=self.model_class.__tablename__,
                error=str(e),
                const_id=const_id
            )
            raise
    
    def get_candidates_by_party(self, party_id: str) -> List[Candidate]:
        """Get all candidates for a party."""
        try:
            return Candidate.query.filter(Candidate.party_id == party_id).all()
        except Exception as e:
            self.logger.log_error(
                operation="get_candidates_by_party",
                table=self.model_class.__tablename__,
                error=str(e),
                party_id=party_id
            )
            raise
    
    def import_scraped_candidates(self, data_file_path: str, election_type: str) -> Dict[str, int]:
        """
        Import candidates from scraped data file.
        
        Args:
            data_file_path: Path to the JSON data file
            election_type: Type of election
            
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
                    # Skip NOTA candidates
                    name = entry.get("Name", "").strip()
                    if name.upper() == "NOTA":
                        skipped += 1
                        continue
                    
                    # Validate required fields
                    const_id = entry.get("Constituency Code")
                    party_name = entry.get("Party")
                    
                    if not name or not const_id or not party_name:
                        skipped += 1
                        continue
                    
                    # Check if constituency exists
                    constituency = Constituency.query.get(const_id)
                    if not constituency:
                        skipped += 1
                        continue
                    
                    # Check if candidate already exists
                    existing = Candidate.query.filter(
                        Candidate.name == name,
                        Candidate.const_id == const_id,
                        Candidate.party_id == party_name,
                        Candidate.elec_type == election_type
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Create candidate
                    create_data = {
                        "name": name,
                        "photo": entry.get("Image URL"),
                        "const_id": const_id,
                        "party_id": party_name,
                        "status": entry.get("Status", "").lower() if entry.get("Status") else None,
                        "elec_type": election_type
                    }
                    
                    self.create(create_data)
                    inserted += 1
                    
                except Exception as e:
                    self.logger.log_error(
                        operation="import_candidate",
                        table=self.model_class.__tablename__,
                        error=str(e),
                        candidate_data=entry
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
                operation="import_scraped_candidates",
                table=self.model_class.__tablename__,
                error=str(e),
                data_file_path=data_file_path
            )
            raise
