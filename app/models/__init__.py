"""
Data Models for Rajniti Election API

Simple Pydantic models that match our existing JSON data structure.
These models can be used with JSON storage now and easily adapted for DB later.
"""

from .candidate import Candidate, LokSabhaCandidate, AssemblyCandidate
from .party import Party
from .constituency import Constituency
from .election import Election

__all__ = [
    "Candidate",
    "LokSabhaCandidate", 
    "AssemblyCandidate",
    "Party",
    "Constituency", 
    "Election"
]