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
     "https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1315.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1324.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1338.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1360.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1363.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1369.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1381.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1388.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1392.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1398.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13117.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13119.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13120.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13121.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13122.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13126.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13127.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13135.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13172.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13193.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13196.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13198.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13200.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13201.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13203.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13204.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13206.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13213.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13216.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13219.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13224.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13225.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13228.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13229.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13233.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13236.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13237.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13255.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13256.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13265.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13273.htm",
]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

output_file = "congscraped_sorted_data.csv"
scrape_and_save_sorted_data(urls, headers, output_file)
