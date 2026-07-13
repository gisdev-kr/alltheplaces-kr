import csv

import pytest

from alltheplaces_kr.osm_conflation import MAPPING_COLUMNS, OSMMapping, write_mapping_csv


def test_mapping_csv_writer_preserves_schema_and_utf8(tmp_path):
    path = tmp_path / "osm_mapping.csv"
    row = OSMMapping(poi_id="설빙-1", spider="sulbing_kr", ref="1", match_status="needs_review", notes="수동 검토")
    write_mapping_csv([row], path)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        assert tuple(reader.fieldnames or ()) == MAPPING_COLUMNS
        assert next(reader)["notes"] == "수동 검토"


def test_mapping_rejects_unknown_status():
    with pytest.raises(ValueError, match="Unsupported OSM mapping status"):
        OSMMapping(poi_id="1", spider="sulbing_kr", ref="1", match_status="auto_import")

