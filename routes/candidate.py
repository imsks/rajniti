import json
from flask import Blueprint, request, jsonify
from database import db
from database.models import Candidate, Constituency, Election

candidate_bp = Blueprint('candidate', __name__)

# Path to your JSON file
CANDIDATE_JSON_PATH = "scripts/candidate.json"

# -------------------- /scrape --------------------
@candidate_bp.route('/election/<election_id>/candidate/scrape', methods=['GET'])
def scrape_candidates(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(CANDIDATE_JSON_PATH) as f:
            candidates = json.load(f)
        return jsonify({
            "message": "Scraped candidate data loaded successfully.",
            "count": len(candidates)
        }), 200
    except FileNotFoundError:
        return jsonify({"error": "Candidate JSON file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- /verify --------------------
@candidate_bp.route('/election/<election_id>/candidate/verify', methods=['GET'])
def verify_candidates(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(CANDIDATE_JSON_PATH) as f:
            candidates = json.load(f)
        return jsonify({"scraped_candidates": candidates}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- /insert --------------------
@candidate_bp.route('/election/<election_id>/candidate/insert', methods=['POST'])
def insert_candidates(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    try:
        with open(CANDIDATE_JSON_PATH) as f:
            candidates = json.load(f)

        inserted = 0
        for entry in candidates:
            const_id = entry.get("Constituency Code")
            name = entry.get("Name")
            party_name = entry.get("Party")
            status = entry.get("Status")
            photo = entry.get("Image URL")
            elec_type = election.type

            # ❌ Skip NOTA
            if name.strip().upper() == "NOTA":
                print(f"Skipping NOTA candidate: {entry}")
                continue

            # ❌ Skip incomplete entries
            if not name or not const_id or not party_name or not status or not elec_type:
                print(f"Skipping incomplete candidate: {entry}")
                continue

            # ❌ Skip invalid constituency
            constituency = Constituency.query.filter_by(id=const_id).first()
            if not constituency:
                print(f"Skipping invalid constituency_id: {const_id}")
                continue

            # ✅ Skip if candidate already exists
            existing = Candidate.query.filter_by(
                name=name,
                const_id=const_id,
                party_id=party_name,
                elec_type=elec_type
            ).first()
            if existing:
                continue

            new_candidate = Candidate(
                name=name,
                photo=photo,
                const_id=const_id,
                party_id=party_name,
                status=status,
                elec_type=elec_type
            )
            db.session.add(new_candidate)
            inserted += 1

        db.session.commit()
        return jsonify({"message": f"{inserted} candidates inserted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
