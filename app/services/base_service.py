"""
Base service class for common database operations.
"""
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy

from app.core.exceptions import DatabaseError, NotFoundError, ConflictError
from app.core.logging_config import DatabaseLogger

T = TypeVar('T')


class BaseService(Generic[T]):
    """Base service class with common CRUD operations."""
    
    def __init__(self, db: SQLAlchemy, model_class: Type[T]):
        """
        Initialize base service.
        
        Args:
            db: SQLAlchemy database instance
            model_class: SQLAlchemy model class
        """
        self.db = db
        self.model_class = model_class
        self.logger = DatabaseLogger()
    
    def get_by_id(self, id_value: Any) -> Optional[T]:
        """
        Get a record by its ID.
        
        Args:
            id_value: ID value to search for
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            return self.model_class.query.get(id_value)
        except SQLAlchemyError as e:
            self.logger.log_error(
                operation="get_by_id",
                table=self.model_class.__tablename__,
                error=str(e),
                id_value=id_value
            )
            raise DatabaseError(f"Failed to get {self.model_class.__name__} by ID", operation="get_by_id")
    
    def get_by_id_or_404(self, id_value: Any) -> T:
        """
        Get a record by its ID, raise NotFoundError if not found.
        
        Args:
            id_value: ID value to search for
            
        Returns:
            Model instance
            
        Raises:
            NotFoundError: If record not found
        """
        record = self.get_by_id(id_value)
        if not record:
            raise NotFoundError(self.model_class.__name__, str(id_value))
        return record
    
    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
        """
        Get all records with optional pagination.
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        try:
            query = self.model_class.query
            
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
                
            return query.all()
        except SQLAlchemyError as e:
            self.logger.log_error(
                operation="get_all",
                table=self.model_class.__tablename__,
                error=str(e),
                limit=limit,
                offset=offset
            )
            raise DatabaseError(f"Failed to get all {self.model_class.__name__} records", operation="get_all")
    
    def count(self) -> int:
        """
        Get total count of records.
        
        Returns:
            Total number of records
        """
        try:
            return self.model_class.query.count()
        except SQLAlchemyError as e:
            self.logger.log_error(
                operation="count",
                table=self.model_class.__tablename__,
                error=str(e)
            )
            raise DatabaseError(f"Failed to count {self.model_class.__name__} records", operation="count")
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create a new record.
        
        Args:
            data: Dictionary of field values
            
        Returns:
            Created model instance
            
        Raises:
            ConflictError: If record already exists
            DatabaseError: If creation fails
        """
        try:
            record = self.model_class(**data)
            self.db.session.add(record)
            self.db.session.commit()
            
            self.logger.log_query(
                operation="create",
                table=self.model_class.__tablename__,
                duration=0.0,
                record_id=getattr(record, 'id', None)
            )
            
            return record
            
        except IntegrityError as e:
            self.db.session.rollback()
            self.logger.log_error(
                operation="create",
                table=self.model_class.__tablename__,
                error=str(e)
            )
            raise ConflictError(f"{self.model_class.__name__} already exists or violates constraints")
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self.logger.log_error(
                operation="create",
                table=self.model_class.__tablename__,
                error=str(e)
            )
            raise DatabaseError(f"Failed to create {self.model_class.__name__}", operation="create")
    
    def update(self, id_value: Any, data: Dict[str, Any]) -> T:
        """
        Update an existing record.
        
        Args:
            id_value: ID of the record to update
            data: Dictionary of field values to update
            
        Returns:
            Updated model instance
            
        Raises:
            NotFoundError: If record not found
            DatabaseError: If update fails
        """
        try:
            record = self.get_by_id_or_404(id_value)
            
            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)
            
            self.db.session.commit()
            
            self.logger.log_query(
                operation="update",
                table=self.model_class.__tablename__,
                duration=0.0,
                record_id=id_value
            )
            
            return record
            
        except NotFoundError:
            raise
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self.logger.log_error(
                operation="update",
                table=self.model_class.__tablename__,
                error=str(e),
                record_id=id_value
            )
            raise DatabaseError(f"Failed to update {self.model_class.__name__}", operation="update")
    
    def delete(self, id_value: Any) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id_value: ID of the record to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If record not found
            DatabaseError: If deletion fails
        """
        try:
            record = self.get_by_id_or_404(id_value)
            
            self.db.session.delete(record)
            self.db.session.commit()
            
            self.logger.log_query(
                operation="delete",
                table=self.model_class.__tablename__,
                duration=0.0,
                record_id=id_value
            )
            
            return True
            
        except NotFoundError:
            raise
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self.logger.log_error(
                operation="delete",
                table=self.model_class.__tablename__,
                error=str(e),
                record_id=id_value
            )
            raise DatabaseError(f"Failed to delete {self.model_class.__name__}", operation="delete")
    
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple records in bulk.
        
        Args:
            data_list: List of dictionaries with field values
            
        Returns:
            List of created model instances
            
        Raises:
            DatabaseError: If bulk creation fails
        """
        try:
            records = [self.model_class(**data) for data in data_list]
            self.db.session.add_all(records)
            self.db.session.commit()
            
            self.logger.log_query(
                operation="bulk_create",
                table=self.model_class.__tablename__,
                duration=0.0,
                count=len(records)
            )
            
            return records
            
        except SQLAlchemyError as e:
            self.db.session.rollback()
            self.logger.log_error(
                operation="bulk_create",
                table=self.model_class.__tablename__,
                error=str(e),
                count=len(data_list)
            )
            raise DatabaseError(f"Failed to bulk create {self.model_class.__name__} records", operation="bulk_create")
