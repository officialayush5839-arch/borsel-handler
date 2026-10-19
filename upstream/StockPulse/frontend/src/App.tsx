import { useEffect, useState } from "react";
import { api } from "./api/client";
import LoadingSpinner from "./components/LoadingSpinner";
import LoginScreen from "./components/LoginScreen";
import NewsSection from "./components/NewsSection";
import StockSelector from "./components/StockSelector";
import TimeRangeSelector from "./components/TimeRangeSelector";
import type { NewsResponse, Stock, TimeRange } from "./types/news";

const TIME_RANGE_LABELS: Record<TimeRange, string> = {
  "24h": "Last 24 hours",
  "48h": "Last 48 hours",
  "72h": "Last 72 hours",
  "1w":  "Last 7 days",
  "2w":  "Last 14 days",
};

function RefreshIcon() {
  return (
    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
    </svg>
  );
}

function BarChartIcon() {
  return (
    <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round"
        d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(() => !!sessionStorage.getItem("site_password"));
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [timerange, setTimerange] = useState<TimeRange>("48h");
  const [newsData, setNewsData] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!authed) {
    return <LoginScreen onSuccess={() => setAuthed(true)} />;
  }

  useEffect(() => {
    api.getStocks().then(setStocks).catch(console.error);
  }, []);

  async function handleFetch() {
    if (!selectedSymbol) return;
    setLoading(true);
    setError(null);
    setNewsData(null);
    try {
      const data = await api.getNews(selectedSymbol, timerange);
      setNewsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#f1f5f9] flex flex-col">

      {/* ── Header ── */}
      <header className="bg-[#0d1b2a] border-b border-[#1e3a5f]">
        <div className="w-full px-8 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <BarChartIcon />
            <span className="text-white font-bold text-base tracking-tight">StockPulse</span>
            <span className="hidden sm:block text-[#4a7fa5] text-sm ml-1">India</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#4a7fa5] bg-[#1a2f45] px-2.5 py-1 rounded font-medium">Nifty 50</span>
            <span className="text-xs text-[#4a7fa5] bg-[#1a2f45] px-2.5 py-1 rounded font-medium">Supply-chain aware</span>
          </div>
        </div>
      </header>

      {/* ── Controls bar ── */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="w-full px-8 py-4">
          <div className="flex flex-wrap items-end gap-5">
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Stock</label>
              <StockSelector stocks={stocks} value={selectedSymbol} onChange={setSelectedSymbol} />
            </div>
            <div className="flex flex-col gap-1.5">
              <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Time Range</label>
              <TimeRangeSelector value={timerange} onChange={setTimerange} />
            </div>
            <button
              type="button"
              onClick={handleFetch}
              disabled={!selectedSymbol || loading}
              className="px-7 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Fetching…" : "Get News"}
            </button>
          </div>
        </div>
      </div>

      {/* ── Main content ── */}
      <main className="flex-1 w-full px-8 py-8">

        {/* Idle */}
        {!loading && !newsData && !error && (
          <div className="flex flex-col items-center justify-center py-32 gap-4 text-center">
            <div className="w-14 h-14 rounded-2xl bg-white border border-slate-200 flex items-center justify-center shadow-sm">
              <svg className="w-7 h-7 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round"
                  d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-700">Select a stock to begin</h2>
              <p className="text-sm text-slate-400 mt-1.5 max-w-sm leading-relaxed">
                Choose any Nifty 50 company and a time window to see direct news, supply chain signals, and sector macro factors — all in one view.
              </p>
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && <LoadingSpinner stock={selectedSymbol} />}

        {/* Error */}
        {error && (
          <div className="max-w-2xl bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <svg className="w-4 h-4 text-red-500 mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-red-700">Something went wrong</p>
              <p className="text-xs text-red-500 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {newsData && !loading && (
          <>
            {/* Result summary */}
            <div className="flex items-start justify-between mb-7 pb-5 border-b border-slate-300">
              <div>
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  {newsData.stock.name}
                </h1>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <span className="text-xs font-semibold text-blue-700 bg-blue-50 border border-blue-200 px-2.5 py-0.5 rounded-full">
                    {newsData.stock.symbol}
                  </span>
                  <span className="text-xs text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    {newsData.stock.sector}
                  </span>
                  <span className="text-xs text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                    {TIME_RANGE_LABELS[newsData.timerange as TimeRange]}
                  </span>
                  <span className="text-xs font-semibold text-slate-700 bg-slate-200 px-2.5 py-0.5 rounded-full">
                    {newsData.total} articles
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={handleFetch}
                className="flex items-center gap-1.5 text-xs font-medium text-slate-500 hover:text-blue-600 transition-colors mt-1 shrink-0"
              >
                <RefreshIcon />
                Refresh
              </button>
            </div>

            {/* No results */}
            {newsData.total === 0 ? (
              <div className="bg-white border border-slate-200 rounded-xl p-14 text-center">
                <svg className="w-10 h-10 text-slate-300 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-slate-600 font-medium text-sm">No articles found</p>
                <p className="text-slate-400 text-xs mt-1">Try a wider time range or check back later</p>
              </div>
            ) : (
              <>
                {(() => {
                  const cats: Array<"direct" | "supply_chain" | "macro"> = ["direct", "supply_chain", "macro"];
                  const visible = cats.filter((c) => newsData.categories[c].length > 0);
                  return visible.map((cat, idx) => (
                    <NewsSection
                      key={cat}
                      category={cat}
                      items={newsData.categories[cat]}
                      isLast={idx === visible.length - 1}
                    />
                  ));
                })()}
              </>
            )}
          </>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-slate-200 bg-white mt-4">
        <div className="w-full px-8 py-4 flex items-center justify-between">
          <p className="text-xs text-slate-400">
            Sources: Economic Times · Business Standard · Mint · NDTV Profit · BusinessLine · Reuters India · Financial Express · CNBC TV18 · BSE Announcements · Marketaux
          </p>
          <p className="text-xs text-slate-300">StockPulse India</p>
        </div>
      </footer>
    </div>
  );
}
