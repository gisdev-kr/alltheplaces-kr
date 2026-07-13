import type { Feature, FeatureCollection, Point } from "geojson";

export type PoiProperties = Record<string, unknown> & {"@spider"?: string; "@source_uri"?: string; "addr:full"?: string; "brand:wikidata"?: string; brand?: string; branch?: string; match_status?: string; name?: string; nsi_id?: string; phone?: string; ref?: string; website?: string};
export type PoiFeature = Feature<Point, PoiProperties>;
export type PoiCollection = FeatureCollection<Point, PoiProperties>;
export interface Metadata {country:string; generated_at:string; matched_count:number; needs_review_count:number; new_candidate_count:number; osm_import_ready:boolean; poi_count:number; project:string; source:string; spider_count:number}

