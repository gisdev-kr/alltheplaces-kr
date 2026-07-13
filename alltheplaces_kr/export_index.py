"""Export and metadata helpers for the Korea wrapper scripts."""

from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from locations.exporters.geojson import mapping
from locations.items import Feature


def read_allowlist(path: Path) -> list[str]:
    spiders = [line.partition("#")[0].strip() for line in path.read_text(encoding="utf-8").splitlines()]
    spiders = [line for line in spiders if line]
    if len(spiders) != len(set(spiders)):
        raise ValueError(f"Duplicate spider names in {path}")
    return spiders


def load_ndgeojson(paths: Iterable[Path]) -> list[dict[str, Any]]:
    features: list[dict[str, Any]] = []
    for path in sorted(paths):
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, 1):
                if not line.strip():
                    continue
                feature = json.loads(line)
                if feature.get("type") != "Feature":
                    raise ValueError(f"{path}:{line_number} is not a GeoJSON Feature")
                features.append(feature)
    return features


def _osm_string(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(part) for part in value)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def geojson_feature_to_item(feature: dict[str, Any]) -> Feature:
    item = Feature()
    properties = dict(feature.get("properties") or {})
    reverse_mapping = {exported: field for field, exported in mapping}
    if ref := properties.pop("ref", None):
        item["ref"] = _osm_string(ref)
    for exported, field in reverse_mapping.items():
        if exported in properties:
            item[field] = _osm_string(properties.pop(exported))
    item["extras"] = {key: _osm_string(value) for key, value in properties.items() if value not in (None, "")}
    if geometry := feature.get("geometry"):
        item["geometry"] = geometry
    return item


def build_metadata(
    features: Sequence[dict[str, Any]], mapping_rows: Sequence[dict[str, Any]], spider_count: int,
    generated_at: str | None = None,
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for row in mapping_rows:
        status = str(row.get("match_status", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "project": "alltheplaces-kr",
        "source": "All the Places-derived Scrapy run",
        "country": "KR",
        "spider_count": spider_count,
        "poi_count": len(features),
        "matched_count": status_counts.get("matched", 0),
        "new_candidate_count": status_counts.get("new_candidate", 0),
        "needs_review_count": status_counts.get("needs_review", 0),
        "osm_import_ready": False,
    }


def write_metadata(metadata: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


REQUIRED_DIST_FILES = (
    "pois.geojson", "pois.ndgeojson", "pois.csv", "pois.osm", "metadata.json",
    "osm_mapping.csv", "osm_candidates.osm",
)


def validate_dist(path: Path) -> None:
    missing = [name for name in REQUIRED_DIST_FILES if not (path / name).is_file()]
    if missing:
        raise ValueError(f"Missing dist files: {', '.join(missing)}")
    collection = json.loads((path / "pois.geojson").read_text(encoding="utf-8"))
    metadata = json.loads((path / "metadata.json").read_text(encoding="utf-8"))
    if collection.get("type") != "FeatureCollection":
        raise ValueError("pois.geojson is not a FeatureCollection")
    if metadata.get("poi_count") != len(collection.get("features", [])):
        raise ValueError("metadata poi_count does not match pois.geojson")

