import requests
from bs4 import BeautifulSoup
import time
import json
import re

def clean_votes(votes):
    if votes:
        # Remove unwanted characters such as '(+' , '(-', '("', and ')'
        cleaned_votes = re.sub(r'[+()"]', '', votes).strip()
        return cleaned_votes
    return None

def clean_margin(margin):
    """Cleans the 'Margin' field by ensuring '(' appears before the margin value, but removes ')'."""
    if margin:
        # Remove closing parenthesis if it exists
        margin = margin.replace(')', '').strip()
        # Add opening parenthesis '(' if margin starts with '+'
        if margin.startswith('+'):
            margin = f"({margin}"
    return margin

def get_with_retry(url, headers, retries=3, timeout=20):
    """Attempt to fetch a URL with retries in case of a timeout or other errors."""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Check if request was successful
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                print("Max retries reached, skipping.")
                return None

def scrape_candidates_data(start, end, base_url, headers, output_file):
    """Scrapes candidate data and saves it to a JSON file."""
    all_data = []

    for i in range(start, end + 1):
        url = f"{base_url}candidateswise-S13{i}.htm"
        response = get_with_retry(url, headers, retries=3, timeout=20)

        if response is None:
            continue  # Skip this URL if it couldn't be fetched

        try:
            # Parse the HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            candidates = soup.find_all("div", class_="cand-info")

            # Extract data for each candidate
            for candidate in candidates:
                # Extract the status
                status_div = candidate.find("div", class_="status")
                status = None
                if status_div:
                    status_class = status_div.get("class", [])
                    if "won" in status_class:
                        status = "Won"
                    elif "lost" in status_class:
                        status = "Lost"
                    elif "nota" in status_class:
                        status = "NOTA"

                # Extract votes and margin
                votes_and_margin = None
                if status_div and len(status_div.find_all("div")) > 1:
                    votes_and_margin = status_div.find_all("div")[1].get_text(strip=True)

                # Handle votes and margin extraction
                votes, margin = None, None
                if votes_and_margin:
                    split_data = votes_and_margin.split(" ")
                    votes = split_data[0] if split_data else None
                    margin = split_data[1] if len(split_data) > 1 else None

                # Clean the votes and margin
                votes = clean_votes(votes)
                margin = clean_margin(margin)  # Apply margin cleaning

                # Extract name and party
                nme_prty_div = candidate.find("div", class_="nme-prty")
                name = nme_prty_div.find("h5").get_text(strip=True) if nme_prty_div and nme_prty_div.find("h5") else None
                party = nme_prty_div.find("h6").get_text(strip=True) if nme_prty_div and nme_prty_div.find("h6") else None

                # Append the data for this candidate
                all_data.append({
                    "Constituency Code": f"S13-{i}",
                    "Name": name,
                    "Party": party,
                    "Status": status,
                    "Votes": votes,
                    "Margin": margin
                })

        except Exception as e:
            print(f"Error processing {url}: {e}")
        
        # Sleep to avoid overwhelming the server
        time.sleep(5)

    # Save data to a JSON file
    if all_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {output_file}.")
    else:
        print("No data scraped.")

# Configuration for scraping
base_url = "https://results.eci.gov.in/ResultAcGenNov2024/"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
}

# Run the scraping function
output_file = "VS_election.json"  # The output file for saving the data
scrape_candidates_data(start=1, end=288, base_url=base_url, headers=headers, output_file=output_file)
