"""
Lok Sabha Election Data Scraper

Single scraper that extracts all election data (parties, constituencies, candidates, metadata)
from ECI Lok Sabha results page.
"""

import logging
import re
import time
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup

from .base import clean_margin, clean_votes, get_with_retry, normalize_base_url, save_json

logger = logging.getLogger(__name__)


class LokSabhaScraper:
    """Scraper for Lok Sabha election data."""

    def __init__(self, url: str):
        """
        Initialize Lok Sabha scraper.
        
        Args:
            url: ECI Lok Sabha results page URL
                 (e.g., https://results.eci.gov.in/PcResultGenJune2024/index.htm)
        """
        self.base_url = normalize_base_url(url)
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
        logger.info(f"Starting Lok Sabha scraping from {self.base_url}")
        
        # Extract year and metadata first
        self._extract_metadata()
        
        # Scrape all data
        logger.info("Scraping party-wise results...")
        self._scrape_parties()
        
        logger.info("Discovering constituencies...")
        self._scrape_constituencies()
        
        logger.info("Candidates already scraped from party pages")
        
        # Save all data
        self._save_all_data()
        
        logger.info(f"Lok Sabha scraping completed successfully!")
        logger.info(f"  - Parties: {len(self.parties_data)}")
        logger.info(f"  - Constituencies: {len(self.constituencies_data)}")
        logger.info(f"  - Candidates: {len(self.candidates_data)}")

    def _extract_metadata(self) -> None:
        """Extract election metadata from the main page."""
        logger.info("Extracting election metadata...")
        
        # Try to extract year from URL as primary method
        year_match = re.search(r'20\d{2}', self.base_url)
        self.year = int(year_match.group(0)) if year_match else 2024
        
        self.election_name = f"Lok Sabha General Election {self.year}"
        self.folder_name = f"lok-sabha-{self.year}"
        
        logger.info(f"Detected: {self.election_name}")
        logger.info(f"Output folder: {self.folder_name}")

    def _scrape_parties(self) -> None:
        """Scrape party-wise results and compile party list with seat counts."""
        # Discover party links from main page
        party_links = self._discover_party_links()
        
        if not party_links:
            logger.warning("No parties discovered")
            return
        
        # Track candidates by party to count seats
        party_candidates = {}
        
        logger.info(f"Found {len(party_links)} parties, scraping results...")
        
        for idx, party_info in enumerate(party_links, 1):
            party_id = party_info["party_id"]
            party_name = party_info.get("name", f"Party {party_id}")
            
            logger.info(f"  [{idx}/{len(party_links)}] {party_name}")
            
            # Try party-wise winning results page
            url = f"{self.base_url}/partywisewinresult-{party_id}.htm"
            response = get_with_retry(url, referer=self.base_url)
            
            if not response:
                # Try alternative URL pattern
                url = f"{self.base_url}/partywisewinresultState-{party_id}.htm"
                response = get_with_retry(url, referer=self.base_url)
            
            if response:
                soup = BeautifulSoup(response.content, "html.parser")
                table = soup.find("table", {"class": "table"})
                
                if table:
                    tbody = table.find("tbody")
                    if tbody:
                        rows = tbody.find_all("tr")
                        for row in rows:
                            cols = row.find_all("td")
                            if len(cols) >= 3:
                                candidate_name = cols[2].text.strip() if len(cols) > 2 else ""
                                constituency = cols[1].text.strip() if len(cols) > 1 else ""
                                votes = cols[3].text.strip() if len(cols) > 3 else ""
                                margin = cols[4].text.strip() if len(cols) > 4 else ""
                                
                                # Store for candidates data
                                if party_id not in party_candidates:
                                    party_candidates[party_id] = []
                                
                                party_candidates[party_id].append({
                                    "party_id": int(party_id),
                                    "constituency": constituency,
                                    "candidate_name": candidate_name,
                                    "votes": votes,
                                    "margin": margin
                                })
            
            time.sleep(0.3)  # Be polite to server
        
        # Build parties list with seat counts
        for party_info in party_links:
            party_id = party_info["party_id"]
            party_name = party_info["name"]
            
            # Parse party name and symbol
            if " - " in party_name:
                name_part, symbol_part = party_name.split(" - ", 1)
            else:
                name_part = party_name
                symbol_part = ""
            
            # Count seats (candidates that won from this party)
            seat_count = len(party_candidates.get(party_id, []))
            
            self.parties_data.append({
                "party_name": name_part.strip(),
                "symbol": symbol_part.strip(),
                "total_seats": seat_count
            })
        
        # Store all candidates from party pages
        for party_id, candidates in party_candidates.items():
            self.candidates_data.extend(candidates)
        
        # Sort parties by seats won (descending)
        self.parties_data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))
        
        logger.info(f"Scraped {len(self.parties_data)} parties")

    def _discover_party_links(self) -> List[Dict[str, str]]:
        """Discover party links from main results page."""
        party_links = []
        
        # Try multiple pages
        urls_to_try = [
            f"{self.base_url}/index.htm",
            f"{self.base_url}/partywiseresult.htm",
        ]
        
        for url in urls_to_try:
            response = get_with_retry(url, referer=self.base_url)
            if not response:
                continue
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Look for party links
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "partywise" in href.lower() and "result" in href.lower():
                    # Extract party ID
                    match = re.search(r"partywise.*?-?(\d+)(?:U05)?\.htm", href, re.IGNORECASE)
                    if match:
                        party_id = match.group(1)
                        party_name = link.get_text(strip=True)
                        
                        if party_name:  # Skip empty names
                            party_links.append({
                                "party_id": party_id,
                                "name": party_name
                            })
        
        # Remove duplicates
        seen = set()
        unique_parties = []
        for party in party_links:
            if party["party_id"] not in seen:
                seen.add(party["party_id"])
                unique_parties.append(party)
        
        return unique_parties

    def _scrape_constituencies(self) -> None:
        """Discover and scrape constituency data."""
        constituency_links = self._discover_constituency_links()
        
        for const in constituency_links:
            # Extract constituency ID from code
            const_id = const["constituency_code"]
            const_name = const.get("name", "")
            
            self.constituencies_data.append({
                "constituency_id": const_id,
                "constituency_name": const_name,
                "state_id": "LS"  # Lok Sabha
            })
        
        logger.info(f"Found {len(self.constituencies_data)} constituencies")

    def _discover_constituency_links(self) -> List[Dict[str, str]]:
        """Auto-discover constituency links from main page."""
        logger.info("Discovering constituency links...")
        constituency_links = []
        
        url = f"{self.base_url}/index.htm"
        response = get_with_retry(url, referer=self.base_url)
        
        if not response:
            logger.warning("Could not fetch index page")
            return constituency_links
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for constituency links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "candidateswise" in href.lower():
                # Extract constituency code
                match = re.search(r"candidateswise-([^.]+)\.htm", href, re.IGNORECASE)
                if match:
                    const_code = match.group(1)
                    const_name = link.get_text(strip=True)
                    
                    constituency_links.append({
                        "constituency_code": const_code,
                        "name": const_name,
                        "url": f"{self.base_url}/{href}" if not href.startswith("http") else href
                    })
        
        # Remove duplicates
        seen = set()
        unique_constituencies = []
        for const in constituency_links:
            if const["constituency_code"] not in seen:
                seen.add(const["constituency_code"])
                unique_constituencies.append(const)
        
        logger.info(f"Discovered {len(unique_constituencies)} constituencies")
        return unique_constituencies

    def _save_all_data(self) -> None:
        """Save all scraped data to JSON files in proper folder structure."""
        base_path = Path("app/data")
        
        # Create folder paths
        lok_sabha_dir = base_path / "lok_sabha" / self.folder_name
        elections_dir = base_path / "elections"
        
        # Save parties
        save_json(self.parties_data, lok_sabha_dir / "parties.json")
        
        # Save constituencies
        save_json(self.constituencies_data, lok_sabha_dir / "constituencies.json")
        
        # Save candidates
        save_json(self.candidates_data, lok_sabha_dir / "candidates.json")
        
        # Build and save election metadata
        self.metadata = {
            "election_id": self.folder_name,
            "name": self.election_name,
            "type": "LOK_SABHA",
            "year": self.year,
            "date": None,
            "total_constituencies": len(self.constituencies_data),
            "total_candidates": len(self.candidates_data),
            "total_parties": len(self.parties_data),
            "result_status": "DECLARED",
            "winning_party": self.parties_data[0]["party_name"] if self.parties_data else None,
            "winning_party_seats": self.parties_data[0]["total_seats"] if self.parties_data else 0,
        }
        
        save_json([self.metadata], elections_dir / f"LS-{self.year}.json")
        
        logger.info(f"All data saved successfully to {lok_sabha_dir}")

