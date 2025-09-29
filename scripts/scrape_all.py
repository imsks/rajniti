#!/usr/bin/env python3
"""
Script to scrape all election data (Lok Sabha and Vidhan Sabha).

Usage:
    python scripts/scrape_all.py [--year YEAR] [--states STATES] [--output-dir DIR]

Examples:
    python scripts/scrape_all.py --year 2024 --states DL,MH
    python scripts/scrape_all.py --year 2025 --states DL
"""

import argparse
import logging
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.scrapers.lok_sabha import LokSabhaScraper  # noqa: E402
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
    parser = argparse.ArgumentParser(description="Scrape all election data")
    parser.add_argument("--year", default="2024", help="Election year (default: 2024)")
    parser.add_argument(
        "--states",
        default="DL,MH",
        help="Comma-separated list of state codes (default: DL,MH)",
    )
    parser.add_argument(
        "--output-dir", default="data", help="Base output directory (default: data)"
    )
    parser.add_argument(
        "--skip-lok-sabha", action="store_true", help="Skip Lok Sabha scraping"
    )
    parser.add_argument(
        "--skip-vidhan-sabha", action="store_true", help="Skip Vidhan Sabha scraping"
    )

    args = parser.parse_args()

    states = [state.strip().upper() for state in args.states.split(",")]

    try:
        logger.info(
            f"Starting comprehensive election data scraping for year {args.year}"
        )

        # Scrape Lok Sabha data
        if not args.skip_lok_sabha:
            logger.info("Scraping Lok Sabha data...")
            lok_sabha_scraper = LokSabhaScraper(
                election_year=args.year, output_dir=f"{args.output_dir}/lok_sabha"
            )
            lok_sabha_scraper.scrape()
            logger.info("Lok Sabha scraping completed")

        # Scrape Vidhan Sabha data for each state
        if not args.skip_vidhan_sabha:
            for state in states:
                logger.info(f"Scraping Vidhan Sabha data for {state}...")

                # Use specialized scrapers for known states
                if state == "DL":
                    scraper = DelhiVidhanSabhaScraper(
                        election_year=args.year,
                        output_dir=f"{args.output_dir}/vidhan_sabha",
                    )
                elif state == "MH":
                    scraper = MaharashtraVidhanSabhaScraper(
                        election_year=args.year,
                        output_dir=f"{args.output_dir}/vidhan_sabha",
                    )
                else:
                    scraper = VidhanSabhaScraper(
                        state_code=state,
                        election_year=args.year,
                        output_dir=f"{args.output_dir}/vidhan_sabha",
                    )

                scraper.scrape()
                logger.info(f"Vidhan Sabha scraping for {state} completed")

        logger.info("All election data scraping completed successfully")

    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
