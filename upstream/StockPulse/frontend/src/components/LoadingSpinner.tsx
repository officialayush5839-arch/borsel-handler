export default function LoadingSpinner({ stock }: { stock: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-5">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 border-4 border-slate-200 rounded-full" />
        <div className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full animate-spin" />
      </div>
      <div className="text-center">
        <p className="text-sm font-semibold text-slate-700">
          Fetching news for {stock}
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Scanning RSS feeds, BSE announcements & Marketaux
        </p>
      </div>
    </div>
  );
}
