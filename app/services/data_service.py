"""
Abstract Data Service Interface

This defines the contract for data access. 
Implementations can use JSON, database, or any other storage mechanism.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.models import (AssemblyCandidate, Constituency, Election,
                        LokSabhaCandidate, Party)


class DataService(ABC):
    """Abstract data service interface"""

    @abstractmethod
    def get_elections(self) -> List[Election]:
        """Get all available elections"""
        pass

    @abstractmethod
    def get_election(self, election_id: str) -> Optional[Election]:
        """Get a specific election by ID"""
        pass

    @abstractmethod
    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election"""
        pass

    @abstractmethod
    def get_parties(self, election_id: str) -> List[Party]:
        """Get all parties for an election"""
        pass

    @abstractmethod
    def get_constituencies(self, election_id: str) -> List[Constituency]:
        """Get all constituencies for an election"""
        pass

    @abstractmethod
    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search candidates by name, party, or constituency"""
        pass

    @abstractmethod
    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific candidate"""
        pass

    @abstractmethod
    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Party]:
        """Get a specific party"""
        pass

    @abstractmethod
    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Constituency]:
        """Get a specific constituency"""
        pass
