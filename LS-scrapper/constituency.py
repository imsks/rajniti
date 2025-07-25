import requests
from bs4 import BeautifulSoup
import json
from time import sleep

party_ids = [
    369, 742, 1680, 140, 582, 1745, 805, 3369, 3620, 3529, 3165, 1888, 1420,
    547, 772, 1, 852, 860, 545, 804, 1847, 544, 1458, 834, 1998, 83, 664, 911,
    1534, 1142, 3388, 2757, 1584, 2484, 3482, 1658, 1046, 2989, 2070, 160, 118, 743
]

BASE_URL = "https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-{}.htm"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://results.eci.gov.in/PcResultGenJune2024/index.htm"
}

all_data = []

for party_id in party_ids:
    url = BASE_URL.format(party_id)
    print(f"Visiting: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"class": "table table-striped table-bordered"})
        if not table:
            print(f"No table found for party {party_id}")
            continue

        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue
            constituency_link = cols[1].find("a")
            constituency = constituency_link.text.strip() if constituency_link else cols[1].text.strip()
            candidate_name = cols[2].text.strip()
            votes = cols[3].text.strip()
            margin = cols[4].text.strip()

            all_data.append({
                "party_id": party_id,
                "constituency": constituency,
                "candidate_name": candidate_name,
                "votes": votes,
                "margin": margin
            })
        sleep(0.5)  # Be polite to the server
    except Exception as e:
        print(f"Failed for party {party_id}: {e}")

# Save combined results
with open("all_party_results.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=4)

print(" All party data scraped and saved to all_party_results.json")
