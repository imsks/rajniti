import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv


output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_html(url, output_file):
    if output_file.exists():
        print(f"Reading cached file: {output_file}")
        return output_file.read_text(encoding="utf-8")
    else:
        print(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            output_file.write_text(html_content, encoding="utf-8")
            return html_content
        else:
            print(f"Failed to fetch {url}. Status code: {response.status_code}")
            return None

def extract_data_from_html(html_content):
    """
    Extract constituency data with S.No, Constituency, Winning Candidate, Total Votes, and Margin from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Adjust this based on the structure of the page

    if not table:
        print("No table found on the page.")
        return []
    
    rows = table.find_all('tr')[1:]  # Skip the header row
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5:  # Adjust based on the number of columns
            s_no = cells[0].text.strip()
            constituency = cells[1].text.strip()
            winning_candidate = cells[2].text.strip()
            total_votes = cells[3].text.strip()
            margin = cells[4].text.strip()
            data.append({
                "S.No": s_no,
                "Constituency": constituency,
                "Winning Candidate": winning_candidate,
                "Total Votes": total_votes,
                "Margin": margin
            })
    return data

def scrape_all_data(constituency_urls):
    """
    Scrape all constituency data from the list of URLs.
    """
    all_data = []
    for url in constituency_urls:
        constituency_id = url.split('-')[-1].split('S')[0]  # Extract unique ID
        output_file = output_dir / f"constituency_{constituency_id}.html"
        html_content = fetch_html(url, output_file)
        if html_content:
            constituency_data = extract_data_from_html(html_content)
            all_data.extend(constituency_data)
    return all_data

# List of URLs for scraping
constituency_urls = [
    "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
    # Add other URLs as needed
]

# Scrape data and save to CSV
all_constituency_data = scrape_all_data(constituency_urls)
csv_file = "constituency_data.csv"
with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["S.No", "Constituency", "Winning Candidate", "Total Votes", "Margin"])
    writer.writeheader()
    writer.writerows(all_constituency_data)

print(f"Scraping completed. Data saved to {csv_file}.")
