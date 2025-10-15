import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.scrapers.lok_sabha import LokSabhaScraper

url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm"
scraper = LokSabhaScraper(url)
scraper.scrape()