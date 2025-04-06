import requests

def load_html(url, html_file):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://results.eci.gov.in/ResultAcGenFeb2025/index.htm",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "DNT": "1",
}


    if html_file.exists():
        print(f"[CACHE] Reading HTML from: {html_file}")
        return html_file.read_text(encoding="utf-8")

    try:
        print(f"[FETCH] Requesting URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            html_file.write_text(response.text, encoding="utf-8")
            print(f"[SAVE] HTML saved to: {html_file}")
            return response.text
        else:
            print(f"[ERROR] Failed to fetch: {url}")
    except requests.RequestException as e:
        print(f"[ERROR] Request exception: {e}")
    return None

def parse_party_table(table):
    rows = table.find_all("tr")[1:]  # skip header
    data = []

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 4:
            party_tag = cols[0].find("a")
            full_name = party_tag.text.strip() if party_tag else cols[0].text.strip()
            party_name, symbol = (full_name.split(" - ", 1) + ["N/A"])[:2]

            try:
                total_seats = int(cols[3].text.strip())
            except ValueError:
                total_seats = 0

            data.append({
                "party_name": party_name,
                "symbol": symbol,
                "total_seats": total_seats
            })
    return data

def sort_party_data(data):
    return sorted(data, key=lambda x: (-x["total_seats"], x["party_name"]))
