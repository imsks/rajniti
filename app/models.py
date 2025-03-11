from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import uuid

db = SQLAlchemy()

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.String(10), primary_key=True)  # State abbreviation (e.g., UP, MH)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Full state name
    cm_party_id = db.Column(db.String, db.ForeignKey('party.id'))
    elections = db.relationship('Election', backref='state', lazy=True)
    constituencies = db.relationship('Constituency', backref='state', lazy=True)

    def __repr__(self):
        return f"<State(id={self.id}, name={self.name})>"

    @staticmethod
    def populate_states():
        """Populates the State table with all Indian states."""
        states = [
            {"id": "AP", "name": "Andhra Pradesh"},
            {"id": "AR", "name": "Arunachal Pradesh"},
            {"id": "AS", "name": "Assam"},
            {"id": "BR", "name": "Bihar"},
            {"id": "CT", "name": "Chhattisgarh"},
            {"id": "GA", "name": "Goa"},
            {"id": "GJ", "name": "Gujarat"},
            {"id": "HR", "name": "Haryana"},
            {"id": "HP", "name": "Himachal Pradesh"},
            {"id": "JH", "name": "Jharkhand"},
            {"id": "KA", "name": "Karnataka"},
            {"id": "KL", "name": "Kerala"},
            {"id": "MP", "name": "Madhya Pradesh"},
            {"id": "MH", "name": "Maharashtra"},
            {"id": "MN", "name": "Manipur"},
            {"id": "ML", "name": "Meghalaya"},
            {"id": "MZ", "name": "Mizoram"},
            {"id": "NL", "name": "Nagaland"},
            {"id": "OD", "name": "Odisha"},
            {"id": "PB", "name": "Punjab"},
            {"id": "RJ", "name": "Rajasthan"},
            {"id": "SK", "name": "Sikkim"},
            {"id": "TN", "name": "Tamil Nadu"},
            {"id": "TG", "name": "Telangana"},
            {"id": "TR", "name": "Tripura"},
            {"id": "UP", "name": "Uttar Pradesh"},
            {"id": "UK", "name": "Uttarakhand"},
            {"id": "WB", "name": "West Bengal"},
            {"id": "AN", "name": "Andaman and Nicobar Islands"},
            {"id": "CH", "name": "Chandigarh"},
            {"id": "DN", "name": "Dadra and Nagar Haveli and Daman and Diu"},
            {"id": "DL", "name": "Delhi"},
            {"id": "JK", "name": "Jammu and Kashmir"},
            {"id": "LA", "name": "Ladakh"},
            {"id": "LD", "name": "Lakshadweep"},
            {"id": "PY", "name": "Puducherry"}
        ]

        try:
            for state in states:
                if not State.query.filter_by(id=state["id"]).first():
                    db.session.add(State(id=state["id"], name=state["name"]))
            
            db.session.commit()
            print("State table populated successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error populating states: {str(e)}")

class Election(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum('LOKSABHA', 'VIDHANSABHA', name='election_type'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    state_id = db.Column(db.String, db.ForeignKey('state.id'), nullable=False)

class Party(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    symbol = db.Column(db.String, nullable=False)

class Candidate(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    const_id = db.Column(db.String, db.ForeignKey('constituency.id'), nullable=False)
    party_id = db.Column(UUID(as_uuid=True), db.ForeignKey('party.id'), nullable=False)
    status = db.Column(db.Enum('WON', 'LOST', name='candidate_status'), nullable=False)
    elec_type = db.Column(db.String, nullable=False)

class Constituency(db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state_id = db.Column(db.String, db.ForeignKey('state.id'), nullable=False)
    mla_id = db.Column(UUID(as_uuid=True), db.ForeignKey('candidate.id'))
    mp_id = db.Column(UUID(as_uuid=True), db.ForeignKey('candidate.id'))
    candidates = db.relationship('Candidate', backref='constituency', lazy=True)
