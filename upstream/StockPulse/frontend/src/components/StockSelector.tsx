import { useState, useRef, useEffect } from "react";
import type { Stock } from "../types/news";

interface Props {
  stocks: Stock[];
  value: string;
  onChange: (symbol: string) => void;
}

export default function StockSelector({ stocks, value, onChange }: Props) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const selected = stocks.find((s) => s.symbol === value);

  const filtered = query.trim()
    ? stocks.filter(
        (s) =>
          s.symbol.toLowerCase().includes(query.toLowerCase()) ||
          s.name.toLowerCase().includes(query.toLowerCase())
      )
    : stocks;

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  function select(symbol: string) {
    onChange(symbol);
    setOpen(false);
    setQuery("");
  }

  return (
    <div ref={containerRef} className="relative w-80">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-left hover:border-slate-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        {selected ? (
          <span className="flex items-center gap-3 min-w-0">
            <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded shrink-0">
              {selected.symbol}
            </span>
            <span className="text-sm text-slate-700 truncate">{selected.name}</span>
          </span>
        ) : (
          <span className="text-sm text-slate-400">Select a stock…</span>
        )}
        <svg
          className={`w-4 h-4 text-slate-400 shrink-0 ml-2 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden">
          <div className="p-2.5 border-b border-slate-100">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                autoFocus
                type="text"
                placeholder="Search by name or symbol"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="w-full pl-8 pr-3 py-2 text-sm bg-slate-50 rounded border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
              />
            </div>
          </div>
          <ul className="max-h-72 overflow-y-auto">
            {filtered.length === 0 && (
              <li className="px-4 py-4 text-sm text-slate-400 text-center">No stocks found</li>
            )}
            {filtered.map((s) => (
              <li key={s.symbol}>
                <button
                  type="button"
                  onClick={() => select(s.symbol)}
                  className={`w-full px-4 py-2.5 text-left hover:bg-slate-50 transition-colors flex items-center gap-3 ${
                    s.symbol === value ? "bg-blue-50" : ""
                  }`}
                >
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded w-24 text-center shrink-0">
                    {s.symbol}
                  </span>
                  <span className="flex-1 min-w-0">
                    <span className="text-sm text-slate-700 block truncate">{s.name}</span>
                  </span>
                  <span className="text-xs text-slate-400 shrink-0">{s.sector}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
