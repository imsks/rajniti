import requests
from pathlib import Path
from bs4 import BeautifulSoup
import json

def fetch_scrape_sort_save_json(url, html_dir, json_file_path):
    """
    Fetch HTML content from a URL, scrape data, sort it, and save to a JSON file.

    Parameters:
        url (str): The webpage URL to scrape.
        html_dir (Path): Directory to save the HTML file.
        json_file_path (str): Path to save the sorted JSON file.
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    }

    html_file = html_dir / f"{url.split('/')[-1]}" 

   
    if html_file.exists():
        print(f"Reading HTML content from cached file: {html_file}")
        html_content = html_file.read_text(encoding="utf-8")
    else:
        print(f"Fetching URL: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Received status code: {response.status_code}")

            if response.status_code == 200:
                html_content = response.text
                html_file.write_text(html_content, encoding="utf-8")
                print(f"HTML saved to: {html_file}")
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                return
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if table:
        print("Scraping and sorting party-wise results...")
        rows = table.find_all("tr")
        data = []

        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) >= 4:
                party_tag = columns[0].find("a")
                if party_tag:
                    party_name_full = party_tag.text.strip()
                else:
                    party_name_full = columns[0].text.strip()

                if " - " in party_name_full:
                    party_name, symbol = party_name_full.split(" - ", 1)
                else:
                    party_name = party_name_full
                    symbol = "N/A"

                total_seats = int(columns[3].text.strip()) if columns[3].text.strip().isdigit() else 0

                # Append the data row
                data.append({
                    "party_name": party_name,
                    "symbol": symbol,
                    "total_seats": total_seats
                })

        # Sort data by total seats (descending) and then by party name (alphabetically)
        data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))

        # Save to JSON
        with open(json_file_path, mode="w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

        print(f"Party-wise results saved to: {json_file_path}")
    else:
        print("No table found in the HTML content.")

# Directory for saving HTML files
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)

# Webpage URL for scraping
webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
# JSON file to save the sorted results
json_file_path = "partywiseresults_sorted.json"

# Call the function
fetch_scrape_sort_save_json(webpage_url, output_dir, json_file_path)
