#!/usr/bin/env python3
"""Generate Jekyll category and brand reports from monthly ATP output."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alltheplaces_kr.schema_reports import build_schema_reports


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_collection(directory: Path, documents: list[tuple[str, str]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for old_page in directory.glob("*.md"):
        old_page.unlink()
    for filename, body in documents:
        (directory / filename).write_text(body, encoding="utf-8")


def build_portal_reports(dataset: Path, metadata_path: Path, nsi_path: Path, portal: Path) -> tuple[dict, list[dict]]:
    coverage, brands = build_schema_reports(load_json(dataset), load_json(nsi_path), load_json(metadata_path))
    data_root = portal / "_data" / "alltheplaces"
    write_json(data_root / "coverage.json", coverage)
    write_json(data_root / "brands.json", brands)

    category_documents = []
    for category in coverage["categories"]:
        title = f"한국 {category['path']} POI 스키마 리포트"
        category_documents.append(
            (
                f"{category['slug']}.md",
                "---\n"
                "layout: atp_category\n"
                f"title: {title}\n"
                f"description: 최신 All the Places KR 출력이 {category['path']} NSI 태그 스키마를 얼마나 충족하는지 보여줍니다.\n"
                f"coverage_path: {category['path']}\n"
                f"permalink: /categories/{category['path']}/\n"
                "---\n",
            )
        )
    replace_collection(portal / "_alltheplaces_categories", category_documents)

    brand_documents = []
    for brand in brands:
        brand_documents.append(
            (
                f"{brand['slug']}.md",
                "---\n"
                "layout: atp_brand\n"
                f"title: {brand['name_ko']} POI 데이터 리포트 | All the Places KR\n"
                f"description: {brand['name_ko']} POI 수집 결과와 NSI 스키마 충족도, 데이터 품질을 확인합니다.\n"
                f"brand_slug: {brand['slug']}\n"
                "---\n",
            )
        )
    replace_collection(portal / "_alltheplaces_brands", brand_documents)
    return coverage, brands


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--nsi", type=Path, required=True)
    parser.add_argument("--portal", type=Path, default=PROJECT_ROOT / "portal")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    coverage, brands = build_portal_reports(args.dataset, args.metadata, args.nsi, args.portal)
    print(
        json.dumps(
            {
                "categories": len(coverage["categories"]),
                "brands": len(brands),
                **coverage["summary"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
