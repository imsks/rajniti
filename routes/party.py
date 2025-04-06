import json
from flask import Blueprint, request, jsonify
from database import db
from database.models import Party, Election

party_bp = Blueprint('party', __name__)

# Use your actual JSON file path
SCRAPED_PARTIES_PATH = "data/MH-party.json"

@party_bp.route('/election/<election_id>/party/scrape', methods=['GET'])
def scraped_party(election_id):
    """Check if election exists and scraped data file is available."""
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(SCRAPED_PARTIES_PATH) as f:
            data = json.load(f)
        return jsonify({
            "message": "Scraped party data loaded",
            "count": len(data)
        })
    except FileNotFoundError:
        return jsonify({"error": "Scraped data file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@party_bp.route('/election/<election_id>/party/verify', methods=['GET'])
def verify_party(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(SCRAPED_PARTIES_PATH) as f:
            data = json.load(f)
        return jsonify({"scraped_parties": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@party_bp.route('/election/<election_id>/party/insert', methods=['POST'])
def insert_party(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(SCRAPED_PARTIES_PATH) as f:
            parties = json.load(f)

        inserted = 0
        for party_data in parties:
            if "party_name" not in party_data or "symbol" not in party_data:
                continue  # skip incomplete entries

            existing = Party.query.filter_by(name=party_data["party_name"]).first()
            if not existing:
                new_party = Party(
                    name=party_data["party_name"],
                    symbol=party_data["symbol"],
                    total_seats=party_data.get("total_seats")  # safe fallback
                )
                db.session.add(new_party)
                inserted += 1

        db.session.commit()
        return jsonify({
            "message": "Parties inserted successfully.",
            "inserted": inserted
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

