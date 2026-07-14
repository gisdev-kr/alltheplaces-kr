import type {
  CarmenGeojsonFeature,
  MaplibreGeocoderApi,
  MaplibreGeocoderApiConfig,
} from "@maplibre/maplibre-gl-geocoder";

const ENDPOINT = "https://nominatim.openstreetmap.org/search";
const MIN_REQUEST_INTERVAL_MS = 1_000;

type NominatimProperties = {
  display_name?: string;
  name?: string;
  category?: string;
  type?: string;
  [key: string]: unknown;
};

type NominatimFeature = GeoJSON.Feature<GeoJSON.Geometry, NominatimProperties> & {
  bbox?: [number, number, number, number];
};

type NominatimResponse = GeoJSON.FeatureCollection<GeoJSON.Geometry, NominatimProperties>;

const wait = (milliseconds: number) =>
  new Promise<void>((resolve) => window.setTimeout(resolve, milliseconds));

function centerOf(feature: NominatimFeature): [number, number] | null {
  if (feature.geometry.type === "Point") {
    const [longitude, latitude] = feature.geometry.coordinates;
    return [longitude, latitude];
  }
  if (feature.bbox) {
    return [
      (feature.bbox[0] + feature.bbox[2]) / 2,
      (feature.bbox[1] + feature.bbox[3]) / 2,
    ];
  }
  return null;
}

function toGeocoderFeature(feature: NominatimFeature): CarmenGeojsonFeature | null {
  const center = centerOf(feature);
  if (!center) return null;

  const placeName = feature.properties.display_name || feature.properties.name;
  if (!placeName) return null;

  return {
    ...feature,
    geometry: {type: "Point", coordinates: center},
    text: feature.properties.name || placeName.split(",", 1)[0],
    place_name: placeName,
    place_type: [feature.properties.type || feature.properties.category || "place"],
    center,
    bbox: feature.bbox,
  };
}

function searchUrl(config: MaplibreGeocoderApiConfig): URL | null {
  const query = typeof config.query === "string" ? config.query.trim() : "";
  if (!query) return null;

  const url = new URL(ENDPOINT);
  url.search = new URLSearchParams({
    q: query,
    format: "geojson",
    addressdetails: "1",
    countrycodes: "kr",
    "accept-language": "ko",
    limit: String(Math.min(config.limit || 5, 5)),
  }).toString();
  return url;
}

export function createKoreaNominatimApi(): MaplibreGeocoderApi {
  const cache = new Map<string, CarmenGeojsonFeature[]>();
  let nextRequestAt = 0;
  let requestQueue = Promise.resolve();

  return {
    async forwardGeocode(config) {
      const url = searchUrl(config);
      if (!url) return {type: "FeatureCollection", features: []};

      const cacheKey = url.searchParams.get("q")!.toLocaleLowerCase("ko");
      const cached = cache.get(cacheKey);
      if (cached) return {type: "FeatureCollection", features: cached};

      const request = requestQueue.then(async () => {
        const delay = Math.max(0, nextRequestAt - Date.now());
        if (delay) await wait(delay);
        nextRequestAt = Date.now() + MIN_REQUEST_INTERVAL_MS;

        const response = await fetch(url, {
          headers: {Accept: "application/geo+json, application/json"},
        });
        if (!response.ok) throw new Error(`Nominatim search failed: ${response.status}`);

        const payload = (await response.json()) as NominatimResponse;
        const features = payload.features
          .map((feature) => toGeocoderFeature(feature as NominatimFeature))
          .filter((feature): feature is CarmenGeojsonFeature => feature !== null);
        cache.set(cacheKey, features);
        return {type: "FeatureCollection" as const, features};
      });

      requestQueue = request.then(() => undefined, () => undefined);
      return request;
    },
  };
}
