from flask import Flask, request, jsonify
from pathlib import Path
import csv
import os
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# Directory for saving HTML files
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)

# Function to scrape and save data
def fetch_scrape_sort_save(url, html_dir, csv_file_path):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    }

    html_file = html_dir / f"{url.split('/')[-1]}"  # Save HTML file locally

    # Fetch and cache the HTML content
    if html_file.exists():
        html_content = html_file.read_text(encoding="utf-8")
    else:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                html_file.write_text(html_content, encoding="utf-8")
            else:
                return {"error": f"Failed to fetch {url}. Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Error fetching {url}: {e}"}

    # Scrape and process data
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if table:
        rows = table.find_all("tr")
        data = []

        # Prepare headers for the CSV
        headers = ["Party Name", "Symbol", "Total Seats"]

        # Process table rows (skip header)
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) >= 4:
                party_tag = columns[0].find("a")
                if party_tag:
                    party_name_full = party_tag.text.strip()
                else:
                    party_name_full = columns[0].text.strip()

                if " - " in party_name_full:
                    party_name, symbol = party_name_full.split(" - ", 1)
                else:
                    party_name = party_name_full
                    symbol = "N/A"

                total_seats = int(columns[3].text.strip()) if columns[3].text.strip().isdigit() else 0

                # Append the data row
                data.append([party_name, symbol, total_seats])

        data.sort(key=lambda x: (-x[2], x[0]))

        # Save to CSV
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(headers)  # Write headers
            writer.writerows(data)  # Write rows
        return {"message": f"Data scraped and saved to {csv_file_path}"}
    else:
        return {"error": "No table found in the HTML content."}

# Flask API endpoints

@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL is required."}), 400

    csv_file_path = data.get("csv_file_path", "partywiseresults_sorted_with_symbols.csv")
    result = fetch_scrape_sort_save(url, output_dir, csv_file_path)
    return jsonify(result)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    file_name = data.get("file_name")
    file_path = output_dir / file_name

    if file_path.exists():
        return jsonify({"message": f"{file_name} exists."})
    else:
        return jsonify({"error": f"{file_name} does not exist."}), 404

@app.route("/insert", methods=["POST"])
def insert():
    data = request.json
    file_name = data.get("file_name")
    file_path = output_dir / file_name

    if not file_path.exists():
        return jsonify({"error": f"{file_name} does not exist. Please scrape the data first."}), 404

    # Here, you can implement additional logic to insert the data into a database.
    return jsonify({"message": f"{file_name} processed for insertion."})

if __name__ == "__main__":
    app.run(debug=True)
