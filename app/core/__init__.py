"""
Core utilities for Rajniti API

Simple, focused utilities without unnecessary complexity.
"""

from .exceptions import RajnitiError
from .response import error_response, success_response

__all__ = ["success_response", "error_response", "RajnitiError"]
