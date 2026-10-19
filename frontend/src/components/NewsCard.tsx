import type { NewsItem } from "../types/news";

interface Props {
  item: NewsItem;
}

function timeAgo(isoString: string): string {
  const diff = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

const CATEGORY_ACCENT: Record<string, string> = {
  direct:       "border-l-blue-600",
  supply_chain: "border-l-amber-500",
  macro:        "border-l-emerald-500",
};

export default function NewsCard({ item }: Props) {
  return (
    <article
      className={`bg-white border border-slate-200 border-l-4 ${CATEGORY_ACCENT[item.category] ?? "border-l-slate-300"} rounded-r-lg rounded-bl-lg p-5 hover:shadow-md transition-shadow`}
    >
      {/* Meta row */}
      <div className="flex items-center gap-2.5 mb-3">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
          {item.source}
        </span>
        <span className="text-slate-300">·</span>
        <time className="text-xs text-slate-400">{timeAgo(item.published_at)}</time>
      </div>

      {/* Headline */}
      <h3 className="text-[15px] font-semibold text-slate-900 leading-snug mb-2.5">
        {item.title}
      </h3>

      {/* Snippet */}
      <p className="text-sm text-slate-600 leading-relaxed mb-4 line-clamp-4">
        {item.snippet}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-100">
        <span className="text-xs text-slate-400 bg-slate-50 border border-slate-200 px-2.5 py-1 rounded-full">
          {item.why_it_matters}
        </span>
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 transition-colors"
        >
          Read article
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </article>
  );
}
