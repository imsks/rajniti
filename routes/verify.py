from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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

# /verify API for state codes
@app.route('/verify/states', methods=['GET'])
def verify_states():
    try:
        states = StateCode.query.all()
        data = [{"state_name": state.state_name, "state_id": state.state_id} for state in states]
        return jsonify({"message": "State codes verification successful", "verified_data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /verify API for partywise
@app.route('/verify/partywise', methods=['GET'])
def verify_partywise():
    try:
        parties = Partywise.query.all()
        data = [{"party_name": party.party_name, "symbol": party.symbol, "total_seats": party.total_seats} for party in parties]
        return jsonify({"message": "Partywise data verification successful", "verified_data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /verify API for constituencywise
@app.route('/verify/constituencywise', methods=['GET'])
def verify_constituencywise():
    try:
        constituencies = Constituencywise.query.all()
        data = [{
            "constituency_id": c.constituency_id, 
            "constituency_name": c.constituency_name, 
            "state_id": c.state_id
        } for c in constituencies]
        return jsonify({"message": "Constituencywise data verification successful", "verified_data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# /verify API for vselection
@app.route('/verify/vselection', methods=['GET'])
def verify_vselection():
    try:
        selections = VSelection.query.all()
        data = [{
            "constituency_code": v.constituency_code,
            "candidate_name": v.candidate_name,
            "party": v.party,
            "status": v.status,
            "votes": v.votes,
            "margin": v.margin,
            "image_url": v.image_url
        } for v in selections]
        return jsonify({"message": "VSelection data verification successful", "verified_data": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

