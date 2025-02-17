from database.db import db

class BaseModel(db.Model):
    __abstract__ = True

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

class PartyResults(BaseModel):
    __tablename__ = 'party_results'
    id = db.Column(db.Integer, primary_key=True)
    party_name = db.Column(db.String(255), unique=True, nullable=False)
    symbol = db.Column(db.String(255), nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

class ConstituencyResults(BaseModel):
    __tablename__ = 'constituency_results'
    constituency_id = db.Column(db.String(50), primary_key=True)
    constituency_name = db.Column(db.String(255), nullable=False)
    state_id = db.Column(db.String(10), nullable=False)

class CandidateResults(BaseModel):
    __tablename__ = 'candidate_results'
    id = db.Column(db.Integer, primary_key=True)
    constituency_code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    party = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50))
    votes = db.Column(db.String(50))
    margin = db.Column(db.String(50))
    image_url = db.Column(db.String(500))