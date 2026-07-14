import { useEffect, useState } from "react";

const GOATCOUNTER_CODE = "gisdev-kr";

async function count(path: string): Promise<string> {
  const url = `https://${GOATCOUNTER_CODE}.goatcounter.com/counter/${encodeURIComponent(path)}.json`;
  const response = await fetch(url, {cache: "no-store"});
  const data = await response.json() as {count?: string};
  if (response.status === 404) return data.count || "0";
  if (!response.ok) throw new Error(`GoatCounter ${response.status}`);
  return data.count || "—";
}

export function TrafficStats() {
  const [page, setPage] = useState("—");
  const [total, setTotal] = useState("—");

  useEffect(() => {
    let active = true;

    const refresh = async () => {
      const [pageResult, totalResult] = await Promise.allSettled([
        count(location.pathname),
        count("TOTAL"),
      ]);
      if (!active) return;
      if (pageResult.status === "fulfilled") setPage(pageResult.value);
      if (totalResult.status === "fulfilled") setTotal(totalResult.value);
    };

    void refresh();

    // count.js records the current visit asynchronously. Refresh once after it
    // has had time to arrive, then keep long-lived tabs reasonably current.
    const afterPageview = window.setTimeout(refresh, 2500);
    const interval = window.setInterval(refresh, 60000);
    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") void refresh();
    };
    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      active = false;
      window.clearTimeout(afterPageview);
      window.clearInterval(interval);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  return <span className="traffic-stats" aria-label="방문 통계">
    <span>페이지 <b>{page}</b></span><i/> <span>전체 <b>{total}</b></span>
  </span>;
}
