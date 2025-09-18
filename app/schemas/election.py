"""
Schemas for election-related API validation.
"""
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import Field, validator

from .base import BaseSchema


class ElectionType(str, Enum):
    """Election type enumeration."""
    LOKSABHA = "LOKSABHA"
    VIDHANSABHA = "VIDHANSABHA"


class ElectionCreateSchema(BaseSchema):
    """Schema for creating an election."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Election name")
    type: ElectionType = Field(..., description="Election type")
    year: int = Field(..., ge=1947, le=2100, description="Election year")
    state_id: str = Field(..., min_length=2, max_length=10, description="State ID")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate election name."""
        if not v.strip():
            raise ValueError("Election name cannot be empty")
        return v.strip()


class ElectionUpdateSchema(BaseSchema):
    """Schema for updating an election."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Election name")
    type: Optional[ElectionType] = Field(None, description="Election type")
    year: Optional[int] = Field(None, ge=1947, le=2100, description="Election year")
    state_id: Optional[str] = Field(None, min_length=2, max_length=10, description="State ID")


class ElectionResponseSchema(BaseSchema):
    """Schema for election response."""
    
    id: UUID = Field(..., description="Election ID")
    name: str = Field(..., description="Election name")
    type: ElectionType = Field(..., description="Election type")
    year: int = Field(..., description="Election year")
    state_id: str = Field(..., description="State ID")


class ElectionFilterSchema(BaseSchema):
    """Schema for filtering elections."""
    
    state_id: Optional[str] = Field(None, description="Filter by state ID")
    year: Optional[int] = Field(None, ge=1947, le=2100, description="Filter by year")
    type: Optional[ElectionType] = Field(None, description="Filter by election type")
