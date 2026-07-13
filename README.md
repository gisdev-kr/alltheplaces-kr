# All the Places KR

All the Places KR is a Korea-focused POI crawler and static data portal derived from the [All the Places](https://github.com/alltheplaces/alltheplaces) codebase. It preserves the All the Places data model and spider pipeline where possible.

It is **not** the official All the Places project. It is **not** an automatic OpenStreetMap import tool.

## Thin-overlay architecture

The official project is pinned at `upstream/alltheplaces` as a Git submodule. This repository contains only:

- an explicit allowlist of official Korea spiders;
- Korea bounding-box validation and monthly build wrappers;
- review-only OSM mapping/conflation artifacts;
- a static MapLibre data portal.

No upstream spider is copied here. NSI matching, Wikidata handling, the ATP item model, cleanup pipelines, and exporters continue to come from the pinned upstream revision.

## Clone and run

```bash
git clone --recurse-submodules https://github.com/gisdev-kr/alltheplaces-kr.git
cd alltheplaces-kr
uv sync --project upstream/alltheplaces --all-groups
uv run --project upstream/alltheplaces python scripts/alltheplaces_kr_run_monthly.py
```

The monthly output is written under `dist/latest/`. The crawl is intentionally limited to [`alltheplaces_kr/spiders.txt`](alltheplaces_kr/spiders.txt).

## Update upstream

```bash
git submodule update --remote upstream/alltheplaces
uv run --project upstream/alltheplaces python -m pytest tests
```

Commit the submodule pointer only after the Korea-specific tests and a sample crawl pass. Common spider fixes should be proposed to the official All the Places repository rather than maintained as local copies.

## Static portal

```bash
corepack enable
pnpm --dir web install
pnpm --dir web dev
```

GitHub Pages serves the production site at <https://gisdev-kr.github.io/alltheplaces-kr/>.

## Data and code licenses

This overlay code is MIT licensed. All the Places code retains its upstream MIT license. Generated location data follows the upstream All the Places CC0 dedication; consult the upstream repository and individual source terms before reuse.

