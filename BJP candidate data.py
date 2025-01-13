import requests
from bs4 import BeautifulSoup
import csv

urls = [
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S132.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S133.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S136.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S137.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S138.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S139.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1311.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1312.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1313.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1317.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1319.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1321.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1323.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1326.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1327.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1328.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1331.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1332.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1334.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1335.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1336.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1339.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1341.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1342.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1343.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1344.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1345.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1346.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1347.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1348.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1349.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1350.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1352.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1353.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1354.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1355.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1358.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1364.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1365.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1366.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1368.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1370.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1371.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1372.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1374.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1375.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1377.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1380.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1382.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1383.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1385.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1389.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1390.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1391.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1394.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1395.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1399.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13102.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13103.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13106.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13109.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13111.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13116.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13118.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13123.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13124.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13125.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13129.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13132.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13133.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13136.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13139.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13141.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13142.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13143.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13145.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13148.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13150.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13151.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13152.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13153.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13155.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13160.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13161.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13163.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13165.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13167.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13169.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13170.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13177.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13179.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13180.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13185.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13187.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13188.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13190.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13191.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13199.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13205.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13207.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13209.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13210.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13211.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13212.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13214.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13215.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13218.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13222.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13223.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13226.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13231.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13232.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13234.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13238.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13239.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13241.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13248.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13249.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13250.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13251.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13252.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13258.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13259.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13260.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13262.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13268.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13274.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13279.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13281.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13282.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13284.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13288.htm",
]

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}


data = []

for url in urls:
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

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

data.sort(key=lambda x: x[0])  

if data:
    csv_file = "scraped_sorted_data.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Content"]) 
        writer.writerows(data)  

    print(f"Sorted data saved to {csv_file}.")
else:
    print("No data scraped.")
