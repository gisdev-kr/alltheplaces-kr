import type { Metadata, PoiCollection, PoiFeature } from "./types";

export const dataUrl = (name: string) => `${import.meta.env.BASE_URL}data/latest/${name}`;
async function getJson<T>(name: string): Promise<T> { const response = await fetch(dataUrl(name)); if (!response.ok) throw new Error(`${name}을 불러오지 못했습니다 (${response.status})`); return response.json() as Promise<T>; }
export async function loadPortalData(): Promise<{collection:PoiCollection;metadata:Metadata}> {
  const [collection,metadata] = await Promise.all([getJson<PoiCollection>("pois.geojson"),getJson<Metadata>("metadata.json")]);
  const features=(collection.features as unknown[]).filter((feature):feature is PoiFeature=>{if(!feature||typeof feature!=="object")return false;const geometry=(feature as {geometry?:{type?:unknown;coordinates?:unknown}|null}).geometry;if(geometry?.type!=="Point"||!Array.isArray(geometry.coordinates)||geometry.coordinates.length<2)return false;const [lon,lat]=geometry.coordinates;return typeof lon==="number"&&Number.isFinite(lon)&&typeof lat==="number"&&Number.isFinite(lat)&&lon>=-180&&lon<=180&&lat>=-90&&lat<=90});
  return {collection:{...collection,features},metadata};
}

