import { useState } from "react";
import type { NewsItem } from "../types/news";
import NewsCard from "./NewsCard";

interface SectionConfig {
  label: string;
  description: string;
  headerBg: string;
  borderColor: string;
  labelColor: string;
  countClass: string;
}

const SECTION_CONFIG: Record<string, SectionConfig> = {
  direct: {
    label: "Company News",
    description: "Direct news, financial results & official BSE announcements",
    headerBg: "bg-blue-50",
    borderColor: "border-blue-200",
    labelColor: "text-blue-800",
    countClass: "text-blue-700 bg-blue-100 border-blue-200",
  },
  supply_chain: {
    label: "Supply Chain & Related",
    description: "Suppliers, input costs, competitors & upstream signals",
    headerBg: "bg-amber-50",
    borderColor: "border-amber-200",
    labelColor: "text-amber-800",
    countClass: "text-amber-700 bg-amber-100 border-amber-200",
  },
  macro: {
    label: "Sector & Macro",
    description: "RBI policy, sector-wide trends & broader market forces",
    headerBg: "bg-emerald-50",
    borderColor: "border-emerald-200",
    labelColor: "text-emerald-800",
    countClass: "text-emerald-700 bg-emerald-100 border-emerald-200",
  },
};

const ACCENT_BAR: Record<string, string> = {
  direct:       "bg-blue-600",
  supply_chain: "bg-amber-500",
  macro:        "bg-emerald-500",
};

interface Props {
  category: "direct" | "supply_chain" | "macro";
  items?: NewsItem[];
  isLast?: boolean;
}

export default function NewsSection({ category, items = [], isLast = false }: Props) {
  const [visibleCount, setVisibleCount] = useState(25);
  const safeItems = Array.isArray(items) ? items : [];
  if (safeItems.length === 0) return null;

  const cfg = SECTION_CONFIG[category] ?? SECTION_CONFIG.direct;
  const visibleItems = safeItems.slice(0, visibleCount);
  const remaining = safeItems.length - visibleCount;

  return (
    <section className="mb-0">
      {/* Section header band */}
      <div className={`flex items-center gap-4 px-5 py-4 ${cfg.headerBg} border ${cfg.borderColor} rounded-t-xl`}>
        <div className={`w-1 h-9 rounded-full shrink-0 ${ACCENT_BAR[category] ?? "bg-blue-600"}`} />
        <div className="flex-1 min-w-0">
          <h2 className={`text-sm font-bold uppercase tracking-wide ${cfg.labelColor}`}>
            {cfg.label}
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">{cfg.description}</p>
        </div>
        <span className={`text-xs font-bold px-3 py-1 rounded-full border shrink-0 ${cfg.countClass}`}>
          {safeItems.length} {safeItems.length === 1 ? "article" : "articles"}
        </span>
      </div>

      {/* Cards */}
      <div className="border-x border-b border-slate-200 rounded-b-xl bg-white divide-y divide-slate-100">
        {visibleItems.map((item, idx) => (
          <div key={`${item.id ?? item.url}-${idx}`} className="p-4">
            <NewsCard item={item} />
          </div>
        ))}

        {remaining > 0 && (
          <div className="p-4 bg-slate-50 text-center">
            <button
              type="button"
              onClick={() => setVisibleCount((prev) => prev + 25)}
              className="px-4 py-2 bg-white border border-slate-300 rounded-lg text-xs font-semibold text-slate-700 hover:bg-slate-100 shadow-sm transition-colors"
            >
              Show More Articles ({remaining} remaining)
            </button>
          </div>
        )}
      </div>

      {/* Divider between sections, not after the last one */}
      {!isLast && (
        <div className="flex items-center gap-3 my-7">
          <div className="flex-1 h-px bg-slate-200" />
          <span className="text-xs text-slate-400 font-medium tracking-wide uppercase">Next Section</span>
          <div className="flex-1 h-px bg-slate-200" />
        </div>
      )}
    </section>
  );
}
