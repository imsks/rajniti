import requests
from bs4 import BeautifulSoup

url = "https://results.eci.gov.in/ResultAcGenNov2024/index.htm"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/index.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    print("Request successful. Parsing data...")

    title = soup.title.text
    print(f"Page Title: {title}")
    
    state_cards = soup.select(".item .state-title")
    for card in state_cards:
        state_name = card.text.strip()
        print(f"State: {state_name}")
else:
    print(f"Failed to fetch the webpage. Status Code: {response.status_code}")




