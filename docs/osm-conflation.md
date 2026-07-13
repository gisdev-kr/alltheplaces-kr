# OSM conflation and mapping

The monthly build produces `osm_mapping.csv` and `osm_candidates.osm` as **review artifacts**. It does not authenticate with OpenStreetMap, create changesets, upload files, or perform automatic imports.

Allowed statuses are `matched`, `new_candidate`, `needs_review`, `do_not_import`, and `retired_source`. The initial implementation conservatively labels every source POI `needs_review` until an explicit OSM comparison dataset and matching rules are supplied.

`osm_candidates.osm` contains only rows deliberately changed to `new_candidate`, and ATP's exporter marks the XML `upload="never"`. Human review, source suitability checks, community discussion where appropriate, and a manual editing workflow remain mandatory.

