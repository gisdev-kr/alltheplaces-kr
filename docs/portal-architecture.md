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
- The newest monthly GeoJSON and `metadata.json` are restored before Jekyll
  runs. Portal KPIs therefore follow the same snapshot as the map without
  running a crawler for UI-only deployments.

## Data-driven pages

- `scripts/alltheplaces_kr_build_portal_reports.py` reads the final monthly
  GeoJSON and the pinned ATP `locations/data/nsi.json` file.
- `coverage.json` contains computed category aggregates. `brands.json`
  contains only brands that appear in the current crawl output.
- `builds.yml` describes available and planned download formats.
- `_alltheplaces_categories` and `_alltheplaces_brands` are regenerated from
  those JSON reports before each Jekyll build, providing SEO URLs without a
  hand-maintained brand inventory.

## NSI schema measurement

Coverage never means “spiders available / NSI brands”. Each final ATP feature
is resolved to its NSI contract using the pipeline-produced `nsi_id`. If that
ID is absent, a unique KR-applicable entry with the same Wikidata and category
may provide an expected contract, but the report does not count it as a
pipeline match.

For every resolved feature the generator records two separate measures:

- schema presence: required NSI tag keys with a non-empty exported value;
- schema conformity: required NSI tags whose exported value exactly matches
  the canonical NSI value.

This follows `ApplyNSICategoriesPipeline.apply_nsi_tags`: missing tags are
filled, while an existing conflicting source value is not overwritten. A
spider that places a branch label in canonical `name`, for example, can have
100% schema presence but a lower conformity score. That is an actionable ATP
review signal.

The NSI version is inherited from the pinned All the Places submodule, so the
normal upstream synchronization process updates both matching behavior and the
portal's expected contracts. NSI IDs remain runtime join keys only and are not
hardcoded in spider code or used as permanent brand URLs.

Category and brand exports remain placeholders until the monthly build creates
real files. No template invents POI counts or data-quality percentages.
