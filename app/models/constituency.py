"""
Constituency data model based on existing JSON structure
"""

from pydantic import BaseModel, Field


class Constituency(BaseModel):
    """Constituency model matching existing JSON structure"""
    constituency_name: str = Field(alias="constituency_name")
    constituency_id: str = Field(alias="constituency_id")
    state_id: str = Field(alias="state_id")
    
    class Config:
        allow_population_by_field_name = True
