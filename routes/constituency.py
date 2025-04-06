# ✅ FILE: routes/constituency_routes.py

import json
from flask import Blueprint, request, jsonify
from database import db
from database.models import Constituency, State

constituency_bp = Blueprint('constituency', __name__)

SCRAPED_CONSTITUENCY_PATH = "data/MH-constituency.json"

@constituency_bp.route('/election/<election_id>/constituency/scrape', methods=['GET'])
def scrape_constituencies(election_id):
    try:
        with open(SCRAPED_CONSTITUENCY_PATH) as f:
            data = json.load(f)
        return jsonify({
            "message": "Scraped constituency data loaded",
            "count": len(data)
        })
    except FileNotFoundError:
        return jsonify({"error": "Scraped data file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@constituency_bp.route('/election/<election_id>/constituency/verify', methods=['GET'])
def verify_constituencies(election_id):
    try:
        with open(SCRAPED_CONSTITUENCY_PATH) as f:
            data = json.load(f)
        return jsonify({"scraped_constituencies": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        })

    except Exception as e:
        db.session.rollback()
        print("Error inserting constituencies:", e)
        return jsonify({"error": str(e)}), 500
