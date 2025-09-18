"""
Schemas for constituency-related API validation.
"""
from typing import Optional
from uuid import UUID
from pydantic import Field, validator

from .base import BaseSchema


class ConstituencyCreateSchema(BaseSchema):
    """Schema for creating a constituency."""
    
    id: str = Field(..., min_length=1, max_length=50, description="Constituency ID")
    name: str = Field(..., min_length=1, max_length=200, description="Constituency name")
    state_id: str = Field(..., min_length=2, max_length=10, description="State ID")
    mla_id: Optional[UUID] = Field(None, description="MLA candidate ID")
    mp_id: Optional[UUID] = Field(None, description="MP candidate ID")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate constituency name."""
        if not v.strip():
            raise ValueError("Constituency name cannot be empty")
        return v.strip()
    
    @validator('id')
    def validate_id(cls, v):
        """Validate constituency ID."""
        if not v.strip():
            raise ValueError("Constituency ID cannot be empty")
        return v.strip()


class ConstituencyUpdateSchema(BaseSchema):
    """Schema for updating a constituency."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Constituency name")
    mla_id: Optional[UUID] = Field(None, description="MLA candidate ID")
    mp_id: Optional[UUID] = Field(None, description="MP candidate ID")


class ConstituencyResponseSchema(BaseSchema):
    """Schema for constituency response."""
    
    id: str = Field(..., description="Constituency ID")
    name: str = Field(..., description="Constituency name")
    state_id: str = Field(..., description="State ID")
    mla_id: Optional[UUID] = Field(None, description="MLA candidate ID")
    mp_id: Optional[UUID] = Field(None, description="MP candidate ID")


class ConstituencyFilterSchema(BaseSchema):
    """Schema for filtering constituencies."""
    
    state_id: Optional[str] = Field(None, description="Filter by state ID")
