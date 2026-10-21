import { useState } from "react";
import { validatePassword } from "../api/client";

interface Props {
  onSuccess: () => void;
}

export default function LoginScreen({ onSuccess }: Props) {
  const [password, setPassword] = useState("admin");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(false);
    const ok = await validatePassword(password);
    if (ok) {
      try {
        sessionStorage.setItem("site_password", password);
      } catch (_) {}
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
          <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xs">
            BH
          </div>
          <span className="text-slate-800 font-bold text-base tracking-tight">Borsel Handler</span>
        </div>

        <h1 className="text-lg font-semibold text-slate-800 text-center mb-1">Welcome back</h1>
        <p className="text-xs text-slate-400 text-center mb-7">
          Enter access password (default: <span className="font-semibold text-blue-600">admin</span>)
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(false); }}
              placeholder="Enter access password (default: admin)"
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
