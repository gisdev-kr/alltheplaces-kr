from alltheplaces_kr.export_index import build_metadata


def test_monthly_metadata_counts_mapping_statuses():
    features = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    rows = [{"match_status": "matched"}, {"match_status": "new_candidate"}, {"match_status": "needs_review"}]
    metadata = build_metadata(features, rows, spider_count=13, generated_at="2026-07-01T00:00:00+00:00")
    assert metadata == {
        "generated_at": "2026-07-01T00:00:00+00:00",
        "project": "alltheplaces-kr",
        "source": "All the Places-derived Scrapy run",
        "country": "KR",
        "spider_count": 13,
        "poi_count": 3,
        "matched_count": 1,
        "new_candidate_count": 1,
        "needs_review_count": 1,
        "osm_import_ready": False,
    }

