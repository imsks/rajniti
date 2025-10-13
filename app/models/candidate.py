"""
Candidate data models based on existing JSON structure
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CandidateStatus(str, Enum):
    WON = "WON"
    LOST = "LOST"


class Candidate(BaseModel):
    """Base candidate model"""

    id: Optional[str] = None  # UUID for the candidate
    name: str
    party: str
    constituency: str
    votes: int
    margin: int
    status: Optional[CandidateStatus] = None


class LokSabhaCandidate(BaseModel):
    """Lok Sabha candidate model matching existing JSON structure"""

    id: Optional[str] = None  # UUID for the candidate
    party_id: int
    constituency: str
    candidate_name: str = Field(alias="candidate_name")
    votes: str  # Keep as string since that's how it's stored
    margin: str  # Keep as string since that's how it's stored

    class Config:
        allow_population_by_field_name = True


class AssemblyCandidate(BaseModel):
    """Assembly candidate model matching existing JSON structure"""

    id: Optional[str] = Field(alias="ID", default=None)  # UUID for the candidate
    constituency_code: str = Field(alias="Constituency Code")
    name: str = Field(alias="Name")
    party: str = Field(alias="Party")
    status: CandidateStatus = Field(alias="Status")
    votes: str = Field(alias="Votes")
    margin: str = Field(alias="Margin")
    image_url: Optional[str] = Field(alias="Image URL", default=None)

    class Config:
        allow_population_by_field_name = True
