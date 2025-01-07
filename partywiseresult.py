import requests
from pathlib import Path
from bs4 import BeautifulSoup


output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)  # Create directory if it doesn't exist

# URL for the specific page
webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

def fetch_and_save_html(url, output_file):
  
    if output_file.exists():
        print(f"Reading HTML content from cached file: {output_file}")
        html_content = output_file.read_text(encoding="utf-8")
    else:
        print(f"Fetching URL: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"Received status code: {response.status_code}")

            if response.status_code == 200:
                html_content = response.text
                output_file.write_text(html_content, encoding="utf-8")
                print(f"HTML saved to: {output_file}")
            else:
                print(f"Failed to fetch {url}. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    return html_content

def scrape_party_results(html_content):
  
    soup = BeautifulSoup(html_content, "html.parser")

    # Locate the table containing party-wise results
    table = soup.find("table")

    if table:
        print("Scraping Party-Wise Results...\n")
        rows = table.find_all("tr")
        
        # Skipping the header row (assumed to be the first row)
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) >= 4:  # Check if there are enough columns (Party, Won, Leading, Total)
                # Extract the party name (first column, which is in anchor tag)
                party_tag = columns[0].find("a")
                if party_tag:
                    party_name = party_tag.text.strip()
                    party_link = party_tag["href"]
                    full_link = f"https://results.eci.gov.in/ResultAcGenNov2024/{party_link}"
                else:
                    party_name = columns[0].text.strip()
                    full_link = None

                # Extract the number of seats won, leading, and total (second, third, and fourth columns)
                won_seats = columns[1].text.strip()
                leading_seats = columns[2].text.strip()
                total_seats = columns[3].text.strip()

                print(f"Party: {party_name}")
                print(f"Seats Won: {won_seats}")
                print(f"Seats Leading: {leading_seats}")
                print(f"Total Seats: {total_seats}")
                if full_link:
                    print(f"Link: {full_link}")
                print("--------------------------")
    else:
        print("No table found in the HTML content.")


output_file = output_dir / "partywiseresult-S13.html"  # Save the file with a suitable name


html_content = fetch_and_save_html(webpage_url, output_file)
if html_content:
    scrape_party_results(html_content)
