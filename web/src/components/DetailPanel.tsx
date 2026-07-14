import type { ReactNode } from "react";
import type { PoiFeature } from "../data/types";

const text = (value: unknown) => value == null ? "" : typeof value === "object" ? JSON.stringify(value) : String(value);

function linkedValue(key: string, value: unknown): ReactNode {
  const rendered = text(value);
  if (!rendered) return "—";
  let href = "";
  if (key === "phone") href = `tel:${rendered}`;
  else if (key === "brand:wikidata") href = `https://www.wikidata.org/wiki/${rendered}`;
  else if (key === "nsi_id") href = `https://nsi.guide/?id=${encodeURIComponent(rendered)}`;
  else if (key === "@spider") href = `https://github.com/alltheplaces/alltheplaces/search?q=${encodeURIComponent(`path:locations/spiders name = "${rendered}"`)}`;
  else if (/^https?:\/\//i.test(rendered)) href = rendered;
  return href ? <a href={href} target={href.startsWith("http") ? "_blank" : undefined} rel={href.startsWith("http") ? "noreferrer" : undefined}>{rendered}{href.startsWith("http") ? " ↗" : ""}</a> : rendered;
}

function Row({label, children}:{label:string; children:ReactNode}) {
  return <div><dt>{label}</dt><dd>{children}</dd></div>;
}

export function DetailPanel({feature, onClose}:{feature:PoiFeature; onClose:()=>void}) {
  const properties = feature.properties || {};
  const [lon, lat] = feature.geometry.coordinates;
  const branch = text(properties.branch);
  const title = branch || text(properties.name || properties.brand || properties.ref || "이름 없는 POI");
  const kicker = text(properties.name || properties.brand || properties["@spider"] || "POI");
  const source = text(properties["@source_uri"] || properties.website);
  const entries = Object.entries(properties)
    .filter(([, value]) => value != null && text(value) !== "")
    .sort(([left], [right]) => left.localeCompare(right, "en"));

  return <aside className="detail-panel" aria-label="선택한 POI 상세">
    <button className="close" onClick={onClose} aria-label="닫기">×</button>
    <span className="detail-kicker">{kicker}</span>
    <h2>{title}</h2>
    <dl className="detail-summary">
      <Row label="주소">{linkedValue("addr:full", properties["addr:full"])}</Row>
      <Row label="전화">{linkedValue("phone", properties.phone)}</Row>
      <Row label="좌표"><a href={`https://www.openstreetmap.org/?mlat=${lat}&mlon=${lon}`} target="_blank" rel="noreferrer">{lon}, {lat} ↗</a></Row>
      <Row label="OSM 검토"><span className="status">{text(properties.match_status) || "needs_review"}</span></Row>
    </dl>
    <details className="raw-details" open>
      <summary>전체 ATP 속성 <span>{entries.length}</span></summary>
      <dl className="raw-properties">
        {entries.map(([key, value]) => <Row key={key} label={key}>{linkedValue(key, value)}</Row>)}
      </dl>
    </details>
    {source && <a className="source" href={source} target="_blank" rel="noreferrer">원본 페이지 열기 ↗</a>}
  </aside>;
}
