"""
Base scraper classes and common utilities for election data scraping.
"""

import json
import logging
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all election scrapers."""

    def __init__(self, output_dir: str = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
            "Cache-Control": "max-age=0",
        }

    def get_with_retry(
        self, url: str, retries: int = 3, timeout: int = 20
    ) -> Optional[requests.Response]:
        """Fetch URL with retry logic."""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(3)

        logger.error(f"Max retries reached for {url}")
        return None

    def save_json(self, data: List[Dict], filename: str) -> None:
        """Save data to JSON file."""
        filepath = self.output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Data saved to {filepath}")

    def clean_votes(self, votes: str) -> Optional[str]:
        """Clean vote count string."""
        if not votes:
            return None
        return re.sub(r'[+()"\s]', "", votes)

    def clean_margin(self, margin: str) -> Optional[str]:
        """Clean margin string."""
        if not margin:
            return None
        margin = margin.replace(")", "").strip()
        return f"({margin}" if margin.startswith("+") else margin

    @abstractmethod
    def scrape(self) -> None:
        """Main scraping method to be implemented by subclasses."""


class ECIScraper(BaseScraper):
    """Base class for ECI (Election Commission of India) scrapers."""

    def __init__(self, base_url: str, output_dir: str = "data"):
        super().__init__(output_dir)
        self.base_url = base_url.rstrip("/")
        # Update referer for ECI requests
        self.headers["Referer"] = self.base_url

    def parse_table(self, html: str, table_selector: str = "table") -> List[Dict]:
        """Parse HTML table into list of dictionaries."""
        soup = BeautifulSoup(html, "html.parser")
        table = soup.select_one(table_selector)

        if not table:
            logger.error("No table found")
            return []

        rows = table.find_all("tr")[1:]  # Skip header
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:  # Minimum columns required
                row_data = {}
                for i, col in enumerate(cols):
                    row_data[f"col_{i}"] = col.get_text(strip=True)
                data.append(row_data)

        return data


class PartyScraper(ECIScraper):
    """Scraper for party-wise election results."""

    def extract_party_data(self, table) -> List[Dict]:
        """Extract party data from table."""
        rows = table.find_all("tr")[1:]  # Skip header
        data = []

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                party_tag = cols[0].find("a")
                full_name = (
                    party_tag.text.strip() if party_tag else cols[0].text.strip()
                )

                # Split party name and symbol
                if " - " in full_name:
                    party_name, symbol = full_name.split(" - ", 1)
                else:
                    party_name = full_name
                    symbol = ""

                try:
                    total_seats = int(cols[3].text.strip())
                except (ValueError, IndexError):
                    total_seats = 0

                data.append(
                    {
                        "party_name": party_name,
                        "symbol": symbol,
                        "total_seats": total_seats,
                    }
                )

        return sorted(data, key=lambda x: (-x["total_seats"], x["party_name"]))


class CandidateScraper(ECIScraper):
    """Scraper for candidate-wise election results."""

    def extract_candidate_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract candidate data from BeautifulSoup object."""
        candidates = soup.find_all("div", class_="cand-box")
        data = []

        for candidate in candidates:
            status_div = candidate.find("div", class_="status")
            status_class = status_div.get("class", []) if status_div else []

            # Determine status
            status = None
            if "won" in status_class:
                status = "WON"
            elif "lost" in status_class:
                status = "LOST"
            elif "nota" in status_class:
                status = "NOTA"

            # Extract votes and margin
            votes, margin = None, None
            if status_div and len(status_div.find_all("div")) > 1:
                vtext = status_div.find_all("div")[1].get_text(strip=True)
                split_data = vtext.split(" ")
                votes = self.clean_votes(split_data[0]) if split_data else None
                margin = (
                    self.clean_margin(split_data[1]) if len(split_data) > 1 else None
                )

            # Extract name and party
            nme_prty_div = candidate.find("div", class_="nme-prty")
            name = (
                nme_prty_div.find("h5").get_text(strip=True) if nme_prty_div else None
            )
            party = (
                nme_prty_div.find("h6").get_text(strip=True) if nme_prty_div else None
            )

            # Extract image URL
            img_tag = candidate.find("img")
            img_src = (
                img_tag["src"].strip() if img_tag and "src" in img_tag.attrs else None
            )
            image_url = (
                self.base_url + "/" + img_src
                if img_src and not img_src.startswith("http")
                else img_src
            )

            data.append(
                {
                    "name": name,
                    "party": party,
                    "status": status,
                    "votes": votes,
                    "margin": margin,
                    "image_url": image_url,
                }
            )

        return data


class ConstituencyScraper(ECIScraper):
    """Scraper for constituency data."""

    def extract_constituency_data(self, html: str) -> List[Dict]:
        """Extract constituency data from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        if not table:
            logger.error("No table found for constituencies")
            return []

        data = []
        for row in table.find_all("tr")[1:]:
            cells = row.find_all("td")
            if len(cells) >= 2:
                text = cells[1].get_text(strip=True)
                match = re.match(r"(.*)\((\d+)\)", text)
                if match:
                    name = match.group(1).strip()
                    cid = match.group(2).strip()
                    data.append(
                        {
                            "constituency_name": name,
                            "constituency_id": cid,
                            "state_id": self.get_state_code(),
                        }
                    )

        return data

    def get_state_code(self) -> str:
        """Get state code - to be implemented by subclasses."""
        return "XX"
