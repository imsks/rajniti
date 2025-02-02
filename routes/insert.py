from flask import Flask, jsonify, request
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

# /insert API for partywise
@app.route('/insert/partywise', methods=['POST'])
def insert_partywise():
    try:
        data = request.get_json()  # Expecting a JSON payload
        
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /insert API for constituencywise
@app.route('/insert/constituencywise', methods=['POST'])
def insert_constituencywise():
    try:
        data = request.get_json()  # Expecting a JSON payload
        
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

        # Commit only once to avoid multiple commits
        db.session.commit()
        return jsonify({"message": "Constituencywise data inserted successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /insert API for vselection
@app.route('/insert/vselection', methods=['POST'])
def insert_vselection():
    try:
        data = request.get_json()  # Expecting a JSON payload
        
        for record in data:
            # Ensure status is not None and provide a default value if necessary
            status = record.get("Status", "Unknown")  # Default to "Unknown" if status is None or missing
            
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
