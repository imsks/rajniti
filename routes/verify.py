from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os

app = Flask(__name__)

# Database configuration in app.config
app.config['DB_NAME'] = 'RAJNEETI'
app.config['DB_USER'] = 'postgres'
app.config['DB_PASSWORD'] = '12345678'
app.config['DB_HOST'] = 'localhost'
app.config['DB_PORT'] = '5432'

# Build the SQLAlchemy URI dynamically using the config values
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{app.config['DB_USER']}:{app.config['DB_PASSWORD']}@{app.config['DB_HOST']}:{app.config['DB_PORT']}/{app.config['DB_NAME']}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    constituency_code = db.Column(db.String(100), nullable=False)
    candidate_name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    votes = db.Column(db.Integer, nullable=False)
    margin = db.Column(db.Integer, nullable=False)


# Load JSON function with file existence check
def load_json(filename):
    data_folder = os.path.join(os.path.dirname(__file__), 'data')
    file_path = os.path.join(data_folder, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found at {file_path}!")
    
    with open(file_path, 'r') as file:
        return json.load(file)


# /scrape API for partywise with duplicate check and removal
@app.route('/scrape/partywise', methods=['GET'])
def scrape_partywise():
    try:
        data = load_json("partywiseresults_sorted.json")
        
        for record in data:
            # Check if the party already exists
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


# /scrape API for constituencywise with duplicate check and removal
@app.route('/scrape/constituencywise', methods=['GET'])
def scrape_constituencywise():
    try:
        data = load_json("constituency_data.json")
        
        for record in data:
            # Check if the constituency_id already exists
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


# /scrape API for vselection with duplicate check and removal
@app.route('/scrape/vselection', methods=['GET'])
def scrape_vselection():
    try:
        data = load_json("VSelection.json")
        
        for record in data:
            status = record.get("Status", "Unknown")  # Default to "Unknown" if status is None or missing
            
            if status is None:
                status = "Unknown"
            
            # Check if the candidate with the same constituency_code and candidate_name already exists
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
                    margin=int(record["Margin"])
                )
                db.session.add(candidate)
        
        db.session.commit()
        return jsonify({"message": "VSelection data inserted successfully!"}), 201
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# /verify API for partywise with duplicate check and removal
@app.route('/verify/partywise', methods=['GET'])
def verify_partywise():
    try:
        data = []
        partywise_data = Partywise.query.all()
        for party in partywise_data:
            data.append({
                "party_name": party.party_name,
                "symbol": party.symbol,
                "total_seats": party.total_seats
            })
        
        # Remove duplicates by using a set
        unique_partywise_data = list({item['party_name']: item for item in data}.values())

        return jsonify({
            "message": "Partywise data verification successful",
            "verified_data": unique_partywise_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# /verify API for constituencywise with duplicate check and removal
@app.route('/verify/constituencywise', methods=['GET'])
def verify_constituencywise():
    try:
        data = []
        constituencywise_data = Constituencywise.query.all()
        for constituency in constituencywise_data:
            data.append({
                "constituency_id": constituency.constituency_id,
                "constituency_name": constituency.constituency_name,
                "state_id": constituency.state_id
            })
        
        # Remove duplicates by using a set
        unique_constituencywise_data = list({item['constituency_id']: item for item in data}.values())

        return jsonify({
            "message": "Constituencywise data verification successful",
            "verified_data": unique_constituencywise_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# /verify API for vselection with duplicate check and removal
@app.route('/verify/vselection', methods=['GET'])
def verify_vselection():
    try:
        data = []
        vselection_data = VSelection.query.all()
        for vselection in vselection_data:
            data.append({
                "constituency_code": vselection.constituency_code,
                "candidate_name": vselection.candidate_name,
                "party": vselection.party,
                "status": vselection.status,
                "votes": vselection.votes,
                "margin": vselection.margin
            })

        # Remove duplicates by using a set
        unique_vselection_data = list({(item['constituency_code'], item['candidate_name']): item for item in data}.values())

        return jsonify({
            "message": "VSelection data verification successful",
            "verified_data": unique_vselection_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
