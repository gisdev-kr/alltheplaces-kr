"""Small Scrapy settings overlay; every unmodified setting comes from ATP."""

from pathlib import Path

import locations.spiders

from locations.settings import *  # noqa: F403
from locations.settings import ITEM_PIPELINES as ATP_ITEM_PIPELINES

ITEM_PIPELINES = dict(ATP_ITEM_PIPELINES)
ITEM_PIPELINES["alltheplaces_kr.korea.KoreaValidationPipeline"] = 358

# Extend ATP's existing spider package path instead of replacing its loader.
# This also keeps ATP exporters, which inspect ``locations.spiders`` directly,
# aware of narrow Korea-only subclasses stored outside the pinned submodule.
LOCAL_SPIDER_PATH = str(Path(__file__).with_name("spiders"))
if LOCAL_SPIDER_PATH not in locations.spiders.__path__:
    locations.spiders.__path__.append(LOCAL_SPIDER_PATH)
SPIDER_MODULES = ["locations.spiders"]
NEWSPIDER_MODULE = "locations.spiders"
LOG_LEVEL = "INFO"
USER_AGENT = "gisdev-kr/alltheplaces-kr (+https://github.com/gisdev-kr/alltheplaces-kr)"

