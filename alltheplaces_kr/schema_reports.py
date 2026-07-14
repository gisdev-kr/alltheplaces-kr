"""Build data-driven NSI schema reports from final ATP GeoJSON output.

The ATP NSI pipeline resolves an entry from Wikidata, category and location,
then copies missing NSI tags without overwriting source values.  These reports
measure the final exported records against that exact NSI tag contract.  They
do not treat the existence of a spider as category coverage.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Any, Iterable
from unicodedata import normalize


CATEGORY_KEYS = (
    "amenity",
    "shop",
    "tourism",
    "leisure",
    "healthcare",
    "office",
    "craft",
    "man_made",
    "highway",
    "railway",
    "aeroway",
)


def percentage(numerator: int, denominator: int) -> float | None:
    return round(numerator * 100 / denominator, 1) if denominator else None


def category_from_properties(properties: dict[str, Any]) -> str:
    for key in CATEGORY_KEYS:
        if value := properties.get(key):
            return f"{key}/{value}"
    return "unclassified"


def nsi_applies_to_korea(entry: dict[str, Any]) -> bool:
    location_set = entry.get("locationSet", {})
    includes = {str(code).removesuffix(".geojson").lower() for code in location_set.get("include", [])}
    excludes = {str(code).removesuffix(".geojson").lower() for code in location_set.get("exclude", [])}
    return ("001" in includes or "kr" in includes) and "kr" not in excludes


def build_nsi_indexes(nsi_document: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    by_id: dict[str, dict[str, Any]] = {}
    by_wikidata: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for group, collection in nsi_document.get("nsi", {}).items():
        if not group.startswith("brands/"):
            continue
        category_path = group.removeprefix("brands/")
        for raw_entry in collection.get("items", []):
            entry = {**raw_entry, "category_path": category_path}
            by_id[entry["id"]] = entry
            if qid := entry.get("tags", {}).get("brand:wikidata"):
                by_wikidata[qid].append(entry)
    return by_id, by_wikidata


def resolve_nsi_entry(
    properties: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_wikidata: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any] | None, str]:
    """Resolve the NSI contract used for reporting.

    A valid pipeline-produced ``nsi_id`` is authoritative.  If it is missing,
    a unique KR-applicable entry with the same Wikidata and category is useful
    as an expected contract, but is explicitly marked as inferred.
    """

    if nsi_id := properties.get("nsi_id"):
        if entry := by_id.get(str(nsi_id)):
            return entry, "nsi_id"

    qid = properties.get("brand:wikidata")
    if not qid:
        return None, "unresolved"
    category_path = category_from_properties(properties)
    candidates = [
        entry
        for entry in by_wikidata.get(str(qid), [])
        if entry["category_path"] == category_path and nsi_applies_to_korea(entry)
    ]
    return (candidates[0], "wikidata_category_kr") if len(candidates) == 1 else (None, "unresolved")


def tag_assessment(properties: dict[str, Any], entry: dict[str, Any] | None) -> dict[str, Any]:
    if not entry:
        return {
            "required": 0,
            "present": 0,
            "exact": 0,
            "missing": [],
            "mismatched": [],
        }

    expected = entry.get("tags", {})
    missing: list[str] = []
    mismatched: list[dict[str, str]] = []
    present = 0
    exact = 0
    for key, expected_value in expected.items():
        actual = properties.get(key)
        if actual is None or actual == "":
            missing.append(key)
            continue
        present += 1
        if str(actual) == str(expected_value):
            exact += 1
        else:
            mismatched.append({"key": key, "expected": str(expected_value), "actual": str(actual)})
    return {
        "required": len(expected),
        "present": present,
        "exact": exact,
        "missing": missing,
        "mismatched": mismatched,
    }


def _ascii_slug(value: str) -> str:
    value = normalize("NFKD", value).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"(^-|-$)", "", re.sub(r"[^a-z0-9]+", "-", value))


def _first(properties: Iterable[dict[str, Any]], *keys: str) -> str:
    for key in keys:
        for item in properties:
            if value := item.get(key):
                return str(value)
    return ""


def _rate_fields(target: dict[str, Any]) -> None:
    target["nsi_match_rate"] = percentage(target["nsi_matched_pois"], target["poi_count"])
    target["schema_presence_rate"] = percentage(target["schema_present_checks"], target["schema_required_checks"])
    target["schema_conformity_rate"] = percentage(target["schema_exact_checks"], target["schema_required_checks"])
    target["fully_present_rate"] = percentage(target["fully_present_pois"], target["schema_evaluated_pois"])
    target["fully_conformant_rate"] = percentage(target["fully_conformant_pois"], target["schema_evaluated_pois"])


def build_schema_reports(
    feature_collection: dict[str, Any],
    nsi_document: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    metadata = metadata or {}
    by_id, by_wikidata = build_nsi_indexes(nsi_document)
    assessed: list[dict[str, Any]] = []

    for feature in feature_collection.get("features", []):
        properties = feature.get("properties", {})
        entry, resolution = resolve_nsi_entry(properties, by_id, by_wikidata)
        assessment = tag_assessment(properties, entry)
        category_path = entry["category_path"] if entry else category_from_properties(properties)
        brand_key = str(
            properties.get("brand:wikidata")
            or properties.get("brand")
            or properties.get("@spider")
            or "unknown"
        )
        assessed.append(
            {
                "feature": feature,
                "properties": properties,
                "entry": entry,
                "resolution": resolution,
                "assessment": assessment,
                "category_path": category_path,
                "brand_key": brand_key,
            }
        )

    grouped_brands: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assessed:
        grouped_brands[row["brand_key"]].append(row)

    brands: list[dict[str, Any]] = []
    used_slugs: set[str] = set()
    for brand_key, rows in grouped_brands.items():
        properties = [row["properties"] for row in rows]
        entries = {row["entry"]["id"]: row["entry"] for row in rows if row["entry"]}
        name_ko = _first(properties, "brand:ko", "brand", "name:ko", "name")
        name_en = _first(properties, "brand:en", "brand", "name:en", "name")
        if entries:
            entry_list = list(entries.values())
            name_ko = _first([entry["tags"] for entry in entry_list], "brand:ko", "name:ko") or name_ko
            name_en = _first([entry["tags"] for entry in entry_list], "brand:en", "name:en", "brand") or name_en
        qid = _first(properties, "brand:wikidata")
        slug = _ascii_slug(name_en) or qid.lower() or _ascii_slug(brand_key) or "unknown-brand"
        if slug in used_slugs:
            slug = f"{slug}-{qid.lower() or len(used_slugs) + 1}"
        used_slugs.add(slug)

        required = sum(row["assessment"]["required"] for row in rows)
        present = sum(row["assessment"]["present"] for row in rows)
        exact = sum(row["assessment"]["exact"] for row in rows)
        evaluated = sum(row["assessment"]["required"] > 0 for row in rows)
        missing_fields = Counter(key for row in rows for key in row["assessment"]["missing"])
        mismatch_fields = Counter(item["key"] for row in rows for item in row["assessment"]["mismatched"])
        category_paths = sorted({row["category_path"] for row in rows})
        brand = {
            "slug": slug,
            "brand_key": brand_key,
            "name": name_en or name_ko or brand_key,
            "name_ko": name_ko or name_en or brand_key,
            "brand_wikidata": qid,
            "nsi_ids": sorted(entries),
            "nsi_resolution_methods": dict(Counter(row["resolution"] for row in rows)),
            "category_path": category_paths[0],
            "category_paths": category_paths,
            "poi_count": len(rows),
            "nsi_matched_pois": sum(row["resolution"] == "nsi_id" for row in rows),
            "schema_evaluated_pois": evaluated,
            "schema_required_checks": required,
            "schema_present_checks": present,
            "schema_exact_checks": exact,
            "fully_present_pois": sum(
                row["assessment"]["required"] > 0
                and row["assessment"]["present"] == row["assessment"]["required"]
                for row in rows
            ),
            "fully_conformant_pois": sum(
                row["assessment"]["required"] > 0
                and row["assessment"]["exact"] == row["assessment"]["required"]
                for row in rows
            ),
            "coordinate_rate": percentage(
                sum(bool((row["feature"].get("geometry") or {}).get("coordinates")) for row in rows), len(rows)
            ),
            "address_rate": percentage(
                sum(any(key.startswith("addr:") and value for key, value in row["properties"].items()) for row in rows),
                len(rows),
            ),
            "phone_rate": percentage(sum(bool(row["properties"].get("phone")) for row in rows), len(rows)),
            "website_rate": percentage(sum(bool(row["properties"].get("website")) for row in rows), len(rows)),
            "spiders": sorted({str(row["properties"].get("@spider", "")) for row in rows if row["properties"].get("@spider")}),
            "missing_fields": [{"key": key, "count": count} for key, count in missing_fields.most_common()],
            "mismatch_fields": [{"key": key, "count": count} for key, count in mismatch_fields.most_common()],
            "expected_tag_sets": [
                {"nsi_id": entry["id"], "category_path": entry["category_path"], "tags": entry.get("tags", {})}
                for entry in entries.values()
            ],
            "generated_at": metadata.get("generated_at", ""),
        }
        _rate_fields(brand)
        brand["status"] = (
            "nsi_unresolved"
            if not evaluated
            else "conformant"
            if brand["schema_conformity_rate"] == 100
            else "needs_review"
        )
        brands.append(brand)

    brands.sort(key=lambda brand: (-brand["poi_count"], brand["name"].lower()))
    brand_by_key = {brand["brand_key"]: brand for brand in brands}
    grouped_categories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in assessed:
        grouped_categories[row["category_path"]].append(row)

    categories: list[dict[str, Any]] = []
    for category_path, rows in grouped_categories.items():
        required = sum(row["assessment"]["required"] for row in rows)
        present = sum(row["assessment"]["present"] for row in rows)
        exact = sum(row["assessment"]["exact"] for row in rows)
        evaluated = sum(row["assessment"]["required"] > 0 for row in rows)
        category = {
            "path": category_path,
            "key": category_path.partition("/")[0],
            "value": category_path.partition("/")[2],
            "slug": category_path.replace("/", "-"),
            "url": f"/categories/{category_path}/",
            "poi_count": len(rows),
            "brand_count": len({row["brand_key"] for row in rows}),
            "nsi_matched_pois": sum(row["resolution"] == "nsi_id" for row in rows),
            "schema_evaluated_pois": evaluated,
            "schema_required_checks": required,
            "schema_present_checks": present,
            "schema_exact_checks": exact,
            "fully_present_pois": sum(
                row["assessment"]["required"] > 0
                and row["assessment"]["present"] == row["assessment"]["required"]
                for row in rows
            ),
            "fully_conformant_pois": sum(
                row["assessment"]["required"] > 0
                and row["assessment"]["exact"] == row["assessment"]["required"]
                for row in rows
            ),
            "brand_slugs": sorted({brand_by_key[row["brand_key"]]["slug"] for row in rows}),
        }
        _rate_fields(category)
        categories.append(category)
    categories.sort(key=lambda category: (-category["poi_count"], category["path"]))

    total_required = sum(row["assessment"]["required"] for row in assessed)
    total_present = sum(row["assessment"]["present"] for row in assessed)
    total_exact = sum(row["assessment"]["exact"] for row in assessed)
    nsi_meta = nsi_document.get("_meta", {})
    coverage = {
        "meta": {
            "generated_at": metadata.get("generated_at", ""),
            "nsi_generated_at": nsi_meta.get("generated", ""),
            "nsi_version": nsi_meta.get("version", ""),
            "nsi_url": nsi_meta.get("url", ""),
            "method": "final ATP GeoJSON properties compared with resolved NSI tags",
        },
        "summary": {
            "poi_count": len(assessed),
            "brand_count": len(brands),
            "category_count": len(categories),
            "nsi_matched_pois": sum(row["resolution"] == "nsi_id" for row in assessed),
            "nsi_match_rate": percentage(sum(row["resolution"] == "nsi_id" for row in assessed), len(assessed)),
            "schema_required_checks": total_required,
            "schema_present_checks": total_present,
            "schema_exact_checks": total_exact,
            "schema_presence_rate": percentage(total_present, total_required),
            "schema_conformity_rate": percentage(total_exact, total_required),
        },
        "categories": categories,
    }
    return coverage, brands
