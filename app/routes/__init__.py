"""Route blueprints for the Rajniti application."""

from .candidate import candidate_bp
from .constituency import constituency_bp
from .election import election_bp
from .party import party_bp
from .data_routes import data_bp

__all__ = ['candidate_bp', 'constituency_bp', 'election_bp', 'party_bp', 'data_bp']

