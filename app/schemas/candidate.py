"""
Schemas for candidate-related API validation.
"""
from enum import Enum
from typing import Optional
from uuid import UUID
from pydantic import Field, validator, HttpUrl

from .base import BaseSchema


class CandidateStatus(str, Enum):
    """Candidate status enumeration."""
    WON = "won"
    LOST = "lost"


class CandidateCreateSchema(BaseSchema):
    """Schema for creating a candidate."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Candidate name")
    photo: Optional[HttpUrl] = Field(None, description="Candidate photo URL")
    const_id: str = Field(..., min_length=1, max_length=50, description="Constituency ID")
    party_id: str = Field(..., min_length=1, max_length=100, description="Party ID")
    status: Optional[CandidateStatus] = Field(None, description="Candidate status")
    elec_type: str = Field(..., min_length=1, max_length=50, description="Election type")
    
    @validator('name')
    def validate_name(cls, v):
        """Validate candidate name."""
        if not v.strip():
            raise ValueError("Candidate name cannot be empty")
        # Skip NOTA candidates
        if v.strip().upper() == "NOTA":
            raise ValueError("NOTA candidates are not allowed")
        return v.strip()


class CandidateUpdateSchema(BaseSchema):
    """Schema for updating a candidate."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Candidate name")
    photo: Optional[HttpUrl] = Field(None, description="Candidate photo URL")
    status: Optional[CandidateStatus] = Field(None, description="Candidate status")


class CandidateResponseSchema(BaseSchema):
    """Schema for candidate response."""
    
    id: UUID = Field(..., description="Candidate ID")
    name: str = Field(..., description="Candidate name")
    photo: Optional[str] = Field(None, description="Candidate photo URL")
    const_id: str = Field(..., description="Constituency ID")
    party_id: str = Field(..., description="Party ID")
    status: Optional[CandidateStatus] = Field(None, description="Candidate status")
    elec_type: str = Field(..., description="Election type")


class CandidateFilterSchema(BaseSchema):
    """Schema for filtering candidates."""
    
    const_id: Optional[str] = Field(None, description="Filter by constituency ID")
    party_id: Optional[str] = Field(None, description="Filter by party ID")
    status: Optional[CandidateStatus] = Field(None, description="Filter by status")
    elec_type: Optional[str] = Field(None, description="Filter by election type")
