#!/usr/bin/env python3
"""
Interactive Election Data Scraper

Simple script to scrape election data from ECI website.
Prompts for URL and automatically detects election type.
"""

import re
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.scrapers import LokSabhaScraper, VidhanSabhaScraper


def validate_url(url: str) -> bool:
    """Validate if URL is from ECI results website."""
    if not url:
        return False
    
    url_lower = url.lower()
    return "results.eci.gov.in" in url_lower


def detect_election_type(url: str) -> str:
    """
    Auto-detect election type from URL.
    
    Returns:
        'lok_sabha', 'vidhan_sabha', or 'unknown'
    """
    url_lower = url.lower()
    
    # Lok Sabha patterns
    if any(pattern in url_lower for pattern in ["pcresult", "loksabha", "general"]):
        return "lok_sabha"
    
    # Vidhan Sabha patterns
    if any(pattern in url_lower for pattern in ["acresult", "assembly", "vidhansabha"]):
        return "vidhan_sabha"
    
    # Try to detect from URL structure
    if re.search(r"pc.*gen", url_lower):
        return "lok_sabha"
    if re.search(r"ac.*gen", url_lower):
        return "vidhan_sabha"
    
    return "unknown"


def prompt_for_url() -> str:
    """Prompt user for ECI results URL."""
    print("\n" + "="*70)
    print("  RAJNITI - ELECTION DATA SCRAPER")
    print("="*70)
    print("\nEnter the ECI results page URL")
    print("Examples:")
    print("  - Lok Sabha: https://results.eci.gov.in/PcResultGenJune2024/index.htm")
    print("  - Vidhan Sabha: https://results.eci.gov.in/ResultAcGenFeb2025")
    print()
    
    while True:
        url = input("URL: ").strip() or "https://results.eci.gov.in/PcResultGenJune2024/index.htm"
        
        if not url:
            print("❌ URL cannot be empty")
            continue
        
        if not validate_url(url):
            print("❌ Invalid URL. Must be from results.eci.gov.in")
            continue
        
        return url


def main():
    """Main interactive scraper."""
    try:
        # Get URL from user
        url = prompt_for_url()
        
        # Detect election type
        election_type = detect_election_type(url)
        
        print(f"\n📊 URL: {url}")
        
        if election_type == "unknown":
            print("\n⚠️  Could not auto-detect election type")
            print("Please select:")
            print("  1. Lok Sabha")
            print("  2. Vidhan Sabha")
            
            while True:
                choice = input("\nEnter choice (1 or 2): ").strip()
                if choice == "1":
                    election_type = "lok_sabha"
                    break
                elif choice == "2":
                    election_type = "vidhan_sabha"
                    break
                else:
                    print("❌ Invalid choice. Enter 1 or 2.")
        
        print(f"🎯 Election Type: {election_type.replace('_', ' ').title()}")
        
        # Confirm and start scraping
        print("\n" + "="*70)
        print("Starting scraper...")
        print("="*70 + "\n")
        
        # Instantiate appropriate scraper
        if election_type == "lok_sabha":
            scraper = LokSabhaScraper(url)
        else:  # vidhan_sabha
            scraper = VidhanSabhaScraper(url)
        
        # Run scraper
        scraper.scrape()
        
        print("\n" + "="*70)
        print("✅ SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nData saved to:")
        print(f"  - app/data/{election_type}/")
        print(f"  - app/data/elections/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
