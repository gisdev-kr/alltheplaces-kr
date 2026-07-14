import { useEffect, useState } from "react";

const GOATCOUNTER_CODE = "gisdev-kr";

async function count(path: string): Promise<string> {
  const url = `https://${GOATCOUNTER_CODE}.goatcounter.com/counter/${encodeURIComponent(path)}.json`;
  const response = await fetch(url);
  if (!response.ok) throw new Error(`GoatCounter ${response.status}`);
  const data = await response.json() as {count?: string};
  return data.count || "—";
}

export function TrafficStats() {
  const [page, setPage] = useState("—");
  const [total, setTotal] = useState("—");

  useEffect(() => {
    count(location.pathname).then(setPage).catch(() => undefined);
    count("TOTAL").then(setTotal).catch(() => undefined);
  }, []);

  return <span className="traffic-stats" aria-label="방문 통계">
    <span>페이지 <b>{page}</b></span><i/> <span>전체 <b>{total}</b></span>
  </span>;
}
