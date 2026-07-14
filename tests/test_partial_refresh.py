import json

from scripts.alltheplaces_kr_build_latest import merge_baseline_features


def feature(spider: str, ref: str) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [127.0, 37.5]},
        "properties": {"@spider": spider, "ref": ref, "addr:country": "KR"},
    }


def test_partial_refresh_replaces_only_selected_spider_records(tmp_path):
    baseline = tmp_path / "pois.geojson"
    baseline.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    feature("paris_baguette_kr", "keep"),
                    feature("jaguar_land_rover", "old"),
                ],
            }
        ),
        encoding="utf-8",
    )

    merged = merge_baseline_features(
        [feature("jaguar_land_rover_kr", "new")],
        baseline,
        {"jaguar_land_rover", "jaguar_land_rover_kr"},
    )

    assert [(item["properties"]["@spider"], item["properties"]["ref"]) for item in merged] == [
        ("paris_baguette_kr", "keep"),
        ("jaguar_land_rover_kr", "new"),
    ]
