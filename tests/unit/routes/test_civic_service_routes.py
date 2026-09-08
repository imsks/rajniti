"""Unit tests for civic service API routes (Citizens' Awareness module)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.services.civic_service_finder import CivicServiceFinder


@pytest.fixture
def civic_finder(tmp_path: Path) -> CivicServiceFinder:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "civic_services.json").write_text(
        json.dumps(
            [
                {
                    "id": "rti-online",
                    "name": "RTI Online",
                    "description": "File an RTI request online.",
                    "url": "https://rtionline.gov.in",
                    "agency": "DoPT",
                    "problems": ["rti"],
                    "platforms": ["web"],
                    "jurisdiction": "central",
                }
            ]
        ),
        encoding="utf-8",
    )
    return CivicServiceFinder(data_dir=data_dir)


@pytest.fixture
def client(app, civic_finder: CivicServiceFinder):
    with patch("app.routes.api_routes.civic_ctrl.service", civic_finder):
        with app.test_client() as c:
            yield c


@pytest.mark.unit
class TestCivicServiceRoutes:
    def test_list_problems(self, client) -> None:
        response = client.get("/api/v1/civic-services/problems")
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["total"] == len(data["problems"])
        rti = next(p for p in data["problems"] if p["id"] == "rti")
        assert rti["service_count"] == 1
        assert rti["prompt"]

    def test_list_services_by_problem(self, client) -> None:
        response = client.get("/api/v1/civic-services?problem=rti")
        assert response.status_code == 200
        data = response.get_json()["data"]
        assert data["total"] == 1
        assert data["services"][0]["name"] == "RTI Online"

    def test_list_services_unknown_problem_400(self, client) -> None:
        response = client.get("/api/v1/civic-services?problem=aliens")
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_get_service_by_id(self, client) -> None:
        response = client.get("/api/v1/civic-services/rti-online")
        assert response.status_code == 200
        assert response.get_json()["data"]["url"] == "https://rtionline.gov.in"

    def test_get_service_by_id_404(self, client) -> None:
        response = client.get("/api/v1/civic-services/does-not-exist")
        assert response.status_code == 404
        assert response.get_json()["success"] is False
