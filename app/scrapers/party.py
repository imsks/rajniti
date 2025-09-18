import requests
import json
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.party_scraper import load_html, parse_party_table, sort_party_data


from utils.party_scraper import load_html, parse_party_table, sort_party_data

def scrape_party_data(url, html_dir, json_file_path):
    html_file = html_dir / "ResultAcGenFeb2025.html"
    html_content = load_html(url, html_file)
    if not html_content:
        return

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    if not table:
        print("[ERROR] No <table> found in the HTML.")
        return

    data = parse_party_table(table)
    sorted_data = sort_party_data(data)

    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(sorted_data, json_file, indent=4, ensure_ascii=False)
    print(f"[DONE] Results saved to: {json_file_path}")

if __name__ == "__main__":
    output_dir = Path("html_files")
    output_dir.mkdir(exist_ok=True)

    url = "https://results.eci.gov.in/ResultAcGenFeb2025/index.htm"
    json_file_path = "DL-party.json"

    scrape_party_data(url, output_dir, json_file_path)