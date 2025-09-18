import json
from flask import Blueprint, request, jsonify
from app.models import db, Constituency, State

constituency_bp = Blueprint('constituency', __name__)

SCRAPED_CONSTITUENCY_PATH = "app/data/constituencies/data.json"

# -------------------- Scrape Constituencies --------------------
@constituency_bp.route('/election/<election_id>/constituency/scrape', methods=['GET'])
def scrape_constituencies(election_id):
    try:
        with open(SCRAPED_CONSTITUENCY_PATH) as f:
            data = json.load(f)
        return jsonify({
            "message": "Scraped constituency data loaded",
            "count": len(data)
        }), 200
    except FileNotFoundError:
        return jsonify({"error": "Scraped data file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Verify Constituencies --------------------
@constituency_bp.route('/election/<election_id>/constituency/verify', methods=['GET'])
def verify_constituencies(election_id):
    try:
        with open(SCRAPED_CONSTITUENCY_PATH) as f:
            data = json.load(f)
        return jsonify({"scraped_constituencies": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Insert Constituencies --------------------
@constituency_bp.route('/election/<election_id>/constituency/insert', methods=['POST'])
def insert_constituencies(election_id):
    try:
        with open(SCRAPED_CONSTITUENCY_PATH) as f:
            constituencies = json.load(f)

        inserted = 0
        for entry in constituencies:
            const_id = entry.get("constituency_id")
            name = entry.get("constituency_name")
            state_id = entry.get("state_id")

            if not const_id or not name or not state_id:
                print(f"Skipping incomplete entry: {entry}")
                continue

            existing = Constituency.query.filter_by(id=const_id).first()
            if not existing:
                state = State.query.filter_by(id=state_id).first()
                if not state:
                    print(f"Skipping invalid state_id: {state_id}")
                    continue

                new_const = Constituency(
                    id=const_id,
                    name=name,
                    state_id=state_id
                )
                db.session.add(new_const)
                inserted += 1

        db.session.commit()
        return jsonify({
            "message": "Constituencies inserted successfully.",
            "inserted": inserted
        }), 201

    except Exception as e:
        db.session.rollback()
        print("Error inserting constituencies:", e)
        return jsonify({"error": str(e)}), 500

# -------------------- Get Constituency by ID --------------------
@constituency_bp.route('/constituency/<constituency_id>', methods=['GET'])
def get_constituency_by_id(constituency_id):
    constituency = Constituency.query.get(constituency_id)
    if not constituency:
        return jsonify({"error": "Constituency not found"}), 404
    return jsonify(constituency.to_dict()), 200

# -------------------- Get All Constituencies --------------------
@constituency_bp.route('/constituencies', methods=['GET'])
def get_all_constituencies():
    all_data = Constituency.get_all()
    return jsonify({"results": all_data, "count": len(all_data)}), 200

# -------------------- Get Constituencies by State --------------------
@constituency_bp.route('/constituencies/state/<state_id>', methods=['GET'])
def get_constituencies_by_state(state_id):
    constituencies = Constituency.query.filter_by(state_id=state_id).all()
    return jsonify({
        "state_id": state_id,
        "results": [c.to_dict() for c in constituencies],
        "count": len(constituencies)
    }), 200
