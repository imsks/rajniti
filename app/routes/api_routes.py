"""
Simple API Routes for Rajniti Election Data

Clean Flask routes following MVC pattern:
- Routes handle HTTP requests/responses
- Controllers handle business logic
- Models define data structure
- Services handle data access
"""

from flask import Blueprint, jsonify, request

from app.controllers import (
    CandidateController,
    ConstituencyController,
    ElectionController,
    PartyController,
)

# Create blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

# Initialize controllers
election_controller = ElectionController()
candidate_controller = CandidateController()
party_controller = PartyController()
constituency_controller = ConstituencyController()


# ==================== ELECTION ROUTES ====================


@api_bp.route("/elections", methods=["GET"])
def get_elections():
    """Get all elections"""
    try:
        elections = election_controller.get_all_elections()
        return jsonify({"success": True, "data": elections, "total": len(elections)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>", methods=["GET"])
def get_election(election_id):
    """Get election details"""
    try:
        election = election_controller.get_election_by_id(election_id)
        if not election:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": election})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>/results", methods=["GET"])
def get_election_results(election_id):
    """Get election results"""
    try:
        limit = request.args.get("limit", type=int)
        results = election_controller.get_election_results(election_id, limit)

        if not results:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>/winners", methods=["GET"])
def get_election_winners(election_id):
    """Get election winners"""
    try:
        winners = election_controller.get_election_winners(election_id)

        if not winners:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": winners})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CANDIDATE ROUTES ====================


@api_bp.route("/candidates/search", methods=["GET"])
def search_candidates():
    """Search candidates"""
    try:
        query = request.args.get("q", "").strip()
        election_id = request.args.get("election_id")
        limit = request.args.get("limit", type=int)

        if not query:
            return (
                jsonify({"success": False, "error": 'Query parameter "q" is required'}),
                400,
            )

        results = candidate_controller.search_candidates(query, election_id, limit)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>/candidates", methods=["GET"])
def get_candidates_by_election(election_id):
    """Get candidates by election"""
    try:
        limit = request.args.get("limit", type=int)
        results = candidate_controller.get_candidates_by_election(election_id, limit)

        if not results:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>/candidates/<candidate_id>", methods=["GET"])
def get_candidate(election_id, candidate_id):
    """Get candidate details"""
    try:
        candidate = candidate_controller.get_candidate_by_id(candidate_id, election_id)

        if not candidate:
            return jsonify({"success": False, "error": "Candidate not found"}), 404

        return jsonify({"success": True, "data": candidate})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/candidates/party/<party_name>", methods=["GET"])
def get_candidates_by_party(party_name):
    """Get candidates by party"""
    try:
        election_id = request.args.get("election_id")
        results = candidate_controller.get_candidates_by_party(party_name, election_id)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route(
    "/elections/<election_id>/constituencies/<constituency_id>/candidates",
    methods=["GET"],
)
def get_candidates_by_constituency(election_id, constituency_id):
    """Get candidates by constituency"""
    try:
        results = candidate_controller.get_candidates_by_constituency(
            constituency_id, election_id
        )

        if not results:
            return (
                jsonify(
                    {"success": False, "error": "Election or constituency not found"}
                ),
                404,
            )

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/candidates/winners", methods=["GET"])
def get_all_winners():
    """Get all winning candidates"""
    try:
        election_id = request.args.get("election_id")
        results = candidate_controller.get_winning_candidates(election_id)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== PARTY ROUTES ====================


@api_bp.route("/elections/<election_id>/parties", methods=["GET"])
def get_parties_by_election(election_id):
    """Get parties by election"""
    try:
        results = party_controller.get_parties_by_election(election_id)

        if not results:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/elections/<election_id>/parties/<party_name>", methods=["GET"])
def get_party_by_name(election_id, party_name):
    """Get party details"""
    try:
        results = party_controller.get_party_by_name(party_name, election_id)

        if not results:
            return (
                jsonify(
                    {"success": False, "error": "Party not found in this election"}
                ),
                404,
            )

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/parties/<party_name>/performance", methods=["GET"])
def get_party_performance(party_name):
    """Get party performance"""
    try:
        election_id = request.args.get("election_id")
        results = party_controller.get_party_performance(party_name, election_id)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/parties", methods=["GET"])
def get_all_parties():
    """Get all parties"""
    try:
        results = party_controller.get_all_parties()

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== CONSTITUENCY ROUTES ====================


@api_bp.route("/elections/<election_id>/constituencies", methods=["GET"])
def get_constituencies_by_election(election_id):
    """Get constituencies by election"""
    try:
        results = constituency_controller.get_constituencies_by_election(election_id)

        if not results:
            return jsonify({"success": False, "error": "Election not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route(
    "/elections/<election_id>/constituencies/<constituency_id>", methods=["GET"]
)
def get_constituency(election_id, constituency_id):
    """Get constituency details"""
    try:
        results = constituency_controller.get_constituency_by_id(
            constituency_id, election_id
        )

        if not results:
            return jsonify({"success": False, "error": "Constituency not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/constituencies/state/<state_code>", methods=["GET"])
def get_constituencies_by_state(state_code):
    """Get constituencies by state"""
    try:
        results = constituency_controller.get_constituencies_by_state(state_code)

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route(
    "/elections/<election_id>/constituencies/<constituency_id>/results", methods=["GET"]
)
def get_constituency_results(election_id, constituency_id):
    """Get constituency results"""
    try:
        results = constituency_controller.get_constituency_results(
            constituency_id, election_id
        )

        if not results:
            return jsonify({"success": False, "error": "Constituency not found"}), 404

        return jsonify({"success": True, "data": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ROOT & HEALTH CHECK ====================


@api_bp.route("/", methods=["GET"])
def api_root():
    """API root endpoint"""
    return jsonify(
        {
            "success": True,
            "message": "Welcome to Rajniti Election Data API",
            "version": "1.0.0",
            "endpoints": {
                "elections": "/api/v1/elections",
                "candidates": "/api/v1/candidates/search?q=<query>",
                "parties": "/api/v1/parties",
                "health": "/api/v1/health",
            },
        }
    )


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"success": True, "message": "Rajniti API is healthy", "version": "1.0.0"}
    )
