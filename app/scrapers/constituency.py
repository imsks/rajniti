import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re

# Setup
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)
json_output = "delhi-cons.json"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Referer": "https://results.eci.gov.in/"
}

urls = [
    "https://results.eci.gov.in/ResultAcGenFeb2025/partywisewinresult-1U05.htm",
    "https://results.eci.gov.in/ResultAcGenFeb2025/partywisewinresult-369U05.htm"
]

def fetch_html(url, file_path):
    """Fetch or read cached HTML"""
    if file_path.exists():
        print(f"[CACHE] Reading: {file_path}")
        return file_path.read_text(encoding="utf-8")
    try:
        print(f"[FETCH] {url}")
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        file_path.write_text(res.text, encoding="utf-8")
        return res.text
    except Exception as e:
        print(f"[ERROR] {e}")
        return None

def extract_constituencies(html):
    """Parse table and extract constituency data"""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table")
    if not table:
        print("[ERROR] No <table> found.")
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
                data.append({
                    "constituency_name": name,
                    "constituency_id": f"DL-{cid}",  # 👈 prefix DL here
                    "state_id": "DL"
                })
    return data

# Main logic
all_data = []
unique_ids = set()

for url in urls:
    file_name = url.split('/')[-1]
    file_path = output_dir / file_name
    html = fetch_html(url, file_path)
    if html:
        data = extract_constituencies(html)
        for item in data:
            if item["constituency_id"] not in unique_ids:
                all_data.append(item)
                unique_ids.add(item["constituency_id"])

# Save to JSON
if all_data:
    all_data.sort(key=lambda x: int(x["constituency_id"].split("-")[1]))  # Sort by number part only
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)
    print(f"[DONE] {len(all_data)} constituencies saved to: {json_output}")
else:
    print("[INFO] No constituency data extracted.")
