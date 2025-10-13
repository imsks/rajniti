"""
Vidhan Sabha Election Data Scraper

Single scraper that extracts all Vidhan Sabha (State Assembly) election data
(parties, constituencies, candidates, metadata) from ECI results page.
"""

import logging
import re
import time
import uuid
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup

from .base import (
    clean_margin,
    clean_votes,
    get_with_retry,
    normalize_base_url,
    save_json,
)

logger = logging.getLogger(__name__)


class VidhanSabhaScraper:
    """Scraper for Vidhan Sabha (State Assembly) election data."""

    def __init__(self, url: str):
        """
        Initialize Vidhan Sabha scraper.

        Args:
            url: ECI Vidhan Sabha results page URL
                 (e.g., https://results.eci.gov.in/ResultAcGenFeb2025)
        """
        self.base_url = normalize_base_url(url)
        self.state_code = None
        self.state_name = None
        self.year = None
        self.election_name = None
        self.folder_name = None

        # Data storage
        self.parties_data = []
        self.constituencies_data = []
        self.candidates_data = []
        self.metadata = {}

    def scrape(self) -> None:
        """Main scraping orchestrator - scrapes all data and saves to JSON files."""
        logger.info(f"Starting Vidhan Sabha scraping from {self.base_url}")

        # Detect state and extract metadata first
        self._detect_state_info()

        # Scrape all data
        logger.info("Scraping party-wise results...")
        self._scrape_parties()

        logger.info("Discovering constituencies...")
        self._scrape_constituencies()

        logger.info("Scraping candidates...")
        self._scrape_candidates()

        # Save all data
        self._save_all_data()

        logger.info(f"Vidhan Sabha scraping completed successfully!")
        logger.info(f"  - State: {self.state_name} ({self.state_code})")
        logger.info(f"  - Parties: {len(self.parties_data)}")
        logger.info(f"  - Constituencies: {len(self.constituencies_data)}")
        logger.info(f"  - Candidates: {len(self.candidates_data)}")

    def _detect_state_info(self) -> None:
        """Auto-detect state code, state name, and year from URL and page content."""
        logger.info("Detecting state and election information...")

        # State patterns for detection
        state_patterns = {
            r"delhi|dl": ("DL", "Delhi"),
            r"maharashtra|mh": ("MH", "Maharashtra"),
            r"karnataka|ka": ("KA", "Karnataka"),
            r"gujarat|gj": ("GJ", "Gujarat"),
            r"rajasthan|rj": ("RJ", "Rajasthan"),
            r"punjab|pb": ("PB", "Punjab"),
            r"haryana|hr": ("HR", "Haryana"),
            r"uttarpradesh|up": ("UP", "Uttar Pradesh"),
            r"bihar|br": ("BR", "Bihar"),
            r"westbengal|wb": ("WB", "West Bengal"),
            r"tamilnadu|tn": ("TN", "Tamil Nadu"),
            r"telangana|tg": ("TG", "Telangana"),
            r"andhrapradesh|ap": ("AP", "Andhra Pradesh"),
            r"madhyapradesh|mp": ("MP", "Madhya Pradesh"),
            r"odisha|or": ("OR", "Odisha"),
            r"kerala|kl": ("KL", "Kerala"),
            r"jharkhand|jh": ("JH", "Jharkhand"),
            r"assam|as": ("AS", "Assam"),
            r"chhattisgarh|cg": ("CG", "Chhattisgarh"),
        }

        # Try to extract from URL first
        url_lower = self.base_url.lower()
        for pattern, (code, name) in state_patterns.items():
            if re.search(pattern, url_lower):
                self.state_code = code
                self.state_name = name
                logger.info(f"Detected from URL: {name} ({code})")
                break

        # Extract year from URL
        year_match = re.search(r"20\d{2}", self.base_url)
        if year_match:
            self.year = int(year_match.group(0))

        # Fetch page to get more info if needed
        if not self.state_code or not self.year:
            response = get_with_retry(
                f"{self.base_url}/index.htm", referer=self.base_url
            )
            if response:
                soup = BeautifulSoup(response.content, "html.parser")

                # Look in title or headings
                title = soup.find("title")
                if title:
                    title_text = title.get_text()

                    # Try to extract state from title if not found yet
                    if not self.state_code:
                        for pattern, (code, name) in state_patterns.items():
                            if re.search(pattern, title_text, re.IGNORECASE):
                                self.state_code = code
                                self.state_name = name
                                logger.info(
                                    f"Detected from page title: {name} ({code})"
                                )
                                break

                    # Extract year from title if not found yet
                    if not self.year:
                        year_match = re.search(r"20\d{2}", title_text)
                        if year_match:
                            self.year = int(year_match.group(0))

        # Defaults if still not found
        if not self.state_code:
            logger.warning("Could not detect state code, using 'XX'")
            self.state_code = "XX"
            self.state_name = "Unknown State"

        if not self.year:
            logger.warning("Could not detect year, using 2024")
            self.year = 2024

        # Set folder name and election name
        self.folder_name = f"{self.state_code}_{self.year}_ASSEMBLY"
        self.election_name = f"{self.state_name} Assembly Election {self.year}"

        logger.info(f"Election: {self.election_name}")
        logger.info(f"Output folder: {self.folder_name}")

    def _scrape_parties(self) -> None:
        """Scrape party-wise results from main results page."""
        url = f"{self.base_url}/index.htm"
        response = get_with_retry(url, referer=self.base_url)

        if not response:
            logger.error("Failed to fetch party results page")
            return

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the party results table
        table = soup.find("table")
        if not table:
            logger.warning("No party table found on main page")
            return

        # Parse party data
        rows = table.find_all("tr")[1:]  # Skip header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                # Extract party name and symbol
                party_tag = cols[0].find("a")
                full_name = (
                    party_tag.text.strip() if party_tag else cols[0].text.strip()
                )

                # Split party name and symbol (usually "Party Name - Symbol")
                if " - " in full_name:
                    party_name, symbol = full_name.split(" - ", 1)
                else:
                    party_name = full_name
                    symbol = ""

                # Extract seats won
                try:
                    total_seats = int(cols[3].text.strip())
                except (ValueError, IndexError):
                    total_seats = 0

                if party_name:  # Skip empty rows
                    self.parties_data.append(
                        {
                            "party_name": party_name.strip(),
                            "symbol": symbol.strip(),
                            "total_seats": total_seats,
                        }
                    )

        # Sort by seats (descending)
        self.parties_data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))

        logger.info(f"Scraped {len(self.parties_data)} parties")

    def _scrape_constituencies(self) -> None:
        """Discover and scrape constituency data."""
        constituency_links = self._discover_constituency_links()

        for const in constituency_links:
            const_id = const["constituency_code"]
            const_name = const.get("name", "")

            self.constituencies_data.append(
                {
                    "constituency_id": const_id,
                    "constituency_name": const_name,
                    "state_id": self.state_code,
                }
            )

        logger.info(f"Found {len(self.constituencies_data)} constituencies")

    def _discover_constituency_links(self) -> List[Dict[str, str]]:
        """Auto-discover constituency links from main page or by sequential probing."""
        logger.info("Discovering constituency links...")
        constituency_links = []

        # Try to find constituency links on main page
        url = f"{self.base_url}/index.htm"
        response = get_with_retry(url, referer=self.base_url)

        if response:
            soup = BeautifulSoup(response.content, "html.parser")

            # Look for constituency links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "candidateswise" in href.lower():
                    # Extract constituency code
                    match = re.search(
                        r"candidateswise-([^.]+)\.htm", href, re.IGNORECASE
                    )
                    if match:
                        const_code = match.group(1)
                        const_name = link.get_text(strip=True)

                        constituency_links.append(
                            {
                                "constituency_code": const_code,
                                "name": const_name,
                                "url": (
                                    f"{self.base_url}/{href}"
                                    if not href.startswith("http")
                                    else href
                                ),
                            }
                        )

        # Remove duplicates
        seen = set()
        unique_constituencies = []
        for const in constituency_links:
            if const["constituency_code"] not in seen:
                seen.add(const["constituency_code"])
                unique_constituencies.append(const)

        # If no constituencies found, try sequential discovery
        if not unique_constituencies:
            logger.info(
                "No constituencies found on main page, trying sequential discovery..."
            )
            unique_constituencies = self._sequential_constituency_discovery()

        logger.info(f"Discovered {len(unique_constituencies)} constituencies")
        return unique_constituencies

    def _sequential_constituency_discovery(self) -> List[Dict[str, str]]:
        """
        Fallback: Try sequential constituency codes.
        Stops after 10 consecutive failures.
        """
        constituencies = []
        consecutive_failures = 0
        max_failures = 10
        i = 1

        logger.info("Attempting sequential constituency discovery...")

        while consecutive_failures < max_failures and i <= 300:
            # Try common patterns: U051, U052, etc.
            const_code = f"U05{i}"
            url = f"{self.base_url}/candidateswise-{const_code}.htm"

            response = get_with_retry(url, retries=1, referer=self.base_url)

            if response and response.status_code == 200:
                constituencies.append(
                    {
                        "constituency_code": const_code,
                        "name": f"Constituency {i}",
                        "url": url,
                    }
                )
                consecutive_failures = 0
                if i % 10 == 0:
                    logger.info(f"  Found {i} constituencies so far...")
            else:
                consecutive_failures += 1

            i += 1
            time.sleep(0.2)  # Be polite

        logger.info(f"Sequential discovery found {len(constituencies)} constituencies")
        return constituencies

    def _scrape_candidates(self) -> None:
        """Scrape detailed candidate data from constituency pages."""
        constituency_links = self._discover_constituency_links()

        if not constituency_links:
            logger.warning("No constituencies to scrape candidates from")
            return

        logger.info(
            f"Scraping candidates from {len(constituency_links)} constituencies..."
        )

        for idx, const in enumerate(constituency_links, 1):
            if idx % 20 == 0:
                logger.info(f"  Progress: {idx}/{len(constituency_links)}")

            url = const.get(
                "url",
                f"{self.base_url}/candidateswise-{const['constituency_code']}.htm",
            )
            response = get_with_retry(url, referer=self.base_url)

            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                candidates = self._extract_candidates_from_page(
                    soup, const["constituency_code"]
                )
                self.candidates_data.extend(candidates)

            time.sleep(0.5)  # Be polite to server

        logger.info(f"Scraped {len(self.candidates_data)} candidate records")

    def _extract_candidates_from_page(
        self, soup: BeautifulSoup, constituency_code: str
    ) -> List[Dict]:
        """Extract candidate data from constituency page."""
        candidates = []

        # Look for candidate boxes (common ECI format)
        cand_boxes = soup.find_all("div", class_="cand-box")

        for cand_box in cand_boxes:
            # Status (won/lost)
            status_div = cand_box.find("div", class_="status")
            status_class = status_div.get("class", []) if status_div else []

            status = None
            if "won" in status_class:
                status = "WON"
            elif "lost" in status_class:
                status = "LOST"

            # Votes and margin
            votes, margin = None, None
            if status_div:
                status_divs = status_div.find_all("div")
                if len(status_divs) > 1:
                    vtext = status_divs[1].get_text(strip=True)
                    parts = vtext.split()
                    if parts:
                        votes = clean_votes(parts[0])
                        if len(parts) > 1:
                            margin = clean_margin(parts[1])

            # Name and party
            nme_prty = cand_box.find("div", class_="nme-prty")
            name = None
            party = None

            if nme_prty:
                h5 = nme_prty.find("h5")
                h6 = nme_prty.find("h6")
                name = h5.get_text(strip=True) if h5 else None
                party = h6.get_text(strip=True) if h6 else None

            # Image URL
            img_tag = cand_box.find("img")
            img_src = None
            if img_tag and "src" in img_tag.attrs:
                img_src = img_tag["src"].strip()
                if img_src and not img_src.startswith("http"):
                    img_src = f"{self.base_url}/{img_src}"

            candidates.append(
                {
                    "ID": str(uuid.uuid4()),
                    "Constituency Code": constituency_code,
                    "Name": name,
                    "Party": party,
                    "Status": status,
                    "Votes": votes,
                    "Margin": margin,
                    "Image URL": img_src,
                }
            )

        return candidates

    def _save_all_data(self) -> None:
        """Save all scraped data to JSON files in proper folder structure."""
        base_path = Path("app/data")

        # Create folder paths
        vidhan_sabha_dir = base_path / "vidhan_sabha" / self.folder_name
        elections_dir = base_path / "elections"

        # Save parties
        save_json(self.parties_data, vidhan_sabha_dir / "parties.json")

        # Save constituencies
        save_json(self.constituencies_data, vidhan_sabha_dir / "constituencies.json")

        # Save candidates
        save_json(self.candidates_data, vidhan_sabha_dir / "candidates.json")

        # Build and save election metadata
        self.metadata = {
            "election_id": self.folder_name,
            "name": self.election_name,
            "type": "VIDHANSABHA",
            "year": self.year,
            "date": None,
            "state_id": self.state_code,
            "state_name": self.state_name,
            "total_constituencies": len(self.constituencies_data),
            "total_candidates": len(self.candidates_data),
            "total_parties": len(self.parties_data),
            "voter_turnout": None,
            "result_status": "DECLARED",
            "result_date": None,
            "winning_party": (
                self.parties_data[0]["party_name"] if self.parties_data else None
            ),
            "winning_party_seats": (
                self.parties_data[0]["total_seats"] if self.parties_data else 0
            ),
            "runner_up_party": (
                self.parties_data[1]["party_name"]
                if len(self.parties_data) > 1
                else None
            ),
            "runner_up_seats": (
                self.parties_data[1]["total_seats"] if len(self.parties_data) > 1 else 0
            ),
        }

        save_json(
            [self.metadata], elections_dir / f"VS-{self.state_code}-{self.year}.json"
        )

        logger.info(f"All data saved successfully to {vidhan_sabha_dir}")
