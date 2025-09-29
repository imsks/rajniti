"""
Vidhan Sabha Election Data Scraper

Scrapes Vidhan Sabha (State Assembly) election data from ECI website.
"""

import logging

from bs4 import BeautifulSoup

from .base import CandidateScraper, ConstituencyScraper, ECIScraper, PartyScraper

logger = logging.getLogger(__name__)


class VidhanSabhaScraper(ECIScraper):
    """Main scraper for Vidhan Sabha elections."""

    def __init__(
        self, state_code: str, election_year: str, output_dir: str = "data/vidhan_sabha"
    ):
        # Different base URLs for different states and years
        base_url = self._get_base_url(state_code, election_year)
        super().__init__(base_url, output_dir)
        self.state_code = state_code
        self.election_year = election_year
        self.party_scraper = VidhanSabhaPartyScraper(base_url, output_dir, state_code)
        self.candidate_scraper = VidhanSabhaCandidateScraper(
            base_url, output_dir, state_code
        )
        self.constituency_scraper = VidhanSabhaConstituencyScraper(
            base_url, output_dir, state_code
        )

    def _get_base_url(self, state_code: str, election_year: str) -> str:
        """Get the appropriate base URL for the state and election year."""
        # This would need to be updated based on actual ECI URLs
        if state_code == "DL" and election_year == "2025":
            return "https://results.eci.gov.in/ResultAcGenFeb2025"
        elif state_code == "MH" and election_year == "2024":
            return "https://results.eci.gov.in/ResultAcGenOct2024"
        else:
            # Default fallback
            return f"https://results.eci.gov.in/ResultAcGen{election_year}"

    def scrape(self) -> None:
        """Scrape all Vidhan Sabha election data for the state."""
        logger.info(
            f"Starting Vidhan Sabha {self.election_year} data scraping "
            f"for {self.state_code}"
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
        """Scrape candidate data for Vidhan Sabha elections."""
        logger.info(f"Scraping Vidhan Sabha candidate data for {self.state_code}")

        # Get constituency range based on state
        start, end = self._get_constituency_range()
        all_data = []

        for i in range(start, end + 1):
            url = f"{self.base_url}/candidateswise-U05{i}.htm"
            response = self.get_with_retry(url)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                candidate_data = self.extract_candidate_data(soup)

                # Add constituency code to each candidate
                for candidate in candidate_data:
                    candidate["constituency_code"] = f"{self.state_code}-{i}"

                all_data.extend(candidate_data)

            # Be polite to the server
            import time

            time.sleep(2)

        self.save_json(all_data, f"{self.state_code}_candidates.json")
        logger.info(f"Scraped {len(all_data)} candidate records")

    def _get_constituency_range(self) -> tuple:
        """Get constituency range based on state."""
        ranges = {
            "DL": (1, 70),  # Delhi has 70 constituencies
            "MH": (1, 288),  # Maharashtra has 288 constituencies
            # Add more states as needed
        }
        return ranges.get(self.state_code, (1, 50))  # Default range


class VidhanSabhaConstituencyScraper(ConstituencyScraper):
    """Scraper for Vidhan Sabha constituency data."""

    def __init__(self, base_url: str, output_dir: str, state_code: str):
        super().__init__(base_url, output_dir)
        self.state_code = state_code

    def get_state_code(self) -> str:
        """Return state code for Vidhan Sabha."""
        return self.state_code

    def scrape(self) -> None:
        """Scrape constituency data for Vidhan Sabha."""
        logger.info(f"Scraping Vidhan Sabha constituency data for {self.state_code}")

        # URLs for constituency data (based on existing code)
        urls = [
            f"{self.base_url}/partywisewinresult-1U05.htm",
            f"{self.base_url}/partywisewinresult-369U05.htm",
        ]

        all_data = []
        unique_ids = set()

        for url in urls:
            response = self.get_with_retry(url)
            if response:
                constituency_data = self.extract_constituency_data(response.text)

                for item in constituency_data:
                    if item["constituency_id"] not in unique_ids:
                        all_data.append(item)
                        unique_ids.add(item["constituency_id"])

        # Sort by constituency number
        all_data.sort(key=lambda x: int(x["constituency_id"].split("-")[1]))

        self.save_json(all_data, f"{self.state_code}_constituencies.json")
        logger.info(f"Scraped {len(all_data)} constituency records")


class DelhiVidhanSabhaScraper(VidhanSabhaScraper):
    """Specialized scraper for Delhi Vidhan Sabha elections."""

    def __init__(
        self, election_year: str = "2025", output_dir: str = "data/vidhan_sabha"
    ):
        super().__init__("DL", election_year, output_dir)


class MaharashtraVidhanSabhaScraper(VidhanSabhaScraper):
    """Specialized scraper for Maharashtra Vidhan Sabha elections."""

    def __init__(
        self, election_year: str = "2024", output_dir: str = "data/vidhan_sabha"
    ):
        super().__init__("MH", election_year, output_dir)
