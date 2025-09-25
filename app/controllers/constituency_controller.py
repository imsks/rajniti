"""
Constituency Controller

Handles business logic for constituency-related operations.
"""

from typing import List, Optional, Dict, Any
from app.services import data_service


class ConstituencyController:
    """Controller for constituency operations"""
    
    def __init__(self):
        self.data_service = data_service
    
    def get_constituencies_by_election(self, election_id: str) -> Optional[Dict[str, Any]]:
        """Get all constituencies for a specific election"""
        election = self.data_service.get_election(election_id)
        if not election:
            return None
        
        constituencies = self.data_service.get_constituencies(election_id)
        constituencies_data = [const.dict() for const in constituencies]
        
        return {
            'election_id': election_id,
            'total_constituencies': len(constituencies_data),
            'constituencies': constituencies_data
        }
    
    def get_constituency_by_id(self, constituency_id: str, election_id: str) -> Optional[Dict[str, Any]]:
        """Get specific constituency details with results"""
        constituency = self.data_service.get_constituency_by_id(constituency_id, election_id)
        if not constituency:
            return None
        
        # Get candidates for this constituency
        candidates = self.data_service.get_candidates(election_id)
        constituency_candidates = []
        winner = None
        
        for candidate in candidates:
            const_field = candidate.get('constituency') or candidate.get('Constituency Code', '')
            if const_field.lower() == constituency_id.lower():
                constituency_candidates.append(candidate)
                
                # Find winner
                status = candidate.get('Status') or candidate.get('status', '')
                if status == 'WON':
                    winner = candidate
        
        # Sort candidates by votes (if available)
        try:
            constituency_candidates.sort(
                key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '')), 
                reverse=True
            )
        except (ValueError, TypeError):
            pass
        
        return {
            'constituency': constituency.dict(),
            'election_id': election_id,
            'total_candidates': len(constituency_candidates),
            'winner': winner,
            'all_candidates': constituency_candidates
        }
    
    def get_constituencies_by_state(self, state_code: str) -> Dict[str, Any]:
        """Get all constituencies in a specific state"""
        results = []
        
        for election in self.data_service.get_elections():
            if election.state_code == state_code:
                constituencies = self.data_service.get_constituencies(election.id)
                for const in constituencies:
                    const_data = const.dict()
                    const_data['election_id'] = election.id
                    const_data['election_name'] = election.name
                    results.append(const_data)
        
        return {
            'state_code': state_code,
            'total_constituencies': len(results),
            'constituencies': results
        }
    
    def get_constituency_results(self, constituency_id: str, election_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed results for a constituency"""
        constituency_data = self.get_constituency_by_id(constituency_id, election_id)
        if not constituency_data:
            return None
        
        candidates = constituency_data['all_candidates']
        
        # Calculate statistics
        total_votes = 0
        victory_margin = 0
        
        for candidate in candidates:
            votes_str = candidate.get('Votes') or candidate.get('votes', '0')
            try:
                votes = int(str(votes_str).replace(',', ''))
                total_votes += votes
            except (ValueError, TypeError):
                pass
        
        # Calculate victory margin (difference between 1st and 2nd)
        if len(candidates) >= 2:
            try:
                first_votes = int(str(candidates[0].get('Votes', candidates[0].get('votes', 0))).replace(',', ''))
                second_votes = int(str(candidates[1].get('Votes', candidates[1].get('votes', 0))).replace(',', ''))
                victory_margin = first_votes - second_votes
            except (ValueError, TypeError):
                victory_margin = 0
        
        return {
            'constituency': constituency_data['constituency'],
            'election_id': election_id,
            'total_candidates': len(candidates),
            'total_votes': total_votes,
            'victory_margin': victory_margin,
            'winner': constituency_data['winner'],
            'results': candidates
        }
