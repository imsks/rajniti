"""
JSON Data Service Implementation

Reads data from existing JSON files in the app/data directory.
This can be easily replaced with a database service later.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.models import Constituency, Election, ElectionType, Party

from .data_service import DataService


class JsonDataService(DataService):
    """JSON file-based data service"""

    def __init__(self):
        self.data_root = Path("app/data")
        self._elections_cache = None
        self._data_cache = {}

    def get_elections(self) -> List[Election]:
        """Get all available elections"""
        if self._elections_cache is None:
            self._elections_cache = [
                Election(
                    id="lok-sabha-2024",
                    name="Lok Sabha General Elections 2024",
                    type=ElectionType.LOK_SABHA,
                    year=2024,
                ),
                Election(
                    id="delhi-assembly-2025",
                    name="Delhi Legislative Assembly Elections 2025",
                    type=ElectionType.VIDHAN_SABHA,
                    year=2025,
                    state="Delhi",
                    state_code="DL",
                ),
                Election(
                    id="maharashtra-assembly-2024",
                    name="Maharashtra Legislative Assembly Elections 2024",
                    type=ElectionType.VIDHAN_SABHA,
                    year=2024,
                    state="Maharashtra",
                    state_code="MH",
                ),
            ]
        return self._elections_cache

    def get_election(self, election_id: str) -> Optional[Election]:
        """Get a specific election by ID"""
        elections = self.get_elections()
        for election in elections:
            if election.id == election_id:
                return election
        return None

    def _load_json_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load data from JSON file with caching"""
        cache_key = str(file_path)
        if cache_key not in self._data_cache:
            try:
                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        self._data_cache[cache_key] = json.load(f)
                else:
                    self._data_cache[cache_key] = []
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                self._data_cache[cache_key] = []
        return self._data_cache[cache_key]

    def get_candidates(self, election_id: str) -> List[Dict[str, Any]]:
        """Get all candidates for an election"""
        election = self.get_election(election_id)
        if not election:
            return []

        if election.type == ElectionType.LOK_SABHA:
            file_path = (
                self.data_root / "lok_sabha" / f"{election_id}" / "candidates.json"
            )
        else:
            if election.state_code == "DL":
                file_path = (
                    self.data_root
                    / "vidhan_sabha"
                    / "DL_2025_ASSEMBLY"
                    / "candidates.json"
                )
            elif election.state_code == "MH":
                file_path = (
                    self.data_root / "vidhan_sabha" / "MH_2024" / "candidates.json"
                )
            else:
                return []

        return self._load_json_file(file_path)

    def get_parties(self, election_id: str) -> List[Party]:
        """Get all parties for an election"""
        election = self.get_election(election_id)
        if not election:
            return []

        if election.type == ElectionType.LOK_SABHA:
            file_path = self.data_root / "lok_sabha" / f"{election_id}" / "parties.json"
        else:
            if election.state_code == "DL":
                file_path = (
                    self.data_root
                    / "vidhan_sabha"
                    / "DL_2025_ASSEMBLY"
                    / "parties.json"
                )
            elif election.state_code == "MH":
                file_path = self.data_root / "vidhan_sabha" / "MH_2024" / "parties.json"
            else:
                return []

        data = self._load_json_file(file_path)
        return [Party(**party_data) for party_data in data]

    def get_constituencies(self, election_id: str) -> List[Constituency]:
        """Get all constituencies for an election"""
        election = self.get_election(election_id)
        if not election:
            return []

        if election.type == ElectionType.LOK_SABHA:
            file_path = (
                self.data_root / "lok_sabha" / f"{election_id}" / "constituencies.json"
            )
        else:
            if election.state_code == "DL":
                file_path = (
                    self.data_root
                    / "vidhan_sabha"
                    / "DL_2025_ASSEMBLY"
                    / "constituencies.json"
                )
            elif election.state_code == "MH":
                file_path = (
                    self.data_root / "vidhan_sabha" / "MH_2024" / "constituencies.json"
                )
            else:
                return []

        data = self._load_json_file(file_path)
        return [Constituency(**const_data) for const_data in data]

    def search_candidates(
        self, query: str, election_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search candidates by name, party, or constituency"""
        results = []
        elections = (
            [self.get_election(election_id)] if election_id else self.get_elections()
        )

        for election in elections:
            if not election:
                continue

            candidates = self.get_candidates(election.id)
            query_lower = query.lower()

            for candidate in candidates:
                # Check different field names based on data structure
                name_field = candidate.get("candidate_name") or candidate.get(
                    "Name", ""
                )
                party_field = candidate.get("Party", "")
                constituency_field = candidate.get("constituency", "") or candidate.get(
                    "Constituency Code", ""
                )

                if (
                    query_lower in name_field.lower()
                    or query_lower in party_field.lower()
                    or query_lower in constituency_field.lower()
                ):
                    candidate_with_election = candidate.copy()
                    candidate_with_election["election_id"] = election.id
                    results.append(candidate_with_election)

        return results

    def get_candidate_by_id(
        self, candidate_id: str, election_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific candidate - simplified for JSON data"""
        candidates = self.get_candidates(election_id)
        # For simplicity, match by name since we don't have proper IDs in JSON
        for candidate in candidates:
            name_field = candidate.get("candidate_name") or candidate.get("Name", "")
            if name_field.replace(" ", "_").lower() == candidate_id.lower():
                return candidate
        return None

    def get_party_by_name(self, party_name: str, election_id: str) -> Optional[Party]:
        """Get a specific party"""
        parties = self.get_parties(election_id)
        for party in parties:
            if party.party_name.lower() == party_name.lower():
                return party
        return None

    def get_constituency_by_id(
        self, constituency_id: str, election_id: str
    ) -> Optional[Constituency]:
        """Get a specific constituency"""
        constituencies = self.get_constituencies(election_id)
        for constituency in constituencies:
            if constituency.constituency_id.lower() == constituency_id.lower():
                return constituency
        return None
