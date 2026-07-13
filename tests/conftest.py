import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATP_ROOT = ROOT / "upstream" / "alltheplaces"
for path in (ROOT, ATP_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

