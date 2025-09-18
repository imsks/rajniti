"""
Database manager for handling all database operations.
Provides a clean interface that gracefully handles disabled database functionality.
"""
from typing import List, Dict, Any, Optional, Union
from flask import current_app

from app.core.logging_config import get_logger
from app.core.exceptions import DatabaseError
from .db_config import DatabaseConfig


class DatabaseManager:
    """Manages all database operations with optional functionality."""
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None):
        """
        Initialize the database manager.
        
        Args:
            db_config: Database configuration instance
        """
        self.db_config = db_config
        self.logger = get_logger("rajniti.database_manager")
    
    def is_available(self) -> bool:
        """Check if database functionality is available."""
        return self.db_config is not None and self.db_config.is_enabled()
    
    def execute_query(self, operation: str, *args, **kwargs) -> Optional[Any]:
        """
        Execute a database operation if database is available.
        
        Args:
            operation: The operation to perform
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation or None if database is not available
        """
        if not self.is_available():
            self.logger.debug(f"Database not available, skipping operation: {operation}")
            return None
        
        try:
            # Here we would implement specific database operations
            # For now, we'll just log the operation
            self.logger.info(f"Database operation: {operation}", args=args, kwargs=kwargs)
            return True
        except Exception as e:
            self.logger.error(f"Database operation failed: {operation}", error=str(e))
            raise DatabaseError(f"Database operation failed: {str(e)}", operation=operation)
    
    def insert_candidates(self, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert candidate data into database.
        
        Args:
            candidates: List of candidate dictionaries
            
        Returns:
            Dictionary with insertion results
        """
        if not self.is_available():
            return {"success": False, "message": "Database not available", "inserted": 0}
        
        try:
            from app.models.models import Candidate
            from sqlalchemy.exc import IntegrityError
            
            db = self.db_config.db
            inserted = 0
            skipped = 0
            errors = []
            
            for candidate_data in candidates:
                try:
                    # Check if candidate already exists
                    existing = Candidate.query.filter_by(
                        name=candidate_data.get("name", ""),
                        const_id=candidate_data.get("const_id", ""),
                        party_id=candidate_data.get("party_id", "")
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    # Create new candidate
                    candidate = Candidate(
                        name=candidate_data.get("name", ""),
                        photo=candidate_data.get("photo"),
                        const_id=candidate_data.get("const_id", ""),
                        party_id=candidate_data.get("party_id", ""),
                        status=candidate_data.get("status"),
                        elec_type=candidate_data.get("elec_type", "")
                    )
                    
                    db.session.add(candidate)
                    inserted += 1
                    
                except IntegrityError as e:
                    db.session.rollback()
                    errors.append(f"Integrity error for candidate {candidate_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
                except Exception as e:
                    errors.append(f"Error inserting candidate {candidate_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
            
            if inserted > 0:
                db.session.commit()
            
            return {
                "success": True,
                "inserted": inserted,
                "skipped": skipped,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error("Failed to insert candidates", error=str(e))
            return {"success": False, "message": str(e), "inserted": 0}
    
    def insert_parties(self, parties: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert party data into database.
        
        Args:
            parties: List of party dictionaries
            
        Returns:
            Dictionary with insertion results
        """
        if not self.is_available():
            return {"success": False, "message": "Database not available", "inserted": 0}
        
        try:
            from app.models.models import Party
            from sqlalchemy.exc import IntegrityError
            
            db = self.db_config.db
            inserted = 0
            updated = 0
            skipped = 0
            errors = []
            
            for party_data in parties:
                try:
                    party_name = party_data.get("name", "")
                    if not party_name:
                        skipped += 1
                        continue
                    
                    # Check if party already exists
                    existing = Party.query.get(party_name)
                    
                    if existing:
                        # Update total_seats if provided
                        if "total_seats" in party_data and party_data["total_seats"] is not None:
                            existing.total_seats = party_data["total_seats"]
                            updated += 1
                        else:
                            skipped += 1
                        continue
                    
                    # Create new party
                    party = Party(
                        name=party_name,
                        symbol=party_data.get("symbol", ""),
                        total_seats=party_data.get("total_seats")
                    )
                    
                    db.session.add(party)
                    inserted += 1
                    
                except IntegrityError as e:
                    db.session.rollback()
                    errors.append(f"Integrity error for party {party_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
                except Exception as e:
                    errors.append(f"Error inserting party {party_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
            
            if inserted > 0 or updated > 0:
                db.session.commit()
            
            return {
                "success": True,
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error("Failed to insert parties", error=str(e))
            return {"success": False, "message": str(e), "inserted": 0}
    
    def insert_constituencies(self, constituencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Insert constituency data into database.
        
        Args:
            constituencies: List of constituency dictionaries
            
        Returns:
            Dictionary with insertion results
        """
        if not self.is_available():
            return {"success": False, "message": "Database not available", "inserted": 0}
        
        try:
            from app.models.models import Constituency
            from sqlalchemy.exc import IntegrityError
            
            db = self.db_config.db
            inserted = 0
            skipped = 0
            errors = []
            
            for const_data in constituencies:
                try:
                    const_id = const_data.get("id", const_data.get("code", ""))
                    if not const_id:
                        skipped += 1
                        continue
                    
                    # Check if constituency already exists
                    existing = Constituency.query.get(const_id)
                    if existing:
                        skipped += 1
                        continue
                    
                    # Create new constituency
                    constituency = Constituency(
                        id=const_id,
                        name=const_data.get("name", ""),
                        state_id=const_data.get("state_id", const_data.get("state", ""))
                    )
                    
                    db.session.add(constituency)
                    inserted += 1
                    
                except IntegrityError as e:
                    db.session.rollback()
                    errors.append(f"Integrity error for constituency {const_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
                except Exception as e:
                    errors.append(f"Error inserting constituency {const_data.get('name', 'Unknown')}: {str(e)}")
                    skipped += 1
            
            if inserted > 0:
                db.session.commit()
            
            return {
                "success": True,
                "inserted": inserted,
                "skipped": skipped,
                "errors": errors
            }
            
        except Exception as e:
            self.logger.error("Failed to insert constituencies", error=str(e))
            return {"success": False, "message": str(e), "inserted": 0}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics if available."""
        if not self.is_available():
            return {"available": False, "message": "Database not available"}
        
        try:
            from app.models.models import Candidate, Party, Constituency, Election, State
            
            stats = {
                "available": True,
                "tables": {
                    "candidates": Candidate.query.count(),
                    "parties": Party.query.count(),
                    "constituencies": Constituency.query.count(),
                    "elections": Election.query.count(),
                    "states": State.query.count()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error("Failed to get database statistics", error=str(e))
            return {"available": False, "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a database health check."""
        if not self.is_available():
            return {
                "status": "disabled",
                "message": "Database functionality is disabled"
            }
        
        try:
            db = self.db_config.db
            # Try a simple query
            db.session.execute("SELECT 1")
            
            return {
                "status": "healthy",
                "message": "Database connection is working"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database connection failed: {str(e)}"
            }
