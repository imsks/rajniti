"""
Candidate Controller

Handles business logic for candidate-related operations.
"""

from typing import Any, Dict, Optional

from app.services import data_service


class CandidateController:
    """Controller for candidate operations"""

    def __init__(self):
        self.data_service = data_service

    def search_candidates(
        self, query: str, election_id: Optional[str] = None, limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Search candidates across elections"""
        results = self.data_service.search_candidates(query, election_id)

        if limit:
            results = results[:limit]

        return {
            "query": query,
            "election_id": election_id,
            "total_results": len(results),
            "candidates": results,
        }

    def get_candidates_by_election(
        self, election_id: str, limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get all candidates for a specific election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        candidates = self.data_service.get_candidates(election_id)

        if limit:
            candidates = candidates[:limit]

        return {
            "election_id": election_id,
            "total_candidates": len(candidates),
            "candidates": candidates,
        }

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific candidate details"""
        candidate = self.data_service.get_candidate_by_id(candidate_id, election_id)
        if not candidate:
            return None

        candidate_with_election = candidate.copy()
        candidate_with_election["election_id"] = election_id
        return candidate_with_election

    def get_candidates_by_party(
        self, party_name: str, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all candidates from a specific party"""
        results = []
        elections = (
            [self.data_service.get_election(election_id)]
            if election_id
            else self.data_service.get_elections()
        )

        for election in elections:
            if not election:
                continue

            candidates = self.data_service.get_candidates(election.id)

            for candidate in candidates:
                party_field = candidate.get("Party", "")
                if party_field.lower() == party_name.lower():
                    candidate_with_election = candidate.copy()
                    candidate_with_election["election_id"] = election.id
                    results.append(candidate_with_election)

        return {
            "party_name": party_name,
            "election_id": election_id,
            "total_candidates": len(results),
            "candidates": results,
        }

    def get_candidates_by_constituency(
        self, constituency_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get all candidates from a specific constituency"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        candidates = self.data_service.get_candidates(election_id)
        constituency_candidates = []

        for candidate in candidates:
            const_field = candidate.get("constituency") or candidate.get(
                "Constituency Code", ""
            )
            if const_field.lower() == constituency_id.lower():
                constituency_candidates.append(candidate)

        return {
            "constituency_id": constituency_id,
            "election_id": election_id,
            "total_candidates": len(constituency_candidates),
            "candidates": constituency_candidates,
        }

    def get_winning_candidates(
        self, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get all winning candidates"""
        results = []
        elections = (
            [self.data_service.get_election(election_id)]
            if election_id
            else self.data_service.get_elections()
        )

        for election in elections:
            if not election:
                continue

            candidates = self.data_service.get_candidates(election.id)

            for candidate in candidates:
                status = candidate.get("Status") or candidate.get("status", "")
                if status == "WON":
                    candidate_with_election = candidate.copy()
                    candidate_with_election["election_id"] = election.id
                    results.append(candidate_with_election)

        return {
            "election_id": election_id,
            "total_winners": len(results),
            "winners": results,
        }
