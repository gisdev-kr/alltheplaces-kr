"""Discover upstream spiders that may emit Korean locations.

Discovery is intentionally advisory.  A source-code signal is useful for finding
multi-country spiders, but the reviewed allowlist remains the execution boundary.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SpiderCandidate:
    name: str
    path: Path
    signals: tuple[str, ...]


def _spider_name(tree: ast.AST) -> str | None:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        value = node.value
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        if any(isinstance(target, ast.Name) and target.id == "name" for target in targets):
            return value.value
    return None


def _signals(path: Path, tree: ast.AST) -> tuple[str, ...]:
    found: set[str] = set()
    if path.stem.endswith("_kr"):
        found.add("filename:_kr")
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id.endswith("_KR"):
            found.add(f"identifier:{node.id}")
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value.strip()
        lowered = value.casefold()
        if lowered in {"kr", "ko-kr", "en-kr"}:
            found.add(f"locale:{value}")
        elif "korea" in lowered:
            found.add("text:korea")
        elif ".co.kr" in lowered:
            found.add("domain:.co.kr")
    return tuple(sorted(found))


def discover_korea_spiders(spider_root: Path) -> list[SpiderCandidate]:
    candidates: list[SpiderCandidate] = []
    for path in sorted(spider_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        name = _spider_name(tree)
        signals = _signals(path, tree)
        if name and signals:
            candidates.append(SpiderCandidate(name=name, path=path, signals=signals))
    return sorted(candidates, key=lambda candidate: candidate.name)
