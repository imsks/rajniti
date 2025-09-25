"""
Parties API Namespace

Provides endpoints for accessing political party information, performance,
and party-specific analytics across all elections.
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
    party_model,
    party_performance_model,
    api_response_model,
    error_response_model
)

# Create namespace
parties_ns = Namespace(
    'parties',
    description='🏛️ Political Parties API\n\nAccess comprehensive information about political parties, their performance, and electoral statistics.'
)

logger = get_logger("rajniti.api.parties")

def load_all_party_data() -> Dict[str, List[Dict]]:
    """Load party and candidate data from all elections"""
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
            parties_file = election_path / "parties.json"
            
            election_data = {
                'candidates': [],
                'parties': []
            }
            
            if candidates_file.exists():
                with open(candidates_file, 'r', encoding='utf-8') as f:
                    election_data['candidates'] = json.load(f)
            
            if parties_file.exists():
                with open(parties_file, 'r', encoding='utf-8') as f:
                    election_data['parties'] = json.load(f)
            
            all_data[election_id] = election_data
            
        except Exception as e:
            logger.warning(f"Failed to load data for {election_id}", error=str(e))
            continue
    
    return all_data

def calculate_party_performance(party_name: str, candidates: List[Dict], election_id: str) -> Dict[str, Any]:
    """Calculate comprehensive performance metrics for a party"""
    party_candidates = [
        candidate for candidate in candidates
        if (candidate.get('Party', '').lower() == party_name.lower() or
            candidate.get('party', '').lower() == party_name.lower())
    ]
    
    if not party_candidates:
        return None
    
    # Basic metrics
    total_contested = len(party_candidates)
    total_won = len([c for c in party_candidates if c.get('Status') == 'WON' or c.get('status') == 'won'])
    total_lost = total_contested - total_won
    
    # Vote metrics
    total_votes = 0
    valid_vote_counts = []
    
    for candidate in party_candidates:
        votes = candidate.get('Votes', candidate.get('votes', 0))
        if votes and str(votes).replace(',', '').isdigit():
            vote_count = int(str(votes).replace(',', ''))
            total_votes += vote_count
            valid_vote_counts.append(vote_count)
    
    # Performance metrics
    win_percentage = round((total_won / total_contested) * 100, 2) if total_contested > 0 else 0
    avg_votes_per_candidate = round(sum(valid_vote_counts) / len(valid_vote_counts), 2) if valid_vote_counts else 0
    
    # Get best and worst performances
    if valid_vote_counts:
        best_performance = max(party_candidates, key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0))
        worst_performance = min(party_candidates, key=lambda x: int(str(x.get('Votes', x.get('votes', 0))).replace(',', '') or 0))
    else:
        best_performance = worst_performance = None
    
    return {
        'party_name': party_name,
        'election_id': election_id,
        'seats_contested': total_contested,
        'seats_won': total_won,
        'seats_lost': total_lost,
        'win_percentage': win_percentage,
        'total_votes': total_votes,
        'average_votes_per_candidate': avg_votes_per_candidate,
        'best_performance': {
            'candidate': best_performance.get('Name', best_performance.get('name', '')) if best_performance else None,
            'constituency': best_performance.get('Constituency Code', best_performance.get('constituency_code', '')) if best_performance else None,
            'votes': int(str(best_performance.get('Votes', best_performance.get('votes', 0))).replace(',', '') or 0) if best_performance else 0
        } if best_performance else None,
        'worst_performance': {
            'candidate': worst_performance.get('Name', worst_performance.get('name', '')) if worst_performance else None,
            'constituency': worst_performance.get('Constituency Code', worst_performance.get('constituency_code', '')) if worst_performance else None,
            'votes': int(str(worst_performance.get('Votes', worst_performance.get('votes', 0))).replace(',', '') or 0) if worst_performance else 0
        } if worst_performance else None,
        'candidates': party_candidates
    }

@parties_ns.route('/overview')
class PartiesOverview(Resource):
    @parties_ns.doc('get_parties_overview')
    @parties_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        📊 Get overview of all political parties
        
        Returns summary information about all political parties across
        all available elections including total seats won and contested.
        """
        try:
            all_data = load_all_party_data()
            
            # Collect all unique parties across elections
            all_parties = {}
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                for candidate in candidates:
                    party_name = candidate.get('Party', candidate.get('party', 'Unknown'))
                    
                    if party_name not in all_parties:
                        all_parties[party_name] = {
                            'name': party_name,
                            'elections_contested': set(),
                            'total_candidates': 0,
                            'total_wins': 0,
                            'total_votes': 0
                        }
                    
                    all_parties[party_name]['elections_contested'].add(election_id)
                    all_parties[party_name]['total_candidates'] += 1
                    
                    if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                        all_parties[party_name]['total_wins'] += 1
                    
                    # Add votes
                    votes = candidate.get('Votes', candidate.get('votes', 0))
                    if votes and str(votes).replace(',', '').isdigit():
                        all_parties[party_name]['total_votes'] += int(str(votes).replace(',', ''))
            
            # Convert to list and calculate percentages
            parties_summary = []
            for party_name, party_data in all_parties.items():
                party_summary = {
                    'name': party_name,
                    'elections_contested': len(party_data['elections_contested']),
                    'total_candidates': party_data['total_candidates'],
                    'total_wins': party_data['total_wins'],
                    'total_votes': party_data['total_votes'],
                    'win_percentage': round((party_data['total_wins'] / party_data['total_candidates']) * 100, 2) if party_data['total_candidates'] > 0 else 0,
                    'avg_votes_per_candidate': round(party_data['total_votes'] / party_data['total_candidates'], 2) if party_data['total_candidates'] > 0 else 0
                }
                parties_summary.append(party_summary)
            
            # Sort by total wins (descending)
            parties_summary.sort(key=lambda x: x['total_wins'], reverse=True)
            
            overview_data = {
                'summary': {
                    'total_parties': len(parties_summary),
                    'total_candidates': sum(p['total_candidates'] for p in parties_summary),
                    'total_winners': sum(p['total_wins'] for p in parties_summary),
                    'elections_covered': len(all_data)
                },
                'top_parties': parties_summary[:20],  # Top 20 parties
                'all_parties': parties_summary
            }
            
            return APIResponse.success(
                data=overview_data,
                message="Parties overview retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get parties overview", error=str(e))
            return APIResponse.internal_error("Failed to retrieve parties overview")

@parties_ns.route('/<string:party_name>')
@parties_ns.param('party_name', 'Political party name (e.g., "Bharatiya Janata Party")')
class PartyDetail(Resource):
    @parties_ns.doc('get_party_detail')
    @parties_ns.marshal_with(api_response_model, code=200)
    @parties_ns.response(404, 'Party not found', error_response_model)
    def get(self, party_name):
        """
        🏛️ Get detailed information about a specific political party
        
        Returns comprehensive details about the specified political party
        including performance across all elections, candidates, and statistics.
        """
        try:
            all_data = load_all_party_data()
            party_performance = {}
            found_party = False
            
            # Calculate performance for each election
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                performance = calculate_party_performance(party_name, candidates, election_id)
                
                if performance and performance['seats_contested'] > 0:
                    party_performance[election_id] = performance
                    found_party = True
            
            if not found_party:
                return APIResponse.not_found("Party", party_name)
            
            # Calculate overall statistics
            total_contested = sum(p['seats_contested'] for p in party_performance.values())
            total_won = sum(p['seats_won'] for p in party_performance.values())
            total_votes = sum(p['total_votes'] for p in party_performance.values())
            
            overall_performance = {
                'party_name': party_name,
                'elections_participated': len(party_performance),
                'total_seats_contested': total_contested,
                'total_seats_won': total_won,
                'overall_win_percentage': round((total_won / total_contested) * 100, 2) if total_contested > 0 else 0,
                'total_votes_received': total_votes,
                'average_votes_per_candidate': round(total_votes / total_contested, 2) if total_contested > 0 else 0
            }
            
            # Find best and worst election performances
            best_election = max(party_performance.values(), key=lambda x: x['win_percentage'])
            worst_election = min(party_performance.values(), key=lambda x: x['win_percentage'])
            
            response_data = {
                'party_info': {
                    'name': party_name,
                    'type': 'Political Party'  # Could be enhanced with more party metadata
                },
                'overall_performance': overall_performance,
                'performance_by_election': party_performance,
                'best_performance': {
                    'election': best_election['election_id'],
                    'win_percentage': best_election['win_percentage'],
                    'seats_won': best_election['seats_won'],
                    'seats_contested': best_election['seats_contested']
                },
                'worst_performance': {
                    'election': worst_election['election_id'],
                    'win_percentage': worst_election['win_percentage'],
                    'seats_won': worst_election['seats_won'],
                    'seats_contested': worst_election['seats_contested']
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Party details for {party_name} retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get party detail", party=party_name, error=str(e))
            return APIResponse.internal_error("Failed to retrieve party details")

@parties_ns.route('/<string:party_name>/candidates')
@parties_ns.param('party_name', 'Political party name')
class PartyCandidates(Resource):
    @parties_ns.doc('get_party_candidates')
    @parties_ns.marshal_with(api_response_model, code=200)
    @parties_ns.response(404, 'Party not found', error_response_model)
    def get(self, party_name):
        """
        👥 Get all candidates from a specific political party
        
        Returns all candidates who contested under the specified political party
        across all elections, with filtering and pagination support.
        """
        try:
            all_data = load_all_party_data()
            all_candidates = []
            found_party = False
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                party_candidates = [
                    candidate for candidate in candidates
                    if (candidate.get('Party', '').lower() == party_name.lower() or
                        candidate.get('party', '').lower() == party_name.lower())
                ]
                
                if party_candidates:
                    found_party = True
                    
                for candidate in party_candidates:
                    candidate['election_id'] = election_id
                    all_candidates.append(candidate)
            
            if not found_party:
                return APIResponse.not_found("Party candidates", party_name)
            
            # Apply filters
            status_filter = request.args.get('status')
            election_filter = request.args.get('election')
            
            if status_filter:
                all_candidates = [
                    c for c in all_candidates 
                    if c.get('Status', '').upper() == status_filter.upper() or c.get('status', '').upper() == status_filter.upper()
                ]
            
            if election_filter:
                all_candidates = [c for c in all_candidates if c.get('election_id') == election_filter]
            
            # Pagination
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 50)), 100)
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_candidates = all_candidates[start_idx:end_idx]
            
            # Summary statistics
            winners = len([c for c in all_candidates if c.get('Status') == 'WON' or c.get('status') == 'won'])
            elections_contested = len(set(c.get('election_id') for c in all_candidates))
            
            response_data = {
                'party_name': party_name,
                'summary': {
                    'total_candidates': len(all_candidates),
                    'total_winners': winners,
                    'elections_contested': elections_contested,
                    'win_percentage': round((winners / len(all_candidates)) * 100, 2) if all_candidates else 0,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (len(all_candidates) + per_page - 1) // per_page
                },
                'candidates': paginated_candidates
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(paginated_candidates)} candidates for {party_name}"
            )
            
        except ValueError as e:
            return APIResponse.error("Invalid pagination parameters", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Failed to get party candidates", party=party_name, error=str(e))
            return APIResponse.internal_error("Failed to retrieve party candidates")

@parties_ns.route('/<string:party_name>/performance')
@parties_ns.param('party_name', 'Political party name')
class PartyPerformance(Resource):
    @parties_ns.doc('get_party_performance')
    @parties_ns.marshal_with(api_response_model, code=200)
    @parties_ns.response(404, 'Party not found', error_response_model)
    def get(self, party_name):
        """
        📈 Get detailed performance analytics for a political party
        
        Returns comprehensive performance metrics, trends, and analytics
        for the specified political party across all elections.
        """
        try:
            all_data = load_all_party_data()
            party_analytics = {}
            found_party = False
            
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                performance = calculate_party_performance(party_name, candidates, election_id)
                
                if performance and performance['seats_contested'] > 0:
                    party_analytics[election_id] = performance
                    found_party = True
            
            if not found_party:
                return APIResponse.not_found("Party performance", party_name)
            
            # Calculate advanced analytics
            elections = list(party_analytics.keys())
            elections.sort()  # Sort chronologically
            
            # Performance trends
            win_percentages = [party_analytics[e]['win_percentage'] for e in elections]
            vote_trends = [party_analytics[e]['total_votes'] for e in elections]
            
            # Constituency analysis
            all_constituencies = set()
            constituency_performance = {}
            
            for election_id, performance in party_analytics.items():
                for candidate in performance['candidates']:
                    const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                    all_constituencies.add(const_code)
                    
                    if const_code not in constituency_performance:
                        constituency_performance[const_code] = {'contested': 0, 'won': 0, 'elections': []}
                    
                    constituency_performance[const_code]['contested'] += 1
                    constituency_performance[const_code]['elections'].append(election_id)
                    
                    if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                        constituency_performance[const_code]['won'] += 1
            
            # Strong vs weak constituencies
            strong_constituencies = [
                {'constituency': k, **v, 'win_rate': round((v['won']/v['contested'])*100, 2)}
                for k, v in constituency_performance.items() 
                if v['contested'] > 1 and v['won'] >= v['contested'] * 0.7  # Won 70%+ of contests
            ]
            
            weak_constituencies = [
                {'constituency': k, **v, 'win_rate': round((v['won']/v['contested'])*100, 2)}
                for k, v in constituency_performance.items() 
                if v['contested'] > 1 and v['won'] == 0  # Never won
            ]
            
            analytics_data = {
                'party_name': party_name,
                'performance_summary': {
                    'total_elections': len(party_analytics),
                    'total_seats_contested': sum(p['seats_contested'] for p in party_analytics.values()),
                    'total_seats_won': sum(p['seats_won'] for p in party_analytics.values()),
                    'overall_win_rate': round((sum(p['seats_won'] for p in party_analytics.values()) / 
                                             sum(p['seats_contested'] for p in party_analytics.values())) * 100, 2),
                    'total_votes': sum(p['total_votes'] for p in party_analytics.values()),
                    'unique_constituencies': len(all_constituencies)
                },
                'trends': {
                    'win_percentage_trend': win_percentages,
                    'vote_trend': vote_trends,
                    'best_election': max(party_analytics.values(), key=lambda x: x['win_percentage'])['election_id'],
                    'worst_election': min(party_analytics.values(), key=lambda x: x['win_percentage'])['election_id']
                },
                'constituency_analysis': {
                    'strong_constituencies': sorted(strong_constituencies, key=lambda x: x['win_rate'], reverse=True),
                    'weak_constituencies': sorted(weak_constituencies, key=lambda x: x['contested'], reverse=True),
                    'total_constituencies_contested': len(all_constituencies)
                },
                'detailed_performance': party_analytics
            }
            
            return APIResponse.success(
                data=analytics_data,
                message=f"Performance analytics for {party_name} retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get party performance", party=party_name, error=str(e))
            return APIResponse.internal_error("Failed to retrieve party performance")

@parties_ns.route('/comparison')
class PartyComparison(Resource):
    @parties_ns.doc('compare_parties')
    @parties_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        ⚖️ Compare performance of multiple political parties
        
        Compare performance metrics of multiple political parties across elections.
        
        **Query Parameters:**
        - `parties`: Comma-separated list of party names to compare
        - `election`: Specific election to compare (optional)
        - `metric`: Comparison metric (win_percentage, total_votes, seats_won)
        """
        try:
            parties_param = request.args.get('parties', '')
            election_filter = request.args.get('election')
            metric = request.args.get('metric', 'win_percentage')
            
            if not parties_param:
                return APIResponse.error(
                    "Please provide parties parameter with comma-separated party names",
                    "VALIDATION_ERROR", 400
                )
            
            party_names = [name.strip() for name in parties_param.split(',')]
            if len(party_names) < 2:
                return APIResponse.error(
                    "Please provide at least 2 parties to compare",
                    "VALIDATION_ERROR", 400
                )
            
            all_data = load_all_party_data()
            comparison_data = {}
            
            for party_name in party_names:
                party_performance = {}
                
                for election_id, election_data in all_data.items():
                    if election_filter and election_id != election_filter:
                        continue
                        
                    candidates = election_data.get('candidates', [])
                    performance = calculate_party_performance(party_name, candidates, election_id)
                    
                    if performance and performance['seats_contested'] > 0:
                        party_performance[election_id] = performance
                
                if party_performance:
                    comparison_data[party_name] = {
                        'performance_by_election': party_performance,
                        'overall': {
                            'total_contested': sum(p['seats_contested'] for p in party_performance.values()),
                            'total_won': sum(p['seats_won'] for p in party_performance.values()),
                            'overall_win_percentage': round((sum(p['seats_won'] for p in party_performance.values()) / 
                                                           sum(p['seats_contested'] for p in party_performance.values())) * 100, 2) 
                                                           if sum(p['seats_contested'] for p in party_performance.values()) > 0 else 0,
                            'total_votes': sum(p['total_votes'] for p in party_performance.values()),
                            'elections_participated': len(party_performance)
                        }
                    }
            
            if not comparison_data:
                return APIResponse.error(
                    "No performance data found for the specified parties",
                    "NOT_FOUND", 404
                )
            
            # Rank parties by selected metric
            rankings = []
            for party_name, party_data in comparison_data.items():
                if metric == 'win_percentage':
                    value = party_data['overall']['overall_win_percentage']
                elif metric == 'total_votes':
                    value = party_data['overall']['total_votes']
                elif metric == 'seats_won':
                    value = party_data['overall']['total_won']
                else:
                    value = party_data['overall']['overall_win_percentage']
                
                rankings.append({'party': party_name, 'value': value, 'metric': metric})
            
            rankings.sort(key=lambda x: x['value'], reverse=True)
            
            response_data = {
                'comparison_parties': party_names,
                'election_filter': election_filter,
                'comparison_metric': metric,
                'rankings': rankings,
                'detailed_comparison': comparison_data
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Comparison of {len(party_names)} parties completed successfully"
            )
            
        except Exception as e:
            logger.error("Failed to compare parties", error=str(e))
            return APIResponse.internal_error("Failed to compare parties")

@parties_ns.route('/national-parties')
class NationalParties(Resource):
    @parties_ns.doc('get_national_parties')
    @parties_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        🇮🇳 Get information about major national political parties
        
        Returns information about parties that contested across multiple states
        and have significant national presence based on their electoral performance.
        """
        try:
            all_data = load_all_party_data()
            party_presence = {}
            
            # Calculate state presence and performance for each party
            for election_id, election_data in all_data.items():
                candidates = election_data.get('candidates', [])
                
                for candidate in candidates:
                    party_name = candidate.get('Party', candidate.get('party', 'Unknown'))
                    
                    if party_name not in party_presence:
                        party_presence[party_name] = {
                            'elections': set(),
                            'states': set(),
                            'total_candidates': 0,
                            'total_wins': 0,
                            'total_votes': 0
                        }
                    
                    party_presence[party_name]['elections'].add(election_id)
                    party_presence[party_name]['total_candidates'] += 1
                    
                    # Extract state from constituency or election
                    if 'lok-sabha' in election_id:
                        # For Lok Sabha, extract state from constituency code
                        const_code = candidate.get('Constituency Code', candidate.get('constituency_code', ''))
                        if const_code and '-' in const_code:
                            state_code = const_code.split('-')[0]
                            party_presence[party_name]['states'].add(state_code)
                    elif 'delhi' in election_id:
                        party_presence[party_name]['states'].add('DL')
                    elif 'maharashtra' in election_id:
                        party_presence[party_name]['states'].add('MH')
                    
                    if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                        party_presence[party_name]['total_wins'] += 1
                    
                    votes = candidate.get('Votes', candidate.get('votes', 0))
                    if votes and str(votes).replace(',', '').isdigit():
                        party_presence[party_name]['total_votes'] += int(str(votes).replace(',', ''))
            
            # Define criteria for national parties
            national_parties = []
            for party_name, presence in party_presence.items():
                # Consider a party national if it:
                # 1. Contested in multiple states (>=3) OR
                # 2. Contested in Lok Sabha with significant presence (>=20 candidates) OR
                # 3. Has significant vote share across elections
                
                states_count = len(presence['states'])
                elections_count = len(presence['elections'])
                lok_sabha_presence = any('lok-sabha' in e for e in presence['elections'])
                
                is_national = (
                    states_count >= 3 or  # Multi-state presence
                    (lok_sabha_presence and presence['total_candidates'] >= 20) or  # Significant Lok Sabha presence
                    presence['total_votes'] >= 1000000  # Significant total votes
                )
                
                if is_national:
                    national_parties.append({
                        'name': party_name,
                        'states_present': states_count,
                        'elections_participated': elections_count,
                        'total_candidates': presence['total_candidates'],
                        'total_wins': presence['total_wins'],
                        'total_votes': presence['total_votes'],
                        'win_percentage': round((presence['total_wins'] / presence['total_candidates']) * 100, 2),
                        'national_footprint_score': states_count * 10 + elections_count * 5 + (presence['total_votes'] // 100000)
                    })
            
            # Sort by national footprint score
            national_parties.sort(key=lambda x: x['national_footprint_score'], reverse=True)
            
            response_data = {
                'national_parties': national_parties,
                'classification_criteria': {
                    'multi_state_presence': 'Parties present in 3+ states',
                    'lok_sabha_threshold': 'Contested 20+ Lok Sabha seats',
                    'vote_threshold': 'Received 1M+ total votes'
                },
                'summary': {
                    'total_national_parties': len(national_parties),
                    'top_party': national_parties[0]['name'] if national_parties else None,
                    'most_widespread': max(national_parties, key=lambda x: x['states_present'])['name'] if national_parties else None
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Retrieved {len(national_parties)} national parties"
            )
            
        except Exception as e:
            logger.error("Failed to get national parties", error=str(e))
            return APIResponse.internal_error("Failed to retrieve national parties")
