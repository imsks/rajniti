#!/usr/bin/env python3
"""
Interactive Election Data Scraper

Prompts for Election URL and type, then scrapes all available data.

Usage:
    python scripts/scrape_interactive.py

The script will interactively ask for:
1. Election results URL (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
2. Election type (LOK_SABHA or VIDHAN_SABHA)
"""

import logging
import re
import sys
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.scrapers.lok_sabha import LokSabhaScraper  # noqa: E402
from app.scrapers.vidhan_sabha import VidhanSabhaScraper  # noqa: E402

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def validate_url(url: str) -> bool:
    """Validate if the URL is a valid ECI results URL."""
    if not url:
        return False

    # Check if it's a valid URL format
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        return False

    # Check if it's an ECI URL
    if "results.eci.gov.in" not in url.lower():
        logger.warning("URL does not appear to be from results.eci.gov.in")
        return True  # Still allow it, just warn

    return True


def detect_election_type(url: str) -> str:
    """
    Try to detect election type from URL.
    Returns 'LOK_SABHA', 'VIDHAN_SABHA', or 'UNKNOWN'.
    """
    url_lower = url.lower()

    # Lok Sabha patterns
    if "pcresultgen" in url_lower or "parliamentaryconstituencies" in url_lower:
        return "LOK_SABHA"

    # Vidhan Sabha patterns
    if (
        "resultacgen" in url_lower
        or "assemblyconstituencies" in url_lower
        or "acgen" in url_lower
    ):
        return "VIDHAN_SABHA"

    return "UNKNOWN"


def get_output_directory(url: str, election_type: str) -> str:
    """Generate output directory based on URL and election type."""
    # Extract identifier from URL
    match = re.search(r"/(PcResultGen|ResultAcGen)([^/]+)/?$", url, re.IGNORECASE)

    if match:
        identifier = match.group(2).strip("/")
    else:
        identifier = "custom"

    if election_type == "LOK_SABHA":
        base_dir = "data/lok_sabha"
    elif election_type == "VIDHAN_SABHA":
        base_dir = "data/vidhan_sabha"
    else:
        base_dir = "data/elections"

    # Create directory name with identifier
    if identifier and identifier != "custom":
        output_dir = f"{base_dir}/{identifier}"
    else:
        output_dir = base_dir

    return output_dir


def prompt_for_url() -> str:
    """Prompt user for election results URL."""
    print("\n" + "=" * 80)
    print("ELECTION DATA SCRAPER - Interactive Mode")
    print("=" * 80)
    print("\nPlease provide the Election Commission of India (ECI) results URL.")
    print("\nExamples:")
    print("  - Lok Sabha 2024: https://results.eci.gov.in/PcResultGen2024")
    print("  - Delhi 2025: https://results.eci.gov.in/ResultAcGenFeb2025")
    print("  - Maharashtra 2024: https://results.eci.gov.in/ResultAcGenOct2024")
    print()

    while True:
        url = input("Enter Election Results URL: ").strip()

        if not url:
            print("❌ URL cannot be empty. Please try again.\n")
            continue

        if not validate_url(url):
            print("❌ Invalid URL format. Please enter a valid URL.\n")
            continue

        return url


def prompt_for_election_type(detected_type: str = None) -> str:
    """Prompt user for election type."""
    print("\n" + "-" * 80)
    print("Election Type Selection")
    print("-" * 80)

    if detected_type and detected_type != "UNKNOWN":
        print(f"\n✓ Auto-detected election type: {detected_type}")
        confirm = input("Is this correct? (Y/n): ").strip().lower()
        if confirm in ["", "y", "yes"]:
            return detected_type

    print("\nPlease select the election type:")
    print("  1. LOK_SABHA (Parliamentary Elections)")
    print("  2. VIDHAN_SABHA (State Assembly Elections)")
    print()

    while True:
        choice = input("Enter choice (1 or 2): ").strip()

        if choice == "1":
            return "LOK_SABHA"
        elif choice == "2":
            return "VIDHAN_SABHA"
        else:
            print("❌ Invalid choice. Please enter 1 or 2.\n")


def confirm_scraping(url: str, election_type: str, output_dir: str) -> bool:
    """Confirm scraping details with user."""
    print("\n" + "=" * 80)
    print("Scraping Configuration")
    print("=" * 80)
    print(f"\nURL:           {url}")
    print(f"Election Type: {election_type}")
    print(f"Output Dir:    {output_dir}")
    print()

    confirm = input("Proceed with scraping? (Y/n): ").strip().lower()
    return confirm in ["", "y", "yes"]


def main():
    """Main interactive scraping function."""
    try:
        # Step 1: Get URL
        url = prompt_for_url()

        # Step 2: Detect and confirm election type
        detected_type = detect_election_type(url)
        election_type = prompt_for_election_type(detected_type)

        # Step 3: Generate output directory
        output_dir = get_output_directory(url, election_type)

        # Step 4: Confirm before starting
        if not confirm_scraping(url, election_type, output_dir):
            print("\n❌ Scraping cancelled by user.")
            sys.exit(0)

        # Step 5: Start scraping
        print("\n" + "=" * 80)
        print("Starting Scraping Process")
        print("=" * 80)
        print()

        if election_type == "LOK_SABHA":
            logger.info("Initializing Lok Sabha scraper...")
            scraper = LokSabhaScraper(base_url=url, output_dir=output_dir)
        elif election_type == "VIDHAN_SABHA":
            logger.info("Initializing Vidhan Sabha scraper...")
            scraper = VidhanSabhaScraper(base_url=url, output_dir=output_dir)
        else:
            logger.error(f"Unknown election type: {election_type}")
            sys.exit(1)

        # Run the scraper
        scraper.scrape()

        # Success message
        print("\n" + "=" * 80)
        print("✓ SCRAPING COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nData saved to: {output_dir}")
        print("\nYou can find the following files:")
        print("  - Candidates data")
        print("  - Parties data")
        print("  - Constituencies data")
        print()

    except KeyboardInterrupt:
        print("\n\n❌ Scraping interrupted by user (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Scraping failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

