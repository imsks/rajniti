"""
Party data model based on existing JSON structure
"""

from pydantic import BaseModel, Field


class Party(BaseModel):
    """Party model matching existing JSON structure"""

    party_name: str = Field(alias="party_name")
    symbol: str
    total_seats: int = Field(alias="total_seats")

    class Config:
        allow_population_by_field_name = True
