import json
import re
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

URL = "https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-369.htm"
OUTPUT_FILE = "output/constituencies_369.json"

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

def extract_constituency_data(driver, url):
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    table = soup.find("table")
    if not table:
        print("[ERROR] No table found!")
        return []

    rows = table.find_all("tr")[1:]  # Skip the header row
    results = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 3:
            constituency_text = cols[2].get_text(strip=True)
            match = re.match(r"(.*)\((\d+)\)", constituency_text)
            if not match:
                continue

            constituency_name = match.group(1).strip()
            cid = match.group(2).strip()
            state_id = cid[:2] if cid.isdigit() else "NA"

            results.append({
                "constituency_name": constituency_name,
                "constituency_id": f"S{state_id}-{cid}",
                "state_id": state_id
            })

    return results

def main():
    Path("output").mkdir(exist_ok=True)
    driver = setup_driver()

    try:
        print("[INFO] Scraping:", URL)
        data = extract_constituency_data(driver, URL)
        if data:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"[OK] Scraped {len(data)} constituencies")
            print(f"[OK] Saved to: {OUTPUT_FILE}")
        else:
            print("[INFO] No data found in the table.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
