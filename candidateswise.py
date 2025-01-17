import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_candidates_data(start, end, base_url, headers, output_file):
    """Scrapes candidate data from a range of URLs and saves it to a sorted CSV."""
    data = []

    for i in range(start, end + 1):
        url = f"{base_url}candidateswise-S13{i}.htm"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            box_wrappers = soup.find_all("div", class_="box-wraper box-boarder")

            if box_wrappers:
                for box in box_wrappers:
                    content = box.get_text(strip=True)
                    data.append([content])
            else:
                print(f"No data found for URL: {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    # Save data to CSV
    if data:
        df = pd.DataFrame(data, columns=["Content"])
        df.sort_values(by="Content", ascending=True, inplace=True)
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"Data saved to {output_file}.")
    else:
        print("No data scraped.")

# Configuration
base_url = "https://results.eci.gov.in/ResultAcGenNov2024/"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
}

output_file = "candidates_data_sorted.csv"

# Run scraper for the range 1 to 288
scrape_candidates_data(start=1, end=288, base_url=base_url, headers=headers, output_file=output_file)
