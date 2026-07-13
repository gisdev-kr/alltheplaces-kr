#!/usr/bin/env python3
"""Combine ATP per-spider NDGeoJSON exports into the monthly KR bundle."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scrapy.exporters import CsvItemExporter

from alltheplaces_kr.export_index import build_metadata, geojson_feature_to_item, load_ndgeojson, read_allowlist, validate_dist, write_metadata
from alltheplaces_kr.korea import is_korea_geojson_feature
from alltheplaces_kr.osm_conflation import build_review_mappings, write_mapping_csv, write_osm_candidates, write_osm_features

DEFAULT_RAW_DIR = PROJECT_ROOT / "dist" / "raw"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "dist" / "latest"
DEFAULT_ALLOWLIST = PROJECT_ROOT / "alltheplaces_kr" / "spiders.txt"


def write_geojson(features: Sequence[dict[str, Any]], output: Path, spider_count: int) -> None:
    collection = {"type": "FeatureCollection", "dataset_attributes": {"project": "alltheplaces-kr", "country": "KR", "spider_count": spider_count}, "features": features}
    output.write_text(json.dumps(collection, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def write_ndgeojson(features: Sequence[dict[str, Any]], output: Path) -> None:
    with output.open("w", encoding="utf-8") as destination:
        for feature in features:
            destination.write(json.dumps(feature, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_csv(features: Sequence[dict[str, Any]], output: Path) -> None:
    with output.open("wb") as destination:
        exporter = CsvItemExporter(destination, encoding="utf-8", include_headers_line=True)
        exporter.start_exporting()
        for feature in features:
            exporter.export_item(geojson_feature_to_item(feature))
        exporter.finish_exporting()


def build_latest(raw_dir: Path, output_dir: Path, allowlist: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    raw_paths = list(raw_dir.glob("*.ndgeojson"))
    if not raw_paths:
        raise ValueError(f"No ATP NDGeoJSON exports found in {raw_dir}")
    features = [feature for feature in load_ndgeojson(raw_paths) if is_korea_geojson_feature(feature)]
    spider_count = len(read_allowlist(allowlist))
    write_geojson(features, output_dir / "pois.geojson", spider_count)
    write_ndgeojson(features, output_dir / "pois.ndgeojson")
    write_csv(features, output_dir / "pois.csv")
    write_osm_features(features, output_dir / "pois.osm")
    mappings = build_review_mappings(features)
    write_mapping_csv(mappings, output_dir / "osm_mapping.csv")
    write_osm_candidates(features, mappings, output_dir / "osm_candidates.osm")
    metadata = build_metadata(features, [mapping.__dict__ for mapping in mappings], spider_count)
    write_metadata(metadata, output_dir / "metadata.json")
    validate_dist(output_dir)
    return metadata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.validate_only:
        validate_dist(args.output_dir)
        print(f"validated {args.output_dir}")
        return 0
    print(json.dumps(build_latest(args.raw_dir, args.output_dir, args.allowlist), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

