"""Review-only OSM mapping interfaces. This module cannot write to the OSM API."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Sequence

from locations.exporters.osm import OSMExporter

from alltheplaces_kr.export_index import geojson_feature_to_item

MatchStatus = Literal["matched", "new_candidate", "needs_review", "do_not_import", "retired_source"]
MATCH_STATUSES = {"matched", "new_candidate", "needs_review", "do_not_import", "retired_source"}
MAPPING_COLUMNS = (
    "poi_id", "spider", "ref", "brand_wikidata", "osm_type", "osm_id", "osm_version",
    "match_status", "match_confidence", "match_method", "distance_m", "name_similarity",
    "matched_at", "changeset_id", "notes",
)


@dataclass(frozen=True)
class OSMMapping:
    poi_id: str
    spider: str
    ref: str
    brand_wikidata: str = ""
    osm_type: str = ""
    osm_id: str = ""
    osm_version: str = ""
    match_status: MatchStatus = "needs_review"
    match_confidence: str = ""
    match_method: str = ""
    distance_m: str = ""
    name_similarity: str = ""
    matched_at: str = ""
    changeset_id: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.match_status not in MATCH_STATUSES:
            raise ValueError(f"Unsupported OSM mapping status: {self.match_status}")


def mapping_for_unmatched_feature(feature: dict[str, Any]) -> OSMMapping:
    properties = feature.get("properties") or {}
    return OSMMapping(
        poi_id=str(feature.get("id", "")), spider=str(properties.get("@spider", "")),
        ref=str(properties.get("ref", "")), brand_wikidata=str(properties.get("brand:wikidata", "")),
        match_status="needs_review", matched_at=datetime.now(timezone.utc).isoformat(),
        notes="No OSM comparison dataset supplied; manual conflation required.",
    )


def build_review_mappings(features: Sequence[dict[str, Any]]) -> list[OSMMapping]:
    return [mapping_for_unmatched_feature(feature) for feature in features]


def write_mapping_csv(rows: Sequence[OSMMapping], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=MAPPING_COLUMNS, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def read_mapping_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))
    for row in rows:
        if row.get("match_status") not in MATCH_STATUSES:
            raise ValueError(f"Unsupported OSM mapping status: {row.get('match_status')}")
    return rows


def write_osm_features(features: Sequence[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        exporter = OSMExporter(output)
        exporter.next_id = -1
        exporter.start_exporting()
        for feature in features:
            exporter.export_item(geojson_feature_to_item(feature))
        exporter.finish_exporting()


def write_osm_candidates(features: Sequence[dict[str, Any]], rows: Sequence[OSMMapping], path: Path) -> None:
    by_id = {row.poi_id: row for row in rows}
    candidates = [feature for feature in features if (row := by_id.get(str(feature.get("id", "")))) and row.match_status == "new_candidate"]
    write_osm_features(candidates, path)

