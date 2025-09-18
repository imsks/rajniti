"""
Schemas for party-related API validation.
"""
from typing import Optional
from pydantic import Field, validator

from .base import BaseSchema


class PartyCreateSchema(BaseSchema):
    """Schema for creating a party."""
    
    name: str = Field(..., min_length=1, max_length=100, description="Party name")
    symbol: str = Field(..., min_length=1, max_length=100, description="Party symbol")
    total_seats: Optional[int] = Field(None, ge=0, description="Total seats won")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate party name."""
        if not v.strip():
            raise ValueError("Party name cannot be empty")
        return v.strip()
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate party symbol."""
        if not v.strip():
            raise ValueError("Party symbol cannot be empty")
        return v.strip()


class PartyUpdateSchema(BaseSchema):
    """Schema for updating a party."""
    
    symbol: Optional[str] = Field(None, min_length=1, max_length=100, description="Party symbol")
    total_seats: Optional[int] = Field(None, ge=0, description="Total seats won")


class PartyResponseSchema(BaseSchema):
    """Schema for party response."""
    
    name: str = Field(..., description="Party name")
    symbol: str = Field(..., description="Party symbol")
    total_seats: Optional[int] = Field(None, description="Total seats won")


class PartySearchSchema(BaseSchema):
    """Schema for searching parties."""
    
    name: Optional[str] = Field(None, min_length=1, description="Search by party name")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate search name."""
        if v and not v.strip():
            raise ValueError("Search name cannot be empty")
        return v.strip() if v else None
