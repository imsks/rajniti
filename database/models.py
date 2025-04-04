from database import db  
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.schema import UniqueConstraint
import uuid

class State(db.Model):
    __tablename__ = 'state'
    id = db.Column(db.String(10), primary_key=True)  # State abbreviation
    name = db.Column(db.String(100), nullable=False, unique=True)
    CM_party_id = db.Column(UUID(as_uuid=True), db.ForeignKey('party.id'), nullable=True)

    elections = db.relationship('Election', backref='state', lazy=True)
    constituencies = db.relationship('Constituency', backref='state', lazy=True)

    def __repr__(self):
        return f"<State(id={self.id}, name={self.name})>"

    def to_dict(self):
        return {"id": self.id, "name": self.name, "CM_party_id": self.CM_party_id}

    @staticmethod
    def get_all():
        return [state.to_dict() for state in State.query.all()]

    @staticmethod
    def get_by_id(state_id):
        state = State.query.filter_by(id=state_id).first()
        return state.to_dict() if state else None

    @staticmethod
    def create(data):
        try:
            state = State(**data)
            db.session.add(state)
            db.session.commit()
            return state.to_dict()
        except Exception as e:
            db.session.rollback()
            print(e)
            return None

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
    __tablename__ = 'election'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.Enum('LOKSABHA', 'VIDHANSABHA', name='election_type'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    state_id = db.Column(db.String(10), db.ForeignKey('state.id'), nullable=False)

    # Add UNIQUE constraint
    __table_args__ = (
        UniqueConstraint('state_id', 'year', 'type', name='unique_state_year_type'),
    )

    def to_dict(self):
        return {"id": str(self.id), "name": self.name, "type": self.type, "year": self.year, "state_id": self.state_id}

    @staticmethod
    def get_all():
        return [e.to_dict() for e in Election.query.all()]

    @staticmethod
    def get_by_id(election_id):
        e = Election.query.get(election_id)
        return e.to_dict() if e else None

    @staticmethod
    def create(data):
        try:
            e = Election(**data)
            db.session.add(e)
            db.session.commit()
            return e.to_dict()
        except Exception as e:
            db.session.rollback()
            print(e)
            return None


class Party(db.Model):
    __tablename__ = 'party'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    symbol = db.Column(db.String, nullable=False)
    total_seats = db.Column(db.Integer, nullable=True)  

    def to_dict(self):
        return {"id": str(self.id), "name": self.name, "symbol": self.symbol, "total_seats": self.total_seats}

    @staticmethod
    def get_all():
        return [p.to_dict() for p in Party.query.all()]

    @staticmethod
    def get_by_id(party_id):
        p = Party.query.get(party_id)
        return p.to_dict() if p else None

    @staticmethod
    def create(data):
        try:
            p = Party(**data)
            db.session.add(p)
            db.session.commit()
            return p.to_dict()
        except Exception as e:
            db.session.rollback()
            print(e)
            return None


class Candidate(db.Model):
    __tablename__ = 'candidate'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String, nullable=False)
    photo = db.Column(db.String)
    const_id = db.Column(db.String, db.ForeignKey('constituency.id'), nullable=False)
    party_id = db.Column(UUID(as_uuid=True), db.ForeignKey('party.id'), nullable=False)
    status = db.Column(db.Enum('WON', 'LOST', name='candidate_status'), nullable=False)
    elec_type = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id), "name": self.name, "photo": self.photo, "const_id": self.const_id,
            "party_id": str(self.party_id), "status": self.status, "elec_type": self.elec_type
        }

    @staticmethod
    def get_all():
        return [c.to_dict() for c in Candidate.query.all()]

    @staticmethod
    def get_by_id(candidate_id):
        c = Candidate.query.get(candidate_id)
        return c.to_dict() if c else None

    @staticmethod
    def create(data):
        try:
            c = Candidate(**data)
            db.session.add(c)
            db.session.commit()
            return c.to_dict()
        except Exception as e:
            db.session.rollback()
            print(e)
            return None


class Constituency(db.Model):
    __tablename__ = 'constituency'
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state_id = db.Column(db.String(10), db.ForeignKey('state.id'), nullable=False)
    mla_id = db.Column(UUID(as_uuid=True), db.ForeignKey('candidate.id'))
    mp_id = db.Column(UUID(as_uuid=True), db.ForeignKey('candidate.id'))

    candidates = db.relationship(
        'Candidate',
        backref='constituency',
        lazy=True,
        foreign_keys='Candidate.const_id'
    )

    mla = db.relationship(
        'Candidate',
        foreign_keys=[mla_id],
        uselist=False
    )
    mp = db.relationship(
        'Candidate',
        foreign_keys=[mp_id],
        uselist=False
    )  

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "state_id": self.state_id,
            "mla_id": str(self.mla_id) if self.mla_id else None,
            "mp_id": str(self.mp_id) if self.mp_id else None
        }

    @staticmethod
    def get_all():
        return [c.to_dict() for c in Constituency.query.all()]

    @staticmethod
    def get_by_id(const_id):
        c = Constituency.query.get(const_id)
        return c.to_dict() if c else None

    @staticmethod
    def create(data):
        try:
            c = Constituency(**data)
            db.session.add(c)
            db.session.commit()
            return c.to_dict()
        except Exception as e:
            db.session.rollback()
            print(e)
            return None
