"""
Base scraper class with standardized retry logic, error handling, and logging.
"""
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup

from app.core.exceptions import ScrapingError, ExternalServiceError
from app.core.logging_config import ScraperLogger


class BaseScraper(ABC):
    """Base class for all scrapers with standardized functionality."""
    
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        retry_attempts: int = 3,
        retry_delay: int = 2,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the base scraper.
        
        Args:
            base_url: Base URL for the scraping target
            timeout: Request timeout in seconds
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Delay between retry attempts in seconds
            cache_dir: Directory for caching responses
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Setup logging
        self.logger = ScraperLogger()
        
        # Setup session with retry strategy
        self.session = self._create_session()
        
        # Common headers
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
            "Upgrade-Insecure-Requests": "1"
        }
    
    def _create_session(self) -> requests.Session:
        """Create a session with retry strategy."""
        session = requests.Session()
        
        # Define retry strategy
        retry_strategy = Retry(
            total=self.retry_attempts,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_cache_path(self, url: str) -> Optional[Path]:
        """Get cache file path for a URL."""
        if not self.cache_dir:
            return None
            
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate cache filename from URL
        filename = url.replace("/", "_").replace(":", "_").replace("?", "_")
        return self.cache_dir / f"{filename}.html"
    
    def _load_from_cache(self, url: str) -> Optional[str]:
        """Load content from cache if available."""
        cache_path = self._get_cache_path(url)
        if cache_path and cache_path.exists():
            self.logger.logger.debug("Loading from cache", url=url, cache_path=str(cache_path))
            return cache_path.read_text(encoding="utf-8")
        return None
    
    def _save_to_cache(self, url: str, content: str) -> None:
        """Save content to cache."""
        cache_path = self._get_cache_path(url)
        if cache_path:
            cache_path.write_text(content, encoding="utf-8")
            self.logger.logger.debug("Saved to cache", url=url, cache_path=str(cache_path))
    
    def fetch_html(self, url: str, use_cache: bool = True) -> str:
        """
        Fetch HTML content from URL with caching support.
        
        Args:
            url: URL to fetch
            use_cache: Whether to use cached content if available
            
        Returns:
            HTML content as string
            
        Raises:
            ScrapingError: If fetching fails after all retries
        """
        # Check cache first
        if use_cache:
            cached_content = self._load_from_cache(url)
            if cached_content:
                return cached_content
        
        start_time = time.time()
        last_error = None
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                self.logger.log_scrape_start(self.__class__.__name__, url, attempt=attempt)
                
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                content = response.text
                
                # Save to cache
                if use_cache:
                    self._save_to_cache(url, content)
                
                duration = time.time() - start_time
                self.logger.log_scrape_success(
                    self.__class__.__name__,
                    url,
                    items_scraped=1,
                    duration=duration,
                    attempt=attempt
                )
                
                return content
                
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                
                if attempt < self.retry_attempts:
                    self.logger.log_retry(
                        self.__class__.__name__,
                        url,
                        attempt=attempt,
                        max_attempts=self.retry_attempts,
                        error=last_error
                    )
                    time.sleep(self.retry_delay * attempt)  # Exponential backoff
                else:
                    self.logger.log_scrape_error(
                        self.__class__.__name__,
                        url,
                        error=last_error,
                        attempt=attempt
                    )
        
        raise ScrapingError(f"Failed to fetch {url} after {self.retry_attempts} attempts: {last_error}", url=url)
    
    def parse_html(self, html_content: str, parser: str = "html.parser") -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            html_content: HTML content to parse
            parser: Parser to use (html.parser, lxml, html5lib)
            
        Returns:
            BeautifulSoup object
        """
        try:
            return BeautifulSoup(html_content, parser)
        except Exception as e:
            raise ScrapingError(f"Failed to parse HTML content: {str(e)}")
    
    def extract_table_data(self, soup: BeautifulSoup, table_selector: str = "table") -> List[List[str]]:
        """
        Extract data from HTML table.
        
        Args:
            soup: BeautifulSoup object
            table_selector: CSS selector for the table
            
        Returns:
            List of rows, each row is a list of cell values
        """
        table = soup.select_one(table_selector)
        if not table:
            raise ScrapingError(f"No table found with selector '{table_selector}'")
        
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cells:  # Skip empty rows
                rows.append(cells)
        
        return rows
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = " ".join(text.split())
        
        # Remove common unwanted characters
        cleaned = cleaned.replace("\u00a0", " ")  # Non-breaking space
        cleaned = cleaned.replace("\n", " ")
        cleaned = cleaned.replace("\t", " ")
        
        return cleaned.strip()
    
    def build_url(self, path: str) -> str:
        """Build full URL from base URL and path."""
        if path.startswith("http"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"
    
    @abstractmethod
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Abstract method for scraping data.
        
        Each scraper must implement this method to define
        their specific scraping logic.
        
        Returns:
            List of scraped data dictionaries
        """
        pass
    
    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate scraped data.
        
        Override this method in subclasses to add specific validation.
        
        Args:
            data: List of scraped data dictionaries
            
        Returns:
            List of validated data dictionaries
        """
        return data
    
    def close(self) -> None:
        """Close the session and cleanup resources."""
        if hasattr(self, "session"):
            self.session.close()
