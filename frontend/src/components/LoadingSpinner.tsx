export default function LoadingSpinner({ stock }: { stock?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-6 gap-2.5">
      <div className="relative w-7 h-7">
        <div className="absolute inset-0 border-2 border-slate-200 rounded-full" />
        <div className="absolute inset-0 border-2 border-transparent border-t-blue-600 rounded-full animate-spin" />
      </div>
      {stock && (
        <div className="text-center">
          <p className="text-xs font-semibold text-slate-700">
            Fetching news for {stock}
          </p>
          <p className="text-[11px] text-slate-400 mt-0.5">
            Scanning RSS feeds, exchange disclosures & regulatory circulars
          </p>
        </div>
      )}
    </div>
  );
}
