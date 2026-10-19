import { useRef, useEffect, useState } from "react";
import type { TimeRange } from "../types/news";

const OPTIONS: { value: TimeRange; label: string; sublabel: string }[] = [
  { value: "24h", label: "Last 24 Hours",  sublabel: "Past day"       },
  { value: "48h", label: "Last 48 Hours",  sublabel: "Past 2 days"    },
  { value: "72h", label: "Last 72 Hours",  sublabel: "Past 3 days"    },
  { value: "1w",  label: "Last 7 Days",    sublabel: "Past week"      },
  { value: "2w",  label: "Last 14 Days",   sublabel: "Past 2 weeks"   },
];

interface Props {
  value: TimeRange;
  onChange: (v: TimeRange) => void;
}

export default function TimeRangeSelector({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const selected = OPTIONS.find((o) => o.value === value)!;

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div ref={ref} className="relative w-52">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-left hover:border-slate-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <span className="flex flex-col">
          <span className="text-sm font-medium text-slate-800">{selected.label}</span>
          <span className="text-xs text-slate-400">{selected.sublabel}</span>
        </span>
        <svg
          className={`w-4 h-4 text-slate-400 shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-full bg-white border border-slate-200 rounded-lg shadow-xl overflow-hidden">
          {OPTIONS.map((opt) => (
            <button
              key={opt.value}
              type="button"
              onClick={() => { onChange(opt.value); setOpen(false); }}
              className={`w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-slate-50 transition-colors ${
                opt.value === value ? "bg-blue-50" : ""
              }`}
            >
              <span className="flex flex-col">
                <span className={`text-sm font-medium ${opt.value === value ? "text-blue-700" : "text-slate-700"}`}>
                  {opt.label}
                </span>
                <span className="text-xs text-slate-400">{opt.sublabel}</span>
              </span>
              {opt.value === value && (
                <svg className="w-4 h-4 text-blue-600 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
