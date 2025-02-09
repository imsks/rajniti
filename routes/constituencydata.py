from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import json
import re

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost:5432/RAJNEETI'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Directory for saving HTML files
output_dir = Path("html_files")
output_dir.mkdir(exist_ok=True)

# JSON file path
constituency_json_file = "constituency.json"

class ConstituencyResults(db.Model):
    constituency_id = db.Column(db.String(50), primary_key=True)
    constituency_name = db.Column(db.String(255), nullable=False)
    state_id = db.Column(db.String(10), nullable=False)

def fetch_html(url, output_file):
    if output_file.exists():
        return output_file.read_text(encoding="utf-8")
    else:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        output_file.write_text(response.text, encoding="utf-8")
        return response.text

def scrape_constituency_data():
    main_page_url = "https://results.eci.gov.in/ResultAcGenNov2024/partywiseresult-S13.htm"
    response = requests.get(main_page_url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = [f"https://results.eci.gov.in/ResultAcGenNov2024/{a['href']}" for a in soup.find_all("a", href=True) if "partywisewinresult" in a['href']]
    
    data = []
    unique_constituencies = set()
    for url in links:
        constituency_id = re.search(r'partywisewinresult-(\d+)S13\.htm', url).group(1)
        html_content = fetch_html(url, output_dir / f"constituency_{constituency_id}.html")
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table')
        if table:
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    constituency_name = cells[1].text.strip()
                    if constituency_id not in unique_constituencies:
                        unique_constituencies.add(constituency_id)
                        data.append({"constituency_name": constituency_name, "constituency_id": constituency_id, "state_id": "S13"})
    
    # Sorting data by constituency_id in ascending order
    data.sort(key=lambda x: int(x["constituency_id"]))
    
    with open(constituency_json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return {"message": "Constituency scraping successful", "data": data}

@app.route("/scrape_constituency", methods=["GET"])
def scrape_constituency():
    return jsonify(scrape_constituency_data())

@app.route("/verify_constituency", methods=["GET"])
def verify_constituency():
    try:
        with open(constituency_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify({"message": "Data verification successful", "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/insert_constituency", methods=["POST"])
def insert_constituency():
    try:
        with open(constituency_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data:
            existing_entry = ConstituencyResults.query.filter_by(constituency_id=entry["constituency_id"]).first()
            if not existing_entry:
                db.session.add(ConstituencyResults(**entry))
        db.session.commit()
        return jsonify({"message": "Constituency data inserted successfully"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
