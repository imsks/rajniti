import requests
from bs4 import BeautifulSoup
import time
import json
import re

def clean_votes(votes):
    if votes:
        cleaned_votes = re.sub(r'[+()"]', '', votes).strip()
        return cleaned_votes
    return None

def clean_margin(margin):
    if margin:
        margin = margin.replace(')', '').strip()
        if margin.startswith('+'):
            margin = f"({margin}"
    return margin

def get_with_retry(url, headers, retries=3, timeout=20):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                print("Max retries reached, skipping.")
                return None

def scrape_candidates_data(start, end, base_url, headers, output_file):
    all_data = []
    for i in range(start, end + 1):
        url = f"{base_url}candidateswise-S13{i}.htm"
        response = get_with_retry(url, headers, retries=3, timeout=20)
        if response is None:
            continue
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            candidates = soup.find_all("div", class_="cand-box")
            for candidate in candidates:
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
                votes_and_margin = None
                if status_div and len(status_div.find_all("div")) > 1:
                    votes_and_margin = status_div.find_all("div")[1].get_text(strip=True)
                votes, margin = None, None
                if votes_and_margin:
                    split_data = votes_and_margin.split(" ")
                    votes = split_data[0] if split_data else None
                    margin = split_data[1] if len(split_data) > 1 else None
                votes = clean_votes(votes)
                margin = clean_margin(margin)
                nme_prty_div = candidate.find("div", class_="nme-prty")
                name = nme_prty_div.find("h5").get_text(strip=True) if nme_prty_div and nme_prty_div.find("h5") else None
                party = nme_prty_div.find("h6").get_text(strip=True) if nme_prty_div and nme_prty_div.find("h6") else None
                image_url = None
                img_tag = candidate.find("img")
                if img_tag and "src" in img_tag.attrs:
                    img_src = img_tag["src"].strip()
                    image_url = base_url + img_src if not img_src.startswith("http") else img_src
                all_data.append({
                    "Constituency Code": f"S13-{i}",
                    "Name": name,
                    "Party": party,
                    "Status": status,
                    "Votes": votes,
                    "Margin": margin,
                    "Image URL": image_url
                })
        except Exception as e:
            print(f"Error processing {url}: {e}")
        time.sleep(5)
    if all_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {output_file}.")
    else:
        print("No data scraped.")

base_url = "https://results.eci.gov.in/ResultAcGenNov2024/"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
}

output_file = "VS_election_with_images.json"
scrape_candidates_data(start=1, end=288, base_url=base_url, headers=headers, output_file=output_file)
