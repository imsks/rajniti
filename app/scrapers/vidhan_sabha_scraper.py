"""
Vidhan Sabha (State Assembly) Election Scraper.
Handles scraping of state assembly election data from ECI.
"""
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

from .base_scraper import BaseScraper
from app.core.exceptions import ScrapingError
from app.core.output_manager import OutputManager


class VidhanSabhaScraper(BaseScraper):
    """Scraper for Vidhan Sabha (State Assembly) elections."""
    
    # State code mappings for ECI URLs
    STATE_CODES = {
        'maharashtra': 'S13',
        'uttar_pradesh': 'S24',
        'bihar': 'S04',
        'west_bengal': 'S25',
        'madhya_pradesh': 'S14',
        'tamil_nadu': 'S22',
        'rajasthan': 'S20',
        'karnataka': 'S10',
        'gujarat': 'S06',
        'odisha': 'S18',
        'telangana': 'S29',
        'kerala': 'S11',
        'jharkhand': 'S27',
        'assam': 'S03',
        'punjab': 'S19',
        'haryana': 'S07',
        'chhattisgarh': 'S26',
        'jammu_kashmir': 'S01',
        'uttarakhand': 'S05',
        'himachal_pradesh': 'S02',
        'arunachal_pradesh': 'S12',
        'goa': 'S30',
        'manipur': 'S14',
        'meghalaya': 'S17',
        'nagaland': 'S13',
        'sikkim': 'S10',
        'tripura': 'S16'
    }
    
    def __init__(self, **kwargs):
        """Initialize Vidhan Sabha scraper with ECI-specific configuration."""
        super().__init__(
            base_url="https://results.eci.gov.in",
            **kwargs
        )
        self.election_type = "vidhan_sabha"
        self.output_manager = OutputManager()
    
    def scrape(
        self, 
        state: str,
        year: int = 2024, 
        output_mode: str = "json",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Scrape Vidhan Sabha election data for a specific state and year.
        
        Args:
            state: State name (lowercase with underscores)
            year: Election year
            output_mode: Output persistence mode ("json", "db", or "both")
            **kwargs: Additional scraping parameters
            
        Returns:
            List of scraped candidate records
        """
        self.logger.log_scrape_start("VidhanSabhaScraper", self.base_url, state=state, year=year)
        
        try:
            # Get state-specific URLs and data
            state_code = self._get_state_code(state)
            main_url = self._build_main_url(state, year)
            
            # Scrape constituency list
            constituencies = self._scrape_constituencies(main_url, state, year)
            
            # Scrape candidate data for each constituency
            all_candidates = []
            for constituency in constituencies:
                candidates = self._scrape_constituency_candidates(constituency, state, year)
                all_candidates.extend(candidates)
            
            # Scrape party data
            parties = self._scrape_parties(main_url, state, year)
            
            # Persist data using output manager
            self._persist_scraped_data(
                candidates=all_candidates,
                parties=parties,
                constituencies=constituencies,
                state=state,
                year=year,
                output_mode=output_mode
            )
            
            self.logger.log_scrape_success(
                "VidhanSabhaScraper", 
                main_url, 
                len(all_candidates), 
                0  # duration will be calculated by caller
            )
            
            return all_candidates
            
        except Exception as e:
            self.logger.log_scrape_error("VidhanSabhaScraper", self.base_url, str(e))
            raise ScrapingError(f"Failed to scrape Vidhan Sabha data for {state}: {str(e)}", url=self.base_url)
    
    def _get_state_code(self, state: str) -> str:
        """Get ECI state code for the given state."""
        return self.STATE_CODES.get(state.lower(), 'S13')  # Default to Maharashtra
    
    def _build_main_url(self, state: str, year: int) -> str:
        """Build the main results URL for a specific state and year."""
        if year == 2024 and state.lower() == 'maharashtra':
            return f"{self.base_url}/DrishtiDocFolder/AcDetails/AC{year}/ac{year}S13-table.htm"
        elif year == 2024:
            state_code = self._get_state_code(state)
            return f"{self.base_url}/DrishtiDocFolder/AcDetails/AC{year}/ac{year}{state_code}-table.htm"
        else:
            # Generic URL pattern for other years
            state_code = self._get_state_code(state)
            return f"{self.base_url}/ac{year}/{state_code}/index.htm"
    
    def _scrape_constituencies(self, main_url: str, state: str, year: int) -> List[Dict[str, Any]]:
        """Scrape list of constituencies from the main page."""
        html_content = self.fetch_html(main_url)
        soup = self.parse_html(html_content)
        
        constituencies = []
        
        # Look for constituency tables - Maharashtra 2024 specific structure
        if year == 2024 and state.lower() == 'maharashtra':
            # Parse constituency table
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header row
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 2:
                        const_code = self.clean_text(cells[0].get_text())
                        const_name = self.clean_text(cells[1].get_text())
                        
                        if const_code and const_name:
                            constituencies.append({
                                'code': const_code,
                                'name': const_name,
                                'state': state,
                                'url': self._build_constituency_url(const_code, state, year)
                            })
        else:
            # Generic constituency extraction for other states/years
            const_links = soup.find_all('a', href=re.compile(r'ac\d+'))
            
            for link in const_links:
                href = link.get('href', '')
                if href:
                    constituencies.append({
                        'name': self.clean_text(link.get_text()),
                        'url': urljoin(main_url, href),
                        'code': self._extract_constituency_code(href),
                        'state': state
                    })
        
        return constituencies
    
    def _build_constituency_url(self, const_code: str, state: str, year: int) -> str:
        """Build URL for individual constituency results."""
        if year == 2024 and state.lower() == 'maharashtra':
            return f"{self.base_url}/DrishtiDocFolder/AcDetails/AC{year}/ac{year}{const_code}-table.htm"
        else:
            state_code = self._get_state_code(state)
            return f"{self.base_url}/ac{year}/{state_code}/{const_code}.htm"
    
    def _scrape_constituency_candidates(
        self, 
        constituency: Dict[str, Any], 
        state: str,
        year: int
    ) -> List[Dict[str, Any]]:
        """Scrape candidate data for a specific constituency."""
        try:
            html_content = self.fetch_html(constituency['url'])
            soup = self.parse_html(html_content)
            
            candidates = []
            
            # Look for candidate tables
            candidate_tables = soup.find_all('table')
            
            for table in candidate_tables:
                rows = table.find_all('tr')
                
                # Skip header rows and find data rows
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    
                    # Skip header rows (usually first 1-2 rows)
                    if i < 2 or len(cells) < 4:
                        continue
                    
                    candidate = self._parse_candidate_row(cells, constituency, state, year)
                    if candidate:
                        candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            self.logger.log_scrape_error(
                "VidhanSabhaScraper", 
                constituency['url'], 
                f"Failed to scrape constituency {constituency['name']}: {str(e)}"
            )
            return []
    
    def _parse_candidate_row(
        self, 
        cells: List[Tag], 
        constituency: Dict[str, Any], 
        state: str,
        year: int
    ) -> Optional[Dict[str, Any]]:
        """Parse a candidate data row from constituency results."""
        try:
            # Maharashtra 2024 structure: Name, Party, Status, Votes, Margin, Image
            if year == 2024 and state.lower() == 'maharashtra':
                candidate_name = self.clean_text(cells[0].get_text()) if len(cells) > 0 else ""
                party_name = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
                status = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                votes = self.clean_text(cells[3].get_text()) if len(cells) > 3 else ""
                margin = self.clean_text(cells[4].get_text()) if len(cells) > 4 else ""
                image_url = self._extract_image_url(cells[5]) if len(cells) > 5 else None
            else:
                # Generic structure
                candidate_name = self.clean_text(cells[0].get_text()) if len(cells) > 0 else ""
                party_name = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
                votes = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                margin = self.clean_text(cells[3].get_text()) if len(cells) > 3 else ""
                status = self._determine_candidate_status_from_position(0)  # Assume first row is winner
                image_url = None
            
            if not candidate_name or not party_name:
                return None
            
            return {
                'name': candidate_name,
                'party': party_name,
                'constituency_code': constituency['code'],
                'constituency_name': constituency['name'],
                'state': state,
                'status': self._normalize_status(status),
                'votes': self._clean_numeric_value(votes),
                'margin': self._clean_numeric_value(margin),
                'image_url': image_url,
                'election_type': 'VIDHANSABHA',
                'year': year
            }
            
        except Exception as e:
            self.logger.log_scrape_error(
                "VidhanSabhaScraper", 
                constituency.get('url', ''), 
                f"Failed to parse candidate row: {str(e)}"
            )
            return None
    
    def _scrape_parties(self, main_url: str, state: str, year: int) -> List[Dict[str, Any]]:
        """Scrape party-wise results data."""
        try:
            # Build party-wise results URL
            if year == 2024 and state.lower() == 'maharashtra':
                party_url = f"{self.base_url}/DrishtiDocFolder/AcDetails/AC{year}/ac{year}S13-partywise.htm"
            else:
                state_code = self._get_state_code(state)
                party_url = f"{self.base_url}/ac{year}/{state_code}/partywise.htm"
            
            html_content = self.fetch_html(party_url)
            soup = self.parse_html(html_content)
            
            parties = []
            
            # Look for party tables
            party_tables = soup.find_all('table')
            
            for table in party_tables:
                rows = table.find_all('tr')
                
                for row in rows[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    if len(cells) >= 2:
                        party = self._parse_party_row(cells, state, year)
                        if party:
                            parties.append(party)
            
            return parties
            
        except Exception as e:
            self.logger.log_scrape_error("VidhanSabhaScraper", main_url, f"Failed to scrape parties: {str(e)}")
            return []
    
    def _parse_party_row(self, cells: List[Tag], state: str, year: int) -> Optional[Dict[str, Any]]:
        """Parse a party data row."""
        try:
            party_name = self.clean_text(cells[0].get_text()) if len(cells) > 0 else ""
            total_seats = self.clean_text(cells[1].get_text()) if len(cells) > 1 else ""
            symbol = self.clean_text(cells[2].get_text()) if len(cells) > 2 else ""
            
            if not party_name:
                return None
            
            return {
                'name': party_name,
                'symbol': symbol,
                'total_seats': self._clean_numeric_value(total_seats),
                'state': state,
                'election_type': 'VIDHANSABHA',
                'year': year
            }
            
        except Exception as e:
            return None
    
    def _persist_scraped_data(
        self, 
        candidates: List[Dict[str, Any]], 
        parties: List[Dict[str, Any]], 
        constituencies: List[Dict[str, Any]],
        state: str,
        year: int,
        output_mode: str
    ) -> None:
        """Persist scraped data using the output manager."""
        
        # Persist candidates
        if candidates:
            self.output_manager.persist_output(
                data=candidates,
                election_type=self.election_type,
                dataset_name=f"{state}-{year}",
                output_mode=output_mode,
                meta={
                    "dataset_name": f"vidhan_sabha_{state}_{year}",
                    "title": f"{state.title().replace('_', ' ')} Assembly Election {year} - Candidate Results",
                    "description": f"Comprehensive candidate results from {year} {state.title().replace('_', ' ')} Vidhan Sabha elections",
                    "election": {
                        "type": "Assembly Election (Vidhan Sabha)",
                        "state": state.title().replace('_', ' '),
                        "year": year,
                        "total_constituencies": len(constituencies)
                    }
                }
            )
        
        # Persist parties
        if parties:
            self.output_manager.persist_output(
                data=parties,
                election_type=self.election_type,
                dataset_name=f"{state}-parties-{year}",
                output_mode=output_mode,
                meta={
                    "dataset_name": f"vidhan_sabha_{state}_parties_{year}",
                    "title": f"{state.title().replace('_', ' ')} Assembly Election {year} - Party Results",
                    "description": f"Party-wise performance in {year} {state.title().replace('_', ' ')} Vidhan Sabha elections",
                    "election": {
                        "type": "Assembly Election (Vidhan Sabha)",
                        "state": state.title().replace('_', ' '),
                        "year": year
                    }
                }
            )
        
        # Persist constituencies
        if constituencies:
            self.output_manager.persist_output(
                data=constituencies,
                election_type=self.election_type,
                dataset_name=f"{state}-constituencies-{year}",
                output_mode=output_mode,
                meta={
                    "dataset_name": f"vidhan_sabha_{state}_constituencies_{year}",
                    "title": f"{state.title().replace('_', ' ')} Assembly Election {year} - Constituencies",
                    "description": f"Constituency information for {year} {state.title().replace('_', ' ')} Vidhan Sabha elections",
                    "election": {
                        "type": "Assembly Election (Vidhan Sabha)",
                        "state": state.title().replace('_', ' '),
                        "year": year,
                        "total_constituencies": len(constituencies)
                    }
                }
            )
    
    def _extract_constituency_code(self, href: str) -> str:
        """Extract constituency code from URL."""
        match = re.search(r'ac(\d+)', href, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _extract_image_url(self, cell: Tag) -> Optional[str]:
        """Extract candidate image URL from table cell."""
        try:
            img_tag = cell.find('img')
            if img_tag:
                src = img_tag.get('src')
                if src:
                    return urljoin(self.base_url, src)
        except Exception:
            pass
        return None
    
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
    
    def _normalize_status(self, status: str) -> Optional[str]:
        """Normalize candidate status values."""
        if not status:
            return None
        
        status_lower = status.lower()
        if status_lower in ["won", "win", "winner"]:
            return "Won"
        elif status_lower in ["lost", "lose", "loser"]:
            return "Lost"
        elif status_lower == "nota":
            return "NOTA"
        else:
            return status
    
    def _determine_candidate_status_from_position(self, position: int) -> str:
        """Determine candidate status based on position in results table."""
        return "Won" if position == 0 else "Lost"
