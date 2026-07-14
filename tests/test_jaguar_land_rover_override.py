import asyncio
from urllib.parse import parse_qs, urlparse

from locations.spiders.jaguar_land_rover import JaguarLandRoverSpider

from alltheplaces_kr import settings  # noqa: F401 - extends locations.spiders.__path__
from alltheplaces_kr.spiders import jaguar_land_rover_kr
from alltheplaces_kr.spiders.jaguar_land_rover_kr import JaguarLandRoverKRSpider


async def collect_requests(spider):
    return [request async for request in spider.start()]


def test_override_requests_only_the_korean_market(monkeypatch):
    monkeypatch.setattr(jaguar_land_rover_kr, "country_iseadgg_centroids", lambda country, radius: [(37.5, 127.0)])

    requests = asyncio.run(collect_requests(JaguarLandRoverKRSpider()))

    assert len(requests) == 2
    assert {request.cb_kwargs["brand"] for request in requests} == {"Jaguar", "Land Rover"}
    for request in requests:
        query = parse_qs(urlparse(request.url).query)
        assert query["requestMarketLocale"] == ["ko_kr"]
        assert query["country"] == ["kr"]
        assert request.cb_kwargs["country"] == "kr"


def test_override_labels_shared_bodyshops_without_inventing_a_wikidata_match(monkeypatch):
    upstream_items = [
        {"name": "효성 프리미어 모터스 - 부산 센텀", "shop": "car_repair"},
        {"name": "기존 브랜드", "brand": "Existing", "brand_wikidata": "Q999", "shop": "car"},
    ]
    monkeypatch.setattr(JaguarLandRoverSpider, "parse", lambda *args, **kwargs: iter(upstream_items))

    items = list(JaguarLandRoverKRSpider().parse(None, "Land Rover", "Q26777551", "kr"))

    assert items[0]["brand"] == "Jaguar Land Rover"
    assert "brand_wikidata" not in items[0]
    assert items[1]["brand"] == "Existing"
    assert items[1]["brand_wikidata"] == "Q999"


def test_atp_exporter_can_find_the_local_spider():
    from locations.exporters.geojson import find_spider_class

    spider_class = find_spider_class("jaguar_land_rover_kr")

    assert spider_class is not None
    assert spider_class.name == "jaguar_land_rover_kr"
