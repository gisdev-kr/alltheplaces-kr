import { dataUrl } from "../data/loadData";
const files=[["GeoJSON","pois.geojson"],["NDGeoJSON","pois.ndgeojson"],["CSV","pois.csv"],["OSM XML","pois.osm"],["Mapping CSV","osm_mapping.csv"]];
export function Downloads(){return <div className="downloads">{files.map(([label,file])=><a key={file} href={dataUrl(file)} download>{label}<span>↓</span></a>)}</div>}

