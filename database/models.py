from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

class State(db.Model):
    __tablename__ = 'state'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cm_party_id = db.Column(db.String, db.ForeignKey('party.id'), nullable=True)  # CM's Party
    elections = db.relationship('Election', backref='state', lazy=True)
    constituencies = db.relationship('Constituency', backref='state', lazy=True)

class Election(db.Model):
    __tablename__ = 'election'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)  # LOKSABHA / VIDHANSABHA
    year = db.Column(db.Integer, nullable=False)
    state_id = db.Column(db.String, db.ForeignKey('state.id'), nullable=False)

class Party(db.Model):
    __tablename__ = 'party'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    symbol = db.Column(db.String, nullable=True)
    candidates = db.relationship('Candidate', backref='party', lazy=True)

class Constituency(db.Model):
    __tablename__ = 'constituency'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    state_id = db.Column(db.String, db.ForeignKey('state.id'), nullable=False)
    mla_id = db.Column(db.String, db.ForeignKey('candidate.id'), nullable=True)  # MLA Candidate ID
    mp_id = db.Column(db.String, db.ForeignKey('candidate.id'), nullable=True)  # MP Candidate ID

class Candidate(db.Model):
    __tablename__ = 'candidate'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String, nullable=True)  # Candidate's image URL
    constituency_id = db.Column(db.String, db.ForeignKey('constituency.id'), nullable=False)
    party_id = db.Column(db.String, db.ForeignKey('party.id'), nullable=False)
    election_id = db.Column(db.String, db.ForeignKey('election.id'), nullable=False)
    status = db.Column(db.Enum('WON', 'LOST', name='status_enum'))
    election_type = db.Column(db.String, nullable=False)  # Lok Sabha / Vidhan Sabha
