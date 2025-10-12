"""
Utility functions for election data scraping.
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard headers for ECI requests - mimicking a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Cache-Control": "max-age=0",
}


# Create a client to maintain cookies and HTTP/2 connections across requests
_client = None


def get_client() -> httpx.Client:
    """
    Get or create a shared httpx client with HTTP/2 support.
    
    HTTP/2 is REQUIRED by the ECI website - HTTP/1.1 requests are blocked.
    Reusing a client helps maintain cookies and connections,
    making requests appear more like a real browser.
    """
    global _client
    if _client is None:
        _client = httpx.Client(
            http2=True,  # Critical: ECI blocks HTTP/1.1
            follow_redirects=True,
            timeout=30.0,
            headers=HEADERS,
        )
    return _client


def get_with_retry(
    url: str, retries: int = 3, timeout: int = 30, referer: str = None
) -> Optional[httpx.Response]:
    """
    Fetch URL with retry logic and exponential backoff using HTTP/2.
    
    IMPORTANT: The ECI website requires HTTP/2 connections and will
    return 403 Forbidden for HTTP/1.1 requests.
    
    Args:
        url: URL to fetch
        retries: Number of retry attempts
        timeout: Request timeout in seconds
        referer: Optional referer header
    
    Returns:
        Response object or None if all retries fail
    """
    client = get_client()
    headers = HEADERS.copy()
    
    # Add referer if provided
    if referer:
        headers["Referer"] = referer
        headers["Sec-Fetch-Site"] = "same-origin"
    
    for attempt in range(retries):
        try:
            logger.info(f"Fetching: {url} (attempt {attempt + 1})")
            response = client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            logger.info(f"✓ Success (HTTP/{response.http_version})")
            
            # Success - add a small delay to be polite
            time.sleep(0.5)
            return response
            
        except httpx.HTTPStatusError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e.response.status_code} {e.response.reason_phrase}")
            
            # Exponential backoff: 2s, 5s, 10s
            if attempt < retries - 1:
                wait_time = 2 * (attempt + 1) ** 1.5
                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
                
        except httpx.RequestError as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            # Exponential backoff
            if attempt < retries - 1:
                wait_time = 2 * (attempt + 1) ** 1.5
                logger.info(f"Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
    
    logger.error(f"Max retries reached for {url}")
    return None


def save_json(data: List[Dict], filepath: Path) -> None:
    """
    Save data to JSON file.
    
    Args:
        data: List of dictionaries to save
        filepath: Path object for output file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logger.info(f"Data saved to {filepath}")


def clean_votes(votes: str) -> Optional[str]:
    """
    Clean vote count string by removing special characters.
    
    Args:
        votes: Raw vote string
    
    Returns:
        Cleaned vote string or None
    """
    if not votes:
        return None
    return re.sub(r'[+()"\s]', "", votes)


def clean_margin(margin: str) -> Optional[str]:
    """
    Clean margin string.
    
    Args:
        margin: Raw margin string
    
    Returns:
        Cleaned margin string or None
    """
    if not margin:
        return None
    margin = margin.replace(")", "").strip()
    return f"({margin}" if margin.startswith("+") else margin


def normalize_base_url(url: str) -> str:
    """
    Normalize URL to base directory by removing trailing files.
    
    Args:
        url: Raw URL that might include index.htm or other files
    
    Returns:
        Normalized base URL without trailing files
    
    Examples:
        https://results.eci.gov.in/PcResultGenJune2024/index.htm
        -> https://results.eci.gov.in/PcResultGenJune2024
        
        https://results.eci.gov.in/ResultAcGenFeb2025/
        -> https://results.eci.gov.in/ResultAcGenFeb2025
    """
    # Remove trailing slash
    url = url.rstrip("/")
    
    # Remove common HTML files from the end
    common_files = [
        "/index.htm",
        "/index.html",
        "/default.htm",
        "/default.html",
    ]
    
    url_lower = url.lower()
    for file_ending in common_files:
        if url_lower.endswith(file_ending):
            url = url[: -len(file_ending)]
            break
    
    logger.info(f"Normalized URL: {url}")
    return url
