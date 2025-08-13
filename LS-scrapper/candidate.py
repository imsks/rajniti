import requests
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://results.eci.gov.in/",
}

URL = "https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-369.htm"

def fetch_page(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    else:
        print(f"[ERROR] Failed to fetch page: HTTP {response.status_code}")
        return None

def parse_candidates(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"class": "table-scroll"})
    if not table:
        print("[ERROR] No data table found.")
        return []

    rows = table.find_all("tr")[1:]  # Skip header row
    all_data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
        constituency_code = cols[0].text.strip()
        name = cols[1].text.strip()
        party = cols[2].text.strip()
        status = cols[3].text.strip()
        votes = cols[4].text.strip()
        margin = cols[5].text.strip()

        image_tag = cols[1].find("img")
        image_url = "https://results.eci.gov.in" + image_tag["src"] if image_tag else ""

        all_data.append({
            "Constituency Code": constituency_code,
            "Name": name,
            "Party": party,
            "Status": status,
            "Votes": votes,
            "Margin": margin,
            "Image URL": image_url
        })

    return all_data

if __name__ == "__main__":
    html = fetch_page(URL)
    if html:
        candidates = parse_candidates(html)
        with open("all_candidates.json", "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=4)
        print(f"[INFO] {len(candidates)} candidates saved to all_candidates.json")
