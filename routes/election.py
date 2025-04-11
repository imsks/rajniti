from flask import Blueprint, jsonify, request
from database import db
from database.models import Election, State

election_bp = Blueprint('election', __name__)

# -------------------- Create Election --------------------
@election_bp.route('/election', methods=['POST'])
def create_election():
    data = request.get_json()
    required_fields = ['name', 'type', 'year', 'state_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    if data['type'] not in ['LOKSABHA', 'VIDHANSABHA']:
        return jsonify({'error': 'Invalid election type. Must be LOKSABHA or VIDHANSABHA.'}), 400

    state = State.get_by_id(data['state_id'])
    if not state:
        return jsonify({'error': 'Invalid state_id.'}), 400

    try:
        election = Election.create(data)
        if not election:
            return jsonify({'error': 'Failed to create election.'}), 500

        return jsonify({
            'message': 'Election created successfully.',
            'election': election
        }), 201

    except Exception as e:
        db.session.rollback()
        if hasattr(e, "orig") and 'unique_state_year_type' in str(e.orig):
            return jsonify({'error': 'Election for this state, year, and type already exists.'}), 400
        return jsonify({'error': str(e)}), 500

# -------------------- Get Election by ID --------------------
@election_bp.route('/election/<election_id>', methods=['GET'])
def get_election(election_id):
    election = Election.get_by_id(election_id)
    if not election:
        return jsonify({'error': 'Election not found.'}), 404
    return jsonify(election), 200

# -------------------- Update Election --------------------
@election_bp.route('/election/<election_id>', methods=['PUT'])
def update_election(election_id):
    data = request.get_json()
    election = Election.query.get(election_id)
    if not election:
        return jsonify({'error': 'Election not found.'}), 404

    try:
        for key in ['name', 'type', 'year', 'state_id']:
            if key in data:
                setattr(election, key, data[key])
        db.session.commit()
        return jsonify({'message': 'Election updated successfully.', 'election': election.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# -------------------- Delete Election --------------------
@election_bp.route('/election/<election_id>', methods=['DELETE'])
def delete_election(election_id):
    election = Election.query.get(election_id)
    if not election:
        return jsonify({'error': 'Election not found.'}), 404

    try:
        db.session.delete(election)
        db.session.commit()
        return jsonify({'message': 'Election deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500