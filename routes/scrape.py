from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os
from sqlalchemy import text

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
    state_id = db.Column(db.String(50), nullable=False)  # Updated to String


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
    data_folder = os.path.join(os.path.dirname(__file__), 'data')  # path to the 'data' folder
    file_path = os.path.join(data_folder, filename)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found at {file_path}!")
    
    with open(file_path, 'r') as file:
        return json.load(file)

# /scrape API for partywise with duplicate check
@app.route('/scrape/partywise', methods=['GET'])
def scrape_partywise():
    try:
        data = load_json("partywiseresults_sorted.json")  # Adjust the path here
        for record in data:
            # Check if the party already exists
            existing_party = Partywise.query.filter_by(party_name=record["party_name"]).first()
            if not existing_party:
                # If party doesn't exist, add it to the database
                party = Partywise(
                    party_name=record["party_name"],
                    symbol=record["symbol"],
                    total_seats=record.get("total_seats", 0)
                )
                db.session.add(party)
        
        # Commit only once to avoid multiple commits
        db.session.commit()
        return jsonify({"message": "Partywise data inserted successfully!"}), 201
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# /scrape API for constituencywise with duplicate check
@app.route('/scrape/constituencywise', methods=['GET'])
def scrape_constituencywise():
    try:
        data = load_json("constituency_data.json")  # Adjust the path here
        for record in data:
            # Check if the constituency_id already exists
            existing_constituency = Constituencywise.query.filter_by(constituency_id=record["constituency_id"]).first()
            if not existing_constituency:
                # If constituency_id doesn't exist, add it to the database
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
        data = load_json("VSelection.json")
        
        for record in data:
            
            status = record.get("Status", "Unknown") 
            if status is None:
                status = "Unknown"
            
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
        
        # Commit all entries after the loop
        db.session.commit()
        return jsonify({"message": "VSelection data inserted successfully!"}), 201
        
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True)
