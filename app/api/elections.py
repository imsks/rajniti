"""
Elections API Namespace

Provides comprehensive endpoints for accessing Indian election data including
Lok Sabha and Vidhan Sabha elections, results, statistics and analytics.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from app.core.responses import APIResponse
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger
from app.api.models import (
    election_summary_model, 
    election_detail_model, 
    candidate_model,
    constituency_results_model,
    party_performance_model,
    electoral_statistics_model,
    api_response_model,
    error_response_model,
    filter_request_model
)

# Create namespace
elections_ns = Namespace(
    'elections', 
    description='🗳️ Election Data & Results API\n\nAccess comprehensive Indian election data including Lok Sabha and Vidhan Sabha results, candidate information, and electoral statistics.'
)

logger = get_logger("rajniti.api.elections")

# ==================== Helper Functions ====================

def load_election_data(election_id: str) -> Dict[str, Any]:
    """Load election data from JSON files"""
    try:
        data_root = Path("app/data")
        
        # Map election IDs to data paths
        election_paths = {
            "lok-sabha-2024": data_root / "lok_sabha" / "lok-sabha-2024",
            "delhi-assembly-2025": data_root / "vidhan_sabha" / "DL_2025_ASSEMBLY", 
            "maharashtra-assembly-2024": data_root / "vidhan_sabha" / "MH_2024"
        }
        
        if election_id not in election_paths:
            raise NotFoundError("Election", election_id)
            
        election_path = election_paths[election_id]
        
        # Load candidate, constituency, and party data
        candidates_file = election_path / "candidates.json"
        constituencies_file = election_path / "constituencies.json"
        parties_file = election_path / "parties.json"
        
        data = {}
        
        if candidates_file.exists():
            with open(candidates_file, 'r', encoding='utf-8') as f:
                data['candidates'] = json.load(f)
                
        if constituencies_file.exists():
            with open(constituencies_file, 'r', encoding='utf-8') as f:
                data['constituencies'] = json.load(f)
                
        if parties_file.exists():
            with open(parties_file, 'r', encoding='utf-8') as f:
                data['parties'] = json.load(f)
        
        return data
        
    except FileNotFoundError:
        raise NotFoundError("Election data", election_id)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in election data", election_id=election_id, error=str(e))
        raise ValidationError(f"Invalid JSON format in {election_id} data")
    except Exception as e:
        logger.error("Failed to load election data", election_id=election_id, error=str(e))
        raise

def get_election_metadata(election_id: str) -> Dict[str, Any]:
    """Get election metadata and summary"""
    election_info = {
        "lok-sabha-2024": {
            "id": "lok-sabha-2024",
            "name": "Lok Sabha General Elections 2024",
            "type": "LOK_SABHA",
            "year": 2024,
            "state": None,
            "state_code": None,
            "total_constituencies": 543,
            "phases": 7,
            "start_date": "2024-04-19",
            "end_date": "2024-06-01", 
            "result_date": "2024-06-04",
            "status": "COMPLETED"
        },
        "delhi-assembly-2025": {
            "id": "delhi-assembly-2025",
            "name": "Delhi Legislative Assembly Elections 2025", 
            "type": "VIDHAN_SABHA",
            "year": 2025,
            "state": "Delhi",
            "state_code": "DL",
            "total_constituencies": 70,
            "phases": 1,
            "start_date": "2025-02-05",
            "end_date": "2025-02-05",
            "result_date": "2025-02-08",
            "status": "COMPLETED"
        },
        "maharashtra-assembly-2024": {
            "id": "maharashtra-assembly-2024",
            "name": "Maharashtra Legislative Assembly Elections 2024",
            "type": "VIDHAN_SABHA", 
            "year": 2024,
            "state": "Maharashtra",
            "state_code": "MH",
            "total_constituencies": 288,
            "phases": 1,
            "start_date": "2024-11-20",
            "end_date": "2024-11-20",
            "result_date": "2024-11-23",
            "status": "COMPLETED"
        }
    }
    
    if election_id not in election_info:
        raise NotFoundError("Election", election_id)
        
    return election_info[election_id]

def apply_filters(data: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Apply filters to election data"""
    if not filters or not data:
        return data
        
    filtered_data = data
    
    for key, value in filters.items():
        if key in ['page', 'per_page', 'limit', 'offset']:
            continue
            
        filtered_data = [
            item for item in filtered_data
            if isinstance(item, dict) and _matches_filter(item, key, value)
        ]
    
    return filtered_data

def _matches_filter(item: Dict[str, Any], key: str, value: Any) -> bool:
    """Check if item matches filter condition"""
    # Handle nested keys (e.g., 'party.name')
    keys = key.split('.')
    current_item = item
    
    try:
        for k in keys:
            if isinstance(current_item, dict) and k in current_item:
                current_item = current_item[k]
            else:
                return False
                
        # Case-insensitive string matching
        if isinstance(value, str) and isinstance(current_item, str):
            return current_item.lower() == value.lower()
        elif isinstance(value, (int, float)):
            return current_item == value
        elif isinstance(value, list):
            return current_item in value
            
        return str(current_item).lower() == str(value).lower()
        
    except (KeyError, TypeError):
        return False

# ==================== API Endpoints ====================

@elections_ns.route('/overview')
class ElectionOverview(Resource):
    @elections_ns.doc('get_election_overview')
    @elections_ns.marshal_with(api_response_model, code=200)
    @elections_ns.response(500, 'Internal Server Error', error_response_model)
    def get(self):
        """
        📊 Get overview of all available elections
        
        Returns a comprehensive overview of all available election datasets including
        summary statistics and metadata for each election.
        """
        try:
            available_elections = [
                "lok-sabha-2024",
                "delhi-assembly-2025", 
                "maharashtra-assembly-2024"
            ]
            
            overview_data = []
            total_candidates = 0
            total_constituencies = 0
            
            for election_id in available_elections:
                try:
                    metadata = get_election_metadata(election_id)
                    election_data = load_election_data(election_id)
                    
                    # Calculate statistics
                    candidates_count = len(election_data.get('candidates', []))
                    constituencies_count = len(election_data.get('constituencies', []))
                    parties_count = len(election_data.get('parties', []))
                    
                    total_candidates += candidates_count
                    total_constituencies += constituencies_count
                    
                    overview_data.append({
                        **metadata,
                        'total_candidates': candidates_count,
                        'total_constituencies': constituencies_count,
                        'total_parties': parties_count
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to load election {election_id}", error=str(e))
                    continue
            
            response_data = {
                'summary': {
                    'total_elections': len(overview_data),
                    'total_candidates': total_candidates,
                    'total_constituencies': total_constituencies,
                    'data_coverage': '2024-2025'
                },
                'elections': overview_data
            }
            
            return APIResponse.success(
                data=response_data,
                message="Election overview retrieved successfully"
            )
            
        except Exception as e:
            logger.error("Failed to get election overview", error=str(e))
            return APIResponse.internal_error("Failed to retrieve election overview")

@elections_ns.route('/<string:election_id>')
@elections_ns.param('election_id', 'Election identifier (e.g., lok-sabha-2024, delhi-assembly-2025)')
class ElectionDetail(Resource):
    @elections_ns.doc('get_election_detail')
    @elections_ns.marshal_with(api_response_model, code=200)
    @elections_ns.response(404, 'Election not found', error_response_model)
    @elections_ns.response(500, 'Internal Server Error', error_response_model)
    def get(self, election_id):
        """
        🗳️ Get detailed information about a specific election
        
        Returns comprehensive details about the specified election including
        metadata, statistics, and summary information.
        """
        try:
            metadata = get_election_metadata(election_id)
            election_data = load_election_data(election_id)
            
            # Calculate detailed statistics
            candidates = election_data.get('candidates', [])
            constituencies = election_data.get('constituencies', [])
            parties = election_data.get('parties', [])
            
            # Calculate winner statistics
            winners = [c for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won']
            total_votes = sum(int(str(c.get('Votes', c.get('votes', 0))).replace(',', '')) for c in candidates if c.get('Votes') or c.get('votes'))
            
            # Party-wise seat count
            party_seats = {}
            for winner in winners:
                party = winner.get('Party', winner.get('party', 'Unknown'))
                party_seats[party] = party_seats.get(party, 0) + 1
            
            detailed_info = {
                **metadata,
                'total_candidates': len(candidates),
                'total_constituencies': len(constituencies), 
                'total_parties': len(parties),
                'total_votes': total_votes,
                'statistics': {
                    'winners_by_party': party_seats,
                    'largest_party': max(party_seats, key=party_seats.get) if party_seats else None,
                    'largest_party_seats': max(party_seats.values()) if party_seats else 0,
                    'total_contested_seats': len(winners),
                    'average_candidates_per_constituency': round(len(candidates) / len(constituencies), 2) if constituencies else 0
                }
            }
            
            return APIResponse.success(
                data=detailed_info,
                message=f"Election details for {election_id} retrieved successfully"
            )
            
        except NotFoundError as e:
            return APIResponse.not_found("Election", election_id)
        except Exception as e:
            logger.error("Failed to get election detail", election_id=election_id, error=str(e))
            return APIResponse.internal_error("Failed to retrieve election details")

@elections_ns.route('/<string:election_id>/results')
@elections_ns.param('election_id', 'Election identifier')
class ElectionResults(Resource):
    @elections_ns.doc('get_election_results')
    @elections_ns.expect(filter_request_model, validate=False)
    @elections_ns.marshal_with(api_response_model, code=200)
    @elections_ns.response(404, 'Election not found', error_response_model)
    def get(self, election_id):
        """
        📈 Get election results with filtering options
        
        Returns detailed election results including candidate information,
        vote counts, margins, and constituency data. Supports various 
        filtering options to narrow down results.
        
        **Query Parameters:**
        - `status`: Filter by result status (WON, LOST)
        - `party`: Filter by political party name
        - `state`: Filter by state code (for national elections)
        - `constituency`: Filter by constituency name/code
        - `min_votes`: Minimum votes threshold
        - `max_votes`: Maximum votes threshold
        - `page`: Page number for pagination
        - `per_page`: Results per page (max 100)
        """
        try:
            metadata = get_election_metadata(election_id)
            election_data = load_election_data(election_id)
            
            candidates = election_data.get('candidates', [])
            if not candidates:
                raise NotFoundError("Election results", election_id)
            
            # Apply filters
            filters = dict(request.args)
            filtered_candidates = apply_filters(candidates, filters)
            
            # Pagination
            page = int(request.args.get('page', 1))
            per_page = min(int(request.args.get('per_page', 50)), 100)
            
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_results = filtered_candidates[start_idx:end_idx]
            
            # Prepare response
            results_data = {
                'election': metadata,
                'results': paginated_results,
                'summary': {
                    'total_results': len(filtered_candidates),
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (len(filtered_candidates) + per_page - 1) // per_page,
                    'filters_applied': {k: v for k, v in filters.items() if k not in ['page', 'per_page']}
                }
            }
            
            return APIResponse.paginated(
                data=paginated_results,
                page=page,
                per_page=per_page,
                total=len(filtered_candidates),
                message=f"Election results for {election_id} retrieved successfully",
                meta={'election': metadata}
            )
            
        except NotFoundError as e:
            return APIResponse.not_found("Election results", election_id)
        except ValueError as e:
            return APIResponse.error("Invalid pagination parameters", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Failed to get election results", election_id=election_id, error=str(e))
            return APIResponse.internal_error("Failed to retrieve election results")

@elections_ns.route('/<string:election_id>/winners')
@elections_ns.param('election_id', 'Election identifier')
class ElectionWinners(Resource):
    @elections_ns.doc('get_election_winners')
    @elections_ns.marshal_with(api_response_model, code=200)
    @elections_ns.response(404, 'Election not found', error_response_model)
    def get(self, election_id):
        """
        🏆 Get all winning candidates from an election
        
        Returns only the winning candidates from the specified election,
        sorted by constituency name for easy reference.
        """
        try:
            metadata = get_election_metadata(election_id)
            election_data = load_election_data(election_id)
            
            candidates = election_data.get('candidates', [])
            
            # Filter only winners
            winners = [
                candidate for candidate in candidates 
                if candidate.get('Status') == 'WON' or candidate.get('status') == 'won'
            ]
            
            if not winners:
                return APIResponse.success(
                    data=[],
                    message=f"No winners found for {election_id}",
                    meta={'election': metadata}
                )
            
            # Sort by constituency
            winners.sort(key=lambda x: x.get('constituency', x.get('Constituency Code', '')))
            
            # Party-wise summary
            party_summary = {}
            for winner in winners:
                party = winner.get('Party', winner.get('party', 'Unknown'))
                party_summary[party] = party_summary.get(party, 0) + 1
            
            response_data = {
                'election': metadata,
                'winners': winners,
                'summary': {
                    'total_winners': len(winners),
                    'party_wise_seats': party_summary,
                    'largest_party': max(party_summary, key=party_summary.get) if party_summary else None
                }
            }
            
            return APIResponse.success(
                data=response_data,
                message=f"Winners for {election_id} retrieved successfully"
            )
            
        except NotFoundError as e:
            return APIResponse.not_found("Election", election_id)
        except Exception as e:
            logger.error("Failed to get election winners", election_id=election_id, error=str(e))
            return APIResponse.internal_error("Failed to retrieve election winners")

@elections_ns.route('/<string:election_id>/statistics')
@elections_ns.param('election_id', 'Election identifier')
class ElectionStatistics(Resource):
    @elections_ns.doc('get_election_statistics')
    @elections_ns.marshal_with(api_response_model, code=200)
    @elections_ns.response(404, 'Election not found', error_response_model)
    def get(self, election_id):
        """
        📊 Get comprehensive election statistics and analytics
        
        Returns detailed statistical analysis of the election including:
        - Party performance metrics
        - Vote share analysis  
        - Constituency-wise breakdowns
        - Margin analysis
        - Demographic insights
        """
        try:
            metadata = get_election_metadata(election_id)
            election_data = load_election_data(election_id)
            
            candidates = election_data.get('candidates', [])
            constituencies = election_data.get('constituencies', [])
            parties = election_data.get('parties', [])
            
            if not candidates:
                raise NotFoundError("Election data", election_id)
            
            # Calculate comprehensive statistics
            statistics = _calculate_election_statistics(candidates, constituencies, parties, metadata)
            
            return APIResponse.success(
                data=statistics,
                message=f"Statistics for {election_id} retrieved successfully"
            )
            
        except NotFoundError as e:
            return APIResponse.not_found("Election", election_id)
        except Exception as e:
            logger.error("Failed to get election statistics", election_id=election_id, error=str(e))
            return APIResponse.internal_error("Failed to retrieve election statistics")

def _calculate_election_statistics(candidates, constituencies, parties, metadata):
    """Calculate comprehensive election statistics"""
    try:
        # Basic counts
        total_candidates = len(candidates)
        total_constituencies = len(constituencies) if constituencies else len(set(c.get('constituency', c.get('Constituency Code', '')) for c in candidates))
        total_parties = len(parties) if parties else len(set(c.get('Party', c.get('party', '')) for c in candidates))
        
        # Winners and vote analysis
        winners = [c for c in candidates if c.get('Status') == 'WON' or c.get('status') == 'won']
        
        # Vote statistics
        vote_stats = []
        margin_stats = []
        
        for candidate in candidates:
            votes = candidate.get('Votes', candidate.get('votes', 0))
            margin = candidate.get('Margin', candidate.get('margin', 0))
            
            if votes and str(votes).isdigit():
                vote_stats.append(int(votes))
            elif votes and isinstance(votes, str):
                # Clean string votes (remove commas, etc.)
                clean_votes = ''.join(c for c in str(votes) if c.isdigit())
                if clean_votes:
                    vote_stats.append(int(clean_votes))
                    
            if margin and str(margin).replace('-', '').isdigit():
                margin_stats.append(int(str(margin).replace('-', '')))
        
        # Party performance
        party_performance = {}
        for candidate in candidates:
            party = candidate.get('Party', candidate.get('party', 'Unknown'))
            if party not in party_performance:
                party_performance[party] = {
                    'contested': 0,
                    'won': 0,
                    'total_votes': 0
                }
            
            party_performance[party]['contested'] += 1
            
            if candidate.get('Status') == 'WON' or candidate.get('status') == 'won':
                party_performance[party]['won'] += 1
            
            votes = candidate.get('Votes', candidate.get('votes', 0))
            if votes:
                try:
                    clean_votes = int(str(votes).replace(',', '')) if isinstance(votes, str) else int(votes)
                    party_performance[party]['total_votes'] += clean_votes
                except (ValueError, TypeError):
                    pass
        
        # Calculate win percentages
        for party_data in party_performance.values():
            if party_data['contested'] > 0:
                party_data['win_percentage'] = round((party_data['won'] / party_data['contested']) * 100, 2)
            else:
                party_data['win_percentage'] = 0
        
        # Sort parties by seats won
        party_rankings = sorted(
            [(party, data) for party, data in party_performance.items()],
            key=lambda x: x[1]['won'],
            reverse=True
        )
        
        statistics = {
            'election_info': metadata,
            'overview': {
                'total_candidates': total_candidates,
                'total_constituencies': total_constituencies,
                'total_parties': total_parties,
                'average_candidates_per_constituency': round(total_candidates / total_constituencies, 2) if total_constituencies > 0 else 0
            },
            'vote_analysis': {
                'total_votes_polled': sum(vote_stats),
                'average_votes_per_candidate': round(sum(vote_stats) / len(vote_stats), 2) if vote_stats else 0,
                'highest_individual_votes': max(vote_stats) if vote_stats else 0,
                'lowest_individual_votes': min(vote_stats) if vote_stats else 0
            },
            'margin_analysis': {
                'average_victory_margin': round(sum(margin_stats) / len(margin_stats), 2) if margin_stats else 0,
                'highest_victory_margin': max(margin_stats) if margin_stats else 0,
                'lowest_victory_margin': min(margin_stats) if margin_stats else 0
            },
            'party_performance': {
                'rankings': party_rankings[:10],  # Top 10 parties
                'total_parties': len(party_performance),
                'single_seat_parties': len([p for p in party_performance.values() if p['won'] == 1])
            }
        }
        
        return statistics
        
    except Exception as e:
        logger.error("Failed to calculate election statistics", error=str(e))
        return {
            'error': 'Failed to calculate statistics',
            'basic_info': {
                'total_candidates': len(candidates),
                'total_constituencies': len(constituencies) if constituencies else 0
            }
        }
