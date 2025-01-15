import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_and_save_sorted_data(urls, headers, output_file):
    data = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all divs with class "box-wraper box-boarder"
                box_wrapper = soup.find_all("div", class_="box-wraper box-boarder")

                if box_wrapper:
                    for box in box_wrapper:
                        content = box.get_text(strip=True)
                        data.append([content])
                else:
                    print(f"No elements found with the class 'box-wraper box-boarder' at {url}")
            else:
                print(f"Failed to fetch the URL {url}. Status code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

    # Convert the data to a pandas DataFrame
    if data:
        df = pd.DataFrame(data, columns=["Content"])

        # Sort the DataFrame based on the "Content" column
        df_sorted = df.sort_values(by="Content", ascending=True)

        # Save the sorted DataFrame to a CSV file
        df_sorted.to_csv(output_file, index=False, encoding="utf-8")

        print(f"Sorted data saved to {output_file}.")
        print("\nPreview of the sorted data:")
        print(df_sorted.head())
    else:
        print("No data scraped.")

# Example usage
urls = [
    "https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S131.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S135.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1310.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1314.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1316.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1318.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1320.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1322.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1359.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1361.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1379.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1384.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1386.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1387.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1393.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13100.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13101.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13104.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13105.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13107.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13108.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13110.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13112.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13113.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13115.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13130.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13131.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13134.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13138.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13140.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13144.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13146.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13147.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13154.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13157.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13166.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13168.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13173.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13174.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13189.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13192.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13194.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13202.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13217.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13221.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13243.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13257.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13261.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13263.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13266.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13267.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13269.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13270.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13272.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13275.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13276.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13286.htm",
    
]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

output_file = "scraped_sorted_data.csv"
scrape_and_save_sorted_data(urls, headers, output_file)
