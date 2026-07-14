# All the Places KR portal architecture

`gisdev-kr/alltheplaces-kr` owns the GitHub Pages project path
`/alltheplaces-kr/`. The organization Jekyll site therefore links to the
project, while this repository assembles the complete project portal.

## Build output

- `portal/` is the Jekyll source for the landing page, database, category
  coverage, and brand reports.
- `web/` remains the React + Vite + MapLibre application. Its base path is
  `/alltheplaces-kr/map/`.
- Both Pages workflows build Jekyll into `portal/_site`, build Vite into
  `web/dist`, and copy the latter to `portal/_site/map` before upload.
- The newest monthly `metadata.json` is copied into
  `portal/_data/alltheplaces/runtime.json` before Jekyll runs. Portal KPIs
  therefore follow the same snapshot as the map without running a crawler for
  UI-only deployments.

## Data-driven pages

- `coverage.yml` is the normalized category coverage interface. Templates do
  not contain coverage numbers.
- `brands.yml` supplies brand metadata, category relationships, and OSM tag
  examples.
- `builds.yml` describes available and planned download formats.
- `_alltheplaces_categories` and `_alltheplaces_brands` provide stable SEO
  URLs and page-specific descriptions. Their layouts join records from the
  data files by slug.

## Future NSI automation

An NSI updater should replace `coverage.yml` and extend `brands.yml` while
preserving their current keys. It should select entries whose country scope
contains `KR` or represents worldwide operation, group them by the NSI
category key/value pair, and compare their Wikidata-linked identities with the
discovered All the Places spider inventory. NSI IDs must not be copied into
spider code because they are not stable identifiers.

Category and brand exports remain placeholders until the monthly build creates
real files. No template invents POI counts or data-quality percentages.
