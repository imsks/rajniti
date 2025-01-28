import requests
from bs4 import BeautifulSoup
import time
import random

# Define the URL and headers
webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/index.htm",
}

# Rate limiter configuration
MIN_DELAY = 3  # Minimum delay in seconds between requests
MAX_DELAY = 7  # Maximum delay in seconds between requests
MAX_RETRIES = 3  # Maximum retries for failed requests

# User-Agent rotation pool
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Linux; Android 10; SM-A505F)",
]

# Function to fetch data with retries and rate control
def fetch_page_with_rate_control(url, headers):
    """Fetch a page with retries."""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Too Many Requests
                print("Too many requests (429). Increasing delay...")
                time.sleep(60)  # Wait longer if rate-limited
            else:
                print(f"Non-200 status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)  # Exponential backoff

    print("Max retries reached. Skipping this request.")
    return None

# Function to scrape data
def scrape_data():
    """Scrape data from the specified webpage."""
    print(f"Fetching data from {webpage_url}")

    # Rotate User-Agent for each request
    headers["User-Agent"] = random.choice(user_agents)

    # Fetch the webpage
    response = fetch_page_with_rate_control(webpage_url, headers)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the target <div> section
        anchor_tags = soup.find_all("a")  # Find all <a> tags
    if anchor_tags:
        print("Found the following anchor tags and href attributes:")
        for anchor in anchor_tags:
            href = anchor.get("href")  # Get href attribute
            text = anchor.text.strip()  # Get the text inside the <a> tag
            if href:
                print(f"Text: {text}, Href: {href}")
    else:
        print("No anchor tags found.")
    

    # Introduce a random delay to mimic human behavior
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

# Main function to run the scraper
def main():
    """Main function to control the scraping process."""
    for _ in range(5):  # Example: Scrape the same page 5 times (or replace with multiple URLs)
        scrape_data()

if __name__ == "__main__":
    main()