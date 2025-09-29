"""
Election Controller

Handles business logic for election-related operations.
"""

from typing import Any, Dict, List, Optional

from app.services import data_service


class ElectionController:
    """Controller for election operations"""

    def __init__(self):
        self.data_service = data_service

    def get_all_elections(self) -> List[Dict[str, Any]]:
        """Get all elections with basic statistics"""
        elections = self.data_service.get_elections()
        result = []

        for election in elections:
            election_data = election.dict()

            # Add basic statistics
            candidates = self.data_service.get_candidates(election.id)
            parties = self.data_service.get_parties(election.id)
            constituencies = self.data_service.get_constituencies(election.id)

            election_data["statistics"] = {
                "total_candidates": len(candidates),
                "total_parties": len(parties),
                "total_constituencies": len(constituencies),
            }

            result.append(election_data)

        return result

    def get_election_by_id(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get election details with comprehensive statistics"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        result = election.dict()

        # Get detailed statistics
        candidates = self.data_service.get_candidates(election_id)
        parties = self.data_service.get_parties(election_id)
        constituencies = self.data_service.get_constituencies(election_id)

        # Count winners
        winners_count = 0
        total_votes = 0

        for candidate in candidates:
            status = candidate.get("Status") or candidate.get("status", "")
            if status == "WON":
                winners_count += 1

            # Try to get vote count
            votes_str = candidate.get("Votes") or candidate.get("votes", "0")
            try:
                votes = int(str(votes_str).replace(",", ""))
                total_votes += votes
            except (ValueError, TypeError):
                pass

        result["statistics"] = {
            "total_candidates": len(candidates),
            "total_parties": len(parties),
            "total_constituencies": len(constituencies),
            "total_winners": winners_count,
            "total_votes": total_votes,
        }

        return result

    def get_election_results(
        self, election_id: str, limit: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """Get election results with candidates"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        candidates = self.data_service.get_candidates(election_id)

        if limit:
            candidates = candidates[:limit]

        return {
            "election": election.dict(),
            "total_candidates": len(candidates),
            "candidates": candidates,
        }

    def get_election_winners(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get only winning candidates for an election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        all_candidates = self.data_service.get_candidates(election_id)
        winners = []

        for candidate in all_candidates:
            status = candidate.get("Status") or candidate.get("status", "")
            if status == "WON":
                winners.append(candidate)

        return {
            "election": election.dict(),
            "total_winners": len(winners),
            "winners": winners,
        }
