"""
API Models and Schemas for Rajniti Election Data API

Defines all the data models, request/response schemas, and validators
used across the API endpoints for consistent documentation and validation.
"""

from flask_restx import fields, Model
from app.api import api

# ==================== Base Models ====================

pagination_model = api.model('Pagination', {
    'page': fields.Integer(description='Current page number', example=1),
    'per_page': fields.Integer(description='Items per page', example=50),
    'pages': fields.Integer(description='Total number of pages', example=20),
    'total': fields.Integer(description='Total number of items', example=1000)
})

meta_model = api.model('Meta', {
    'request_id': fields.String(description='Unique request identifier'),
    'timestamp': fields.DateTime(description='Response timestamp'),
    'version': fields.String(description='API version', example='2.0.0'),
    'source': fields.String(description='Data source', example='Election Commission of India'),
    'last_updated': fields.DateTime(description='Data last updated timestamp')
})

# ==================== Election Models ====================

election_summary_model = api.model('ElectionSummary', {
    'id': fields.String(required=True, description='Election identifier', example='lok-sabha-2024'),
    'name': fields.String(required=True, description='Election name', example='Lok Sabha Elections 2024'),
    'type': fields.String(required=True, description='Election type', example='LOK_SABHA', enum=['LOK_SABHA', 'VIDHAN_SABHA']),
    'year': fields.Integer(required=True, description='Election year', example=2024),
    'state': fields.String(description='State/UT (for assembly elections)', example='Delhi'),
    'total_constituencies': fields.Integer(description='Total constituencies', example=543),
    'total_candidates': fields.Integer(description='Total candidates', example=8000),
    'status': fields.String(description='Election status', example='COMPLETED', enum=['SCHEDULED', 'ONGOING', 'COMPLETED']),
    'start_date': fields.Date(description='Election start date'),
    'end_date': fields.Date(description='Election end date'),
    'result_date': fields.Date(description='Result declaration date')
})

election_detail_model = api.model('ElectionDetail', {
    'id': fields.String(required=True, description='Election identifier'),
    'name': fields.String(required=True, description='Election name'),
    'type': fields.String(required=True, description='Election type'),
    'year': fields.Integer(required=True, description='Election year'),
    'state': fields.String(description='State/UT name'),
    'state_code': fields.String(description='State/UT code', example='DL'),
    'total_constituencies': fields.Integer(description='Total constituencies'),
    'total_candidates': fields.Integer(description='Total candidates'),
    'total_parties': fields.Integer(description='Total parties'),
    'total_votes': fields.Integer(description='Total votes polled'),
    'voter_turnout': fields.Float(description='Voter turnout percentage'),
    'status': fields.String(description='Election status'),
    'phases': fields.Integer(description='Number of voting phases'),
    'start_date': fields.Date(description='Election start date'),
    'end_date': fields.Date(description='Election end date'),
    'result_date': fields.Date(description='Result declaration date'),
    'statistics': fields.Raw(description='Additional election statistics')
})

# ==================== Candidate Models ====================

candidate_model = api.model('Candidate', {
    'id': fields.String(description='Unique candidate identifier'),
    'name': fields.String(required=True, description='Candidate full name', example='Narendra Modi'),
    'party': fields.String(required=True, description='Political party name', example='Bharatiya Janata Party'),
    'party_symbol': fields.String(description='Party election symbol', example='Lotus'),
    'constituency_code': fields.String(required=True, description='Constituency code', example='GJ-26'),
    'constituency_name': fields.String(required=True, description='Constituency name', example='Vadodara'),
    'state': fields.String(required=True, description='State/UT name', example='Gujarat'),
    'election_year': fields.Integer(required=True, description='Election year', example=2024),
    'election_type': fields.String(required=True, description='Election type', example='LOK_SABHA'),
    'status': fields.String(required=True, description='Election result status', example='WON', enum=['WON', 'LOST', 'RUNNER_UP']),
    'votes': fields.Integer(description='Total votes received', example=855502),
    'vote_share': fields.Float(description='Vote share percentage', example=65.84),
    'margin': fields.Integer(description='Victory/defeat margin', example=540000),
    'margin_percentage': fields.Float(description='Margin as percentage', example=41.58),
    'position': fields.Integer(description='Position in constituency (1=winner)', example=1),
    'deposit_lost': fields.Boolean(description='Whether candidate lost security deposit', example=False),
    'criminal_cases': fields.Integer(description='Number of criminal cases', example=0),
    'assets': fields.Integer(description='Total assets declared (in INR)', example=23000000),
    'education': fields.String(description='Educational qualification', example='Master of Arts'),
    'age': fields.Integer(description='Age at time of election', example=73),
    'gender': fields.String(description='Gender', example='Male', enum=['Male', 'Female', 'Other']),
    'category': fields.String(description='Candidate category', example='General', enum=['General', 'SC', 'ST', 'OBC']),
    'image_url': fields.Url(description='Candidate photograph URL'),
    'social_media': fields.Raw(description='Social media handles'),
    'previous_elections': fields.Raw(description='Previous election history')
})

candidate_summary_model = api.model('CandidateSummary', {
    'name': fields.String(required=True, description='Candidate name'),
    'party': fields.String(required=True, description='Political party'),
    'constituency': fields.String(required=True, description='Constituency name'),
    'status': fields.String(required=True, description='Result status'),
    'votes': fields.Integer(description='Votes received'),
    'margin': fields.Integer(description='Victory/defeat margin')
})

# ==================== Constituency Models ====================

constituency_model = api.model('Constituency', {
    'code': fields.String(required=True, description='Constituency code', example='DL-1'),
    'name': fields.String(required=True, description='Constituency name', example='Chandni Chowk'),
    'state': fields.String(required=True, description='State/UT name', example='Delhi'),
    'state_code': fields.String(required=True, description='State/UT code', example='DL'),
    'type': fields.String(required=True, description='Constituency type', example='GENERAL', enum=['GENERAL', 'SC', 'ST']),
    'election_type': fields.String(required=True, description='Election type', example='VIDHAN_SABHA'),
    'total_electors': fields.Integer(description='Total registered voters', example=150000),
    'total_votes_polled': fields.Integer(description='Total votes polled', example=120000),
    'voter_turnout': fields.Float(description='Voter turnout percentage', example=80.0),
    'total_candidates': fields.Integer(description='Total candidates', example=8),
    'valid_votes': fields.Integer(description='Valid votes', example=119000),
    'rejected_votes': fields.Integer(description='Rejected votes', example=1000),
    'nota_votes': fields.Integer(description='NOTA votes', example=500),
    'winner': fields.Nested(candidate_summary_model, description='Winning candidate'),
    'runner_up': fields.Nested(candidate_summary_model, description='Runner-up candidate'),
    'victory_margin': fields.Integer(description='Victory margin', example=5000),
    'margin_percentage': fields.Float(description='Margin percentage', example=4.2)
})

constituency_results_model = api.model('ConstituencyResults', {
    'constituency': fields.Nested(constituency_model, description='Constituency information'),
    'candidates': fields.List(fields.Nested(candidate_model), description='All candidates in constituency'),
    'results_summary': fields.Raw(description='Results summary and statistics')
})

# ==================== Party Models ====================

party_model = api.model('Party', {
    'name': fields.String(required=True, description='Party full name', example='Bharatiya Janata Party'),
    'short_name': fields.String(description='Party abbreviation', example='BJP'),
    'symbol': fields.String(required=True, description='Election symbol', example='Lotus'),
    'type': fields.String(description='Party type', example='National', enum=['National', 'State', 'Regional']),
    'founded_year': fields.Integer(description='Year party was founded', example=1980),
    'ideology': fields.String(description='Political ideology', example='Right-wing'),
    'alliance': fields.String(description='Electoral alliance', example='NDA'),
    'headquarters': fields.String(description='Party headquarters location', example='New Delhi'),
    'president': fields.String(description='Current party president', example='J. P. Nadda'),
    'website': fields.Url(description='Official party website'),
    'social_media': fields.Raw(description='Social media handles')
})

party_performance_model = api.model('PartyPerformance', {
    'party': fields.Nested(party_model, description='Party information'),
    'election_id': fields.String(required=True, description='Election identifier'),
    'seats_contested': fields.Integer(description='Total seats contested', example=400),
    'seats_won': fields.Integer(description='Total seats won', example=240),
    'seats_lost': fields.Integer(description='Total seats lost', example=160),
    'win_percentage': fields.Float(description='Win percentage', example=60.0),
    'total_votes': fields.Integer(description='Total votes received', example=23000000),
    'vote_share': fields.Float(description='National/state vote share', example=37.4),
    'deposits_lost': fields.Integer(description='Candidates who lost deposit', example=10),
    'strike_rate': fields.Float(description='Win percentage of contested seats', example=60.0),
    'best_performance': fields.Raw(description='Best performing constituencies'),
    'worst_performance': fields.Raw(description='Worst performing constituencies')
})

# ==================== Analytics Models ====================

trend_analysis_model = api.model('TrendAnalysis', {
    'metric': fields.String(required=True, description='Metric name', example='vote_share'),
    'period': fields.String(required=True, description='Time period', example='2019-2024'),
    'change': fields.Float(description='Change in percentage points', example=2.5),
    'change_percentage': fields.Float(description='Percentage change', example=6.8),
    'trend': fields.String(description='Trend direction', example='INCREASING', enum=['INCREASING', 'DECREASING', 'STABLE']),
    'data_points': fields.List(fields.Raw(), description='Historical data points')
})

demographic_analysis_model = api.model('DemographicAnalysis', {
    'category': fields.String(required=True, description='Demographic category', example='age_group'),
    'breakdown': fields.Raw(required=True, description='Demographic breakdown data'),
    'insights': fields.List(fields.String(), description='Key insights from analysis')
})

electoral_statistics_model = api.model('ElectoralStatistics', {
    'election_id': fields.String(required=True, description='Election identifier'),
    'total_constituencies': fields.Integer(description='Total constituencies'),
    'total_candidates': fields.Integer(description='Total candidates'),
    'total_parties': fields.Integer(description='Total parties'),
    'average_candidates_per_constituency': fields.Float(description='Average candidates per constituency'),
    'highest_victory_margin': fields.Raw(description='Highest victory margin details'),
    'lowest_victory_margin': fields.Raw(description='Lowest victory margin details'),
    'highest_voter_turnout': fields.Raw(description='Highest voter turnout constituency'),
    'lowest_voter_turnout': fields.Raw(description='Lowest voter turnout constituency'),
    'party_performance': fields.List(fields.Nested(party_performance_model), description='Party-wise performance'),
    'demographic_analysis': fields.List(fields.Nested(demographic_analysis_model), description='Demographic insights'),
    'trends': fields.List(fields.Nested(trend_analysis_model), description='Electoral trends')
})

# ==================== Response Models ====================

api_response_model = api.model('APIResponse', {
    'success': fields.Boolean(required=True, description='Request success status', example=True),
    'message': fields.String(required=True, description='Response message', example='Data retrieved successfully'),
    'data': fields.Raw(description='Response data'),
    'meta': fields.Nested(meta_model, description='Response metadata'),
    'pagination': fields.Nested(pagination_model, description='Pagination information'),
    'error': fields.Raw(description='Error details (only present if success=false)')
})

error_response_model = api.model('ErrorResponse', {
    'success': fields.Boolean(required=True, description='Request success status', example=False),
    'message': fields.String(required=True, description='Error message', example='Resource not found'),
    'error_code': fields.String(description='Error code', example='NOT_FOUND'),
    'details': fields.Raw(description='Additional error details')
})

# ==================== Request Models ====================

search_request_model = api.model('SearchRequest', {
    'query': fields.String(required=True, description='Search query', example='modi'),
    'type': fields.String(description='Search type', example='candidate', enum=['candidate', 'party', 'constituency']),
    'filters': fields.Raw(description='Additional filters'),
    'limit': fields.Integer(description='Maximum results to return', example=20, min=1, max=100),
    'offset': fields.Integer(description='Number of results to skip', example=0, min=0)
})

filter_request_model = api.model('FilterRequest', {
    'state': fields.String(description='State/UT code', example='DL'),
    'party': fields.String(description='Party name', example='Bharatiya Janata Party'),
    'status': fields.String(description='Result status', example='WON', enum=['WON', 'LOST']),
    'year': fields.Integer(description='Election year', example=2024),
    'constituency_type': fields.String(description='Constituency type', example='GENERAL', enum=['GENERAL', 'SC', 'ST']),
    'min_votes': fields.Integer(description='Minimum votes', example=1000),
    'max_votes': fields.Integer(description='Maximum votes', example=1000000),
    'min_margin': fields.Integer(description='Minimum victory margin', example=100),
    'max_margin': fields.Integer(description='Maximum victory margin', example=100000)
})

# ==================== Export Models ====================

__all__ = [
    'pagination_model', 'meta_model', 'api_response_model', 'error_response_model',
    'election_summary_model', 'election_detail_model',
    'candidate_model', 'candidate_summary_model',
    'constituency_model', 'constituency_results_model',  
    'party_model', 'party_performance_model',
    'trend_analysis_model', 'demographic_analysis_model', 'electoral_statistics_model',
    'search_request_model', 'filter_request_model'
]
