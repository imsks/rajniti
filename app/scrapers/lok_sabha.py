"""
Lok Sabha Election Data Scraper

Scrapes Lok Sabha election data from ECI website.
"""

import logging
from typing import Dict, List

from bs4 import BeautifulSoup

from .base import CandidateScraper, ConstituencyScraper, ECIScraper, PartyScraper

logger = logging.getLogger(__name__)


class LokSabhaScraper(ECIScraper):
    """Main scraper for Lok Sabha elections."""

    def __init__(self, base_url: str, output_dir: str = "data/lok_sabha"):
        """
        Initialize Lok Sabha scraper with base URL.

        Args:
            base_url: ECI results page URL (e.g., https://results.eci.gov.in/PcResultGen2024)
            output_dir: Directory to save scraped data
        """
        super().__init__(base_url, output_dir)
        self.party_scraper = LokSabhaPartyScraper(base_url, output_dir)
        self.candidate_scraper = LokSabhaCandidateScraper(base_url, output_dir)
        self.constituency_scraper = LokSabhaConstituencyScraper(base_url, output_dir)

    def scrape(self) -> None:
        """Scrape all Lok Sabha election data."""
        logger.info(f"Starting Lok Sabha data scraping from {self.base_url}")

        # Scrape party-wise results
        self.party_scraper.scrape()

        # Scrape candidate data
        self.candidate_scraper.scrape()

        # Scrape constituency data
        self.constituency_scraper.scrape()

        logger.info("Lok Sabha scraping completed")


class LokSabhaPartyScraper(PartyScraper):
    """Scraper for Lok Sabha party-wise results."""

    def __init__(self, base_url: str, output_dir: str):
        super().__init__(base_url, output_dir)

    def scrape(self) -> None:
        """Scrape party-wise results using auto-discovery."""
        logger.info("Scraping Lok Sabha party-wise results")

        # Auto-discover party links
        party_links = self.discover_party_links()

        if not party_links:
            logger.warning("No parties discovered via auto-discovery")
            return

        all_data = []
        total_parties = len(party_links)

        for idx, party_info in enumerate(party_links, 1):
            party_id = party_info["party_id"]
            party_name = party_info.get("name", f"Party {party_id}")
            logger.info(f"Scraping party {idx}/{total_parties}: {party_name}")

            url = f"{self.base_url}/partywisewinresultState-{party_id}.htm"
            response = self.get_with_retry(url)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find(
                    "table", {"class": "table table-striped table-bordered"}
                )

                if table:
                    tbody = table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        for row in rows:
                            cols = row.find_all("td")
                            if len(cols) >= 5:
                                constituency_link = cols[1].find("a")
                                constituency = (
                                    constituency_link.text.strip()
                                    if constituency_link
                                    else cols[1].text.strip()
                                )
                                candidate_name = cols[2].text.strip()
                                votes = cols[3].text.strip()
                                margin = cols[4].text.strip()

                                all_data.append(
                                    {
                                        "party_id": party_id,
                                        "party_name": party_name,
                                        "constituency": constituency,
                                        "candidate_name": candidate_name,
                                        "votes": votes,
                                        "margin": margin,
                                    }
                                )

            # Be polite to the server
            import time

            time.sleep(0.5)

        # Save party-wise results
        self.save_json(all_data, "lok_sabha_party_results.json")
        logger.info(f"Scraped {len(all_data)} party-wise results from {total_parties} parties")


class LokSabhaCandidateScraper(CandidateScraper):
    """Scraper for Lok Sabha candidate data."""

    def scrape(self) -> None:
        """Scrape candidate data for Lok Sabha elections using auto-discovery."""
        logger.info("Scraping Lok Sabha candidate data")

        # Auto-discover constituency links
        constituency_links = self.discover_constituency_links()

        if not constituency_links:
            logger.warning("No constituencies discovered, trying fallback approach")
            # Fallback: Try to scrape from a known party page
            constituency_links = self._fallback_discovery()

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

            time.sleep(1)

        self.save_json(all_data, "lok_sabha_candidates.json")
        logger.info(f"Scraped {len(all_data)} candidate records from {total_constituencies} constituencies")

    def _fallback_discovery(self) -> List[Dict[str, str]]:
        """Fallback method to discover candidates from party-wise results."""
        logger.info("Using fallback discovery from party results page")
        constituencies = []

        # Try common party result pages
        party_ids = ["369", "1"]  # BJP and INC as common starting points
        for party_id in party_ids:
            url = f"{self.base_url}/partywisewinresult-{party_id}.htm"
            response = self.get_with_retry(url)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                # Look for constituency links
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    if "candidateswise" in href.lower():
                        import re

                        match = re.search(r"candidateswise-([^.]+)\.htm", href)
                        if match:
                            const_code = match.group(1)
                            constituencies.append(
                                {
                                    "constituency_code": const_code,
                                    "name": link.get_text(strip=True),
                                    "url": f"{self.base_url}/{href}",
                                }
                            )

        # Remove duplicates
        seen = set()
        unique = []
        for const in constituencies:
            if const["constituency_code"] not in seen:
                seen.add(const["constituency_code"])
                unique.append(const)

        logger.info(f"Fallback discovered {len(unique)} constituencies")
        return unique


class LokSabhaConstituencyScraper(ConstituencyScraper):
    """Scraper for Lok Sabha constituency data."""

    def get_state_code(self) -> str:
        """Return state code for Lok Sabha."""
        return "LS"  # Lok Sabha

    def scrape(self) -> None:
        """Scrape constituency data for Lok Sabha using auto-discovery."""
        logger.info("Scraping Lok Sabha constituency data")

        # Use auto-discovery to find constituencies
        constituency_links = self.discover_constituency_links()

        constituencies = []
        for constituency in constituency_links:
            constituencies.append(
                {
                    "constituency_id": constituency["constituency_code"],
                    "constituency_name": constituency.get("name", ""),
                    "state_id": "LS",
                }
            )

        # Sort by constituency ID
        try:
            constituencies.sort(key=lambda x: int(x["constituency_id"]))
        except (ValueError, KeyError):
            constituencies.sort(key=lambda x: x.get("constituency_id", ""))

        self.save_json(constituencies, "lok_sabha_constituencies.json")
        logger.info(f"Scraped {len(constituencies)} constituency records")
