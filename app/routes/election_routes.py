from flask import Blueprint, jsonify
from app.services.scraping_service import scrape_election_data
from app.services.verification_service import verify_data
from app.models import Election
from app import db

election_bp = Blueprint("election", __name__)

@election_bp.route("/scrape", methods=["GET"])
def scrape():
    data = scrape_election_data()
    return jsonify({"message": "Scraping successful", "data": data}), 200

@election_bp.route("/verify", methods=["POST"])
def verify():
    data = scrape_election_data()
    result = verify_data(data)
    return jsonify(result), 200

@election_bp.route("/insert", methods=["POST"])
def insert():
    data = scrape_election_data()
    
    existing = Election.query.filter_by(id=data["id"]).first()
    if existing:
        return jsonify({"error": "Election already exists"}), 400

    new_election = Election(**data)
    db.session.add(new_election)
    db.session.commit()

    return jsonify({"message": "Election inserted successfully!"}), 201
