from pathlib import Path

from alltheplaces_kr.export_index import read_allowlist


def test_allowlist_is_official_korea_suffix_only():
    allowlist = read_allowlist(Path(__file__).parents[1] / "alltheplaces_kr" / "spiders.txt")
    assert len(allowlist) == 13
    assert "kr_starbucks" not in allowlist
    assert all(name.endswith("_kr") for name in allowlist)

