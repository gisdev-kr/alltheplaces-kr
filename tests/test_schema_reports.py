from alltheplaces_kr.schema_reports import build_schema_reports, nsi_applies_to_korea, tag_assessment


NSI = {
    "_meta": {"version": "test", "generated": "2026-07-01T00:00:00Z"},
    "nsi": {
        "brands/amenity/cafe": {
            "items": [
                {
                    "id": "test-cafe-123456",
                    "locationSet": {"include": ["kr"]},
                    "tags": {
                        "amenity": "cafe",
                        "brand": "테스트카페",
                        "brand:wikidata": "Q1",
                        "name": "테스트카페",
                    },
                }
            ]
        }
    },
}


def feature(name: str = "테스트카페", nsi_id: str | None = "test-cafe-123456") -> dict:
    properties = {
        "@spider": "test_cafe_kr",
        "addr:country": "KR",
        "amenity": "cafe",
        "brand": "테스트카페",
        "brand:wikidata": "Q1",
        "name": name,
        "phone": "+82 2-000-0000",
    }
    if nsi_id:
        properties["nsi_id"] = nsi_id
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [127.0, 37.5]}, "properties": properties}


def test_nsi_location_supports_kr_and_global_but_respects_exclusion():
    assert nsi_applies_to_korea({"locationSet": {"include": ["kr"]}})
    assert nsi_applies_to_korea({"locationSet": {"include": ["001"]}})
    assert not nsi_applies_to_korea({"locationSet": {"include": ["001"], "exclude": ["kr"]}})


def test_tag_assessment_separates_presence_from_exact_value():
    entry = NSI["nsi"]["brands/amenity/cafe"]["items"][0]
    assessment = tag_assessment(feature(name="테스트카페 강남점")["properties"], entry)
    assert assessment["required"] == 4
    assert assessment["present"] == 4
    assert assessment["exact"] == 3
    assert assessment["mismatched"] == [{"key": "name", "expected": "테스트카페", "actual": "테스트카페 강남점"}]


def test_reports_measure_output_schema_not_spider_inventory():
    collection = {"type": "FeatureCollection", "features": [feature(), feature(name="강남점")]}
    coverage, brands = build_schema_reports(collection, NSI, {"generated_at": "2026-07-01T00:00:00Z"})
    category = coverage["categories"][0]
    brand = brands[0]

    assert category["brand_count"] == 1
    assert category["poi_count"] == 2
    assert category["schema_presence_rate"] == 100.0
    assert category["schema_conformity_rate"] == 87.5
    assert brand["nsi_match_rate"] == 100.0
    assert brand["mismatch_fields"] == [{"key": "name", "count": 1}]


def test_unique_wikidata_category_kr_can_supply_expected_contract_without_claiming_pipeline_match():
    collection = {"type": "FeatureCollection", "features": [feature(nsi_id=None)]}
    coverage, brands = build_schema_reports(collection, NSI)
    assert coverage["summary"]["nsi_matched_pois"] == 0
    assert brands[0]["schema_evaluated_pois"] == 1
    assert brands[0]["nsi_resolution_methods"] == {"wikidata_category_kr": 1}


def test_unbranded_pois_do_not_become_fake_brand_reports():
    unbranded = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [129.1, 35.2]},
        "properties": {
            "@spider": "jaguar_land_rover",
            "addr:country": "KR",
            "name": "효성 프리미어 모터스 - 부산 센텀",
            "shop": "car_repair",
        },
    }

    coverage, brands = build_schema_reports({"type": "FeatureCollection", "features": [unbranded]}, NSI)

    assert brands == []
    assert coverage["summary"]["brand_count"] == 0
    assert coverage["summary"]["unbranded_pois"] == 1
    assert coverage["categories"][0]["brand_count"] == 0
    assert coverage["categories"][0]["brand_slugs"] == []
