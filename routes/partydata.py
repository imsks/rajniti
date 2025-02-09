from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/RAJNEETI'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Directory for saving HTML files
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)

# JSON file to save the sorted results
json_file_path = "party_results.json"

class PartyResults(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String(255), nullable=False, unique=True)
    symbol = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

def fetch_scrape_sort_save_json(url, html_dir, json_file_path):
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    }

    html_file = html_dir / f"{url.split('/')[-1]}"
    
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

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if table:
        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) >= 4:
                party_tag = columns[0].find("a")
                party_name_full = party_tag.text.strip() if party_tag else columns[0].text.strip()

                if " - " in party_name_full:
                    party_name, symbol = party_name_full.split(" - ", 1)
                else:
                    party_name, symbol = party_name_full, "N/A"

                total_seats = int(columns[3].text.strip()) if len(columns) > 3 and columns[3].text.strip().isdigit() else 0
                data.append({"party_name": party_name, "symbol": symbol, "total_seats": total_seats})

        data.sort(key=lambda x: (-x["total_seats"], x["party_name"]))

        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        return {"message": "Scraping successful", "data": data}
    else:
        return {"error": "No table found in the HTML content."}

@app.route("/scrape", methods=["GET"])
def scrape():
    webpage_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
    result = fetch_scrape_sort_save_json(webpage_url, output_dir, json_file_path)
    return jsonify(result)

@app.route("/verify", methods=["GET"])
def verify():
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)
        return jsonify({"message": "Data verification successful", "data": data})
    except FileNotFoundError:
        return jsonify({"error": "JSON file not found. Please run /scrape first."}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON file."}), 500

@app.route("/insert", methods=["POST"])
def insert_data():
    try:
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            data = json.load(json_file)

        for entry in data:
            existing_record = PartyResults.query.filter_by(party_name=entry['party_name']).first()
            if not existing_record:
                record = PartyResults(
                    party_name=entry['party_name'],
                    symbol=entry['symbol'],
                    total_seats=entry['total_seats']
                )
                db.session.add(record)
        
        db.session.commit()
        return jsonify({"message": "Data successfully inserted into PostgreSQL"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
