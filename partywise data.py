import requests
from pathlib import Path
from bs4 import BeautifulSoup
import csv

def fetch_scrape_sort_save(url, html_dir, csv_file_path):
    """
    Fetch HTML content from a URL, scrape data, sort it, and save to a CSV file.

    Parameters:
        url (str): The webpage URL to scrape.
        html_dir (Path): Directory to save the HTML file.
        csv_file_path (str): Path to save the sorted CSV file.
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    }

    html_file = html_dir / f"{url.split('/')[-1]}"  

    #
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

    # Scrape and process data
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if table:
        print("Scraping and sorting party-wise results...")
        rows = table.find_all("tr")
        data = []

        # Prepare headers for the CSV
        headers = ["Party Name", "Seats Won", "Seats Leading", "Total Seats", "Link"]

        # Process table rows (skip header)
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) >= 4:
                party_tag = columns[0].find("a")
                if party_tag:
                    party_name = party_tag.text.strip()
                    party_link = party_tag["href"]
                    full_link = f"https://results.eci.gov.in/ResultAcGenNov2024/{party_link}"
                else:
                    party_name = columns[0].text.strip()
                    full_link = None

                # Convert seat numbers to integers for sorting
                won_seats = int(columns[1].text.strip()) if columns[1].text.strip().isdigit() else 0
                leading_seats = int(columns[2].text.strip()) if columns[2].text.strip().isdigit() else 0
                total_seats = int(columns[3].text.strip()) if columns[3].text.strip().isdigit() else 0

                # Append the data row
                data.append([party_name, won_seats, leading_seats, total_seats, full_link or "N/A"])

        # Sort data by total seats (descending) and then by party name (alphabetically)
        data.sort(key=lambda x: (-x[3], x[0]))

        # Save to CSV
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)  
            writer.writerows(data)  
        print(f"Party-wise results saved to: {csv_file_path}")
    else:
        print("No table found in the HTML content.")


output_dir = Path("html_files") 
output_dir.mkdir(exist_ok=True)

webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
csv_file_path = "partywiseresults_sorted.csv"


fetch_scrape_sort_save(webpage_url, output_dir, csv_file_path)
