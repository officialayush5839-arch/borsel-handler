import type { NewsResponse, Stock } from "../types/news";

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "";

function getPassword(): string {
  return sessionStorage.getItem("site_password") ?? "";
}

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "X-Password": getPassword() },
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
};
