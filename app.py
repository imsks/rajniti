from flask import Flask, request, jsonify
from flask_migrate import Migrate
from database import db    
from database.models import State, Election
from sqlalchemy.exc import IntegrityError


def create_app():
    app = Flask(__name__)

    # Configure DB
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/INDIA'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)

    # ----------- POST API for Election -----------
    @app.route('/api/elections', methods=['POST'])
    def create_election():
        data = request.get_json()

        # Input validation
        required_fields = ['name', 'type', 'year', 'state_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        if data['type'] not in ['LOKSABHA', 'VIDHANSABHA']:
            return jsonify({'error': 'Invalid election type. Must be LOKSABHA or VIDHANSABHA.'}), 400

        state = State.query.filter_by(id=data['state_id']).first()
        if not state:
            return jsonify({'error': 'Invalid state_id.'}), 400

        try:
            election = Election(
                name=data['name'],
                type=data['type'],
                year=data['year'],
                state_id=data['state_id']
            )
            db.session.add(election)
            db.session.commit()

            return jsonify({
                'message': 'Election created successfully.',
                'election_id': str(election.id)
            }), 201

        except IntegrityError as e:
            db.session.rollback()
            if 'unique_state_year_type' in str(e.orig):
                return jsonify({'error': 'Election for this state, year, and type already exists.'}), 400
            return jsonify({'error': 'Database Integrity Error!'}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return app
