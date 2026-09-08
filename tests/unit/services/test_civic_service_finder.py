"""Unit tests for the civic service finder (Citizens' Awareness module)."""

import json
from pathlib import Path

import pytest

from app.schemas.civic_services import GUIDED_QUESTIONS
from app.services.civic_service_finder import CivicServiceFinder


@pytest.fixture
def finder(tmp_path: Path) -> CivicServiceFinder:
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
                },
                {
                    "id": "swachhata-app",
                    "name": "Swachhata App",
                    "description": "Report garbage in your street.",
                    "url": "https://swachh.city",
                    "agency": "MoHUA",
                    "problems": ["civic-complaint"],
                    "platforms": ["android", "web"],
                    "jurisdiction": "state",
                },
                {
                    "id": "bad-tags",
                    "name": "Unknown Tag Service",
                    "url": "https://example.gov.in",
                    "problems": ["not-a-real-problem"],
                    "platforms": ["web"],
                    "jurisdiction": "central",
                },
                {
                    "id": "missing-url",
                    "name": "No URL Service",
                    "problems": ["rti"],
                    "platforms": ["web"],
                    "jurisdiction": "central",
                },
            ]
        ),
        encoding="utf-8",
    )
    return CivicServiceFinder(data_dir=data_dir)


@pytest.mark.unit
class TestCivicServiceFinder:
    def test_invalid_records_are_dropped(self, finder: CivicServiceFinder) -> None:
        ids = [s["id"] for s in finder.get_all()]
        assert ids == ["rti-online", "swachhata-app"]

    def test_missing_data_file_returns_empty(self, tmp_path: Path) -> None:
        assert CivicServiceFinder(data_dir=tmp_path / "nope").get_all() == []

    def test_get_by_id(self, finder: CivicServiceFinder) -> None:
        assert finder.get_by_id("RTI-Online")["name"] == "RTI Online"
        assert finder.get_by_id("does-not-exist") is None

    def test_get_problems_lists_all_questions_with_counts(
        self, finder: CivicServiceFinder
    ) -> None:
        problems = finder.get_problems()
        assert len(problems) == len(GUIDED_QUESTIONS)
        by_id = {p["id"]: p for p in problems}
        assert by_id["rti"]["service_count"] == 1
        assert by_id["corruption"]["service_count"] == 0
        assert by_id["rti"]["prompt"]

    def test_find_by_problem(self, finder: CivicServiceFinder) -> None:
        results = finder.find(problem="civic-complaint")
        assert [s["id"] for s in results] == ["swachhata-app"]

    def test_find_by_platform_and_jurisdiction(
        self, finder: CivicServiceFinder
    ) -> None:
        assert len(finder.find(platform="web")) == 2
        assert [s["id"] for s in finder.find(platform="android")] == ["swachhata-app"]
        assert [s["id"] for s in finder.find(jurisdiction="central")] == ["rti-online"]

    def test_find_by_query(self, finder: CivicServiceFinder) -> None:
        assert [s["id"] for s in finder.find(query="garbage")] == ["swachhata-app"]
        assert [s["id"] for s in finder.find(query="dopt")] == ["rti-online"]
        assert finder.find(query="nothing here") == []

    def test_find_limit(self, finder: CivicServiceFinder) -> None:
        assert len(finder.find(limit=1)) == 1

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"problem": "unknown-problem"},
            {"platform": "fax"},
            {"jurisdiction": "galactic"},
        ],
    )
    def test_find_rejects_unknown_tags(
        self, finder: CivicServiceFinder, kwargs: dict
    ) -> None:
        with pytest.raises(ValueError):
            finder.find(**kwargs)


@pytest.mark.unit
class TestCuratedDataset:
    def test_shipped_dataset_is_valid(self) -> None:
        services = CivicServiceFinder().get_all()
        assert len(services) >= 10
        assert len(services) == len({s["id"] for s in services})
        for service in services:
            assert service["url"].startswith("https://")
            assert service["description"]
