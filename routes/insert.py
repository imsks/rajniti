from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json
import os
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
    image_url = db.Column(db.String(255), nullable=True)

# Insert data into tables
@app.route('/insert/state_codes', methods=['POST'])
def insert_state_codes():
    try:
        data = request.get_json()
        new_states = [StateCode(**record) for record in data]
        db.session.bulk_save_objects(new_states)
        db.session.commit()
        return jsonify({"message": "State codes inserted successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/insert/partywise', methods=['POST'])
def insert_partywise():
    try:
        data = request.get_json()
        new_parties = [Partywise(**record) for record in data]
        db.session.bulk_save_objects(new_parties)
        db.session.commit()
        return jsonify({"message": "Partywise data inserted successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/insert/constituencywise', methods=['POST'])
def insert_constituencywise():
    try:
        data = request.get_json()
        new_constituencies = [Constituencywise(**record) for record in data]
        db.session.bulk_save_objects(new_constituencies)
        db.session.commit()
        return jsonify({"message": "Constituencywise data inserted successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/insert/vselection', methods=['POST'])
def insert_vselection():
    try:
        data = request.get_json()
        new_candidates = [VSelection(**record) for record in data]
        db.session.bulk_save_objects(new_candidates)
        db.session.commit()
        return jsonify({"message": "VSelection data inserted successfully!"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
