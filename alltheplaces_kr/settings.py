"""Small Scrapy settings overlay; every unmodified setting comes from ATP."""

from locations.settings import *  # noqa: F403
from locations.settings import ITEM_PIPELINES as ATP_ITEM_PIPELINES

ITEM_PIPELINES = dict(ATP_ITEM_PIPELINES)
ITEM_PIPELINES["alltheplaces_kr.korea.KoreaValidationPipeline"] = 358

# Keep official ATP discovery only. This repository deliberately contains no local spiders.
SPIDER_MODULES = ["locations.spiders"]
NEWSPIDER_MODULE = "locations.spiders"
USER_AGENT = "gisdev-kr/alltheplaces-kr (+https://github.com/gisdev-kr/alltheplaces-kr)"

