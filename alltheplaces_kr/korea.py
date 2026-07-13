"""Korea-only validation that complements ATP's cleanup pipelines."""

from dataclasses import dataclass
from typing import Any

from scrapy.exceptions import DropItem

from locations.items import Feature, get_lat_lon


@dataclass(frozen=True)
class KoreaBounds:
    min_lat: float = 33.0
    min_lon: float = 124.5
    max_lat: float = 38.7
    max_lon: float = 132.0

    def contains(self, lat: float, lon: float) -> bool:
        return self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon


SOUTH_KOREA_BOUNDS = KoreaBounds()


def is_in_south_korea_bbox(lat: float | str, lon: float | str, bounds: KoreaBounds = SOUTH_KOREA_BOUNDS) -> bool:
    try:
        return bounds.contains(float(lat), float(lon))
    except (TypeError, ValueError):
        return False


def geojson_feature_coordinates(feature: dict[str, Any]) -> tuple[float, float] | None:
    geometry = feature.get("geometry") or {}
    if geometry.get("type") != "Point":
        return None
    coordinates = geometry.get("coordinates") or []
    if len(coordinates) != 2:
        return None
    try:
        return float(coordinates[1]), float(coordinates[0])
    except (TypeError, ValueError):
        return None


def is_korea_geojson_feature(feature: dict[str, Any]) -> bool:
    properties = feature.get("properties") or {}
    country = properties.get("addr:country")
    if country and str(country).upper() != "KR":
        return False
    coordinates = geojson_feature_coordinates(feature)
    return coordinates is None or is_in_south_korea_bbox(*coordinates)


class KoreaValidationPipeline:
    """Force KR and reject explicitly foreign or out-of-bounds POIs."""

    def process_item(self, item: Feature) -> Feature:
        country = item.get("country")
        if country and str(country).upper() != "KR":
            raise DropItem(f"All the Places KR rejected non-KR country value: {country}")
        item["country"] = "KR"
        if coordinates := get_lat_lon(item):
            if not is_in_south_korea_bbox(*coordinates):
                raise DropItem(f"All the Places KR rejected coordinate outside Korea bounds: {coordinates}")
        return item

