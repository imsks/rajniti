"""
Vidhan Sabha Election Data Scraper

Scrapes Vidhan Sabha (State Assembly) election data from ECI website.
"""

import logging
from typing import Dict, List

from bs4 import BeautifulSoup

from .base import CandidateScraper, ConstituencyScraper, ECIScraper, PartyScraper

logger = logging.getLogger(__name__)


class VidhanSabhaScraper(ECIScraper):
    """Main scraper for Vidhan Sabha elections."""

    def __init__(
        self,
        base_url: str,
        output_dir: str = "data/vidhan_sabha",
        state_code: str = None,
    ):
        """
        Initialize Vidhan Sabha scraper with base URL.

        Args:
            base_url: ECI results page URL (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
            output_dir: Directory to save scraped data
            state_code: Optional state code (will be auto-extracted if not provided)
        """
        super().__init__(base_url, output_dir)
        self.state_code = state_code or self._extract_state_code()
        self.party_scraper = VidhanSabhaPartyScraper(base_url, output_dir, self.state_code)
        self.candidate_scraper = VidhanSabhaCandidateScraper(
            base_url, output_dir, self.state_code
        )
        self.constituency_scraper = VidhanSabhaConstituencyScraper(
            base_url, output_dir, self.state_code
        )

    def _extract_state_code(self) -> str:
        """
        Extract state code from URL or page content.
        Falls back to 'VS' (Vidhan Sabha) if unable to determine.
        """
        import re

        # Try to extract from URL patterns
        url_lower = self.base_url.lower()

        # Common state codes in URLs
        state_patterns = {
            r"delhi|dl": "DL",
            r"maharashtra|mh": "MH",
            r"karnataka|ka": "KA",
            r"gujarat|gj": "GJ",
            r"rajasthan|rj": "RJ",
            r"punjab|pb": "PB",
            r"haryana|hr": "HR",
            r"uttarpradesh|up": "UP",
            r"bihar|br": "BR",
            r"westbengal|wb": "WB",
        }

        for pattern, code in state_patterns.items():
            if re.search(pattern, url_lower):
                logger.info(f"Extracted state code: {code}")
                return code

        # Try fetching from the page
        response = self.get_with_retry(f"{self.base_url}/index.htm")
        if response:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.content, "html.parser")
            # Look for state name in title or headings
            title = soup.find("title")
            if title:
                title_text = title.get_text()
                for pattern, code in state_patterns.items():
                    if re.search(pattern, title_text, re.IGNORECASE):
                        logger.info(f"Extracted state code from page: {code}")
                        return code

        logger.warning("Could not extract state code, using default 'VS'")
        return "VS"

    def scrape(self) -> None:
        """Scrape all Vidhan Sabha election data for the state."""
        logger.info(
            f"Starting Vidhan Sabha data scraping for {self.state_code} from {self.base_url}"
        )

        # Scrape party-wise results
        self.party_scraper.scrape()

        # Scrape candidate data
        self.candidate_scraper.scrape()

        # Scrape constituency data
        self.constituency_scraper.scrape()

        logger.info(f"Vidhan Sabha {self.state_code} scraping completed")


class VidhanSabhaPartyScraper(PartyScraper):
    """Scraper for Vidhan Sabha party-wise results."""

    def __init__(self, base_url: str, output_dir: str, state_code: str):
        super().__init__(base_url, output_dir)
        self.state_code = state_code

    def scrape(self) -> None:
        """Scrape party-wise results for Vidhan Sabha."""
        logger.info(f"Scraping Vidhan Sabha party-wise results for {self.state_code}")

        # Main party results page
        url = f"{self.base_url}/index.htm"
        response = self.get_with_retry(url)

        if response:
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table")

            if table:
                party_data = self.extract_party_data(table)
                self.save_json(party_data, f"{self.state_code}_party_results.json")
                logger.info(f"Scraped {len(party_data)} party records")


class VidhanSabhaCandidateScraper(CandidateScraper):
    """Scraper for Vidhan Sabha candidate data."""

    def __init__(self, base_url: str, output_dir: str, state_code: str):
        super().__init__(base_url, output_dir)
        self.state_code = state_code

    def scrape(self) -> None:
        """Scrape candidate data for Vidhan Sabha elections using auto-discovery."""
        logger.info(f"Scraping Vidhan Sabha candidate data for {self.state_code}")

        # Auto-discover constituency links
        constituency_links = self.discover_constituency_links()

        if not constituency_links:
            logger.warning(
                "No constituencies discovered, trying sequential approach as fallback"
            )
            constituency_links = self._fallback_sequential_discovery()

        all_data = []
        total_constituencies = len(constituency_links)

        for idx, constituency in enumerate(constituency_links, 1):
            logger.info(
                f"Scraping constituency {idx}/{total_constituencies}: "
                f"{constituency.get('name', constituency['constituency_code'])}"
            )

            url = constituency.get("url") or f"{self.base_url}/candidateswise-{constituency['constituency_code']}.htm"
            response = self.get_with_retry(url)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                candidate_data = self.extract_candidate_data(soup)

                # Add constituency code to each candidate
                for candidate in candidate_data:
                    candidate["constituency_code"] = constituency["constituency_code"]
                    candidate["constituency_name"] = constituency.get("name", "")

                all_data.extend(candidate_data)

            # Be polite to the server
            import time

            time.sleep(2)

        self.save_json(all_data, f"{self.state_code}_candidates.json")
        logger.info(f"Scraped {len(all_data)} candidate records from {total_constituencies} constituencies")

    def _fallback_sequential_discovery(self) -> List[Dict[str, str]]:
        """
        Fallback method to discover constituencies by trying sequential codes.
        Stops after 10 consecutive 404s.
        """
        logger.info("Using fallback sequential discovery method")
        constituencies = []
        consecutive_failures = 0
        max_failures = 10
        i = 1

        while consecutive_failures < max_failures:
            url = f"{self.base_url}/candidateswise-U05{i}.htm"
            response = self.get_with_retry(url, retries=1)

            if response and response.status_code == 200:
                constituencies.append(
                    {
                        "constituency_code": f"U05{i}",
                        "name": f"Constituency {i}",
                        "url": url,
                    }
                )
                consecutive_failures = 0
                logger.info(f"Found constituency: U05{i}")
            else:
                consecutive_failures += 1

            i += 1

            # Safety limit
            if i > 500:
                break

        logger.info(f"Fallback discovery found {len(constituencies)} constituencies")
        return constituencies


class VidhanSabhaConstituencyScraper(ConstituencyScraper):
    """Scraper for Vidhan Sabha constituency data."""

    def __init__(self, base_url: str, output_dir: str, state_code: str):
        super().__init__(base_url, output_dir)
        self.state_code = state_code

    def get_state_code(self) -> str:
        """Return state code for Vidhan Sabha."""
        return self.state_code

    def scrape(self) -> None:
        """Scrape constituency data for Vidhan Sabha using auto-discovery."""
        logger.info(f"Scraping Vidhan Sabha constituency data for {self.state_code}")

        # Use auto-discovery to find constituency data
        constituency_links = self.discover_constituency_links()

        all_data = []
        unique_ids = set()

        # If auto-discovery worked, use those results
        if constituency_links:
            for constituency in constituency_links:
                const_id = constituency["constituency_code"]
                if const_id not in unique_ids:
                    all_data.append(
                        {
                            "constituency_id": const_id,
                            "constituency_name": constituency.get("name", ""),
                            "state_id": self.state_code,
                        }
                    )
                    unique_ids.add(const_id)
        else:
            # Fallback: Try discovering from party-wise result pages
            logger.info("Trying party-wise pages for constituency discovery")
            party_suffixes = ["1U05", "369U05", ""]
            
            for suffix in party_suffixes:
                url = f"{self.base_url}/partywisewinresult-{suffix}.htm"
                response = self.get_with_retry(url)
                if response:
                    constituency_data = self.extract_constituency_data(response.text)

                    for item in constituency_data:
                        if item["constituency_id"] not in unique_ids:
                            all_data.append(item)
                            unique_ids.add(item["constituency_id"])

        # Sort by constituency ID
        try:
            all_data.sort(key=lambda x: int(x["constituency_id"].replace("U05", "")))
        except (ValueError, KeyError):
            all_data.sort(key=lambda x: x.get("constituency_id", ""))

        self.save_json(all_data, f"{self.state_code}_constituencies.json")
        logger.info(f"Scraped {len(all_data)} constituency records")


class DelhiVidhanSabhaScraper(VidhanSabhaScraper):
    """Specialized scraper for Delhi Vidhan Sabha elections."""

    def __init__(
        self, base_url: str = None, output_dir: str = "data/vidhan_sabha"
    ):
        """
        Initialize Delhi Vidhan Sabha scraper.
        
        Args:
            base_url: ECI results page URL. If not provided, defaults to latest available.
            output_dir: Directory to save scraped data
        """
        if base_url is None:
            # Default to 2025 elections
            base_url = "https://results.eci.gov.in/ResultAcGenFeb2025"
            logger.info(f"No URL provided, using default: {base_url}")
        super().__init__(base_url, output_dir, state_code="DL")


class MaharashtraVidhanSabhaScraper(VidhanSabhaScraper):
    """Specialized scraper for Maharashtra Vidhan Sabha elections."""

    def __init__(
        self, base_url: str = None, output_dir: str = "data/vidhan_sabha"
    ):
        """
        Initialize Maharashtra Vidhan Sabha scraper.
        
        Args:
            base_url: ECI results page URL. If not provided, defaults to latest available.
            output_dir: Directory to save scraped data
        """
        if base_url is None:
            # Default to 2024 elections
            base_url = "https://results.eci.gov.in/ResultAcGenOct2024"
            logger.info(f"No URL provided, using default: {base_url}")
        super().__init__(base_url, output_dir, state_code="MH")
