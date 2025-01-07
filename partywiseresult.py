import requests
from pathlib import Path
from bs4 import BeautifulSoup

# Directory to save HTML files
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
    """
    Fetch HTML content from the URL and save it to a file.
    If the file exists, read from it instead of making a request.
    """
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

def scrape_inner_data(full_link):
    """
    Fetch and scrape data from the full link.
    """
    print(f"Fetching data from: {full_link}")
    try:
        response = requests.get(full_link, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Example: Extract table data from the inner page
            table = soup.find("table")
            if table:
                print("Data from the full link:")
                for row in table.find_all("tr"):
                    columns = row.find_all("td")
                    row_data = [col.get_text(strip=True) for col in columns]
                    print(row_data)
            else:
                print("No table found in the full link.")
        else:
            print(f"Failed to fetch data from {full_link}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {full_link}: {e}")

def scrape_constituency_data(html_content):
    """
    Scrape constituency data from the given HTML content.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Locate the table containing constituency data
    table = soup.find("table")

    if table:
        print("Scraping Constituency Data...\n")
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) > 1:  # Ensure there's at least one column to scrape
                constituency_name = columns[1].get_text(strip=True)  # Extract the text of the second column
                constituency_tag = columns[1].find("a")  # Find anchor tag in the second column

                if constituency_tag and 'href' in constituency_tag.attrs:
                    href = constituency_tag["href"]  # Extract href attribute
                    full_link = f"https://results.eci.gov.in/ResultAcGenNov2024/{href}"
                else:
                    full_link = None

                print(f"Constituency: {constituency_name}")
                if full_link:
                    print(f"Link: {full_link}")
                    scrape_inner_data(full_link)  # Fetch and scrape data from the full link
                else:
                    print("No Link Available")
                print("--------------------------")
    else:
        print("No table found in the HTML content.")

# Path to save the HTML file
output_file = output_dir / "partywiseresult.html"  # Updated file name to match the new URL

# Fetch or load the HTML file and scrape the data
html_content = fetch_and_save_html(webpage_url, output_file)
if html_content:
    scrape_constituency_data(html_content)
