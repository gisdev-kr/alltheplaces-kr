(function () {
  const code = "gisdev-kr";
  const tracker = document.querySelector("script[data-goatcounter]");
  let path = location.pathname;
  try {
    const settings = JSON.parse(tracker?.getAttribute("data-goatcounter-settings") || "{}");
    if (settings.path) path = settings.path;
  } catch (_) {}

  async function count(counterPath) {
    const response = await fetch(`https://${code}.goatcounter.com/counter/${encodeURIComponent(counterPath)}.json`, {cache: "no-store"});
    const data = await response.json();
    if (response.status === 404) return data.count || "0";
    if (!response.ok) throw new Error(`GoatCounter ${response.status}`);
    return data.count || "—";
  }

  async function refreshCounts() {
    const [page, total] = await Promise.allSettled([count(path), count("TOTAL")]);
    if (page.status === "fulfilled") document.querySelectorAll("[data-page-count]").forEach((node) => { node.textContent = page.value; });
    if (total.status === "fulfilled") document.querySelectorAll("[data-total-count]").forEach((node) => { node.textContent = total.value; });
  }

  refreshCounts();
  window.setTimeout(refreshCounts, 2500);
  window.setInterval(refreshCounts, 60000);
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") refreshCounts(); });

  const formatBytes = (bytes) => {
    if (!Number.isFinite(bytes) || bytes <= 0) return "—";
    const units = ["B", "KB", "MB", "GB"];
    const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    return `${(bytes / Math.pow(1024, index)).toFixed(index > 1 ? 1 : 0)} ${units[index]}`;
  };
  document.querySelectorAll("[data-file-size]").forEach(async (node) => {
    try {
      const response = await fetch(node.dataset.fileSize, {method: "HEAD", cache: "no-store"});
      const length = Number(response.headers.get("content-length"));
      node.textContent = response.ok ? formatBytes(length) : "—";
    } catch (_) { node.textContent = "—"; }
  });
})();
