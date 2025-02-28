from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class State(db.Model):
    __tablename__ = 'state'
    
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    cm_party_id = db.Column(db.String, db.ForeignKey('party.id'), nullable=True)  # CM's Party
    elections = db.relationship('Election', backref='state', lazy=True)
    constituencies = db.relationship('Constituency', backref='state', lazy=True)

    @staticmethod
    def populate_states():
        """Populates the State table with all Indian states if they don’t exist."""
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

        for state in states:
            if not State.query.filter_by(id=state["id"]).first():
                db.session.add(State(id=state["id"], name=state["name"]))

        db.session.commit()
        print("✅ State table populated successfully.")

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
    image = db.Column(db.String, nullable=True)  # Candidate's image URL
    constituency_id = db.Column(db.String, db.ForeignKey('constituency.id'), nullable=False)
    party_id = db.Column(db.String, db.ForeignKey('party.id'), nullable=False)
    election_id = db.Column(db.String, db.ForeignKey('election.id'), nullable=False)
    status = db.Column(db.Enum('WON', 'LOST', name='status_enum'))
    election_type = db.Column(db.String, nullable=False)  # Lok Sabha / Vidhan Sabha

