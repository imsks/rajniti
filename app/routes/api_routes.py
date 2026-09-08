"""
API Routes for Rajniti — Politician-centric design.

All election/party/constituency data is embedded in the Politician model,
so every route revolves around politicians.
"""

import logging

from flask import Blueprint, jsonify, request

from app.controllers.politician_controller import PoliticianController

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

politician_ctrl = PoliticianController()


# ==================== POLITICIAN ROUTES ====================


@api_bp.route("/politicians", methods=["GET"])
def list_politicians():
    """
    List politicians with optional filters.

    Query params:
        type: MP | MLA (optional)
        limit: int (default 100)
    """
    try:
        election_type = request.args.get("type")
        limit = min(request.args.get("limit", default=100, type=int), 200)
        result = politician_ctrl.get_all(election_type=election_type, limit=limit)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/search", methods=["GET"])
def search_politicians():
    """
    Search politicians by name, state, constituency, party.

    Query params:
        q: search query (required)
        type: MP | MLA (optional)
        state: state name filter (optional)
        party: party name filter (optional)
        limit: int (default 50)
    """
    try:
        query = request.args.get("q", "").strip()
        if not query:
            return (
                jsonify({"success": False, "error": "Query parameter 'q' is required"}),
                400,
            )

        result = politician_ctrl.search(
            query=query,
            election_type=request.args.get("type"),
            state=request.args.get("state"),
            party=request.args.get("party"),
            limit=min(request.args.get("limit", default=50, type=int), 200),
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/catalog", methods=["GET"])
def politician_catalog():
    """
    Paginated lightweight politician list for public SEO directory.

    Query params:
        page: int (default 1)
        per_page: int (default 48, max 100)
        type: MP | MLA (optional)
        state: state name filter (optional)
        q: name search (optional)
        party: comma-separated party names filter (optional)
    """
    try:
        election_type = request.args.get("type")
        page = request.args.get("page", default=1, type=int)
        per_page = min(request.args.get("per_page", default=48, type=int), 100)
        state = request.args.get("state")
        q = request.args.get("q")
        party_param = request.args.get("party")
        parties = (
            [x for x in (s.strip() for s in party_param.split(",")) if x]
            if party_param
            else None
        )
        result = politician_ctrl.list_catalog(
            page=page,
            per_page=per_page,
            election_type=election_type,
            state=state,
            q=q,
            parties=parties,
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/sitemap-entries", methods=["GET"])
def politician_sitemap_entries():
    """Lightweight slug entries for sitemap generation."""
    try:
        result = politician_ctrl.sitemap_entries()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/<politician_id>", methods=["GET"])
def get_politician(politician_id):
    """Get a single politician by ID."""
    try:
        politician = politician_ctrl.get_by_id(politician_id)
        if not politician:
            return jsonify({"success": False, "error": "Politician not found"}), 404
        return jsonify({"success": True, "data": politician})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/slug/<politician_slug>", methods=["GET"])
def get_politician_by_slug(politician_slug):
    """Get a single politician by slug."""
    try:
        politician = politician_ctrl.get_by_slug(politician_slug)
        if not politician:
            return jsonify({"success": False, "error": "Politician not found"}), 404
        return jsonify({"success": True, "data": politician})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/state/<state>", methods=["GET"])
def get_politicians_by_state(state):
    """Get all politicians from a state."""
    try:
        election_type = request.args.get("type")
        result = politician_ctrl.get_by_state(state, election_type=election_type)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/politicians/party/<party>", methods=["GET"])
def get_politicians_by_party(party):
    """Get all politicians from a party."""
    try:
        election_type = request.args.get("type")
        result = politician_ctrl.get_by_party(party, election_type=election_type)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== AGGREGATION ROUTES ====================


@api_bp.route("/stats", methods=["GET"])
def get_stats():
    """Get summary statistics."""
    try:
        election_type = request.args.get("type")
        result = politician_ctrl.get_stats(election_type=election_type)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/states", methods=["GET"])
def get_states():
    """Get list of unique states."""
    try:
        election_type = request.args.get("type")
        states = politician_ctrl.get_states(election_type=election_type)
        return jsonify(
            {"success": True, "data": {"states": states, "total": len(states)}}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/parties", methods=["GET"])
def get_parties():
    """Get list of unique parties."""
    try:
        election_type = request.args.get("type")
        parties = politician_ctrl.get_parties(election_type=election_type)
        return jsonify(
            {"success": True, "data": {"parties": parties, "total": len(parties)}}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== QUESTIONS ROUTES (Vector DB — reimplementation pending) ====================

_VECTOR_QA_UNAVAILABLE = (
    "Semantic Q&A over the vector store is not implemented yet. "
    "Follow docs/VECTOR_DBS.md to reintroduce Chroma and wire these endpoints."
)


@api_bp.route("/questions", methods=["GET"])
def get_predefined_questions():
    """Get predefined questions."""
    try:
        from app.schemas.questions import PREDEFINED_QUESTIONS

        return jsonify(
            {
                "success": True,
                "data": {
                    "questions": PREDEFINED_QUESTIONS,
                    "total": len(PREDEFINED_QUESTIONS),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/questions/ask", methods=["POST"])
def ask_question():
    """Ask a question — semantic search over politician data (not yet wired)."""
    try:
        data = request.get_json()
        if not data or not data.get("question"):
            return jsonify({"success": False, "error": "Question is required"}), 400

        qs = _get_questions_service()
        if not qs:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Questions service unavailable. Vector DB may not be configured.",
                    }
                ),
                503,
            )

        result = qs.answer_question(
            question=data["question"],
            n_results=min(data.get("n_results", 5), 50),
        )
        return (
            jsonify(
                {
                    "success": False,
                    "error": _VECTOR_QA_UNAVAILABLE,
                    "code": "VECTOR_QA_NOT_IMPLEMENTED",
                }
            ),
            501,
        )
    except Exception as e:
        logger.error("ask_question error: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500


@api_bp.route("/questions/<question_id>/answer", methods=["GET"])
def answer_predefined_question(question_id):
    """Answer a predefined question by ID (not yet wired)."""
    try:
        qs = _get_questions_service()
        if not qs:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Questions service unavailable.",
                    }
                ),
                503,
            )

        n_results = min(request.args.get("n_results", default=5, type=int), 50)
        result = qs.answer_predefined_question(
            question_id=question_id,
            n_results=n_results,
        )
        return (
            jsonify(
                {
                    "success": False,
                    "error": _VECTOR_QA_UNAVAILABLE,
                    "code": "VECTOR_QA_NOT_IMPLEMENTED",
                    "question_id": question_id,
                }
            ),
            501,
        )
    except Exception as e:
        logger.error("answer_predefined_question error: %s", e)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ROOT & HEALTH ====================


@api_bp.route("/", methods=["GET"])
def api_root():
    """API root."""
    return jsonify(
        {
            "success": True,
            "message": "Welcome to Rajniti API",
            "version": "2.0.0",
            "endpoints": {
                "politicians": "/api/v1/politicians",
                "search": "/api/v1/politicians/search?q=<query>",
                "by_state": "/api/v1/politicians/state/<state>",
                "by_party": "/api/v1/politicians/party/<party>",
                "stats": "/api/v1/stats",
                "states": "/api/v1/states",
                "parties": "/api/v1/parties",
                "questions": "/api/v1/questions",
                "ask": "/api/v1/questions/ask (POST, 501 until vector store is wired)",
                "health": "/api/v1/health",
            },
        }
    )


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check."""
    from app.database.session import check_db_health

    db_ok = check_db_health()
    return jsonify(
        {
            "success": True,
            "message": "Rajniti API is healthy",
            "version": "2.0.0",
            "database": {
                "connected": db_ok,
                "status": "healthy" if db_ok else "not configured",
            },
        }
    )
