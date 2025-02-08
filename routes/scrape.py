from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os
import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)

# Database configuration in app.config
app.config['DB_NAME'] = 'RAJNEETI'
app.config['DB_USER'] = 'postgres'
app.config['DB_PASSWORD'] = '12345678'
app.config['DB_HOST'] = 'localhost'
app.config['DB_PORT'] = '5432'

# Build the SQLAlchemy URI dynamically using the config values
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
class StateCode(db.Model):
    __tablename__ = 'state_codes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(100), unique=True, nullable=False)
    state_id = db.Column(db.String(10), unique=True, nullable=False)

class Partywise(db.Model):
    __tablename__ = 'partywise'
    id = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String(100), unique=True, nullable=False)
    symbol = db.Column(db.String(50), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

class Constituencywise(db.Model):
    __tablename__ = 'constituencywise'
    id = db.Column(db.Integer, primary_key=True)
    constituency_id = db.Column(db.Integer, unique=True, nullable=False)
    constituency_name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.String(50), nullable=False)

class VSelection(db.Model):
    __tablename__ = 'vselection'
    
    constituency_code = db.Column(db.String(100), primary_key=True, nullable=False)
    candidate_name = db.Column(db.String(100), primary_key=True, nullable=False)
    party = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=True)
    votes = db.Column(db.Integer, nullable=False)
    margin = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)  # Optional


# Load JSON function with file existence check
def load_json(filename):
    data_folder = os.path.join(os.path.dirname(__file__), 'data')  # path to the 'data' folder
    file_path = os.path.join(data_folder, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found at {file_path}!")
    
    with open(file_path, 'r') as file:
        return json.load(file)

# Scrape and store state codes
@app.route('/scrape/states', methods=['GET'])
def scrape_states():
    url = "https://kb.bullseyelocations.com/article/60-india-state-codes"
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch data"}), 500
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')

    if not table:
        return jsonify({"error": "Table not found on the webpage"}), 400

    rows = table.find_all('tr')
    new_states = []

    for row in rows[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) >= 2:
            state_name = cols[0].get_text(strip=True)
            state_id = cols[1].get_text(strip=True)

            # Check for existing record
            existing_state = StateCode.query.filter_by(state_id=state_id).first()
            if not existing_state:
                new_states.append(StateCode(state_name=state_name, state_id=state_id))

    if new_states:
        try:
            db.session.bulk_save_objects(new_states)
            db.session.commit()
            return jsonify({"message": "State codes inserted successfully!"}), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"message": "No new state codes added!"}), 200

# /scrape API for partywise
@app.route('/scrape/partywise', methods=['GET'])
def scrape_partywise():
    try:
        data = load_json("partywiseresults_sorted.json")
        for record in data:
            existing_party = Partywise.query.filter_by(party_name=record["party_name"]).first()
            if not existing_party:
                party = Partywise(
                    party_name=record["party_name"],
                    symbol=record["symbol"],
                    total_seats=record.get("total_seats", 0)
                )
                db.session.add(party)
        
        db.session.commit()
        return jsonify({"message": "Partywise data inserted successfully!"}), 201
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /scrape API for constituencywise
@app.route('/scrape/constituencywise', methods=['GET'])
def scrape_constituencywise():
    try:
        data = load_json("constituency_data.json")
        for record in data:
            existing_constituency = Constituencywise.query.filter_by(constituency_id=record["constituency_id"]).first()
            if not existing_constituency:
                constituency = Constituencywise(
                    constituency_id=record["constituency_id"],
                    constituency_name=record["constituency_name"],
                    state_id=record["state_id"]
                )
                db.session.add(constituency)
        
        db.session.commit()
        return jsonify({"message": "Constituencywise data inserted successfully!"}), 201
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scrape/vselection', methods=['GET'])
def scrape_vselection():
    try:
        data = load_json("VS_election_with_images.json")
        new_candidates = []
        
        for record in data:
            status = record.get("Status") if record.get("Status") else "Unknown"  # Handle missing status
            image_url = record.get("Image URL", None)
            
            existing_candidate = VSelection.query.filter_by(
                constituency_code=record["Constituency Code"], 
                candidate_name=record["Name"]
            ).first()
            
            if not existing_candidate:
                candidate = VSelection(
                    constituency_code=record["Constituency Code"],  
                    candidate_name=record["Name"], 
                    party=record["Party"], 
                    status=status,  
                    votes=int(record["Votes"]),  
                    margin=int(record["Margin"]), 
                    image_url=image_url
                )
                new_candidates.append(candidate)
        
        if new_candidates:
            db.session.bulk_save_objects(new_candidates)
            db.session.commit()
        
        return jsonify({"message": "VSelection data inserted successfully!"}), 201
        
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
