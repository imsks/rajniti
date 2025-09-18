"""
Scrapers module for election data collection.
Provides election-type specific scrapers for Lok Sabha and Vidhan Sabha elections.
"""

from .base_scraper import BaseScraper
from .lok_sabha_scraper import LokSabhaScraper
from .vidhan_sabha_scraper import VidhanSabhaScraper

__all__ = [
    'BaseScraper',
    'LokSabhaScraper',
    'VidhanSabhaScraper'
]
