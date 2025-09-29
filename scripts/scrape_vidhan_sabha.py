#!/usr/bin/env python3
"""
Script to scrape Vidhan Sabha election data.

Usage:
    python scripts/scrape_vidhan_sabha.py --state STATE [--year YEAR] [--output-dir DIR]

Examples:
    python scripts/scrape_vidhan_sabha.py --state DL --year 2025
    python scripts/scrape_vidhan_sabha.py --state MH --year 2024
"""

import argparse
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.scrapers.vidhan_sabha import (  # noqa: E402
    DelhiVidhanSabhaScraper,
    MaharashtraVidhanSabhaScraper,
    VidhanSabhaScraper,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Scrape Vidhan Sabha election data")
    parser.add_argument("--state", required=True, help="State code (e.g., DL, MH)")
    parser.add_argument("--year", default="2024", help="Election year (default: 2024)")
    parser.add_argument(
        "--output-dir",
        default="data/vidhan_sabha",
        help="Output directory (default: data/vidhan_sabha)",
    )

    args = parser.parse_args()

    try:
        logger.info(f"Starting Vidhan Sabha {args.year} data scraping for {args.state}")

        # Use specialized scrapers for known states
        if args.state.upper() == "DL":
            scraper = DelhiVidhanSabhaScraper(
                election_year=args.year, output_dir=args.output_dir
            )
        elif args.state.upper() == "MH":
            scraper = MaharashtraVidhanSabhaScraper(
                election_year=args.year, output_dir=args.output_dir
            )
        else:
            # Generic scraper for other states
            scraper = VidhanSabhaScraper(
                state_code=args.state.upper(),
                election_year=args.year,
                output_dir=args.output_dir,
            )

        scraper.scrape()

        logger.info(f"Vidhan Sabha {args.state} scraping completed successfully")

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
