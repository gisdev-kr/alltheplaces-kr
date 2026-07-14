import { useState } from "react";

export function AdSlot() {
  const enabled = import.meta.env.VITE_ADSENSE_ENABLED === "true";
  const [visible, setVisible] = useState(enabled);
  if (!visible) return null;
  return <aside className="ad-popup" aria-label="광고 영역">
    <button type="button" onClick={() => setVisible(false)} aria-label="광고 닫기">×</button>
    <span>ADVERTISEMENT</span>
    <div data-ad-client={import.meta.env.VITE_ADSENSE_CLIENT || undefined}>광고 영역</div>
  </aside>;
}
