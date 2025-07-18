from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
from pathlib import Path
import time

def fetch_html_from_main_link(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print(f"[INFO] Opening: {url}")
    driver.get(url)

    time.sleep(4)  # Let the JavaScript render the table

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()
    return soup

def extract_partywise_table(soup):
    table = soup.find("table")
    if not table:
        print("[ERROR] No party table found.")
        return []

    results = []
    rows = table.find_all("tr")[1:]  # Skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            full_name = cols[0].text.strip()
            total = int(cols[3].text.strip())

            if " - " in full_name:
                party_name, symbol = full_name.rsplit(" - ", 1)
            else:
                party_name = full_name
                symbol = ""

            results.append({
                "party_name": party_name,
                "symbol": symbol,
                "total_seats": total
            })

    return sorted(results, key=lambda x: x["total_seats"], reverse=True)

if __name__ == "__main__":
    url = "https://results.eci.gov.in/PcResultGenJune2024/index.htm#"
    output_file = Path("partywise_status.json")

    soup = fetch_html_from_main_link(url)
    data = extract_partywise_table(soup)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"[INFO] Party-wise result status saved to: {output_file}")

