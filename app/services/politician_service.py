import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from app.agents.citation_audit_merge import politician_citation_coverage_summary
from app.core.slugify import short_id_from_uuid, slugify

logger = logging.getLogger(__name__)

ElectionType = Literal["MP", "MLA"]

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------- NORMALIZE ----------
def normalize(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z ]", "", name)
    return name.strip()


class PoliticianService:

    def __init__(self, data_dir: Optional[Path] = None) -> None:
        self._data_dir = Path(data_dir) if data_dir else _DATA_DIR
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._slugs_ensured: bool = False
        self._by_id: Dict[str, Dict[str, Any]] = {}
        self._by_slug: Dict[str, Dict[str, Any]] = {}
        self._by_short_id: Dict[str, Dict[str, Any]] = {}

        self._perf_map = self._load_performance()

    # ---------- LOAD PERFORMANCE ----------
    def _load_performance(self) -> Dict[str, Dict]:
        path = self._data_dir / "performance.json"

        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {normalize(p["name"]): p["performance"] for p in data}

        except Exception as e:
            logger.error("Performance load error: %s", e)
            return {}

    # ---------- ADD PERFORMANCE ----------
    def _attach_performance(self, p: Dict[str, Any]) -> Dict[str, Any]:
        name = normalize(p.get("name", ""))

        p["performance"] = self._perf_map.get(
            name, {"attendance": 0, "questions": 0, "debates": 0}
        )

        return p

    # ---------- ADD METADATA ----------
    def _attach_metadata(self, p: Dict[str, Any]) -> Dict[str, Any]:
        p["updated_at"] = p.get("lastUpdated")
        p.update(politician_citation_coverage_summary(p))
        return p

    # ---------- SLUG ----------
    def _ensure_slugs(self) -> None:
        if self._slugs_ensured:
            return

        mp_records = self._load("MP")
        mla_records = self._load("MLA")
        all_records = mp_records + mla_records

        base_counts: Dict[str, int] = {}

        for p in all_records:
            base = slugify(p.get("name", "")) or "politician"
            base_counts[base] = base_counts.get(base, 0) + 1

        self._by_id = {}
        self._by_slug = {}
        self._by_short_id = {}

        for p in all_records:
            pid = str(p.get("id", ""))
            base = slugify(p.get("name", "")) or "politician"
            short_id = short_id_from_uuid(pid) or "00000000"

            slug = base if base_counts[base] <= 1 else f"{base}-{short_id}"
            p["slug"] = slug

            if pid:
                self._by_id[pid] = p
                self._by_short_id[short_id] = p
            self._by_slug[slug] = p

        self._slugs_ensured = True

    def _attach_slugs_to_records(self, records: List[Dict[str, Any]]) -> None:
        """Fresh :meth:`_load` dicts omit ``slug``; copy from the slug index."""
        for p in records:
            pid = str(p.get("id", ""))
            if pid and pid in self._by_id:
                p["slug"] = self._by_id[pid].get("slug")

    # ---------- LOAD ----------
    def _path(self, election_type: ElectionType) -> Path:
        return self._data_dir / f"{election_type.lower()}.json"

    def _load(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        fp = self._path(election_type)

        if not fp.exists():
            return []

        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------- API ----------
    def get_all(self, election_type: ElectionType) -> List[Dict[str, Any]]:
        self._ensure_slugs()
        data = self._load(election_type)
        self._attach_slugs_to_records(data)

        return [self._attach_metadata(self._attach_performance(p)) for p in data]

    def get_all_politicians(self) -> List[Dict[str, Any]]:
        self._ensure_slugs()
        data = self._load("MP") + self._load("MLA")
        self._attach_slugs_to_records(data)

        return [self._attach_metadata(self._attach_performance(p)) for p in data]

    def get_by_id(self, politician_id: str) -> Optional[Dict[str, Any]]:
        self._ensure_slugs()
        pid = str(politician_id).strip()
        p = self._by_id.get(pid) or self._by_id.get(pid.lower())

        return self._attach_metadata(self._attach_performance(p)) if p else None

    def get_by_slug(self, politician_slug: str) -> Optional[Dict[str, Any]]:
        self._ensure_slugs()
        slug = str(politician_slug).strip()
        p = self._by_slug.get(slug)

        if not p:
            short_match = re.search(r"-([0-9a-fA-F]{8})$", slug)
            if short_match:
                p = self._by_short_id.get(short_match.group(1).lower())

        return self._attach_metadata(self._attach_performance(p)) if p else None

    def get_by_party(self, party: str, election_type: Optional[str] = None):
        self._ensure_slugs()
        party_l = party.lower()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )
        self._attach_slugs_to_records(data)

        results = []

        for p in data:
            elections = (p.get("political_background") or {}).get("elections") or []
            if not elections:
                continue

            # ✅ latest election ONLY
            latest = max(elections, key=lambda x: x.get("year", 0))
            current_party = (latest.get("party") or "").lower()

            if current_party == party_l:
                results.append(self._attach_performance(p))

        return results

    def search(
        self,
        query: str,
        *,
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        party: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:

        self._ensure_slugs()
        q = query.lower().strip()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )
        self._attach_slugs_to_records(data)

        state_l = state.strip().lower() if state and state.strip() else None
        party_l = party.strip().lower() if party and party.strip() else None

        results: List[Dict[str, Any]] = []

        for p in data:
            if q not in p.get("name", "").lower():
                continue

            if state_l is not None:
                if (p.get("state") or "").lower() != state_l:
                    continue

            if party_l is not None:
                elections = (p.get("political_background") or {}).get("elections") or []
                if party_l is not None:
                    elections = (p.get("political_background") or {}).get("elections") or []
                    if not elections:
                        continue

                    latest = max(elections, key=lambda x: x.get("year", 0))
                    latest_party = (latest.get("party") or "").lower()

                    if latest_party != party_l:
                        continue

            results.append(self._attach_metadata(self._attach_performance(p)))

            if len(results) >= limit:
                break

        return results

    def update_politician(self, politician_id: str, updates: Dict[str, Any]) -> bool:
        """Merge ``updates`` into the politician record and persist ``mp.json`` / ``mla.json``.

        Returns True if a record was found and written. Keeps :meth:`_by_id` in sync when
        slug indexing has already been built.
        """
        if not politician_id or not updates:
            return False

        pid = str(politician_id)

        for election_type in ("MP", "MLA"):
            path = self._path(election_type)
            if not path.exists():
                continue

            records = self._load(election_type)
            for rec in records:
                if str(rec.get("id")) != pid:
                    continue

                for key, value in updates.items():
                    rec[key] = value

                now = (
                    datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.")
                    + f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"
                )
                rec["lastUpdated"] = now

                try:
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(records, f, indent=2, ensure_ascii=False)
                        f.write("\n")
                except OSError as exc:
                    logger.error("Failed to write politician data %s: %s", path, exc)
                    return False

                if self._slugs_ensured and pid in self._by_id:
                    for key, value in updates.items():
                        self._by_id[pid][key] = value
                    self._by_id[pid]["lastUpdated"] = now

                return True

        logger.warning("Politician not found for update: %s", pid)
        return False

        # ---------- FILTERS ----------

    def get_by_state(
        self,
        state: str,
        election_type: Optional[ElectionType] = None,
    ) -> List[Dict[str, Any]]:

        self._ensure_slugs()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        self._attach_slugs_to_records(data)

        state_l = state.strip().lower()

        return [
            self._attach_metadata(self._attach_performance(p))
            for p in data
            if (p.get("state") or "").lower() == state_l
        ]

    def get_by_party(
        self,
        party: str,
        election_type: Optional[ElectionType] = None,
    ) -> List[Dict[str, Any]]:

        self._ensure_slugs()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        self._attach_slugs_to_records(data)

        party_l = party.strip().lower()

        results: List[Dict[str, Any]] = []

        for p in data:
            elections = (p.get("political_background") or {}).get("elections") or []

            if any((e.get("party") or "").lower() == party_l for e in elections):
                results.append(self._attach_metadata(self._attach_performance(p)))

        return results

    # ---------- AGGREGATIONS ----------

    def get_states(
        self,
        election_type: Optional[ElectionType] = None,
    ) -> List[str]:

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        states = {(p.get("state") or "").strip() for p in data if p.get("state")}

        return sorted(states)

    def get_parties(
        self,
        election_type: Optional[ElectionType] = None,
    ) -> List[str]:

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        parties = set()

        for p in data:
            elections = (p.get("political_background") or {}).get("elections") or []

            for e in elections:
                party = (e.get("party") or "").strip()

                if party:
                    parties.add(party)

        return sorted(parties)

    def stats(
        self,
        election_type: Optional[ElectionType] = None,
    ) -> Dict[str, Any]:

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )

        return {
            "total_politicians": len(data),
            "states": len(self.get_states(election_type)),
            "parties": len(self.get_parties(election_type)),
        }

    # ---------- CATALOG (SEO) ----------

    _CATALOG_FIELDS = ("id", "slug", "name", "type", "state", "constituency", "photo")

    @staticmethod
    def _latest_party(p: Dict[str, Any]) -> Optional[str]:
        """Latest (first listed) party name from a politician's election history."""
        elections = (p.get("political_background") or {}).get("elections") or []
        for e in elections:
            party = (e.get("party") or "").strip()
            if party:
                return party
        return None

    def _to_catalog_record(self, p: Dict[str, Any]) -> Dict[str, Any]:
        record = {k: p.get(k) for k in self._CATALOG_FIELDS}
        record["party"] = self._latest_party(p)
        return record

    def list_catalog(
        self,
        *,
        page: int = 1,
        per_page: int = 48,
        election_type: Optional[ElectionType] = None,
        state: Optional[str] = None,
        q: Optional[str] = None,
        parties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Paginated lightweight politician list for public SEO directory."""
        self._ensure_slugs()

        data = (
            self._load(election_type)
            if election_type
            else self._load("MP") + self._load("MLA")
        )
        self._attach_slugs_to_records(data)

        state_l = state.strip().lower() if state and state.strip() else None
        q_l = q.strip().lower() if q and q.strip() else None
        party_set = (
            {x.strip().lower() for x in parties if x and x.strip()} if parties else None
        )

        filtered: List[Dict[str, Any]] = []
        for p in data:
            if state_l is not None and (p.get("state") or "").lower() != state_l:
                continue
            if q_l is not None and q_l not in (p.get("name") or "").lower():
                continue
            if party_set is not None:
                rec_party = (self._latest_party(p) or "").lower()
                if rec_party not in party_set:
                    continue
            filtered.append(p)

        total = len(filtered)
        page = max(1, page)
        per_page = max(1, min(per_page, 100))
        start = (page - 1) * per_page
        page_items = filtered[start : start + per_page]

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "politicians": [self._to_catalog_record(p) for p in page_items],
        }

    def sitemap_entries(self) -> List[Dict[str, str]]:
        """Lightweight slug entries for sitemap generation."""
        self._ensure_slugs()
        data = self._load("MP") + self._load("MLA")
        self._attach_slugs_to_records(data)

        entries: List[Dict[str, str]] = []
        seen: set[str] = set()
        for p in data:
            slug = (p.get("slug") or p.get("id") or "").strip()
            if not slug or slug in seen:
                continue
            seen.add(slug)
            entries.append(
                {
                    "slug": slug,
                    "type": str(p.get("type") or ""),
                }
            )
        return entries
