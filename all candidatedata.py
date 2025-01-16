import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_and_save_sorted_data(urls, headers, output_file):
    """Scrapes data, sorts, and saves to CSV."""
    data = []

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            soup = BeautifulSoup(response.content, 'html.parser')

            box_wrapper = soup.find_all("div", class_="box-wraper box-boarder")

            if box_wrapper:
                for box in box_wrapper:
                    content = box.get_text(strip=True)
                    data.append([content])
            else:
                print(f"No elements found at {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
        except Exception as e:
            print(f"Error parsing {url}: {e}")

    if data:
        df = pd.DataFrame(data, columns=["Content"])
        df_sorted = df.sort_values(by="Content", ascending=True)
        df_sorted.to_csv(output_file, index=False, encoding="utf-8")

        print(f"Data saved to {output_file}.")
        print(df_sorted.head())
    else:
        print("No data scraped.")

# Combined URLs
all_urls = [
    
   # Nationalist Congress Party - NCP
   
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

  # SHIV SENA (SHS)
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

 # Second set of URLs (BJP)

"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S132.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S133.htm",
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

#shiv sena (udhav balasahab thakrey)
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1325.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1329.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1340.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1376.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1396.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13156.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13158.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13159.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13164.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13175.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13176.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13181.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13182.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13183.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13184.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13197.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13240.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13242.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13246.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13264.htm",

#INC (INDIAN NATIONAL CONGRESS)
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S134.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1330.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1333.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1351.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1356.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1357.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1362.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1367.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1373.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1378.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13162.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13178.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13186.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13220.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13235.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13285.htm",

# Nationalist Congress Party – Sharadchandra Pawar - NCPSP
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13149.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13208.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13227.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13230.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13244.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13245.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13247.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13254.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13283.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13287.htm",

# Samajwadi Party (SP)

"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13137.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13171.htm",

# Jan Surajya Shakti - JSS
    
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13277.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13278.htm",
    
 # Rashtriya Yuva Swabhiman Party - RSHYVSWBHM
 "https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1337.htm",
    
#Rashtriya Samaj Paksha - RSPS
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S1397.htm",

#All India Majlis-E-Ittehadul Muslimeen - AIMIM	
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13114.htm",

#Communist Party of India (Marxist) - CPI(M)
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13128.htm",
	
#Peasants And Workers Party of India - PWPI	
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13253.htm",

#Rajarshi Shahu Vikas Aghadi - RSVA
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13280.htm",
	
#Independent - IND
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13195.htm",
"https://results.eci.gov.in/ResultAcGenNov2024/candidateswise-S13271.htm",
]


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
}

output_file = "all_scraped_sorted_data.csv" # one output file
scrape_and_save_sorted_data(all_urls, headers, output_file)
