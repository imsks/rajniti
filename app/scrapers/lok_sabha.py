"""
Lok Sabha Election Data Scraper

Scrapes Lok Sabha election data from ECI website.
"""

import logging

from bs4 import BeautifulSoup

from .base import CandidateScraper, ConstituencyScraper, ECIScraper, PartyScraper

logger = logging.getLogger(__name__)


class LokSabhaScraper(ECIScraper):
    """Main scraper for Lok Sabha elections."""

    def __init__(self, election_year: str = "2024", output_dir: str = "data/lok_sabha"):
        base_url = f"https://results.eci.gov.in/PcResultGen{election_year}"
        super().__init__(base_url, output_dir)
        self.election_year = election_year
        self.party_scraper = LokSabhaPartyScraper(base_url, output_dir)
        self.candidate_scraper = LokSabhaCandidateScraper(base_url, output_dir)
        self.constituency_scraper = LokSabhaConstituencyScraper(base_url, output_dir)

    def scrape(self) -> None:
        """Scrape all Lok Sabha election data."""
        logger.info(f"Starting Lok Sabha {self.election_year} data scraping")

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
        self.party_ids = [
            369,
            742,
            1680,
            140,
            582,
            1745,
            805,
            3369,
            3620,
            3529,
            3165,
            1888,
            1420,
            547,
            772,
            1,
            852,
            860,
            545,
            804,
            1847,
            544,
            1458,
            834,
            1998,
            83,
            664,
            911,
            1534,
            1142,
            3388,
            2757,
            1584,
            2484,
            3482,
            1658,
            1046,
            2989,
            2070,
            160,
            118,
            743,
        ]

    def scrape(self) -> None:
        """Scrape party-wise results for all parties."""
        logger.info("Scraping Lok Sabha party-wise results")

        all_data = []

        for party_id in self.party_ids:
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
        self.save_json(all_data, f"lok_sabha_{self.election_year}_party_results.json")
        logger.info(f"Scraped {len(all_data)} party-wise results")


class LokSabhaCandidateScraper(CandidateScraper):
    """Scraper for Lok Sabha candidate data."""

    def scrape(self) -> None:
        """Scrape candidate data for Lok Sabha elections."""
        logger.info("Scraping Lok Sabha candidate data")

        # Main results page
        url = f"{self.base_url}/partywisewinresult-369.htm"
        response = self.get_with_retry(url)

        if response:
            soup = BeautifulSoup(response.content, "html.parser")
            table = soup.find("table", {"class": "table-scroll"})

            if table:
                rows = table.find_all("tr")[1:]  # Skip header
                all_data = []

                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) < 6:
                        continue

                    constituency_code = cols[0].text.strip()
                    name = cols[1].text.strip()
                    party = cols[2].text.strip()
                    status = cols[3].text.strip()
                    votes = cols[4].text.strip()
                    margin = cols[5].text.strip()

                    image_tag = cols[1].find("img")
                    image_url = (
                        f"{self.base_url}/{image_tag['src']}" if image_tag else ""
                    )

                    all_data.append(
                        {
                            "constituency_code": constituency_code,
                            "name": name,
                            "party": party,
                            "status": status,
                            "votes": votes,
                            "margin": margin,
                            "image_url": image_url,
                        }
                    )

                self.save_json(
                    all_data, f"lok_sabha_{self.election_year}_candidates.json"
                )
                logger.info(f"Scraped {len(all_data)} candidate records")


class LokSabhaConstituencyScraper(ConstituencyScraper):
    """Scraper for Lok Sabha constituency data."""

    def get_state_code(self) -> str:
        """Return state code for Lok Sabha."""
        return "LS"  # Lok Sabha

    def scrape(self) -> None:
        """Scrape constituency data for Lok Sabha."""
        logger.info("Scraping Lok Sabha constituency data")

        # This would need to be implemented based on specific constituency URLs
        # For now, we'll create a placeholder structure
        constituencies = []

        # You would need to implement the actual constituency scraping logic here
        # based on the specific URLs and structure for Lok Sabha constituencies

        self.save_json(
            constituencies, f"lok_sabha_{self.election_year}_constituencies.json"
        )
        logger.info(f"Scraped {len(constituencies)} constituency records")
