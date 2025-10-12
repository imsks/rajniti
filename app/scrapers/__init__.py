"""
Election data scrapers for Lok Sabha and Vidhan Sabha elections.
"""

from .base import (
    clean_margin,
    clean_votes,
    get_with_retry,
    normalize_base_url,
    save_json,
)
from .lok_sabha import LokSabhaScraper
from .vidhan_sabha import VidhanSabhaScraper

__all__ = [
    # Scrapers
    "LokSabhaScraper",
    "VidhanSabhaScraper",
    # Utility functions
    "get_with_retry",
    "save_json",
    "clean_votes",
    "clean_margin",
    "normalize_base_url",
]
