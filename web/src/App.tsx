import { useEffect, useMemo, useState } from "react";
import { AdSlot } from "./components/AdSlot";
import { DetailPanel } from "./components/DetailPanel";
import { Downloads } from "./components/Downloads";
import { Filters } from "./components/Filters";
import { TrafficStats } from "./components/TrafficStats";
import { UnifiedSearch } from "./components/UnifiedSearch";
import { loadPortalData } from "./data/loadData";
import type { Metadata, PoiCollection, PoiFeature } from "./data/types";
import { PoiMap } from "./map/PoiMap";
import type { KoreaLocationResult } from "./map/koreaNominatim";

const empty: PoiCollection = {type:"FeatureCollection", features:[]};
const value = (input:unknown) => input == null ? "" : String(input);
const unique = (items:string[]) => [...new Set(items.filter(Boolean))].sort((a,b) => a.localeCompare(b,"ko"));
const portalRoot = "/alltheplaces-kr/";
const initialParams = new URLSearchParams(window.location.search);

export default function App() {
  const [collection,setCollection] = useState(empty);
  const [metadata,setMetadata] = useState<Metadata|null>(null);
  const [selected,setSelected] = useState<PoiFeature|null>(null);
  const [locationTarget,setLocationTarget] = useState<KoreaLocationResult|null>(null);
  const [query,setQuery] = useState(initialParams.get("q")||"");
  const [brand,setBrand] = useState(initialParams.get("brand")||"");
  const [spider,setSpider] = useState("");
  const [status,setStatus] = useState("");
  const [category,setCategory] = useState({key:initialParams.get("key")||"",value:initialParams.get("value")||""});
  const [panel,setPanel] = useState<"filters"|"downloads"|"about"|null>(null);
  const [error,setError] = useState("");

  useEffect(() => {
    loadPortalData().then(({collection,metadata}) => {setCollection(collection);setMetadata(metadata)})
      .catch(reason => setError(reason instanceof Error ? reason.message : String(reason)));
  }, []);

  const options = useMemo(() => ({
    brands:unique(collection.features.map(feature => value(feature.properties?.brand))),
    spiders:unique(collection.features.map(feature => value(feature.properties?.["@spider"]))),
    statuses:unique(collection.features.map(feature => value(feature.properties?.match_status))),
  }), [collection]);
  const filtered = useMemo<PoiCollection>(() => {
    const needle=query.trim().toLocaleLowerCase("ko");
    return {...collection,features:collection.features.filter(feature => {
      const properties=feature.properties||{};
      const haystack=[properties.name,properties.branch,properties.brand,properties["addr:full"],properties["@spider"],properties.ref].map(value).join(" ").toLocaleLowerCase("ko");
      return (!needle||haystack.includes(needle))&&(!brand||value(properties.brand)===brand)&&(!spider||value(properties["@spider"])===spider)&&(!status||value(properties.match_status)===status)&&(!category.key||!category.value||value(properties[category.key])===category.value);
    })};
  }, [collection,query,brand,spider,status,category]);
  const reset=()=>{setQuery("");setBrand("");setSpider("");setStatus("");setCategory({key:"",value:""});setLocationTarget(null);window.history.replaceState({},"",location.pathname)};
  const active=Boolean(query||brand||spider||status||category.key);
  const date=metadata?new Date(metadata.generated_at).toLocaleDateString("ko-KR",{year:"numeric",month:"2-digit",day:"2-digit"}):"불러오는 중";

  return <div className="app">
    <header className="topbar">
      <div className="identity"><a className="org" href="https://gisdev-kr.github.io">GISdev-kr</a><span className="slash">/</span><a className="title" href={portalRoot}>All the Places KR Map</a></div>
      <nav><TrafficStats/><a className="portal-link" href={portalRoot}>프로젝트 소개</a><a className="portal-link database-link" href={`${portalRoot}database/`}>데이터 다운로드</a><button onClick={()=>setPanel(panel==="about"?null:"about")}>지도 안내</button><a className="github-link" href="https://github.com/gisdev-kr/alltheplaces-kr">GitHub ↗</a></nav>
    </header>
    <main className="stage">
      {!error&&<PoiMap data={filtered} onSelect={setSelected} target={locationTarget}/>}
      <section className="dataset-card">
        <div className="dataset-title"><span className="mark">KR</span><div><h1>All the Places KR Map</h1><p>한국 POI 데이터를 지도에서 탐색합니다.</p></div></div>
        <div className="dataset-stats"><span><b>{collection.features.length.toLocaleString("ko-KR")}</b> POI</span><span><b>{metadata?.spider_count??"—"}</b> spiders</span><span><b>{date}</b> generated</span></div>
      </section>
      <UnifiedSearch value={query} brands={options.brands} onChange={setQuery} onLocation={(location)=>setLocationTarget({...location})}/>
      <div className="toolbar"><button className={panel==="filters"||active?"active":""} onClick={()=>setPanel(panel==="filters"?null:"filters")}>필터 {active&&<i/>}</button><button className={panel==="downloads"?"active":""} onClick={()=>setPanel(panel==="downloads"?null:"downloads")}>다운로드</button></div>
      {panel==="filters"&&<section className="floating filters-panel"><header><strong>표시할 POI</strong><button onClick={()=>setPanel(null)}>×</button></header><Filters {...options} brand={brand} spider={spider} status={status} onBrand={setBrand} onSpider={setSpider} onStatus={setStatus}/><button className="reset" onClick={reset} disabled={!active}>필터 초기화</button></section>}
      {panel==="downloads"&&<section className="floating downloads-panel"><header><strong>월간 데이터</strong><button onClick={()=>setPanel(null)}>×</button></header><p>필터와 무관한 전체 최신 스냅샷입니다.</p><Downloads/></section>}
      {panel==="about"&&<section className="floating about-panel"><header><strong>이 지도에 관하여</strong><button onClick={()=>setPanel(null)}>×</button></header><p>공식 All the Places 코드는 Git submodule로 사용합니다. 한국 위치만 후처리하며 OSM 파일은 수동 검토용입니다.</p><a href={portalRoot}>All the Places KR 프로젝트 소개 →</a></section>}
      <div className="legend"><span><i className="review"/>검토 필요</span><span><i className="matched"/>OSM 매치</span><span><i className="candidate"/>신규 후보</span></div>
      <div className="count"><b>{filtered.features.length.toLocaleString("ko-KR")}</b>개 표시 중 {category.key&&<span className="category-filter">{category.key}={category.value}</span>} {active&&<button onClick={reset}>전체 보기</button>}</div>
      {selected&&<DetailPanel feature={selected} onClose={()=>setSelected(null)}/>}
      {!metadata&&!error&&<div className="message">POI 데이터를 불러오는 중입니다…</div>}
      {error&&<div className="message error"><strong>데이터를 불러오지 못했습니다.</strong><span>{error}</span></div>}
      <AdSlot/>
    </main>
  </div>;
}
