import type {
  NewsResponse,
  Stock,
  ArticleRecord,
  SourceHealthStatus,
  PlatformStats
} from "../types/news";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

function getPassword(): string {
  return sessionStorage.getItem("site_password") ?? "";
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("X-Password", getPassword());

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function validatePassword(password: string): Promise<boolean> {
  const res = await fetch(`${BASE_URL}/api/auth`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password }),
  });
  return res.ok;
}

export const api = {
  getStocks(): Promise<Stock[]> {
    return request<Stock[]>("/api/stocks");
  },
  getNews(symbol: string, timerange: string): Promise<NewsResponse> {
    return request<NewsResponse>(`/api/news?symbol=${encodeURIComponent(symbol)}&timerange=${timerange}`);
  },
  getStats(): Promise<PlatformStats> {
    return request<PlatformStats>("/api/v1/stats");
  },
  getSources(): Promise<SourceHealthStatus[]> {
    return request<SourceHealthStatus[]>("/api/v1/sources");
  },
  getRecords(params: {
    symbol?: string;
    sector?: string;
    category?: string;
    source_name?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ total: number; page: number; page_size: number; items: ArticleRecord[] }> {
    const q = new URLSearchParams();
    if (params.symbol) q.set("symbol", params.symbol);
    if (params.sector) q.set("sector", params.sector);
    if (params.category) q.set("category", params.category);
    if (params.source_name) q.set("source_name", params.source_name);
    if (params.page) q.set("page", params.page.toString());
    if (params.page_size) q.set("page_size", params.page_size.toString());
    return request(`/api/v1/records?${q.toString()}`);
  },
  searchRecords(query: string, page = 1, pageSize = 50): Promise<{ total: number; page: number; items: ArticleRecord[] }> {
    return request(`/api/v1/records/search?q=${encodeURIComponent(query)}&page=${page}&page_size=${pageSize}`);
  },
  getRecordDetail(id: number): Promise<ArticleRecord> {
    return request<ArticleRecord>(`/api/v1/records/${id}`);
  },
  triggerIngest(lookbackHours = 48): Promise<{ status: string; lookback_hours: number; timestamp: string }> {
    return request("/api/v1/ingest/trigger?lookback_hours=" + lookbackHours, {
      method: "POST",
    });
  },
  getExportUrl(params: {
    format: "csv" | "parquet";
    limit?: number;
    symbol?: string;
    sector?: string;
    category?: string;
    source_name?: string;
    source_type?: string;
    query?: string;
  }): string {
    const q = new URLSearchParams();
    q.set("format", params.format);
    if (params.limit) q.set("limit", params.limit.toString());
    if (params.symbol) q.set("symbol", params.symbol);
    if (params.sector) q.set("sector", params.sector);
    if (params.category) q.set("category", params.category);
    if (params.source_name) q.set("source_name", params.source_name);
    if (params.source_type) q.set("source_type", params.source_type);
    if (params.query) q.set("query", params.query);
    return `${BASE_URL}/api/v1/export?${q.toString()}`;
  },
};
