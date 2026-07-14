from pathlib import Path

from alltheplaces_kr.spider_selection import discover_korea_spiders


def test_discovers_suffix_and_locale_signals(tmp_path: Path):
    (tmp_path / "brand_kr.py").write_text(
        'from scrapy import Spider\nclass BrandSpider(Spider):\n    name = "brand_kr"\n', encoding="utf-8"
    )
    (tmp_path / "global_brand.py").write_text(
        'from scrapy import Spider\nCOUNTRIES = [("ko", "kr", "KR")]\n'
        'class GlobalSpider(Spider):\n    name = "global_brand"\n', encoding="utf-8"
    )
    (tmp_path / "other.py").write_text(
        'from scrapy import Spider\nclass OtherSpider(Spider):\n    name = "other"\n', encoding="utf-8"
    )

    candidates = {candidate.name: candidate for candidate in discover_korea_spiders(tmp_path)}

    assert set(candidates) == {"brand_kr", "global_brand"}
    assert "filename:_kr" in candidates["brand_kr"].signals
    assert "locale:KR" in candidates["global_brand"].signals
