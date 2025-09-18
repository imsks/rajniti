import json
from flask import Blueprint, request, jsonify
from app.models import db, Candidate, Constituency, Election

candidate_bp = Blueprint('candidate', __name__)

CANDIDATE_JSON_PATH = "app/data/candidates/data.json"

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

            if name.strip().upper() == "NOTA":
                continue

            if not name or not const_id or not party_name or not elec_type:
                continue

            constituency = Constituency.query.filter_by(id=const_id).first()
            if not constituency:
                continue

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
                status=status.lower() if status else None,
                elec_type=elec_type
            )
            db.session.add(new_candidate)
            inserted += 1

        db.session.commit()
        return jsonify({"message": f"{inserted} candidates inserted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# -------------------- GET APIs --------------------

@candidate_bp.route('/candidates', methods=['GET'])
def get_all_candidates():
    candidates = Candidate.query.all()
    return jsonify({"candidates": [c.to_dict() for c in candidates]})

@candidate_bp.route('/candidate/<candidate_id>', methods=['GET'])
def get_candidate_by_id(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return jsonify({"error": "Candidate not found"}), 404
    return jsonify(candidate.to_dict())

@candidate_bp.route('/candidates/constituency/<const_id>', methods=['GET'])
def get_candidates_by_constituency(const_id):
    candidates = Candidate.query.filter_by(const_id=const_id).all()
    return jsonify({"results": [c.to_dict() for c in candidates], "count": len(candidates)})

@candidate_bp.route('/candidates/party/<party_name>', methods=['GET'])
def get_candidates_by_party(party_name):
    candidates = Candidate.query.filter_by(party_id=party_name).all()
    return jsonify({"results": [c.to_dict() for c in candidates], "count": len(candidates)})
