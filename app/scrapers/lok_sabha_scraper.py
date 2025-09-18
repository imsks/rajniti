"""
Lok Sabha (Parliamentary) Election Scraper.
Handles scraping of national parliamentary election data from ECI.
"""
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper
from app.core.exceptions import ScrapingError
from app.core.output_manager import OutputManager


class LokSabhaScraper(BaseScraper):
    """Scraper for Lok Sabha (Parliamentary) elections."""
    
    def __init__(self, **kwargs):
        """Initialize Lok Sabha scraper with ECI-specific configuration."""
        super().__init__(
            base_url="https://results.eci.gov.in",
            **kwargs
        )
        self.election_type = "lok_sabha"
        self.output_manager = OutputManager()
    
    def scrape(
        self, 
        year: int = 2024, 
        output_mode: str = "json",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape Lok Sabha election data for a specific year.
        
        Args:
            year: Election year
            output_mode: Output persistence mode ("json", "db", or "both")
            **kwargs: Additional scraping parameters
            
        Returns:
            List of scraped candidate records
        """
        self.logger.log_scrape_start("LokSabhaScraper", self.base_url, year=year)
        
        try:
            # Get the main results page URL for the year
            main_url = self._build_main_url(year)
            
            # Scrape constituency list
            constituencies = self._scrape_constituencies(main_url, year)
            
            # Scrape candidate data for each constituency
            all_candidates = []
            for constituency in constituencies:
                candidates = self._scrape_constituency_candidates(constituency, year)
                all_candidates.extend(candidates)
            
            # Scrape party data
            parties = self._scrape_parties(main_url, year)
            
            # Persist data using output manager
            self._persist_scraped_data(
                candidates=all_candidates,
                parties=parties,
                year=year,
                output_mode=output_mode
            )
            
            self.logger.log_scrape_success(
                "LokSabhaScraper", 
                main_url, 
                len(all_candidates), 
                0  # duration will be calculated by caller
            )
            
            return all_candidates
            
        except Exception as e:
            self.logger.log_scrape_error("LokSabhaScraper", self.base_url, str(e))
            raise ScrapingError(f"Failed to scrape Lok Sabha data: {str(e)}", url=self.base_url)
    
    def _build_main_url(self, year: int) -> str:
        """Build the main results URL for a specific year."""
        if year == 2024:
            return f"{self.base_url}/DRISTHI24/PC/EN/index.htm"
        elif year == 2019:
            return f"{self.base_url}/pc/en/partywise-34.htm"
        else:
            # Generic URL pattern - may need adjustment
            return f"{self.base_url}/pc{year}/en/index.htm"
    
    def _scrape_constituencies(self, main_url: str, year: int) -> List[Dict[str, Any]]:
        """Scrape list of constituencies from the main page."""
        html_content = self.fetch_html(main_url)
        soup = self.parse_html(html_content)
        
        constituencies = []
        
        # Look for constituency links - ECI structure may vary by year
        if year == 2024:
            # 2024-specific parsing logic
            const_links = soup.find_all('a', href=re.compile(r'pc\d+\.htm'))
        else:
            # Generic constituency link pattern
            const_links = soup.find_all('a', href=re.compile(r'(pc|PC)\d+'))
        
        for link in const_links:
            href = link.get('href', '')
            if href:
                constituencies.append({
                    'name': self.clean_text(link.get_text()),
                    'url': urljoin(main_url, href),
                    'code': self._extract_constituency_code(href)
                })
        
        return constituencies
    
    def _scrape_constituency_candidates(
        self, 
        constituency: Dict[str, Any], 
        year: int
    ) -> List[Dict[str, Any]]:
        """Scrape candidate data for a specific constituency."""
        try:
            html_content = self.fetch_html(constituency['url'])
            soup = self.parse_html(html_content)
            
            candidates = []
            
            # Look for candidate tables - structure varies by year
            candidate_tables = soup.find_all('table')
            
            for table in candidate_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 4:  # Minimum expected columns
                        candidate = self._parse_candidate_row(cells, constituency, year)
                        if candidate:
                            candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            self.logger.log_scrape_error(
                "LokSabhaScraper", 
                constituency['url'], 
                f"Failed to scrape constituency {constituency['name']}: {str(e)}"
            )
            return []
    
    def _parse_candidate_row(
        self, 
        cells: List[Tag], 
        constituency: Dict[str, Any], 
        year: int
    ) -> Optional[Dict[str, Any]]:
        """Parse a candidate data row from constituency results."""
        try:
            # Common field extraction - adjust indices based on ECI table structure
            if year == 2024:
                # 2024 structure
                candidate_name = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
                party_name = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                votes = self.clean_text(cells[3].get_text()) if len(cells) > 3 else ""
                margin = self.clean_text(cells[4].get_text()) if len(cells) > 4 else ""
            else:
                # Generic structure
                candidate_name = self.clean_text(cells[0].get_text()) if len(cells) > 0 else ""
                party_name = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
                votes = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                margin = self.clean_text(cells[3].get_text()) if len(cells) > 3 else ""
            
            if not candidate_name or not party_name:
                return None
            
            return {
                'candidate_name': candidate_name,
                'party': party_name,
                'constituency': constituency['name'],
                'constituency_code': constituency['code'],
                'votes': self._clean_numeric_value(votes),
                'margin': self._clean_numeric_value(margin),
                'status': self._determine_candidate_status(cells),
                'election_type': 'LOKSABHA',
                'year': year
            }
            
        except Exception as e:
            self.logger.log_scrape_error(
                "LokSabhaScraper", 
                constituency.get('url', ''), 
                f"Failed to parse candidate row: {str(e)}"
            )
            return None
    
    def _scrape_parties(self, main_url: str, year: int) -> List[Dict[str, Any]]:
        """Scrape party-wise results data."""
        try:
            # Navigate to party-wise results page
            if year == 2024:
                party_url = f"{self.base_url}/DRISTHI24/PC/EN/partywise-index.htm"
            else:
                party_url = f"{self.base_url}/pc{year}/en/partywise.htm"
            
            html_content = self.fetch_html(party_url)
            soup = self.parse_html(html_content)
            
            parties = []
            
            # Look for party tables
            party_tables = soup.find_all('table')
            
            for table in party_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 3:
                        party = self._parse_party_row(cells, year)
                        if party:
                            parties.append(party)
            
            return parties
            
        except Exception as e:
            self.logger.log_scrape_error("LokSabhaScraper", main_url, f"Failed to scrape parties: {str(e)}")
            return []
    
    def _parse_party_row(self, cells: List[Tag], year: int) -> Optional[Dict[str, Any]]:
        """Parse a party data row."""
        try:
            party_name = self.clean_text(cells[0].get_text()) if len(cells) > 0 else ""
            symbol = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
            total_seats = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
            
            if not party_name:
                return None
            
            return {
                'name': party_name,
                'symbol': symbol,
                'total_seats': self._clean_numeric_value(total_seats),
                'election_type': 'LOKSABHA',
                'year': year
            }
            
        except Exception as e:
            return None
    
    def _persist_scraped_data(
        self, 
        candidates: List[Dict[str, Any]], 
        parties: List[Dict[str, Any]], 
        year: int,
        output_mode: str
    ) -> None:
        """Persist scraped data using the output manager."""
        
        # Persist candidates
        if candidates:
            self.output_manager.persist_output(
                data=candidates,
                election_type=self.election_type,
                dataset_name=f"candidates-{year}",
                output_mode=output_mode,
                meta={
                    "dataset_name": f"lok_sabha_candidates_{year}",
                    "title": f"Lok Sabha Election {year} - Candidate Results",
                    "description": f"Comprehensive candidate results from {year} Lok Sabha elections",
                    "election": {
                        "type": "General Election (Lok Sabha)",
                        "year": year,
                        "total_constituencies": 543
                    }
                }
            )
        
        # Persist parties
        if parties:
            self.output_manager.persist_output(
                data=parties,
                election_type=self.election_type,
                dataset_name=f"parties-{year}",
                output_mode=output_mode,
                meta={
                    "dataset_name": f"lok_sabha_parties_{year}",
                    "title": f"Lok Sabha Election {year} - Party Results",
                    "description": f"Party-wise performance in {year} Lok Sabha elections",
                    "election": {
                        "type": "General Election (Lok Sabha)",
                        "year": year
                    }
                }
            )
    
    def _extract_constituency_code(self, href: str) -> str:
        """Extract constituency code from URL."""
        match = re.search(r'pc(\d+)', href, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _clean_numeric_value(self, value: str) -> Optional[int]:
        """Clean and convert numeric values."""
        if not value:
            return None
        
        # Remove common formatting characters
        cleaned = re.sub(r'[+,.\s]', '', value)
        
        try:
            return int(cleaned) if cleaned.isdigit() else None
        except ValueError:
            return None
    
    def _determine_candidate_status(self, cells: List[Tag]) -> Optional[str]:
        """Determine if candidate won or lost based on table formatting or content."""
        # Look for visual indicators like bold text, special symbols, or explicit status
        for cell in cells:
            cell_text = cell.get_text().lower()
            if 'won' in cell_text or 'winner' in cell_text:
                return 'won'
            elif 'lost' in cell_text or 'loser' in cell_text:
                return 'lost'
            
            # Check for formatting indicators (bold, etc.)
            if cell.find('b') or cell.find('strong'):
                return 'won'
        
        return None
