from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PartyResults(db.Model):
    __tablename__ = 'party_results'
    id = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String(255), nullable=False, unique=True)
    symbol = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    party_type = db.Column(db.String(50), nullable=False, default="State")

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

class Constituency(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    constituency_name = db.Column(db.String(255), nullable=False)
    constituency_id = db.Column(db.String(50), nullable=False, unique=True)
    state_id = db.Column(db.String(10), nullable=False)

class CandidateResults(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    constituency_code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    party = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50))
    votes = db.Column(db.String(50))
    margin = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
