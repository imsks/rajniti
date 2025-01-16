from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import io  # Import for in-memory CSV

app = Flask(__name__)

def scrape_data(urls, headers):
    """Scrapes data from URLs and returns it as a list of lists."""
    data = []
    for url in urls:
        try:
            print(f"Scraping: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            time.sleep(1)

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
            return jsonify({"error": f"Error fetching {url}: {str(e)}", "url": url}), response.status_code if hasattr(response, 'status_code') else 500
        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return jsonify({"error": f"Error parsing {url}: {str(e)}", "url": url}), 500

    return data

@app.route('/scrape', methods=['GET'])
def scrape_route():
    urls_param = request.args.get('urls') 
    if not urls_param:
        return jsonify({"error": "No 'urls' parameter provided. Provide comma separated urls"}), 400
    
    urls = urls_param.split(',')

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Cache-Control": "max-age=0",
        "Referer": "https://results.eci.gov.in/ResultAcGenNov2024/partywisewinresult-369S13.htm",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    }
    scraped_data = scrape_data(urls, headers)

    if isinstance(scraped_data, tuple): #check if error
        return scraped_data

    if scraped_data:
        df = pd.DataFrame(scraped_data, columns=["Content"])
        df_sorted = df.sort_values(by="Content", ascending=True)

        
        csv_buffer = io.StringIO()
        df_sorted.to_csv(csv_buffer, index=False, encoding="utf-8")
        csv_content = csv_buffer.getvalue()

        return jsonify({"csv_data": csv_content}), 200 
    else:
        return jsonify({"message": "No data scraped from the provided URLs."}), 200

if __name__ == '__main__':
    app.run(debug=True)
