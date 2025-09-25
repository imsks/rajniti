"""
Candidates API Namespace

Provides endpoints for accessing candidate information, search functionality,
and candidate-specific analytics across all elections.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from flask import request
from flask_restx import Namespace, Resource
from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger
from app.api.models import (
    candidate_model,
    api_response_model,
    error_response_model,
    search_request_model,
    filter_request_model
)

# Create namespace
candidates_ns = Namespace(
    'candidates', 
    description='👥 Candidate Information API\n\nSearch and access detailed information about election candidates across all elections.'
)

logger = get_logger("rajniti.api.candidates")

# ==================== Helper Functions ====================

def load_all_candidates() -> List[Dict[str, Any]]:
    """Load candidates from all election datasets"""
    all_candidates = []
    data_root = Path("app/data")
    
    election_paths = {
        "lok-sabha-2024": data_root / "lok_sabha" / "lok-sabha-2024" / "candidates.json",
        "delhi-assembly-2025": data_root / "vidhan_sabha" / "DL_2025_ASSEMBLY" / "candidates.json", 
        "maharashtra-assembly-2024": data_root / "vidhan_sabha" / "MH_2024" / "candidates.json"
    }
    
    for election_id, candidates_file in election_paths.items():
        try:
            if candidates_file.exists():
                with open(candidates_file, 'r', encoding='utf-8') as f:
                    candidates = json.load(f)
                    
                # Add election context to each candidate
                for candidate in candidates:
                    candidate['election_id'] = election_id
                    candidate['election_type'] = 'LOK_SABHA' if 'lok-sabha' in election_id else 'VIDHAN_SABHA'
                    
                    # Normalize field names
                    if 'Name' in candidate:
                        candidate['name'] = candidate['Name']
                    if 'Party' in candidate:
                        candidate['party'] = candidate['Party']
                    if 'Constituency Code' in candidate:
                        candidate['constituency_code'] = candidate['Constituency Code']
                    if 'Status' in candidate:
                        candidate['status'] = candidate['Status']
                    if 'Votes' in candidate:
                        candidate['votes'] = candidate['Votes']
                    if 'Margin' in candidate:
                        candidate['margin'] = candidate['Margin']
                        
                all_candidates.extend(candidates)
                
        except Exception as e:
            logger.warning(f"Failed to load candidates from {election_id}", error=str(e))
            continue
    
    return all_candidates

def search_candidates(query: str, candidates: List[Dict], limit: int = 50) -> List[Dict]:
    """Search candidates by name, party, or constituency"""
    if not query or len(query) < 2:
        return candidates[:limit]
    
    query_lower = query.lower()
    matches = []
    
    for candidate in candidates:
        # Check name match (highest priority)
        name = candidate.get('name', candidate.get('Name', '')).lower()
        if query_lower in name:
            candidate['_match_score'] = 100
            candidate['_match_field'] = 'name'
            matches.append(candidate)
            continue
            
        # Check party match
        party = candidate.get('party', candidate.get('Party', '')).lower()  
        if query_lower in party:
            candidate['_match_score'] = 80
            candidate['_match_field'] = 'party'
            matches.append(candidate)
            continue
            
        # Check constituency match
        constituency = candidate.get('constituency', candidate.get('Constituency Code', '')).lower()
        if query_lower in constituency:
            candidate['_match_score'] = 60
            candidate['_match_field'] = 'constituency'
            matches.append(candidate)
            continue
    
    # Sort by match score and return top results
    matches.sort(key=lambda x: x.get('_match_score', 0), reverse=True)
    return matches[:limit]

def apply_candidate_filters(candidates: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Apply filters to candidate list"""
    if not filters:
        return candidates
        
    filtered = candidates
    
    for key, value in filters.items():
        if key in ['page', 'per_page', 'limit', 'offset', 'q', 'query']:
            continue
            
        filtered = [
            candidate for candidate in filtered
            if _candidate_matches_filter(candidate, key, value)
        ]
    
    return filtered

def _candidate_matches_filter(candidate: Dict[str, Any], key: str, value: Any) -> bool:
    """Check if candidate matches specific filter"""
    # Handle common field mappings
    field_mappings = {
        'status': ['Status', 'status'],
        'party': ['Party', 'party'],
        'name': ['Name', 'name'],
        'constituency': ['constituency', 'Constituency Code'],
        'election': ['election_id'],
        'type': ['election_type'],
        'votes': ['Votes', 'votes'],
        'margin': ['Margin', 'margin']
    }
    
    possible_fields = field_mappings.get(key, [key])
    
    for field in possible_fields:
        if field in candidate:
            candidate_value = candidate[field]
            
            # String matching (case-insensitive)
            if isinstance(value, str) and isinstance(candidate_value, str):
                return value.lower() in candidate_value.lower()
            elif isinstance(value, str):
                return value.lower() in str(candidate_value).lower()
            # Exact matching for numbers
            elif isinstance(value, (int, float)):
                try:
                    return float(candidate_value) == float(value)
                except (ValueError, TypeError):
                    return False
            # List membership
            elif isinstance(value, list):
                return candidate_value in value
    
    return False

# ==================== API Endpoints ====================

@candidates_ns.route('/search')
class CandidateSearch(Resource):
    @candidates_ns.doc('search_candidates')
    @candidates_ns.expect(search_request_model, validate=False)
    @candidates_ns.marshal_with(api_response_model, code=200)
    @candidates_ns.response(400, 'Bad Request', error_response_model)
    def get(self):
        """
        🔍 Search candidates across all elections
        
        Search for candidates by name, party, or constituency across all available
        election datasets. Supports fuzzy matching and returns ranked results.
        
        **Query Parameters:**
        - `q` or `query`: Search query (minimum 2 characters)
        - `election`: Filter by election ID (optional)
        - `party`: Filter by party name (optional)
        - `status`: Filter by result status (WON/LOST) (optional)
        - `limit`: Maximum results to return (default: 50, max: 100)
        """
        try:
            query = request.args.get('q') or request.args.get('query', '')
            limit = min(int(request.args.get('limit', 50)), 100)
            
            if not query or len(query.strip()) < 2:
                return APIResponse.error(
                    "Search query must be at least 2 characters long",
                    "VALIDATION_ERROR",
                    400
                )
            
            # Load all candidates
            all_candidates = load_all_candidates()
            
            # Apply additional filters first
            filters = {k: v for k, v in request.args.items() if k not in ['q', 'query', 'limit']}
            if filters:
                all_candidates = apply_candidate_filters(all_candidates, filters)
            
            # Search candidates
            search_results = search_candidates(query.strip(), all_candidates, limit)
            
            # Clean up internal fields
            for candidate in search_results:
                candidate.pop('_match_score', None)
                candidate.pop('_match_field', None)
            
            return APIResponse.success(
                data={
                    'query': query.strip(),
                    'total_results': len(search_results),
                    'candidates': search_results,
                    'filters_applied': filters
                },
                message=f"Found {len(search_results)} candidates matching '{query}'"
            )
            
        except ValueError as e:
            return APIResponse.error("Invalid limit parameter", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Failed to search candidates", error=str(e))
            return APIResponse.internal_error("Failed to search candidates")

@candidates_ns.route('/winners')  
class AllWinners(Resource):
    @candidates_ns.doc('get_all_winners')
    @candidates_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        🏆 Get all winning candidates across elections
        
        Returns all winning candidates from all available elections,
        grouped by election for easy analysis.
        """
        try:
            all_candidates = load_all_candidates()
            
            # Filter only winners
            winners = [
                candidate for candidate in all_candidates
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won'
            ]
            
            # Group by election
            winners_by_election = {}
            for winner in winners:
                election_id = winner.get('election_id', 'unknown')
                if election_id not in winners_by_election:
                    winners_by_election[election_id] = []
                winners_by_election[election_id].append(winner)
            
            # Calculate summary statistics
            party_summary = {}
            for winner in winners:
                party = winner.get('party', winner.get('Party', 'Unknown'))
                party_summary[party] = party_summary.get(party, 0) + 1
            
            response_data = {
                'summary': {
                    'total_winners': len(winners),
                    'elections_covered': len(winners_by_election),
                    'top_parties': sorted(party_summary.items(), key=lambda x: x[1], reverse=True)[:10]
                },
                'winners_by_election': winners_by_election
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(winners)} winners across all elections"
            )
            
        except Exception as e:
            logger.error("Failed to get winners", error=str(e))
            return APIResponse.internal_error("Failed to retrieve winners")

@candidates_ns.route('/party/<string:party_name>')
@candidates_ns.param('party_name', 'Political party name (e.g., "Bharatiya Janata Party")')
class Partykandidates(Resource):
    @candidates_ns.doc('get_candidates_by_party')
    @candidates_ns.marshal_with(api_response_model, code=200)
    @candidates_ns.response(404, 'Party not found', error_response_model)
    def get(self, party_name):
        """
        🏛️ Get all candidates from a specific political party
        
        Returns all candidates who contested elections under the specified
        political party, across all available elections.
        """
        try:
            all_candidates = load_all_candidates()
            
            # Filter by party (case-insensitive)
            party_candidates = [
                candidate for candidate in all_candidates
                if (candidate.get('Party', '').lower() == party_name.lower() or
                    candidate.get('party', '').lower() == party_name.lower())
            ]
            
            if not party_candidates:
                return APIResponse.not_found("Party candidates", party_name)
            
            # Group by election and status
            by_election = {}
            winners = 0
            total_votes = 0
            
            for candidate in party_candidates:
                election_id = candidate.get('election_id', 'unknown')
                if election_id not in by_election:
                    by_election[election_id] = {'total': 0, 'won': 0, 'candidates': []}
                
                by_election[election_id]['total'] += 1
                by_election[election_id]['candidates'].append(candidate)
                
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                    by_election[election_id]['won'] += 1
                    winners += 1
                
                # Add up votes
                votes = candidate.get('Votes', candidate.get('votes', 0))
                if votes and str(votes).replace(',', '').isdigit():
                    total_votes += int(str(votes).replace(',', ''))
            
            response_data = {
                'party_name': party_name,
                'summary': {
                    'total_candidates': len(party_candidates),
                    'total_winners': winners,
                    'elections_contested': len(by_election),
                    'total_votes_received': total_votes,
                    'win_percentage': round((winners / len(party_candidates)) * 100, 2) if party_candidates else 0
                },
                'performance_by_election': by_election,
                'all_candidates': party_candidates
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(party_candidates)} candidates for {party_name}"
            )
            
        except Exception as e:
            logger.error("Failed to get party candidates", party=party_name, error=str(e))
            return APIResponse.internal_error("Failed to retrieve party candidates")

@candidates_ns.route('/constituency/<string:constituency_code>')
@candidates_ns.param('constituency_code', 'Constituency code (e.g., "DL-1", "GJ-26")')
class ConstituencyкандиЊates(Resource):
    @candidates_ns.doc('get_candidates_by_constituency')
    @candidates_ns.marshal_with(api_response_model, code=200)
    @candidates_ns.response(404, 'Constituency not found', error_response_model)
    def get(self, constituency_code):
        """
        🗳️ Get all candidates from a specific constituency
        
        Returns all candidates who contested from the specified constituency,
        including winner, runners-up, and vote details.
        """
        try:
            all_candidates = load_all_candidates()
            
            # Filter by constituency
            constituency_candidates = [
                candidate for candidate in all_candidates
                if (candidate.get('Constituency Code', '').upper() == constituency_code.upper() or
                    candidate.get('constituency_code', '').upper() == constituency_code.upper())
            ]
            
            if not constituency_candidates:
                return APIResponse.not_found("Constituency candidates", constituency_code)
            
            # Sort by votes (descending) to get ranking
            constituency_candidates.sort(
                key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0),
                reverse=True
            )
            
            # Identify winner and runner-up
            winner = None
            runner_up = None
            
            for i, candidate in enumerate(constituency_candidates):
                candidate['position'] = i + 1
                
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                    winner = candidate
                elif i == 1:  # Second highest votes
                    runner_up = candidate
            
            # Calculate victory margin
            victory_margin = 0
            if len(constituency_candidates) >= 2:
                votes1 = int(str(constituency_candidates[0].get('Votes', constituency_candidates[0].get('votes', 0))).replace(',', '') or 0)
                votes2 = int(str(constituency_candidates[1].get('Votes', constituency_candidates[1].get('votes', 0))).replace(',', '') or 0)
                victory_margin = votes1 - votes2
            
            response_data = {
                'constituency_code': constituency_code,
                'election_id': constituency_candidates[0].get('election_id', 'unknown'),
                'total_candidates': len(constituency_candidates),
                'winner': winner,
                'runner_up': runner_up,
                'victory_margin': victory_margin,
                'all_candidates': constituency_candidates,
                'vote_distribution': [
                    {
                        'position': i + 1,
                        'name': candidate.get('name', candidate.get('Name', '')),
                        'party': candidate.get('party', candidate.get('Party', '')),
                        'votes': candidate.get('votes', candidate.get('Votes', 0)),
                        'percentage': round((int(str(candidate.get('Votes', candidate.get('votes', 0))).replace(',', '') or 0) / 
                                          sum(int(str(c.get('Votes', c.get('votes', 0))).replace(',', '') or 0) for c in constituency_candidates)) * 100, 2)
                        if sum(int(str(c.get('Votes', c.get('votes', 0))).replace(',', '') or 0) for c in constituency_candidates) > 0 else 0
                    }
                    for i, candidate in enumerate(constituency_candidates)
                ]
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(constituency_candidates)} candidates for {constituency_code}"
            )
            
        except Exception as e:
            logger.error("Failed to get constituency candidates", constituency=constituency_code, error=str(e))
            return APIResponse.internal_error("Failed to retrieve constituency candidates")

@candidates_ns.route('/statistics')
class CandidateStatistics(Resource):
    @candidates_ns.doc('get_candidate_statistics')
    @candidates_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get comprehensive candidate statistics
        
        Returns detailed statistical analysis of candidates across all elections
        including demographic breakdowns, performance metrics, and trends.
        """
        try:
            all_candidates = load_all_candidates()
            
            if not all_candidates:
                return APIResponse.success(
                    data={'message': 'No candidate data available'},
                    message="No candidates found"
                )
            
            # Calculate comprehensive statistics
            statistics = {
                'overview': {
                    'total_candidates': len(all_candidates),
                    'total_winners': len([c for c in all_candidates if c.get('Status') == 'WON' or c.get('status') == 'won']),
                    'unique_parties': len(set(c.get('Party', c.get('party', 'Unknown')) for c in all_candidates)),
                    'elections_covered': len(set(c.get('election_id', 'unknown') for c in all_candidates))
                },
                'by_election': {},
                'by_party': {},
                'vote_analysis': {
                    'total_votes_cast': 0,
                    'average_votes_per_candidate': 0,
                    'highest_individual_score': {'votes': 0, 'candidate': '', 'constituency': ''},
                    'lowest_individual_score': {'votes': float('inf'), 'candidate': '', 'constituency': ''}
                }
            }
            
            # Group by election
            for candidate in all_candidates:
                election_id = candidate.get('election_id', 'unknown')
                if election_id not in statistics['by_election']:
                    statistics['by_election'][election_id] = {
                        'total_candidates': 0,
                        'winners': 0,
                        'parties': set()
                    }
                
                statistics['by_election'][election_id]['total_candidates'] += 1
                statistics['by_election'][election_id]['parties'].add(candidate.get('Party', candidate.get('party', 'Unknown')))
                
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                    statistics['by_election'][election_id]['winners'] += 1
            
            # Convert sets to counts
            for election_data in statistics['by_election'].values():
                election_data['unique_parties'] = len(election_data['parties'])
                del election_data['parties']
            
            # Group by party
            for candidate in all_candidates:
                party = candidate.get('Party', candidate.get('party', 'Unknown'))
                if party not in statistics['by_party']:
                    statistics['by_party'][party] = {
                        'candidates': 0,
                        'winners': 0,
                        'elections': set()
                    }
                
                statistics['by_party'][party]['candidates'] += 1
                statistics['by_party'][party]['elections'].add(candidate.get('election_id', 'unknown'))
                
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                    statistics['by_party'][party]['winners'] += 1
                
                # Vote analysis
                votes = candidate.get('Votes', candidate.get('votes', 0))
                if votes and str(votes).replace(',', '').isdigit():
                    vote_count = int(str(votes).replace(',', ''))
                    statistics['vote_analysis']['total_votes_cast'] += vote_count
                    
                    # Track highest/lowest
                    if vote_count > statistics['vote_analysis']['highest_individual_score']['votes']:
                        statistics['vote_analysis']['highest_individual_score'] = {
                            'votes': vote_count,
                            'candidate': candidate.get('Name', candidate.get('name', '')),
                            'constituency': candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                        }
                    
                    if vote_count < statistics['vote_analysis']['lowest_individual_score']['votes']:
                        statistics['vote_analysis']['lowest_individual_score'] = {
                            'votes': vote_count,
                            'candidate': candidate.get('Name', candidate.get('name', '')),
                            'constituency': candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                        }
            
            # Finalize party statistics
            for party_data in statistics['by_party'].values():
                party_data['elections_contested'] = len(party_data['elections'])
                party_data['win_rate'] = round((party_data['winners'] / party_data['candidates']) * 100, 2) if party_data['candidates'] > 0 else 0
                del party_data['elections']
            
            # Calculate average votes
            if statistics['overview']['total_candidates'] > 0:
                statistics['vote_analysis']['average_votes_per_candidate'] = round(
                    statistics['vote_analysis']['total_votes_cast'] / statistics['overview']['total_candidates'], 2
                )
            
            # Sort parties by performance
            statistics['top_parties'] = sorted(
                statistics['by_party'].items(),
                key=lambda x: (x[1]['winners'], x[1]['candidates']),
                reverse=True
            )[:10]
            
            return APIResponse.success(
                data=statistics,
                message="Candidate statistics retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get candidate statistics", error=str(e))
            return APIResponse.internal_error("Failed to retrieve candidate statistics")
