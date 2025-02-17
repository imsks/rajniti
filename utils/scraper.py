import requests
from bs4 import BeautifulSoup
import json
import re
import time
from pathlib import Path

class BaseScraper:
    def __init__(self, config):
        self.config = config
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

    def fetch_html(self, url, filename):
        file_path = self.config.HTML_DIR / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        
        response = requests.get(url, headers=self.headers, timeout=10)
        response.raise_for_status()
        file_path.write_text(response.text, encoding="utf-8")
        return response.text

    def save_json(self, data, filename):
        output_path = self.config.JSON_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return output_path

    def load_json(self, filename):
        json_path = self.config.JSON_DIR / filename
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

class PartyScraper(BaseScraper):
    def scrape(self, url):
        html_content = self.fetch_html(url, "party_results.html")
        soup = BeautifulSoup(html_content, "html.parser")
        
        data = []
        for row in soup.select("table tr")[1:]:
            cols = row.find_all("td")
            if len(cols) >= 4:
                party_info = cols[0].get_text(strip=True).split(" - ", 1)
                party_name = party_info[0]
                symbol = party_info[1] if len(party_info) > 1 else "N/A"
                total_seats = int(cols[3].get_text(strip=True)) if cols[3].get_text(strip=True).isdigit() else 0
                
                data.append({
                    "party_name": party_name,
                    "symbol": symbol,
                    "total_seats": total_seats
                })
        
        data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))
        return self.save_json(data, "party_results.json")

class ConstituencyScraper(BaseScraper):
    def scrape(self, url):
        html_content = self.fetch_html(url, "constituency_list.html")
        soup = BeautifulSoup(html_content, "html.parser")
        
        data = []
        for link in soup.select("a[href*='partywisewinresult']"):
            try:
                const_id = re.search(r'partywisewinresult-(\d+)S13', link['href']).group(1)
                const_url = f"{url.rsplit('/', 1)[0]}/{link['href']}"
                
                const_html = self.fetch_html(const_url, f"constituency_{const_id}.html")
                const_soup = BeautifulSoup(const_html, "html.parser")
                
                name = const_soup.find('h3', class_='constituency-name').get_text(strip=True)
                data.append({
                    "constituency_id": const_id,
                    "constituency_name": name,
                    "state_id": "S13"
                })
            except Exception as e:
                print(f"Error processing constituency {const_id}: {str(e)}")
        
        return self.save_json(data, "constituency_results.json")

class CandidateScraper(BaseScraper):
    def scrape(self, base_url, start, end):
        all_data = []
        for i in range(start, end + 1):
            try:
                url = f"{base_url}candidateswise-S13{i}.htm"
                html_content = self.fetch_html(url, f"candidates_{i}.html")
                soup = BeautifulSoup(html_content, "html.parser")
                
                for candidate in soup.select('.candidate-card'):
                    data = {
                        "constituency_code": f"S13-{i}",
                        "name": candidate.select_one('.candidate-name').get_text(strip=True),
                        "party": candidate.select_one('.candidate-party').get_text(strip=True),
                        "status": candidate.select_one('.candidate-status').get_text(strip=True) if candidate.select_one('.candidate-status') else None,
                        "votes": candidate.select_one('.candidate-votes').get_text(strip=True) if candidate.select_one('.candidate-votes') else None,
                        "margin": candidate.select_one('.candidate-margin').get_text(strip=True) if candidate.select_one('.candidate-margin') else None,
                        "image_url": candidate.select_one('img.candidate-photo')['src'] if candidate.select_one('img.candidate-photo') else None
                    }
                    all_data.append(data)
                
                time.sleep(1) 
            except Exception as e:
                print(f"Error processing page {i}: {str(e)}")
        
        return self.save_json(all_data, "candidate_results.json")