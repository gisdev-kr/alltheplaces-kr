#!/usr/bin/env python3
"""List upstream spiders with Korea-related source signals for allowlist review."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ATP_SPIDERS = PROJECT_ROOT / "upstream" / "alltheplaces" / "locations" / "spiders"
ALLOWLIST = PROJECT_ROOT / "alltheplaces_kr" / "spiders.txt"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from alltheplaces_kr.spider_selection import discover_korea_spiders


def read_allowlist(path: Path) -> list[str]:
    return [
        line
        for raw_line in path.read_text(encoding="utf-8").splitlines()
        if (line := raw_line.strip()) and not line.startswith("#")
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--unreviewed-only", action="store_true")
    args = parser.parse_args()
    reviewed = set(read_allowlist(ALLOWLIST))
    rows = [
        {
            "name": candidate.name,
            "reviewed": candidate.name in reviewed,
            "signals": list(candidate.signals),
            "path": candidate.path.relative_to(ATP_SPIDERS).as_posix(),
        }
        for candidate in discover_korea_spiders(ATP_SPIDERS)
        if not args.unreviewed_only or candidate.name not in reviewed
    ]
    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            state = "reviewed" if row["reviewed"] else "REVIEW"
            print(f"{state:8} {row['name']:28} {', '.join(row['signals'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
