export interface Stock {
  symbol: string;
  name: string;
  sector: string;
}

export interface NewsItem {
  title: string;
  snippet: string;
  url: string;
  source: string;
  published_at: string;
  category: "direct" | "supply_chain" | "macro";
  why_it_matters: string;
}

export interface NewsCategories {
  direct: NewsItem[];
  supply_chain: NewsItem[];
  macro: NewsItem[];
}

export interface NewsResponse {
  stock: Stock;
  timerange: string;
  categories: NewsCategories;
  total: number;
  fetched_at: string;
}

export type TimeRange = "24h" | "48h" | "72h" | "1w" | "2w";
