import { useState } from "react";
import { validatePassword } from "../api/client";

interface Props {
  onSuccess: () => void;
}

export default function LoginScreen({ onSuccess }: Props) {
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(false);
    const ok = await validatePassword(password);
    if (ok) {
      sessionStorage.setItem("site_password", password);
      onSuccess();
    } else {
      setError(true);
    }
    setLoading(false);
  }

  return (
    <div className="min-h-screen bg-[#f1f5f9] flex flex-col items-center justify-center">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-lg p-10 w-full max-w-sm">
        <div className="flex items-center gap-2.5 mb-8 justify-center">
          <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span className="text-slate-800 font-bold text-base tracking-tight">StockPulse India</span>
        </div>

        <h1 className="text-lg font-semibold text-slate-800 text-center mb-1">Welcome back</h1>
        <p className="text-sm text-slate-400 text-center mb-7">Enter your access password to continue</p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(false); }}
              placeholder="Enter access password"
              autoFocus
              className={`w-full px-4 py-2.5 border rounded-lg text-sm text-slate-800 placeholder-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors ${
                error ? "border-red-300 bg-red-50" : "border-slate-200 bg-white"
              }`}
            />
            {error && (
              <p className="text-xs text-red-500 mt-0.5">Incorrect password. Please try again.</p>
            )}
          </div>

          <button
            type="submit"
            disabled={!password || loading}
            className="w-full py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 active:bg-blue-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Checking…" : "Continue"}
          </button>
        </form>
      </div>
    </div>
  );
}
