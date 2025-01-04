import requests
from bs4 import BeautifulSoup


webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm"  # Replace with the actual URL


headers =  {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/index.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}


response = requests.get(webpage_url, headers=headers)

if response.status_code == 200:
   
    soup = BeautifulSoup(response.text, 'html.parser')
    
   
    target_div = soup.find("div", {"class": "custom-table"}) 
    if target_div:
        print("Data in <div>:", target_div.text.strip())  
    else:
        print("Target <div> not found.")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
