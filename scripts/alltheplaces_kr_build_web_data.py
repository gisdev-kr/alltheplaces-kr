#!/usr/bin/env python3
"""Copy the validated monthly bundle into Vite's static data directory."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "dist" / "latest"
TARGET = ROOT / "web" / "public" / "data" / "latest"


def main() -> int:
    TARGET.mkdir(parents=True, exist_ok=True)
    statuses: dict[str, str] = {}
    with (SOURCE / "osm_mapping.csv").open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            statuses[row["poi_id"]] = row["match_status"]
    collection = json.loads((SOURCE / "pois.geojson").read_text(encoding="utf-8"))
    for feature in collection.get("features", []):
        feature.setdefault("properties", {})["match_status"] = statuses.get(str(feature.get("id", "")), "needs_review")
    (TARGET / "pois.geojson").write_text(json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    for name in ("pois.ndgeojson", "pois.csv", "pois.osm", "osm_mapping.csv", "osm_candidates.osm", "metadata.json"):
        shutil.copy2(SOURCE / name, TARGET / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

