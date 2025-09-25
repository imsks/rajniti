"""
Search API Namespace

Provides comprehensive search functionality across all election data
including candidates, parties, constituencies, and advanced search features.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from flask import request
from flask_restx import Namespace, Resource
from app.core.responses import APIResponse
from app.core.exceptions import ValidationError
from app.core.logging_config import get_logger
from app.api.models import (
    search_request_model,
    api_response_model,
    error_response_model
)

# Create namespace
search_ns = Namespace(
    'search',
    description='🔍 Universal Search API\n\nPowerful search functionality across all election data with advanced filtering and ranking.'
)

logger = get_logger("rajniti.api.search")

def load_all_search_data() -> Dict[str, Any]:
    """Load all election data for search functionality"""
    search_data = {
        'candidates': [],
        'constituencies': [],
        'parties': [],
        'elections': []
    }
    
    data_root = Path("app/data")
    
    election_configs = [
        {
            'id': 'lok-sabha-2024',
            'name': 'Lok Sabha General Elections 2024',
            'type': 'LOK_SABHA',
            'year': 2024,
            'path': data_root / "lok_sabha" / "lok-sabha-2024"
        },
        {
            'id': 'delhi-assembly-2025', 
            'name': 'Delhi Legislative Assembly Elections 2025',
            'type': 'VIDHAN_SABHA',
            'year': 2025,
            'state': 'Delhi',
            'path': data_root / "vidhan_sabha" / "DL_2025_ASSEMBLY"
        },
        {
            'id': 'maharashtra-assembly-2024',
            'name': 'Maharashtra Legislative Assembly Elections 2024', 
            'type': 'VIDHAN_SABHA',
            'year': 2024,
            'state': 'Maharashtra',
            'path': data_root / "vidhan_sabha" / "MH_2024"
        }
    ]
    
    for election_config in election_configs:
        try:
            election_path = election_config['path']
            election_id = election_config['id']
            
            # Add election metadata
            search_data['elections'].append({
                'id': election_id,
                'name': election_config['name'],
                'type': election_config['type'],
                'year': election_config['year'],
                'state': election_config.get('state'),
                'searchable_text': f"{election_config['name']} {election_config['type']} {election_config['year']}"
            })
            
            # Load candidates
            candidates_file = election_path / "candidates.json"
            if candidates_file.exists():
                with open(candidates_file, 'r', encoding='utf-8') as f:
                    candidates = json.load(f)
                    
                for candidate in candidates:
                    search_candidate = {
                        'type': 'candidate',
                        'election_id': election_id,
                        'id': f"{election_id}_{candidate.get('Name', candidate.get('name', ''))}".replace(' ', '_'),
                        'name': candidate.get('Name', candidate.get('name', '')),
                        'party': candidate.get('Party', candidate.get('party', '')),
                        'constituency': candidate.get('Constituency Code', candidate.get('constituency_code', '')),
                        'status': candidate.get('Status', candidate.get('status', '')),
                        'votes': candidate.get('Votes', candidate.get('votes', 0)),
                        'margin': candidate.get('Margin', candidate.get('margin', 0)),
                        'image_url': candidate.get('Image URL', candidate.get('image_url', '')),
                        'searchable_text': f"{candidate.get('Name', candidate.get('name', ''))} {candidate.get('Party', candidate.get('party', ''))} {candidate.get('Constituency Code', candidate.get('constituency_code', ''))}",
                        'raw_data': candidate
                    }
                    search_data['candidates'].append(search_candidate)
            
            # Load constituencies  
            constituencies_file = election_path / "constituencies.json"
            if constituencies_file.exists():
                with open(constituencies_file, 'r', encoding='utf-8') as f:
                    constituencies = json.load(f)
                    
                for constituency in constituencies:
                    search_constituency = {
                        'type': 'constituency',
                        'election_id': election_id,
                        'id': f"{election_id}_{constituency.get('code', constituency.get('id', ''))}",
                        'name': constituency.get('name', ''),
                        'code': constituency.get('code', constituency.get('id', '')),
                        'state': constituency.get('state', election_config.get('state', '')),
                        'searchable_text': f"{constituency.get('name', '')} {constituency.get('code', '')}",
                        'raw_data': constituency
                    }
                    search_data['constituencies'].append(search_constituency)
            
            # Load parties
            parties_file = election_path / "parties.json" 
            if parties_file.exists():
                with open(parties_file, 'r', encoding='utf-8') as f:
                    parties = json.load(f)
                    
                for party in parties:
                    search_party = {
                        'type': 'party',
                        'election_id': election_id,
                        'id': f"{election_id}_{party.get('name', party.get('party_name', ''))}".replace(' ', '_'),
                        'name': party.get('name', party.get('party_name', '')),
                        'symbol': party.get('symbol', ''),
                        'seats_won': party.get('seats_won', party.get('total_seats', 0)),
                        'searchable_text': f"{party.get('name', party.get('party_name', ''))} {party.get('symbol', '')}",
                        'raw_data': party
                    }
                    search_data['parties'].append(search_party)
                    
        except Exception as e:
            logger.warning(f"Failed to load search data for {election_id}", error=str(e))
            continue
    
    return search_data

def calculate_search_score(item: Dict[str, Any], query: str, search_type: str = None) -> float:
    """Calculate relevance score for search results"""
    query_lower = query.lower()
    score = 0.0
    
    # Primary field matches (highest weight)
    if search_type == 'candidate' or item['type'] == 'candidate':
        if query_lower in item.get('name', '').lower():
            score += 100
        if query_lower in item.get('party', '').lower():
            score += 80
        if query_lower in item.get('constituency', '').lower():
            score += 60
    elif search_type == 'party' or item['type'] == 'party':
        if query_lower in item.get('name', '').lower():
            score += 100
        if query_lower in item.get('symbol', '').lower():
            score += 70
    elif search_type == 'constituency' or item['type'] == 'constituency':
        if query_lower in item.get('name', '').lower():
            score += 100
        if query_lower in item.get('code', '').lower():
            score += 90
        if query_lower in item.get('state', '').lower():
            score += 50
    elif search_type == 'election' or item['type'] == 'election':
        if query_lower in item.get('name', '').lower():
            score += 100
        if str(item.get('year', '')) == query:
            score += 90
    
    # Exact match bonus
    if query_lower == item.get('name', '').lower():
        score += 50
    
    # Partial match in searchable text
    searchable_text = item.get('searchable_text', '').lower()
    if query_lower in searchable_text:
        score += 30
    
    # Word boundary matches (higher priority)
    words = query_lower.split()
    for word in words:
        if len(word) >= 3:  # Only consider words with 3+ characters
            if re.search(r'\b' + re.escape(word) + r'\b', searchable_text):
                score += 20
    
    return score

def perform_search(query: str, search_data: Dict[str, Any], search_type: str = None, 
                  filters: Dict[str, Any] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """Perform search across all data types"""
    if not query or len(query.strip()) < 2:
        return []
    
    query = query.strip()
    results = []
    
    # Determine what data types to search
    if search_type:
        data_types = [search_type] if search_type in search_data else []
    else:
        data_types = ['candidates', 'parties', 'constituencies', 'elections']
    
    # Search each data type
    for data_type in data_types:
        items = search_data.get(data_type, [])
        
        for item in items:
            # Apply filters first
            if filters and not matches_filters(item, filters):
                continue
            
            # Calculate relevance score
            score = calculate_search_score(item, query, search_type)
            
            if score > 0:
                result_item = item.copy()
                result_item['search_score'] = score
                result_item['match_reason'] = determine_match_reason(item, query)
                results.append(result_item)
    
    # Sort by relevance score (descending)
    results.sort(key=lambda x: x['search_score'], reverse=True)
    
    return results[:limit]

def matches_filters(item: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Check if item matches the provided filters"""
    for filter_key, filter_value in filters.items():
        if filter_key == 'election':
            if item.get('election_id') != filter_value:
                return False
        elif filter_key == 'state':
            if filter_value.lower() not in item.get('state', '').lower():
                return False
        elif filter_key == 'status':
            if filter_value.upper() != item.get('status', '').upper():
                return False
        elif filter_key == 'party':
            if filter_value.lower() not in item.get('party', '').lower():
                return False
        elif filter_key == 'type':
            if item.get('type') != filter_value:
                return False
    
    return True

def determine_match_reason(item: Dict[str, Any], query: str) -> str:
    """Determine why an item matched the search query"""
    query_lower = query.lower()
    
    if query_lower in item.get('name', '').lower():
        return 'name_match'
    elif query_lower in item.get('party', '').lower():
        return 'party_match'
    elif query_lower in item.get('constituency', '').lower():
        return 'constituency_match'
    elif query_lower in item.get('symbol', '').lower():
        return 'symbol_match'
    elif query_lower in item.get('state', '').lower():
        return 'state_match'
    else:
        return 'text_match'

@search_ns.route('/')
class UniversalSearch(Resource):
    @search_ns.doc('universal_search')
    @search_ns.expect(search_request_model, validate=False)
    @search_ns.marshal_with(api_response_model, code=200)
    @search_ns.response(400, 'Bad Request', error_response_model)
    def get(self):
        """
        🔍 Universal search across all election data
        
        Search across candidates, parties, constituencies, and elections with
        intelligent ranking and comprehensive filtering options.
        
        **Query Parameters:**
        - `q` or `query`: Search query (minimum 2 characters) **(required)**
        - `type`: Search type filter (candidate, party, constituency, election)
        - `election`: Filter by election ID
        - `state`: Filter by state/UT  
        - `party`: Filter by political party
        - `status`: Filter by result status (WON/LOST)
        - `limit`: Maximum results (default: 50, max: 100)
        
        **Examples:**
        - `/search?q=modi&type=candidate`
        - `/search?q=bjp&type=party&election=lok-sabha-2024`
        - `/search?q=delhi&limit=20`
        """
        try:
            query = request.args.get('q') or request.args.get('query', '')
            search_type = request.args.get('type')
            limit = min(int(request.args.get('limit', 50)), 100)
            
            if not query or len(query.strip()) < 2:
                return APIResponse.error(
                    "Search query must be at least 2 characters long", 
                    "VALIDATION_ERROR", 400
                )
            
            # Validate search type
            valid_types = ['candidate', 'party', 'constituency', 'election']
            if search_type and search_type not in valid_types:
                return APIResponse.error(
                    f"Invalid search type. Must be one of: {', '.join(valid_types)}",
                    "VALIDATION_ERROR", 400
                )
            
            # Extract filters
            filters = {}
            for param in ['election', 'state', 'party', 'status']:
                value = request.args.get(param)
                if value:
                    filters[param] = value
            
            # Load search data
            search_data = load_all_search_data()
            
            # Perform search
            results = perform_search(query, search_data, search_type, filters, limit)
            
            # Prepare response
            search_results = {
                'query': query.strip(),
                'search_type': search_type,
                'filters': filters,
                'total_results': len(results),
                'results': results,
                'suggestions': generate_suggestions(query, search_data) if len(results) < 5 else []
            }
            
            return APIResponse.success(
                data=search_results,
                message=f"Found {len(results)} results for '{query}'"
            )
            
        except ValueError as e:
            return APIResponse.error("Invalid limit parameter", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Search failed", query=query, error=str(e))
            return APIResponse.internal_error("Search operation failed")

@search_ns.route('/suggestions')
class SearchSuggestions(Resource):
    @search_ns.doc('get_search_suggestions')
    @search_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        💡 Get search suggestions and autocomplete
        
        Returns search suggestions based on partial query to help users
        discover relevant content and improve search experience.
        
        **Query Parameters:**
        - `q`: Partial search query (minimum 1 character)
        - `type`: Suggestion type filter (candidate, party, constituency)
        - `limit`: Maximum suggestions (default: 10, max: 20)
        """
        try:
            query = request.args.get('q', '')
            suggestion_type = request.args.get('type')
            limit = min(int(request.args.get('limit', 10)), 20)
            
            if len(query) < 1:
                return APIResponse.error(
                    "Query must be at least 1 character long",
                    "VALIDATION_ERROR", 400
                )
            
            search_data = load_all_search_data()
            suggestions = generate_suggestions(query, search_data, suggestion_type, limit)
            
            return APIResponse.success(
                data={
                    'query': query,
                    'suggestion_type': suggestion_type,
                    'suggestions': suggestions
                },
                message=f"Generated {len(suggestions)} suggestions"
            )
            
        except ValueError as e:
            return APIResponse.error("Invalid limit parameter", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Failed to generate suggestions", error=str(e))
            return APIResponse.internal_error("Failed to generate suggestions")

def generate_suggestions(query: str, search_data: Dict[str, Any], 
                        suggestion_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
    """Generate search suggestions based on partial query"""
    suggestions = []
    query_lower = query.lower()
    
    # Determine data types to suggest from
    if suggestion_type:
        data_types = [f"{suggestion_type}s"] if f"{suggestion_type}s" in search_data else []
    else:
        data_types = ['candidates', 'parties', 'constituencies', 'elections']
    
    for data_type in data_types:
        items = search_data.get(data_type, [])
        
        for item in items:
            name = item.get('name', '')
            
            # Check if name starts with query (prefix match)
            if name.lower().startswith(query_lower):
                suggestions.append({
                    'text': name,
                    'type': item['type'],
                    'category': data_type.rstrip('s'),
                    'match_type': 'prefix',
                    'additional_info': get_additional_info(item)
                })
            # Check if any word in name starts with query
            elif any(word.lower().startswith(query_lower) for word in name.split()):
                suggestions.append({
                    'text': name,
                    'type': item['type'],
                    'category': data_type.rstrip('s'),
                    'match_type': 'word_prefix',
                    'additional_info': get_additional_info(item)
                })
            # Check if query is contained in name
            elif query_lower in name.lower() and len(query) >= 3:
                suggestions.append({
                    'text': name,
                    'type': item['type'],
                    'category': data_type.rstrip('s'),
                    'match_type': 'contains',
                    'additional_info': get_additional_info(item)
                })
    
    # Remove duplicates and sort by relevance
    seen = set()
    unique_suggestions = []
    
    for suggestion in suggestions:
        if suggestion['text'] not in seen:
            seen.add(suggestion['text'])
            unique_suggestions.append(suggestion)
    
    # Sort by match type priority and alphabetically
    match_priority = {'prefix': 1, 'word_prefix': 2, 'contains': 3}
    unique_suggestions.sort(key=lambda x: (match_priority.get(x['match_type'], 4), x['text']))
    
    return unique_suggestions[:limit]

def get_additional_info(item: Dict[str, Any]) -> str:
    """Get additional context information for suggestions"""
    if item['type'] == 'candidate':
        return f"{item.get('party', '')} • {item.get('constituency', '')}"
    elif item['type'] == 'party':
        return f"{item.get('symbol', '')} • {item.get('seats_won', 0)} seats"
    elif item['type'] == 'constituency':
        return f"{item.get('state', '')} • {item.get('code', '')}"
    elif item['type'] == 'election':
        return f"{item.get('year', '')} • {item.get('type', '')}"
    else:
        return ""

@search_ns.route('/advanced')
class AdvancedSearch(Resource):
    @search_ns.doc('advanced_search')
    @search_ns.marshal_with(api_response_model, code=200)
    def get(self):
        """
        🎯 Advanced search with complex filtering
        
        Perform advanced searches with multiple criteria, boolean operations,
        and sophisticated filtering options for power users.
        
        **Query Parameters:**
        - `q`: Main search query
        - `candidates`: Candidate name patterns (comma-separated)
        - `parties`: Party name patterns (comma-separated)  
        - `constituencies`: Constituency patterns (comma-separated)
        - `elections`: Election IDs (comma-separated)
        - `status`: Result status (WON/LOST)
        - `min_votes`: Minimum vote threshold
        - `max_votes`: Maximum vote threshold
        - `state`: State/UT filter
        - `year`: Election year
        - `sort`: Sort by (name, votes, margin, relevance) - default: relevance
        - `order`: Sort order (asc, desc) - default: desc
        - `limit`: Maximum results (default: 50)
        
        **Examples:**
        - `/search/advanced?parties=BJP,Congress&status=WON&min_votes=50000`
        - `/search/advanced?state=delhi&year=2025&sort=votes`
        """
        try:
            # Extract all search parameters
            main_query = request.args.get('q', '')
            candidates_filter = request.args.get('candidates', '')
            parties_filter = request.args.get('parties', '')
            constituencies_filter = request.args.get('constituencies', '')
            elections_filter = request.args.get('elections', '')
            status_filter = request.args.get('status', '')
            state_filter = request.args.get('state', '')
            year_filter = request.args.get('year', '')
            
            # Numeric filters
            min_votes = request.args.get('min_votes', type=int)
            max_votes = request.args.get('max_votes', type=int)
            
            # Sorting
            sort_by = request.args.get('sort', 'relevance')
            sort_order = request.args.get('order', 'desc')
            limit = min(int(request.args.get('limit', 50)), 100)
            
            # Load search data
            search_data = load_all_search_data()
            
            # Apply advanced filtering
            filtered_results = []
            
            # Start with all candidates (most common search target)
            candidates = search_data.get('candidates', [])
            
            for candidate in candidates:
                matches = True
                
                # Apply all filters
                if main_query and main_query.lower() not in candidate.get('searchable_text', '').lower():
                    matches = False
                
                if candidates_filter:
                    candidate_patterns = [p.strip() for p in candidates_filter.split(',')]
                    if not any(pattern.lower() in candidate.get('name', '').lower() for pattern in candidate_patterns):
                        matches = False
                
                if parties_filter:
                    party_patterns = [p.strip() for p in parties_filter.split(',')]
                    if not any(pattern.lower() in candidate.get('party', '').lower() for pattern in party_patterns):
                        matches = False
                
                if constituencies_filter:
                    constituency_patterns = [p.strip() for p in constituencies_filter.split(',')]
                    if not any(pattern.lower() in candidate.get('constituency', '').lower() for pattern in constituency_patterns):
                        matches = False
                
                if elections_filter:
                    election_ids = [e.strip() for e in elections_filter.split(',')]
                    if candidate.get('election_id') not in election_ids:
                        matches = False
                
                if status_filter and candidate.get('status', '').upper() != status_filter.upper():
                    matches = False
                
                if state_filter:
                    # For Lok Sabha, extract state from constituency code
                    candidate_state = ''
                    if 'lok-sabha' in candidate.get('election_id', ''):
                        const_code = candidate.get('constituency', '')
                        if const_code and '-' in const_code:
                            candidate_state = const_code.split('-')[0]
                    else:
                        # For assembly elections, use election state
                        if 'delhi' in candidate.get('election_id', ''):
                            candidate_state = 'DL'
                        elif 'maharashtra' in candidate.get('election_id', ''):
                            candidate_state = 'MH'
                    
                    if candidate_state.upper() != state_filter.upper():
                        matches = False
                
                if year_filter:
                    election_year = None
                    if 'lok-sabha-2024' in candidate.get('election_id', ''):
                        election_year = '2024'
                    elif 'delhi-assembly-2025' in candidate.get('election_id', ''):
                        election_year = '2025'
                    elif 'maharashtra-assembly-2024' in candidate.get('election_id', ''):
                        election_year = '2024'
                    
                    if election_year != year_filter:
                        matches = False
                
                # Numeric filters
                if min_votes or max_votes:
                    votes = candidate.get('votes', 0)
                    try:
                        vote_count = int(str(votes).replace(',', '')) if votes else 0
                        if min_votes and vote_count < min_votes:
                            matches = False
                        if max_votes and vote_count > max_votes:
                            matches = False
                    except (ValueError, TypeError):
                        if min_votes or max_votes:
                            matches = False
                
                if matches:
                    # Calculate relevance score if main query provided
                    if main_query:
                        candidate['search_score'] = calculate_search_score(candidate, main_query, 'candidate')
                    else:
                        candidate['search_score'] = 50  # Default relevance
                    
                    filtered_results.append(candidate)
            
            # Sort results
            if sort_by == 'name':
                filtered_results.sort(key=lambda x: x.get('name', ''), reverse=(sort_order == 'desc'))
            elif sort_by == 'votes':
                filtered_results.sort(
                    key=lambda x: int(str(x.get('votes', 0)).replace(',', '') or 0), 
                    reverse=(sort_order == 'desc')
                )
            elif sort_by == 'margin':
                filtered_results.sort(
                    key=lambda x: abs(int(str(x.get('margin', 0)).replace('-', '').replace(',', '') or 0)), 
                    reverse=(sort_order == 'desc')
                )
            else:  # relevance (default)
                filtered_results.sort(key=lambda x: x.get('search_score', 0), reverse=True)
            
            # Limit results
            final_results = filtered_results[:limit]
            
            # Prepare search summary
            search_summary = {
                'total_results': len(final_results),
                'filters_applied': {
                    'main_query': main_query,
                    'candidates': candidates_filter,
                    'parties': parties_filter,
                    'constituencies': constituencies_filter,
                    'elections': elections_filter,
                    'status': status_filter,
                    'state': state_filter,
                    'year': year_filter,
                    'min_votes': min_votes,
                    'max_votes': max_votes
                },
                'sorting': {
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
            
            return APIResponse.success(
                data={
                    'search_summary': search_summary,
                    'results': final_results
                },
                message=f"Advanced search completed: {len(final_results)} results found"
            )
            
        except ValueError as e:
            return APIResponse.error("Invalid numeric parameter", "VALIDATION_ERROR", 400)
        except Exception as e:
            logger.error("Advanced search failed", error=str(e))
            return APIResponse.internal_error("Advanced search operation failed")
