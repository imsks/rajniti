"""
Election data model 
"""

from pydantic import BaseModel
from enum import Enum
from typing import Optional


class ElectionType(str, Enum):
    LOK_SABHA = "LOK_SABHA"
    VIDHAN_SABHA = "VIDHAN_SABHA"


class Election(BaseModel):
    """Election model for organizing our data"""
    id: str  # e.g., "lok-sabha-2024", "delhi-assembly-2025"
    name: str
    type: ElectionType
    year: int
    state: Optional[str] = None  # Only for state elections
    state_code: Optional[str] = None  # e.g., "DL", "MH"
