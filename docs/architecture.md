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

There are no overlay-local spiders by design. Starbucks Korea is therefore absent until a suitable spider is accepted upstream.

