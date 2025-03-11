import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import re

output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)                         

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

def fetch_html(url, output_file):
    try:
        if output_file.exists():
            print(f"Reading cached file: {output_file}")
            return output_file.read_text(encoding="utf-8")
        else:
            print(f"Fetching URL: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            output_file.write_text(html_content, encoding="utf-8")
            return html_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_links_from_main_page(main_page_url):
    try:
        print(f"Fetching main page: {main_page_url}")
        response = requests.get(main_page_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if re.match(r"partywisewinresult-\d+S13\.htm$", href):
                full_url = f"https://results.eci.gov.in/ResultAcGenNov2024/{href}"
                links.append(full_url)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error accessing main page {main_page_url}: {e}")
        return []

def extract_data_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')

    if not table:
        print("No table found on the page.")
        return []
    
    rows = table.find_all('tr')[1:]  
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 2: 
            constituency_full = cells[1].text.strip()
            match = re.match(r"(.*)\((\d+)\)", constituency_full)
            if match:
                constituency_name = match.group(1).strip()
                constituency_id = match.group(2).strip()
                data.append({
                    "constituency_name": constituency_name,
                    "constituency_id": constituency_id,
                    "state_id": "S13"
                })
    return data

def scrape_all_data(main_page_url):
    print(f"Extracting links from the main page: {main_page_url}")
    links = extract_links_from_main_page(main_page_url)
    if not links:
        print("No related links found.")
        return []

    all_data = []
    unique_constituencies = set()
    
    for url in links:
        print(f"Processing URL: {url}")
        constituency_id = url.split('-')[-1].split('S')[0]
        output_file = output_dir / f"constituency_{constituency_id}.html"
        html_content = fetch_html(url, output_file)
        if html_content:
            constituency_data = extract_data_from_html(html_content)
            for entry in constituency_data:
                if entry["constituency_id"] not in unique_constituencies:
                    unique_constituencies.add(entry["constituency_id"])
                    all_data.append(entry)
    return all_data

# Main page URL for scraping
main_page_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"

all_constituency_data = scrape_all_data(main_page_url)

if all_constituency_data:
    json_file = "constituency_data.json"
    try:
        # Sort data by Constituency ID before saving
        sorted_data = sorted(all_constituency_data, key=lambda x: int(x["constituency_id"]))
        with open(json_file, mode="w", encoding="utf-8") as file:
            json.dump(sorted_data, file, indent=4, ensure_ascii=False)
        print(f"Scraping completed successfully. Data saved to {json_file}.")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")
else:
    print("No data found to save.")

