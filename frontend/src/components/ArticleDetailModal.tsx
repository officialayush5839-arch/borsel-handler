import type { ArticleRecord } from "../types/news";

interface Props {
  article: ArticleRecord | null;
  onClose: () => void;
}

export default function ArticleDetailModal({ article, onClose }: Props) {
  if (!article) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-xl shadow-xl border border-slate-200 max-w-2xl w-full max-h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold px-2.5 py-1 rounded bg-blue-50 text-blue-700 border border-blue-200">
              {article.source_name}
            </span>
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-slate-100 text-slate-600">
              {article.category.replace("_", " ").toUpperCase()}
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-5 overflow-y-auto space-y-4">
          <h2 className="text-lg font-bold text-slate-900 leading-snug">
            {article.title}
          </h2>

          <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-slate-500 pb-3 border-b border-slate-100">
            <div>Published: <span className="font-medium text-slate-700">{new Date(article.published_at).toUTCString()}</span></div>
            <div>Ingested: <span className="font-medium text-slate-700">{new Date(article.collected_at).toUTCString()}</span></div>
            {article.symbol && (
              <div>Ticker: <span className="font-bold text-blue-600">{article.symbol}</span></div>
            )}
            {article.sector && (
              <div>Sector: <span className="font-medium text-slate-700">{article.sector}</span></div>
            )}
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Snippet / Summary</h4>
            <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-slate-100">
              {article.snippet}
            </p>
          </div>

          {/* URLs & Provenance */}
          <div className="space-y-2 text-xs">
            <h4 className="font-semibold text-slate-400 uppercase tracking-wider">Provenance & Links</h4>
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-100 space-y-1.5 break-all">
              <div><span className="font-semibold text-slate-600">Canonical URL:</span> <a href={article.canonical_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{article.canonical_url}</a></div>
              <div><span className="font-semibold text-slate-600">Original URL:</span> <a href={article.original_url} target="_blank" rel="noreferrer" className="text-slate-500 hover:underline">{article.original_url}</a></div>
              <div><span className="font-semibold text-slate-600">SHA-256 Hash:</span> <code className="font-mono text-[11px] text-slate-600">{article.record_hash}</code></div>
              <div><span className="font-semibold text-slate-600">Confidence Score:</span> <span className="font-medium text-slate-800">{article.confidence_score.toFixed(1)}%</span></div>
            </div>
          </div>

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div>
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5">Tags</h4>
              <div className="flex flex-wrap gap-1.5">
                {article.tags.map((t, idx) => (
                  <span key={idx} className="text-xs px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-slate-200">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 rounded-lg hover:bg-slate-100 transition-colors"
          >
            Close
          </button>
          <a
            href={article.canonical_url || article.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors flex items-center gap-1.5"
          >
            Visit Original Source
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        </div>
      </div>
    </div>
  );
}
