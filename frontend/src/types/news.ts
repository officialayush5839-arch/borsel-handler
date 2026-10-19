export interface Stock {
  symbol: string;
  name: string;
  sector: string;
}

export interface NewsItem {
  id?: number;
  title: string;
  snippet: string;
  url: string;
  source: string;
  source_type?: string;
  published_at: string;
  category: string;
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

export interface ArticleRecord {
  id: number;
  record_hash: string;
  title: string;
  snippet: string;
  original_url: string;
  canonical_url: string;
  published_at: string;
  collected_at: string;
  source_name: string;
  source_type: string;
  source_record_id?: string;
  company_name?: string;
  symbol?: string;
  sector?: string;
  category: string;
  confidence_score: number;
  tags: string[];
  raw_metadata: Record<string, any>;
}

export interface SourceHealthStatus {
  source_name: string;
  source_type: string;
  status: string;
  last_run: string | null;
  last_finished: string | null;
  items_indexed: number;
  last_error: string | null;
  description: string;
}

export interface PlatformStats {
  total_articles: number;
  total_duplicates_prevented: number;
  total_collection_runs: number;
  category_distribution: Record<string, number>;
  source_distribution: Record<string, number>;
  last_collection_run?: {
    source_name: string;
    status: string;
    finished_at: string;
  } | null;
}

export type TimeRange = "24h" | "48h" | "72h" | "1w" | "2w" | "all";
