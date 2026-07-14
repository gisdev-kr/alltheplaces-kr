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

export type KoreaLocationResult = {
  id: string;
  name: string;
  placeName: string;
  center: [number, number];
  bbox?: [number, number, number, number];
};

const cache = new Map<string, KoreaLocationResult[]>();
let nextRequestAt = 0;
let requestQueue = Promise.resolve();

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

function toLocation(feature: NominatimFeature): KoreaLocationResult | null {
  const center = centerOf(feature);
  if (!center) return null;

  const placeName = feature.properties.display_name || feature.properties.name;
  if (!placeName) return null;

  return {
    id: String(feature.id || `${placeName}-${center.join("-")}`),
    name: feature.properties.name || placeName.split(",", 1)[0],
    placeName,
    center,
    bbox: feature.bbox,
  };
}

function searchUrl(input: string): URL | null {
  const query = input.trim();
  if (!query) return null;

  const url = new URL(ENDPOINT);
  url.search = new URLSearchParams({
    q: query,
    format: "geojson",
    addressdetails: "1",
    countrycodes: "kr",
    "accept-language": "ko",
    limit: "5",
  }).toString();
  return url;
}

export async function searchKoreaLocations(input: string): Promise<KoreaLocationResult[]> {
  const url = searchUrl(input);
  if (!url) return [];

  const cacheKey = url.searchParams.get("q")!.toLocaleLowerCase("ko");
  const cached = cache.get(cacheKey);
  if (cached) return cached;

  const request = requestQueue.then(async () => {
    const delay = Math.max(0, nextRequestAt - Date.now());
    if (delay) await wait(delay);
    nextRequestAt = Date.now() + MIN_REQUEST_INTERVAL_MS;

    const response = await fetch(url, {
      headers: {Accept: "application/geo+json, application/json"},
    });
    if (!response.ok) throw new Error(`Nominatim search failed: ${response.status}`);

    const payload = (await response.json()) as NominatimResponse;
    const locations = payload.features
      .map((feature) => toLocation(feature as NominatimFeature))
      .filter((location): location is KoreaLocationResult => location !== null);
    cache.set(cacheKey, locations);
    return locations;
  });

  requestQueue = request.then(() => undefined, () => undefined);
  return request;
}
