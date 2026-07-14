from pathlib import Path

from alltheplaces_kr.export_index import read_allowlist
from scripts.alltheplaces_kr_run_monthly import validate_allowlist


def test_allowlist_includes_reviewed_multi_country_spiders():
    allowlist = read_allowlist(Path(__file__).parents[1] / "alltheplaces_kr" / "spiders.txt")
    assert len(allowlist) == 20
    assert "kr_starbucks" not in allowlist
    assert {"birkenstock", "cbre", "jaguar_land_rover_kr", "mango", "nespresso", "popeyes", "zara"} <= set(allowlist)
    assert "jaguar_land_rover" not in allowlist


def test_allowlist_validation_does_not_require_a_country_suffix():
    validate_allowlist(["paris_baguette_kr", "nespresso"], {"paris_baguette_kr", "nespresso"})
