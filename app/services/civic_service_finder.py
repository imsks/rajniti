"""
Civic Service Finder — Citizens' Awareness module.

Answers "what problem are you facing?" with the government apps, portals and
helplines that can actually help. Data is manually curated in
`app/data/civic_services.json` and tagged with the fixed taxonomy in
`app/schemas/civic_services.py`.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.schemas.civic_services import (
    GUIDED_QUESTIONS,
    JURISDICTIONS,
    PLATFORMS,
    PROBLEM_DOMAINS,
)

logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_FILE = "civic_services.json"


class CivicServiceFinder:
    """Read-only lookup over the curated government service catalogue."""

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self._data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self._services: Optional[List[Dict[str, Any]]] = None

    # ---------- LOAD ----------
    def _load(self) -> List[Dict[str, Any]]:
        if self._services is not None:
            return self._services

        path = self._data_dir / _DATA_FILE
        if not path.exists():
            logger.error("Civic services data file not found: %s", path)
            self._services = []
            return self._services

        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except Exception as e:
            logger.error("Civic services load error: %s", e)
            self._services = []
            return self._services

        self._services = [s for s in raw if self._is_valid(s)]
        return self._services

    @staticmethod
    def _is_valid(service: Dict[str, Any]) -> bool:
        """Drop records that are missing fields or use tags outside the taxonomy."""
        if not isinstance(service, dict):
            return False

        service_id = service.get("id")
        for field in ("id", "name", "url"):
            if not service.get(field):
                logger.warning("Civic service %r is missing '%s'", service_id, field)
                return False

        problems = service.get("problems") or []
        platforms = service.get("platforms") or []
        jurisdiction = service.get("jurisdiction")

        unknown = [p for p in problems if p not in PROBLEM_DOMAINS]
        unknown += [p for p in platforms if p not in PLATFORMS]
        if unknown or not problems or not platforms:
            logger.warning("Civic service %r has invalid tags: %s", service_id, unknown)
            return False

        if jurisdiction not in JURISDICTIONS:
            logger.warning(
                "Civic service %r has invalid jurisdiction: %r",
                service_id,
                jurisdiction,
            )
            return False

        return True

    # ---------- READ ----------
    def get_all(self) -> List[Dict[str, Any]]:
        return list(self._load())

    def get_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        service_id = (service_id or "").strip().lower()
        for service in self._load():
            if service["id"].lower() == service_id:
                return service
        return None

    def get_problems(self) -> List[Dict[str, Any]]:
        """Guided-flow questions, each with how many services answer it."""
        services = self._load()
        problems = []
        for question in GUIDED_QUESTIONS:
            count = sum(1 for s in services if question["id"] in s["problems"])
            problems.append({**question, "service_count": count})
        return problems

    def find(
        self,
        problem: Optional[str] = None,
        platform: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Filter the catalogue. Unknown tag values raise ValueError."""
        results = self._load()

        if problem:
            problem = problem.strip().lower()
            if problem not in PROBLEM_DOMAINS:
                raise ValueError(f"Unknown problem: {problem}")
            results = [s for s in results if problem in s["problems"]]

        if platform:
            platform = platform.strip().lower()
            if platform not in PLATFORMS:
                raise ValueError(f"Unknown platform: {platform}")
            results = [s for s in results if platform in s["platforms"]]

        if jurisdiction:
            jurisdiction = jurisdiction.strip().lower()
            if jurisdiction not in JURISDICTIONS:
                raise ValueError(f"Unknown jurisdiction: {jurisdiction}")
            results = [s for s in results if s["jurisdiction"] == jurisdiction]

        if query:
            needle = query.strip().lower()
            results = [
                s
                for s in results
                if needle in s["name"].lower()
                or needle in (s.get("description") or "").lower()
                or needle in (s.get("agency") or "").lower()
            ]

        limit = max(1, min(limit, 100))
        return results[:limit]
