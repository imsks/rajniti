"""
Party Controller

Handles business logic for party-related operations.
"""

from typing import Any, Dict, List, Optional

from app.services import data_service


class PartyController:
    """Controller for party operations"""

    def __init__(self):
        self.data_service = data_service

    def get_parties_by_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get all parties for a specific election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None

        parties = self.data_service.get_parties(election_id)
        parties_data = [party.dict() for party in parties]

        return {
            "election_id": election_id,
            "total_parties": len(parties_data),
            "parties": parties_data,
        }

    def get_party_by_name(
        self, party_name: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get specific party details"""
        party = self.data_service.get_party_by_name(party_name, election_id)
        if not party:
            return None

        return {"election_id": election_id, "party": party.dict()}

    def get_party_performance(
        self, party_name: str, election_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get party performance across elections"""
        results = {}
        elections = (
            [self.data_service.get_election(election_id)]
            if election_id
            else self.data_service.get_elections()
        )

        for election in elections:
            if not election:
                continue

            # Get party info
            party = self.data_service.get_party_by_name(party_name, election.id)
            if not party:
                continue

            # Get candidates from this party
            candidates = self.data_service.get_candidates(election.id)
            party_candidates = []
            winners = 0
            total_votes = 0

            for candidate in candidates:
                party_field = candidate.get("Party", "")
                if party_field.lower() == party_name.lower():
                    party_candidates.append(candidate)

                    # Count winners
                    status = candidate.get("Status") or candidate.get("status", "")
                    if status == "WON":
                        winners += 1

                    # Sum votes
                    votes_str = candidate.get("Votes") or candidate.get("votes", "0")
                    try:
                        votes = int(str(votes_str).replace(",", ""))
                        total_votes += votes
                    except (ValueError, TypeError):
                        pass

            results[election.id] = {
                "election_name": election.name,
                "party_info": party.dict(),
                "candidates_count": len(party_candidates),
                "seats_won": winners,
                "total_votes": total_votes,
                "win_percentage": round((winners / len(party_candidates) * 100), 2)
                if party_candidates
                else 0,
            }

        return {"party_name": party_name, "performance_by_election": results}

    def get_all_parties(self) -> Dict[str, Any]:
        """Get all parties across all elections"""
        all_parties = {}

        for election in self.data_service.get_elections():
            parties = self.data_service.get_parties(election.id)
            for party in parties:
                party_name = party.party_name
                if party_name not in all_parties:
                    all_parties[party_name] = {
                        "party_name": party_name,
                        "symbol": party.symbol,
                        "elections": [],
                        "total_seats": 0,
                    }

                all_parties[party_name]["elections"].append(
                    {
                        "election_id": election.id,
                        "election_name": election.name,
                        "seats_won": party.total_seats,
                    }
                )
                all_parties[party_name]["total_seats"] += party.total_seats

        return {
            "total_unique_parties": len(all_parties),
            "parties": list(all_parties.values()),
        }
