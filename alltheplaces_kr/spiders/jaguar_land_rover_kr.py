"""Korea-only wrapper for ATP's multi-country Jaguar Land Rover spider."""

from typing import AsyncIterator
from urllib.parse import quote

from scrapy import Request

from locations.extensions.add_lineage import Lineage
from locations.geo import country_iseadgg_centroids
from locations.spiders.jaguar_land_rover import JaguarLandRoverSpider


BRANDS = (("Land Rover", "Q26777551"), ("Jaguar", "Q21170490"))
SHARED_BODYSHOP_BRAND = "Jaguar Land Rover"


class JaguarLandRoverKRSpider(JaguarLandRoverSpider):
    """Reuse ATP parsing while requesting only the Korean market.

    The upstream parser currently leaves bodyshop-only records without brand
    fields. Korean bodyshops with this shape are returned by both the Jaguar
    and Land Rover queries with the same ref, so assigning whichever request
    finishes first would be unstable. Label them with the shared marque name
    and deliberately leave Wikidata unset rather than inventing an NSI match.
    """

    name = "jaguar_land_rover_kr"
    lineage = Lineage.Brands

    async def start(self) -> AsyncIterator[Request]:
        for brand, brand_wikidata in BRANDS:
            for lat, lng in country_iseadgg_centroids("KR", 458):
                yield Request(
                    "https://retailerlocator.jaguarlandrover.com/dealers?"
                    f"lat={lat}&"
                    f"lng={lng}&"
                    "requestMarketLocale=ko_kr&"
                    f"brand={quote(brand)}&"
                    "radius=460&"
                    "unitOfMeasure=Kilometers&"
                    "country=kr",
                    cb_kwargs={
                        "brand": brand,
                        "brand_wikidata": brand_wikidata,
                        "country": "kr",
                    },
                )

    def parse(self, response, brand, brand_wikidata, country):
        for item in super().parse(response, brand, brand_wikidata, country):
            if not item.get("brand"):
                item["brand"] = SHARED_BODYSHOP_BRAND
            yield item
