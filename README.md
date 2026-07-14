# All the Places KR

All the Places KR is a Korea-focused POI crawler and static data portal derived from the [All the Places](https://github.com/alltheplaces/alltheplaces) codebase. It preserves the All the Places data model and spider pipeline where possible.

It is **not** the official All the Places project. It is **not** an automatic OpenStreetMap import tool.

## Thin-overlay architecture

The official project is pinned at `upstream/alltheplaces` as a Git submodule. This repository contains only:

- an explicit allowlist of reviewed Korea and multi-country spiders;
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

Spider names are not used as the only country signal. Run
`scripts/alltheplaces_kr_discover_spiders.py` to find `_kr` spiders and multi-country
spiders whose source mentions Korean locale/country signals. Discovery is advisory:
new candidates enter the monthly run only after they are reviewed and added to the
allowlist, and emitted features are still filtered by `addr:country=KR` and Korea's
bounding box.

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

Category and brand reports are generated from the latest monthly GeoJSON. The
generator compares every exported POI with the NSI entry resolved by ATP's
pipeline and reports required-tag presence separately from exact canonical
value conformity:

```bash
python scripts/alltheplaces_kr_build_portal_reports.py \
  --dataset dist/latest/pois.geojson \
  --metadata dist/latest/metadata.json \
  --nsi upstream/alltheplaces/locations/data/nsi.json
```

The report never uses spider inventory as schema coverage. Brand pages include
only brands present in the current crawl and are regenerated on monthly and UI
deployments.

The portal records visits in the shared `gisdev-kr` GoatCounter account and can
show the current page and whole-site counts. Public counters must be enabled in
GoatCounter under **Settings → Allow adding visitor counts on your website**;
until then the UI keeps the values as `—`.

The dismissible bottom ad container is disabled by default. To include it in a
future build, set `VITE_ADSENSE_ENABLED=true` and provide
`VITE_ADSENSE_CLIENT`; see `web/.env.example`. It never blocks the map, filters,
details, or downloads.

## Data and code licenses

This overlay code is MIT licensed. All the Places code retains its upstream MIT license. Generated location data follows the upstream All the Places CC0 dedication; consult the upstream repository and individual source terms before reuse.
