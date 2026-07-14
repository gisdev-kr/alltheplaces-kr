import { useMemo, useRef, useState } from "react";
import { searchKoreaLocations, type KoreaLocationResult } from "../map/koreaNominatim";

type Props = {
  value: string;
  brands: string[];
  onChange: (value: string) => void;
  onLocation: (location: KoreaLocationResult) => void;
};

const normalized = (value: string) => value.trim().toLocaleLowerCase("ko");

export function UnifiedSearch({value, brands, onChange, onLocation}: Props) {
  const [open, setOpen] = useState(false);
  const [locations, setLocations] = useState<KoreaLocationResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [message, setMessage] = useState("");
  const requestId = useRef(0);

  const brandSuggestions = useMemo(() => {
    const needle = normalized(value);
    if (!needle) return [];
    return brands
      .filter((brand) => normalized(brand).includes(needle))
      .sort((left, right) => {
        const leftStarts = normalized(left).startsWith(needle) ? 0 : 1;
        const rightStarts = normalized(right).startsWith(needle) ? 0 : 1;
        return leftStarts - rightStarts || left.localeCompare(right, "ko");
      })
      .slice(0, 6);
  }, [brands, value]);

  const clear = () => {
    requestId.current += 1;
    onChange("");
    setLocations([]);
    setSearching(false);
    setMessage("");
    setOpen(false);
  };

  const runSearch = async () => {
    const query = value.trim();
    if (!query || searching) return;

    const exactBrand = brands.find((brand) => normalized(brand) === normalized(query));
    if (exactBrand) {
      onChange(exactBrand);
      setLocations([]);
      setMessage("");
      setOpen(false);
      return;
    }

    const currentRequest = ++requestId.current;
    setSearching(true);
    setMessage("");
    setOpen(true);
    try {
      const results = await searchKoreaLocations(query);
      if (currentRequest !== requestId.current) return;
      setLocations(results);
      setMessage(results.length ? "" : "한국 내 검색 결과가 없습니다.");
    } catch {
      if (currentRequest !== requestId.current) return;
      setLocations([]);
      setMessage("지역 검색을 완료하지 못했습니다. 잠시 후 다시 시도해 주세요.");
    } finally {
      if (currentRequest === requestId.current) setSearching(false);
    }
  };

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    void runSearch();
  };

  const showResults = open && Boolean(value.trim()) &&
    (brandSuggestions.length > 0 || locations.length > 0 || searching || Boolean(message));

  return <form
    className="unified-search"
    role="search"
    onSubmit={submit}
    onFocusCapture={() => setOpen(true)}
    onBlurCapture={(event) => {
      if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setOpen(false);
    }}
  >
    <div className="search-box">
      <button type="submit" className="search-submit" aria-label="지역·장소 검색"><svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4 4"/></svg></button>
      <input
        type="text"
        inputMode="search"
        value={value}
        onChange={(event) => {
          requestId.current += 1;
          onChange(event.target.value);
          setLocations([]);
          setSearching(false);
          setMessage("");
          setOpen(true);
        }}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            void runSearch();
          }
        }}
        placeholder="브랜드·주소 검색, 지역은 Enter"
        aria-label="브랜드, 주소 및 지역 검색"
        aria-autocomplete="list"
        aria-expanded={showResults}
        aria-controls="unified-search-results"
        autoComplete="off"
      />
      {value && <button type="button" className="search-clear" onClick={clear} aria-label="검색어 지우기">×</button>}
    </div>
    {showResults && <div className="search-results" id="unified-search-results" role="listbox">
      {brandSuggestions.map((brand) => <button key={brand} type="button" role="option" aria-selected="false" onClick={() => {
        requestId.current += 1;
        onChange(brand);
        setLocations([]);
        setSearching(false);
        setMessage("");
        setOpen(false);
      }}><span>{brand}</span><small>브랜드</small></button>)}
      {locations.map((location) => <button key={location.id} type="button" role="option" aria-selected="false" onClick={() => {
        onLocation(location);
        setOpen(false);
      }}><span>{location.name}</span><small>{location.placeName}</small></button>)}
      {searching && <p className="search-message">한국 지역을 찾는 중…</p>}
      {!searching && message && <p className="search-message">{message}</p>}
      {brandSuggestions.length > 0 && locations.length === 0 && !searching && !message && <p className="search-hint">지역·장소 검색은 Enter를 누르세요.</p>}
    </div>}
  </form>;
}
