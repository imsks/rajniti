import requests
from bs4 import BeautifulSoup
from pathlib import Path
import csv
import re


output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

def fetch_html(url, output_file):
    """
    Fetch HTML content from a URL using a session and cache it locally.
    """
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
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching {url}: {http_err}")
        return None
    except Exception as err:
        print(f"Error occurred while fetching {url}: {err}")
        return None

def extract_links_from_main_page(main_page_url):
    """
    Extract all links matching the pattern `partywisewinresult-<ID>S13.htm` from the main page.
    """
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
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while accessing main page {main_page_url}: {http_err}")
        return []
    except Exception as err:
        print(f"Error occurred while accessing main page {main_page_url}: {err}")
        return []

def extract_data_from_html(html_content):
    """
    Extract constituency data with S.No, Constituency, Winning Candidate, Total Votes, and Margin from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')  # Adjust based on the structure of the page

    if not table:
        print("No table found on the page.")
        return []
    
    rows = table.find_all('tr')[1:]  
    data = []
    for row in rows:
        cells = row.find_all('td')
        if len(cells) >= 5: 
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

def scrape_all_data(main_page_url):
    """
    Scrape all constituency data from links ending with `S13.htm`.
    """
    print(f"Extracting links from the main page: {main_page_url}")
    links = extract_links_from_main_page(main_page_url)
    if not links:
        print("No related links found.")
        return []

    all_data = []
    for url in links:
        print(f"Processing URL: {url}")
        constituency_id = url.split('-')[-1].split('S')[0]
        output_file = output_dir / f"constituency_{constituency_id}.html"
        html_content = fetch_html(url, output_file)
        if html_content:
            constituency_data = extract_data_from_html(html_content)
            all_data.extend(constituency_data)
    return all_data

# Main page URL for scraping
main_page_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"


all_constituency_data = scrape_all_data(main_page_url)

if all_constituency_data:
    csv_file = "constituency_data.csv"
    try:
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["S.No", "Constituency", "Winning Candidate", "Total Votes", "Margin"])
            writer.writeheader()
            writer.writerows(all_constituency_data)
        print(f"Scraping completed successfully. Data saved to {csv_file}.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
else:
    print("No data found to save.")

