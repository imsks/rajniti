"""
Utility functions for election data scraping.
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard headers for ECI requests
HEADERS = {
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
    url: str, retries: int = 3, timeout: int = 20, referer: str = None
) -> Optional[requests.Response]:
    """
    Fetch URL with retry logic.
    
    Args:
        url: URL to fetch
        retries: Number of retry attempts
        timeout: Request timeout in seconds
        referer: Optional referer header
    
    Returns:
        Response object or None if all retries fail
    """
    headers = HEADERS.copy()
    if referer:
        headers["Referer"] = referer
    
    for attempt in range(retries):
        try:
            logger.info(f"Fetching: {url} (attempt {attempt + 1})")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(3)
    
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
