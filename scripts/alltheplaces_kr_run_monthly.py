#!/usr/bin/env python3
"""Run only the reviewed Korea spider allowlist from the pinned ATP checkout."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ATP_ROOT = PROJECT_ROOT / "upstream" / "alltheplaces"
DEFAULT_ALLOWLIST = PROJECT_ROOT / "alltheplaces_kr" / "spiders.txt"
DEFAULT_RAW_DIR = PROJECT_ROOT / "dist" / "raw"
DEFAULT_DIST_DIR = PROJECT_ROOT / "dist" / "latest"
DEFAULT_NSI = ATP_ROOT / "locations" / "data" / "nsi.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alltheplaces_kr.export_index import read_allowlist


def scrapy_environment() -> dict[str, str]:
    environment = os.environ.copy()
    pythonpath = [str(PROJECT_ROOT), str(ATP_ROOT)]
    if environment.get("PYTHONPATH"):
        pythonpath.append(environment["PYTHONPATH"])
    environment["PYTHONPATH"] = os.pathsep.join(pythonpath)
    environment["SCRAPY_SETTINGS_MODULE"] = "alltheplaces_kr.settings"
    return environment


def available_spiders(environment: dict[str, str]) -> set[str]:
    result = subprocess.run(
        [sys.executable, "-m", "scrapy", "list"], cwd=ATP_ROOT, env=environment,
        check=True, capture_output=True, text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def validate_allowlist(spiders: list[str], available: set[str]) -> None:
    missing = sorted(set(spiders) - available)
    if missing:
        raise ValueError(f"Allowlisted spiders are not registered in pinned ATP: {', '.join(missing)}")


def crawl(spiders: list[str], raw_dir: Path, environment: dict[str, str]) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    for old_file in raw_dir.glob("*.ndgeojson"):
        old_file.unlink()
    for index, spider in enumerate(spiders, 1):
        output = raw_dir / f"{spider}.ndgeojson"
        print(f"[{index}/{len(spiders)}] {spider} -> {output}", flush=True)
        subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", spider, "-O", str(output)],
            cwd=ATP_ROOT, env=environment, check=True,
        )


def run_script(name: str, *arguments: str) -> None:
    subprocess.run([sys.executable, str(PROJECT_ROOT / "scripts" / name), *arguments], cwd=PROJECT_ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowlist", type=Path, default=DEFAULT_ALLOWLIST)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--crawl-only", action="store_true")
    parser.add_argument("--list-only", action="store_true", help="Validate and print the allowlist without crawling.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not ATP_ROOT.joinpath("pyproject.toml").is_file():
        raise FileNotFoundError("Missing ATP submodule. Run: git submodule update --init --recursive")
    spiders = read_allowlist(args.allowlist)
    environment = scrapy_environment()
    validate_allowlist(spiders, available_spiders(environment))
    if args.list_only:
        print("\n".join(spiders))
        return 0
    crawl(spiders, args.raw_dir, environment)
    if not args.crawl_only:
        run_script("alltheplaces_kr_build_latest.py", "--raw-dir", str(args.raw_dir))
        run_script("alltheplaces_kr_build_web_data.py")
        run_script(
            "alltheplaces_kr_build_portal_reports.py",
            "--dataset",
            str(DEFAULT_DIST_DIR / "pois.geojson"),
            "--metadata",
            str(DEFAULT_DIST_DIR / "metadata.json"),
            "--nsi",
            str(DEFAULT_NSI),
            "--portal",
            str(PROJECT_ROOT / "portal"),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
