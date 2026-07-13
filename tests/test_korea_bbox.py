from alltheplaces_kr.korea import is_in_south_korea_bbox, is_korea_geojson_feature


def test_seoul_is_inside_korea_guard_box():
    assert is_in_south_korea_bbox(37.5665, 126.9780)


def test_foreign_coordinates_are_rejected():
    assert not is_in_south_korea_bbox(35.6762, 139.6503)


def test_explicit_foreign_country_is_rejected_even_without_geometry():
    assert not is_korea_geojson_feature({"type": "Feature", "properties": {"addr:country": "JP"}, "geometry": None})

