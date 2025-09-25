"""
Constituencies API Namespace

Provides endpoints for accessing constituency information, results,
and constituency-specific analytics.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from flask import request
from flask_restx import Namespace, Resource
from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.api.models import (
    constituency_model,
    api_response_model,
    error_response_model
)

# Create namespace
constituencies_ns = Namespace(
    'constituencies',
    description='🗳️ Constituency Information API\n\nAccess detailed information about electoral constituencies, results, and analytics.'
)

logger = get_logger("rajniti.api.constituencies")

def load_all_constituency_data() -> Dict[str, List[Dict]]:
    """Load constituency and candidate data from all elections"""
    all_data = {}
    data_root = Path("app/data")
    
    election_paths = {
        "lok-sabha-2024": data_root / "lok_sabha" / "lok-sabha-2024",
        "delhi-assembly-2025": data_root / "vidhan_sabha" / "DL_2025_ASSEMBLY", 
        "maharashtra-assembly-2024": data_root / "vidhan_sabha" / "MH_2024"
    }
    
    for election_id, election_path in election_paths.items():
        try:
            candidates_file = election_path / "candidates.json"
            constituencies_file = election_path / "constituencies.json"
            
            election_data = {
                'candidates': [],
                'constituencies': []
            }
            
            if candidates_file.exists():
                with open(candidates_file, 'r', encoding='utf-8') as f:
                    election_data['candidates'] = json.load(f)
            
            if constituencies_file.exists():
                with open(constituencies_file, 'r', encoding='utf-8') as f:
                    election_data['constituencies'] = json.load(f)
            
            all_data[election_id] = election_data
            
        except Exception as e:
            logger.warning(f"Failed to load data for {election_id}", error=str(e))
            continue
    
    return all_data

def get_constituency_results(constituency_code: str, election_data: Dict) -> Dict[str, Any]:
    """Get detailed results for a specific constituency"""
    candidates = election_data.get('candidates', [])
    
    # Filter candidates for this constituency
    constituency_candidates = [
        candidate for candidate in candidates
        if (candidate.get('Constituency Code', '').upper() == constituency_code.upper() or
            candidate.get('constituency_code', '').upper() == constituency_code.upper())
    ]
    
    if not constituency_candidates:
        return None
    
    # Sort by votes (descending)
    constituency_candidates.sort(
        key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0),
        reverse=True
    )
    
    # Calculate total votes and statistics
    total_votes = sum(
        int(str(candidate.get('Votes', candidate.get('votes', 0))).replace(',', '') or 0) 
        for candidate in constituency_candidates
    )
    
    # Identify winner
    winner = None
    runner_up = None
    
    for i, candidate in enumerate(constituency_candidates):
        candidate['position'] = i + 1
        candidate['vote_percentage'] = round(
            (int(str(candidate.get('Votes', candidate.get('votes', 0))).replace(',', '') or 0) / total_votes) * 100, 2
        ) if total_votes > 0 else 0
        
        if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
            winner = candidate
        elif i == 1:  # Second place
            runner_up = candidate
    
    # Victory margin
    victory_margin = 0
    if len(constituency_candidates) >= 2:
        votes1 = int(str(constituency_candidates[0].get('Votes', constituency_candidates[0].get('votes', 0))).replace(',', '') or 0)
        votes2 = int(str(constituency_candidates[1].get('Votes', constituency_candidates[1].get('votes', 0))).replace(',', '') or 0)
        victory_margin = votes1 - votes2
    
    return {
        'constituency_code': constituency_code,
        'total_candidates': len(constituency_candidates),
        'total_votes_polled': total_votes,
        'winner': winner,
        'runner_up': runner_up,
        'victory_margin': victory_margin,
        'victory_margin_percentage': round((victory_margin / total_votes) * 100, 2) if total_votes > 0 else 0,
        'candidates': constituency_candidates
    }

@constituencies_ns.route('/overview')
class ConstituenciesOverview(Resource):
    @constituencies_ns.doc('get_constituencies_overview')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get overview of all constituencies across elections
        
        Returns summary information about all constituencies across
        all available election datasets.
        """
        try:
            all_data = load_all_constituency_data()
            
            overview = {
                'total_elections': len(all_data),
                'total_constituencies': 0,
                'by_election': {}
            }
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                constituencies = election_data.get('constituencies', [])
                
                # Get unique constituencies from candidates data
                unique_constituencies = set(
                    candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                    for candidate in candidates
                    if candidate.get('Constituency Code') or candidate.get('constituency_code')
                )
                
                # Use constituencies file if available, otherwise use unique from candidates
                constituency_count = len(constituencies) if constituencies else len(unique_constituencies)
                overview['total_constituencies'] += constituency_count
                
                overview['by_election'][election_id] = {
                    'constituencies': constituency_count,
                    'total_candidates': len(candidates),
                    'avg_candidates_per_constituency': round(len(candidates) / constituency_count, 2) if constituency_count > 0 else 0
                }
            
            return APIResponse.success(
                data=overview,
                message="Constituencies overview retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get constituencies overview", error=str(e))
            return APIResponse.internal_error("Failed to retrieve constituencies overview")

@constituencies_ns.route('/<string:constituency_code>')
@constituencies_ns.param('constituency_code', 'Constituency code (e.g., DL-1, GJ-26)')
class ConstituencyDetail(Resource):
    @constituencies_ns.doc('get_constituency_detail')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    @constituencies_ns.response(404, 'Constituency not found', error_response_model)
    def get(self, constituency_code):
        """
        🗳️ Get detailed information about a specific constituency
        
        Returns comprehensive details about the specified constituency
        including candidates, results, and voting statistics.
        """
        try:
            all_data = load_all_constituency_data()
            constituency_results = {}
            
            # Find constituency across all elections
            for election_id, election_data in all_data.items():
                results = get_constituency_results(constituency_code, election_data)
                if results:
                    results['election_id'] = election_id
                    constituency_results[election_id] = results
            
            if not constituency_results:
                return APIResponse.not_found("Constituency", constituency_code)
            
            # Get the most recent election data for basic info
            latest_election = max(constituency_results.keys())
            latest_results = constituency_results[latest_election]
            
            response_data = {
                'constituency_code': constituency_code,
                'elections_contested': len(constituency_results),
                'latest_election': latest_election,
                'current_winner': latest_results.get('winner'),
                'historical_results': constituency_results,
                'performance_summary': {
                    'total_elections': len(constituency_results),
                    'different_winners': len(set(
                        result['winner']['party'] if result.get('winner') else None
                        for result in constituency_results.values()
                    )),
                    'average_candidates': round(sum(
                        result['total_candidates'] for result in constituency_results.values()
                    ) / len(constituency_results), 2),
                    'average_margin': round(sum(
                        result['victory_margin'] for result in constituency_results.values()
                    ) / len(constituency_results), 2)
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Constituency details for {constituency_code} retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get constituency detail", constituency=constituency_code, error=str(e))
            return APIResponse.internal_error("Failed to retrieve constituency details")

@constituencies_ns.route('/<string:constituency_code>/candidates')
@constituencies_ns.param('constituency_code', 'Constituency code')
class ConstituencyCandidates(Resource):
    @constituencies_ns.doc('get_constituency_candidates')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    @constituencies_ns.response(404, 'Constituency not found', error_response_model)
    def get(self, constituency_code):
        """
        👥 Get all candidates for a specific constituency
        
        Returns all candidates who contested from the specified constituency
        across all available elections, with detailed voting information.
        """
        try:
            all_data = load_all_constituency_data()
            all_candidates = []
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                constituency_candidates = [
                    candidate for candidate in candidates
                    if (candidate.get('Constituency Code', '').upper() == constituency_code.upper() or
                        candidate.get('constituency_code', '').upper() == constituency_code.upper())
                ]
                
                for candidate in constituency_candidates:
                    candidate['election_id'] = election_id
                    all_candidates.append(candidate)
            
            if not all_candidates:
                return APIResponse.not_found("Constituency candidates", constituency_code)
            
            # Group by election
            by_election = {}
            unique_parties = set()
            
            for candidate in all_candidates:
                election_id = candidate.get('election_id')
                if election_id not in by_election:
                    by_election[election_id] = []
                
                by_election[election_id].append(candidate)
                unique_parties.add(candidate.get('Party', candidate.get('party', 'Unknown')))
            
            # Sort candidates within each election by votes
            for election_candidates in by_election.values():
                election_candidates.sort(
                    key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0),
                    reverse=True
                )
            
            response_data = {
                'constituency_code': constituency_code,
                'summary': {
                    'total_candidates': len(all_candidates),
                    'elections_covered': len(by_election),
                    'unique_parties': len(unique_parties),
                    'parties_contested': list(unique_parties)
                },
                'candidates_by_election': by_election,
                'all_candidates': all_candidates
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(all_candidates)} candidates for {constituency_code}"
            )
            
        except Exception as e:
            logger.error("Failed to get constituency candidates", constituency=constituency_code, error=str(e))
            return APIResponse.internal_error("Failed to retrieve constituency candidates")

@constituencies_ns.route('/state/<string:state_code>')
@constituencies_ns.param('state_code', 'State code (e.g., DL, MH, GJ)')
class StateConstituencies(Resource):
    @constituencies_ns.doc('get_state_constituencies')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    @constituencies_ns.response(404, 'State not found', error_response_model)
    def get(self, state_code):
        """
        🏛️ Get all constituencies in a specific state
        
        Returns all constituencies within the specified state/UT
        along with their results and statistics.
        """
        try:
            all_data = load_all_constituency_data()
            state_constituencies = {}
            
            # Map state codes to election IDs (simplified mapping)
            state_elections = {
                'DL': ['delhi-assembly-2025'],
                'MH': ['maharashtra-assembly-2024'],
                # For Lok Sabha, we'll need to filter by state prefix
            }
            
            # Add Lok Sabha constituencies for all states
            for election_id, election_data in all_data.items():
                if 'lok-sabha' in election_id:
                    candidates = election_data.get('candidates', [])
                    
                    # Get constituencies that start with the state code
                    state_candidates = [
                        candidate for candidate in candidates
                        if candidate.get('constituency', candidate.get('Constituency Code', '')).upper().startswith(state_code.upper() + '-')
                    ]
                    
                    if state_candidates:
                        if state_code.upper() not in state_elections:
                            state_elections[state_code.upper()] = []
                        state_elections[state_code.upper()].append(election_id)
            
            if state_code.upper() not in state_elections:
                return APIResponse.not_found("State constituencies", state_code)
            
            # Process each election for this state
            for election_id in state_elections[state_code.upper()]:
                if election_id in all_data:
                    election_data = all_data[election_id]
                    candidates = election_data.get('candidates', [])
                    
                    # Filter candidates for this state
                    if 'lok-sabha' in election_id:
                        state_candidates = [
                            candidate for candidate in candidates
                            if candidate.get('constituency', candidate.get('Constituency Code', '')).upper().startswith(state_code.upper() + '-')
                        ]
                    else:
                        state_candidates = candidates  # For state elections, all candidates are from the state
                    
                    # Group by constituency
                    constituencies_in_election = {}
                    for candidate in state_candidates:
                        const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                        if const_code not in constituencies_in_election:
                            constituencies_in_election[const_code] = []
                        constituencies_in_election[const_code].append(candidate)
                    
                    # Get results for each constituency
                    for const_code, const_candidates in constituencies_in_election.items():
                        if const_code not in state_constituencies:
                            state_constituencies[const_code] = {}
                        
                        const_results = get_constituency_results(const_code, {'candidates': const_candidates})
                        if const_results:
                            const_results['election_id'] = election_id
                            state_constituencies[const_code][election_id] = const_results
            
            if not state_constituencies:
                return APIResponse.not_found("State constituencies", state_code)
            
            # Calculate summary statistics
            total_constituencies = len(state_constituencies)
            total_candidates = sum(
                sum(len(election_results['candidates']) for election_results in const_data.values())
                for const_data in state_constituencies.values()
            )
            
            # Get party-wise performance across all constituencies
            party_performance = {}
            for const_data in state_constituencies.values():
                for election_results in const_data.values():
                    winner = election_results.get('winner')
                    if winner:
                        party = winner.get('Party', winner.get('party', 'Unknown'))
                        party_performance[party] = party_performance.get(party, 0) + 1
            
            response_data = {
                'state_code': state_code.upper(),
                'summary': {
                    'total_constituencies': total_constituencies,
                    'total_candidates': total_candidates,
                    'elections_covered': len(set(
                        election_id for const_data in state_constituencies.values()
                        for election_id in const_data.keys()
                    )),
                    'party_performance': party_performance,
                    'leading_party': max(party_performance, key=party_performance.get) if party_performance else None
                },
                'constituencies': state_constituencies
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {total_constituencies} constituencies for state {state_code}"
            )
            
        except Exception as e:
            logger.error("Failed to get state constituencies", state=state_code, error=str(e))
            return APIResponse.internal_error("Failed to retrieve state constituencies")

@constituencies_ns.route('/closest-contests')
class ClosestContests(Resource):
    @constituencies_ns.doc('get_closest_contests')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        ⚖️ Get constituencies with closest victory margins
        
        Returns constituencies where the victory margin was smallest,
        indicating the most competitive contests.
        """
        try:
            all_data = load_all_constituency_data()
            closest_contests = []
            
            # Get all constituency results
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                # Group by constituency
                by_constituency = {}
                for candidate in candidates:
                    const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                    if const_code not in by_constituency:
                        by_constituency[const_code] = []
                    by_constituency[const_code].append(candidate)
                
                # Calculate margins for each constituency
                for const_code, const_candidates in by_constituency.items():
                    if len(const_candidates) >= 2:
                        const_candidates.sort(
                            key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0),
                            reverse=True
                        )
                        
                        votes1 = int(str(const_candidates[0].get('Votes', const_candidates[0].get('votes', 0))).replace(',', '') or 0)
                        votes2 = int(str(const_candidates[1].get('Votes', const_candidates[1].get('votes', 0))).replace(',', '') or 0)
                        margin = votes1 - votes2
                        total_votes = sum(
                            int(str(c.get('Votes', c.get('votes', 0))).replace(',', '') or 0) 
                            for c in const_candidates
                        )
                        
                        closest_contests.append({
                            'election_id': election_id,
                            'constituency_code': const_code,
                            'winner': {
                                'name': const_candidates[0].get('Name', const_candidates[0].get('name', '')),
                                'party': const_candidates[0].get('Party', const_candidates[0].get('party', '')),
                                'votes': votes1
                            },
                            'runner_up': {
                                'name': const_candidates[1].get('Name', const_candidates[1].get('name', '')),
                                'party': const_candidates[1].get('Party', const_candidates[1].get('party', '')),
                                'votes': votes2
                            },
                            'victory_margin': margin,
                            'margin_percentage': round((margin / total_votes) * 100, 3) if total_votes > 0 else 0,
                            'total_votes': total_votes
                        })
            
            # Sort by victory margin (ascending)
            closest_contests.sort(key=lambda x: x['victory_margin'])
            
            # Take top 20 closest contests
            top_closest = closest_contests[:20]
            
            return APIResponse.success(
                data={
                    'closest_contests': top_closest,
                    'summary': {
                        'total_analyzed': len(closest_contests),
                        'closest_margin': top_closest[0]['victory_margin'] if top_closest else 0,
                        'closest_margin_percentage': top_closest[0]['margin_percentage'] if top_closest else 0
                    }
                },
                message=f"Retrieved {len(top_closest)} closest contests"
            )
            
        except Exception as e:
            logger.error("Failed to get closest contests", error=str(e))
            return APIResponse.internal_error("Failed to retrieve closest contests")

@constituencies_ns.route('/highest-turnout')  
class HighestTurnout(Resource):
    @constituencies_ns.doc('get_highest_turnout')
    @constituencies_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get constituencies with highest voter turnout
        
        Returns constituencies with the highest number of votes polled,
        indicating high voter participation.
        """
        try:
            all_data = load_all_constituency_data()
            turnout_data = []
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                # Group by constituency and calculate total votes
                by_constituency = {}
                for candidate in candidates:
                    const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                    if const_code not in by_constituency:
                        by_constituency[const_code] = []
                    by_constituency[const_code].append(candidate)
                
                for const_code, const_candidates in by_constituency.items():
                    total_votes = sum(
                        int(str(candidate.get('Votes', candidate.get('votes', 0))).replace(',', '') or 0)
                        for candidate in const_candidates
                    )
                    
                    if total_votes > 0:
                        winner = max(
                            const_candidates,
                            key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0)
                        )
                        
                        turnout_data.append({
                            'election_id': election_id,
                            'constituency_code': const_code,
                            'total_votes_polled': total_votes,
                            'total_candidates': len(const_candidates),
                            'winner': {
                                'name': winner.get('Name', winner.get('name', '')),
                                'party': winner.get('Party', winner.get('party', '')),
                                'votes': int(str(winner.get('Votes', winner.get('votes', 0))).replace(',', '') or 0)
                            }
                        })
            
            # Sort by total votes (descending)
            turnout_data.sort(key=lambda x: x['total_votes_polled'], reverse=True)
            
            # Take top 20
            top_turnout = turnout_data[:20]
            
            return APIResponse.success(
                data={
                    'highest_turnout_constituencies': top_turnout,
                    'summary': {
                        'total_analyzed': len(turnout_data),
                        'highest_turnout': top_turnout[0]['total_votes_polled'] if top_turnout else 0,
                        'average_turnout': round(sum(x['total_votes_polled'] for x in turnout_data) / len(turnout_data), 2) if turnout_data else 0
                    }
                },
                message=f"Retrieved {len(top_turnout)} highest turnout constituencies"
            )
            
        except Exception as e:
            logger.error("Failed to get highest turnout data", error=str(e))
            return APIResponse.internal_error("Failed to retrieve turnout data")
