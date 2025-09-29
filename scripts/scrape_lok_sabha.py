#!/usr/bin/env python3
"""
Script to scrape Lok Sabha election data.

Usage:
    python scripts/scrape_lok_sabha.py [--year YEAR] [--output-dir DIR]
"""

import argparse
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.scrapers.lok_sabha import LokSabhaScraper  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Scrape Lok Sabha election data")
    parser.add_argument("--year", default="2024", help="Election year (default: 2024)")
    parser.add_argument(
        "--output-dir",
        default="data/lok_sabha",
        help="Output directory (default: data/lok_sabha)",
    )

    args = parser.parse_args()

    try:
        logger.info(f"Starting Lok Sabha {args.year} data scraping")

        scraper = LokSabhaScraper(election_year=args.year, output_dir=args.output_dir)

        scraper.scrape()

        logger.info("Lok Sabha scraping completed successfully")

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
