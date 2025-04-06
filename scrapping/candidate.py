import requests
from bs4 import BeautifulSoup
import time
import json
import re


def clean_votes(votes):
    return re.sub(r'[+()"\s]', '', votes) if votes else None

def clean_margin(margin):
    if margin:
        margin = margin.replace(')', '').strip()
        return f"({margin}" if margin.startswith('+') else margin
    return None

def get_with_retry(url, headers, retries=3, timeout=20):
    for attempt in range(retries):
        try:
            print(f"[INFO] Fetching: {url}")
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"[Retry {attempt + 1}] Failed: {e}")
            time.sleep(3)
    print("[ERROR] Max retries reached. Skipping...")
    return None

def scrape_candidates_data(start, end, base_url, headers, output_file):
    all_data = []
    for i in range(start, end + 1):
        url = f"{base_url}candidateswise-U05{i}.htm"
        response = get_with_retry(url, headers)
        if response is None:
            continue

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            candidates = soup.find_all("div", class_="cand-box")

            for candidate in candidates:
                status_div = candidate.find("div", class_="status")
                status_class = status_div.get("class", []) if status_div else []

                status = None
                if "won" in status_class:
                    status = "Won"
                elif "lost" in status_class:
                    status = "Lost"
                elif "nota" in status_class:
                    status = "NOTA"

                votes, margin = None, None
                if status_div and len(status_div.find_all("div")) > 1:
                    vtext = status_div.find_all("div")[1].get_text(strip=True)
                    split_data = vtext.split(" ")
                    votes = clean_votes(split_data[0]) if split_data else None
                    margin = clean_margin(split_data[1]) if len(split_data) > 1 else None

                nme_prty_div = candidate.find("div", class_="nme-prty")
                name = nme_prty_div.find("h5").get_text(strip=True) if nme_prty_div else None
                party = nme_prty_div.find("h6").get_text(strip=True) if nme_prty_div else None

                img_tag = candidate.find("img")
                img_src = img_tag["src"].strip() if img_tag and "src" in img_tag.attrs else None
                image_url = base_url + img_src if img_src and not img_src.startswith("http") else img_src

                all_data.append({
                    "Constituency Code": f"DL-{i}",
                    "Name": name,
                    "Party": party,
                    "Status": status,
                    "Votes": votes,
                    "Margin": margin,
                    "Image URL": image_url
                })

        except Exception as e:
            print(f"[ERROR] Parsing failed for {url}: {e}")

        time.sleep(2)

    if all_data:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)
        print(f"[SUCCESS] Data saved to {output_file}.")
    else:
        print("[INFO] No data scraped.")

# ==== Configuration ====
base_url = "https://results.eci.gov.in/ResultAcGenFeb2025/"
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Referer": "https://results.eci.gov.in/ResultAcGenFeb2025/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
}

output_file = "DL_candidate_data.json"
scrape_candidates_data(start=1, end=70, base_url=base_url, headers=headers, output_file=output_file)