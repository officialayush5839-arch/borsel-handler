import { useState, useEffect } from "react";
import { api } from "../api/client";
import type { SourceHealthStatus, PlatformStats } from "../types/news";

export default function SourceHealthDashboard() {
  const [sources, setSources] = useState<SourceHealthStatus[]>([]);
  const [stats, setStats] = useState<PlatformStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [triggerResult, setTriggerResult] = useState<string | null>(null);
  const [lookback, setLookback] = useState(48);

  async function loadData() {
    setLoading(true);
    try {
      const [srcData, statsData] = await Promise.all([
        api.getSources(),
        api.getStats(),
      ]);
      setSources(srcData);
      setStats(statsData);
    } catch (err) {
      console.error("Failed to load health and stats", err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  async function handleTrigger() {
    setTriggering(true);
    setTriggerResult(null);
    try {
      const res = await api.triggerIngest(lookback);
      setTriggerResult(`Collection job initiated across all 7 sources (lookback ${res.lookback_hours}h).`);
      setTimeout(loadData, 3000);
    } catch (err) {
      setTriggerResult(`Failed to initiate ingestion: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div className="space-y-6">
      {/* ── Summary Cards ── */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Articles Indexed</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.total_articles.toLocaleString()}</div>
            <div className="text-xs text-blue-600 font-medium mt-1">Authoritative historical repository</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Duplicates Prevented</span>
            <div className="text-2xl font-bold text-emerald-600 mt-1">{stats.total_duplicates_prevented.toLocaleString()}</div>
            <div className="text-xs text-slate-500 font-medium mt-1">Multi-tier deduplication engine</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Collection Runs</span>
            <div className="text-2xl font-bold text-slate-900 mt-1">{stats.total_collection_runs.toLocaleString()}</div>
            <div className="text-xs text-slate-500 font-medium mt-1">Across 7 source channels</div>
          </div>

          <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Taxonomy Categories</span>
            <div className="text-2xl font-bold text-blue-600 mt-1">{Object.keys(stats.category_distribution || {}).length}</div>
            <div className="text-xs text-slate-500 font-medium mt-1">Rule-based classification</div>
          </div>
        </div>
      )}

      {/* ── Manual Trigger & Actions Bar ── */}
      <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Ingestion Orchestration</h3>
          <p className="text-xs text-slate-500">Trigger on-demand background collection run across all monitored sources.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <label className="text-xs text-slate-500 font-medium">Lookback:</label>
            <select
              value={lookback}
              onChange={(e) => setLookback(Number(e.target.value))}
              className="text-xs font-medium bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 text-slate-700"
            >
              <option value={24}>24 Hours</option>
              <option value={48}>48 Hours</option>
              <option value={72}>72 Hours</option>
              <option value={168}>7 Days</option>
            </select>
          </div>

          <button
            onClick={handleTrigger}
            disabled={triggering}
            className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 rounded-lg transition-colors flex items-center gap-2"
          >
            {triggering ? (
              <>
                <svg className="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Initiating Collection...
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Trigger Ingestion Now
              </>
            )}
          </button>
        </div>
      </div>

      {triggerResult && (
        <div className="bg-blue-50 border border-blue-200 text-blue-800 text-xs px-4 py-3 rounded-lg flex items-center justify-between">
          <span>{triggerResult}</span>
          <button onClick={() => setTriggerResult(null)} className="text-blue-500 hover:text-blue-700 font-bold ml-2">×</button>
        </div>
      )}

      {/* ── Source Status Table ── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Monitored Indian Financial Sources</h3>
            <p className="text-xs text-slate-500">Live operational health, error reporting, and item counts.</p>
          </div>
          <button
            onClick={loadData}
            className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5"
          >
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-xs text-slate-400">Loading source health metrics...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-500 border-b border-slate-100 uppercase tracking-wider font-semibold">
                <tr>
                  <th className="px-6 py-3">Source Name</th>
                  <th className="px-6 py-3">Channel Type</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Records Indexed</th>
                  <th className="px-6 py-3">Last Execution</th>
                  <th className="px-6 py-3">Health / Error</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {sources.map((s, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                    <td className="px-6 py-3.5 font-semibold text-slate-900">
                      {s.source_name}
                      <span className="block text-[11px] font-normal text-slate-400">{s.description}</span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono text-[11px]">
                        {s.source_type}
                      </span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full font-medium text-[11px] ${
                        s.status === "success" ? "bg-emerald-50 text-emerald-700 border border-emerald-200" :
                        s.status === "running" ? "bg-blue-50 text-blue-700 border border-blue-200 animate-pulse" :
                        s.status === "failed" ? "bg-rose-50 text-rose-700 border border-rose-200" :
                        "bg-slate-100 text-slate-600"
                      }`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${
                          s.status === "success" ? "bg-emerald-500" :
                          s.status === "running" ? "bg-blue-500" :
                          s.status === "failed" ? "bg-rose-500" :
                          "bg-slate-400"
                        }`}></span>
                        {s.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 font-bold text-slate-900">
                      {s.items_indexed.toLocaleString()}
                    </td>
                    <td className="px-6 py-3.5 text-slate-500">
                      {s.last_run ? new Date(s.last_run).toLocaleString() : "Never"}
                    </td>
                    <td className="px-6 py-3.5">
                      {s.last_error ? (
                        <span className="text-rose-600 font-mono text-[11px] max-w-xs truncate block" title={s.last_error}>
                          {s.last_error}
                        </span>
                      ) : (
                        <span className="text-emerald-600 font-medium">Operational</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
