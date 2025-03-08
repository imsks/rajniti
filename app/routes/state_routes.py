from flask import Blueprint, jsonify
from app.models import State
from app import db

state_bp = Blueprint("State", __name__)

@state_bp.route("/state", methods=["GET"])
def get_states():
    states = State.query.all()
    return jsonify([{"id": state.id, "name": state.name} for state in states]), 200
