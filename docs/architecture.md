# Architecture

`alltheplaces-kr` is an overlay, not a forked crawler implementation.

```text
alltheplaces/alltheplaces (pinned Git submodule)
  ├─ locations/items.py
  ├─ locations/pipelines/*
  ├─ locations/exporters/*
  └─ locations/spiders/*_kr.py
                 │
                 ▼
alltheplaces-kr overlay
  ├─ explicit spider allowlist
  ├─ KR bounds validation
  ├─ monthly dist assembly
  ├─ review-only OSM mapping
  └─ static MapLibre portal
```

The submodule pointer is the reproducibility boundary. Upstream synchronization changes that one pointer and is reviewed through a pull request. The overlay never replaces ATP's item model, NSI/Wikidata handling, phone or country cleanup, duplicate pipeline, or exporters.

## Adding a Korean franchise

1. Add or improve the spider in the official All the Places repository following its conventions.
2. Wait until it is merged upstream.
3. Update the submodule pointer in this repository.
4. Add its exact spider name to `alltheplaces_kr/spiders.txt`.
5. Run `--list-only`, the Korea tests, and a sample crawl.

Overlay-local spiders are exceptional wrappers, not independent crawler
implementations. They must inherit an ATP spider and limit themselves to a
Korea request scope or a documented output correction. The current
`jaguar_land_rover_kr` wrapper requests only `ko_kr`, labels bodyshop-only
locations returned by both marque queries as `Jaguar Land Rover`, and otherwise
delegates parsing and all pipelines to ATP. It should be removed when an
equivalent upstream fix is available in the pinned submodule.

## Partial spider refresh

The scheduled workflow runs the complete reviewed allowlist. A manual workflow
run can instead provide a comma-separated `spiders` input. The build restores
the newest successful artifact, removes only the selected spider records (and
any declared predecessor names), appends the new crawl, then rebuilds GeoJSON,
CSV, OSM, metadata, schema reports, and Pages. This is intended for correcting
one source without re-running unrelated APIs.

