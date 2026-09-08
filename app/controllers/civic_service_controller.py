"""
Civic Service Controller

Business logic for the Citizens' Awareness government service finder.
All data flows through CivicServiceFinder (reads civic_services.json).
"""

from typing import Any, Dict, Optional

from app.services.civic_service_finder import CivicServiceFinder

# Singleton service instance
_service = CivicServiceFinder()


class CivicServiceController:
    """Controller for civic service operations."""

    def __init__(self) -> None:
        self.service = _service

    def get_problems(self) -> Dict[str, Any]:
        problems = self.service.get_problems()
        return {"total": len(problems), "problems": problems}

    def find(
        self,
        problem: Optional[str] = None,
        platform: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        query: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        results = self.service.find(
            problem=problem,
            platform=platform,
            jurisdiction=jurisdiction,
            query=query,
            limit=limit,
        )
        return {
            "problem": problem,
            "total": len(results),
            "services": results,
        }

    def get_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        return self.service.get_by_id(service_id)
