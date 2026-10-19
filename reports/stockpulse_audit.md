# StockPulse Architecture & Capability Audit Report

**Repository:** `upstream/StockPulse`  
**Base Commit:** `e68271802c950885c68706b0d5bfe57a05e8ceed` (Thu May 21 17:56:28 2026 +0530)  
**Evaluator:** Borsel Handler Integration Engine  
**Verification Standard:** Five-State Evidence-Based Verification (VERIFIED, PARTIALLY VERIFIED, DOCUMENTED ONLY, MISSING, BLOCKED)

---

## 1. Architectural Overview

StockPulse is designed as a lightweight, on-demand news aggregator for Nifty 50 stocks. It implements an asynchronous Python backend using FastAPI and an interactive single-page application frontend built with React 18, Vite, and Tailwind CSS v4.

The core architecture operates without any database persistence layer. When an end-user selects a stock symbol and time range on the UI, the frontend issues a `GET /api/news?symbol=<SYM>&timerange=<RANGE>` request. The backend fans out multiple concurrent asynchronous tasks using `httpx` to fetch external feeds and APIs, parses items in memory, matches keywords against a static dependency map, deduplicates items in memory by an MD5 hash of lowercase titles, and returns categorized JSON to the client.

```
[React 18 / Vite Frontend]
         │ (GET /api/news?symbol=INFY&timerange=48h)
         ▼
[FastAPI Backend - routers/news.py]
         │
         ├──▶ [rss_service.py] ──▶ 14 Curated RSS Feeds (Cached in TTLCache for 30m)
         ├──▶ [bse_service.py] ──▶ BSE India Corporate Announcements API
         ├──▶ [marketaux_service.py] ──▶ Marketaux Commercial API (Optional)
         └──▶ [newsapi_service.py] ──▶ Stub (Disabled)
```

---

## 2. Capability Audit & Evidence Matrix

| Capability Area | Status | Evidence File(s) & Lines | Detailed Analysis |
|---|---|---|---|
| **News & RSS Collectors** | **VERIFIED** | `backend/services/rss_service.py:16-31, 96-145` | Implements asynchronous fetching across 14 curated Indian financial RSS feeds using `httpx` and `feedparser`. Feed items are parsed and cached in a 30-minute in-memory `TTLCache`. |
| **BSE Announcements** | **VERIFIED** | `backend/services/bse_service.py:10, 82-139` | Directly queries BSE India public API (`https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`) for corporate announcements using scrip code lookup. |
| **NSE Announcements** | **MISSING** | `backend/services/` | No implementation found for collecting NSE corporate announcements, exchange feeds, or circulars. |
| **API Routes & Backend** | **VERIFIED** | `backend/main.py:29-55`<br>`backend/routers/news.py:20-59` | Clean FastAPI endpoints: `GET /health`, `POST /api/auth`, `GET /api/stocks`, `GET /api/news`. Uses Pydantic schemas for request/response serialization. |
| **Company & Ticker Mapping** | **VERIFIED** | `backend/data/stocks.py:1-53`<br>`backend/services/bse_service.py:13-65` | Mappings present for 51 Nifty 50 stocks (symbol, full name, sector, BSE scrip code). Static hardcoded dictionaries; not database-driven. |
| **Sector & Supply Chain Mapping** | **VERIFIED** | `backend/data/dependency_map.py:12-945` | Extensive 945-line curated dictionary mapping all Nifty 50 stocks to competitors, input suppliers, commodity factors, and macro keywords. |
| **News Categorization** | **PARTIALLY VERIFIED** | `backend/models/schemas.py:18`<br>`backend/routers/news.py:118-128` | Partitions articles into exactly 3 static UI buckets: `direct`, `supply_chain`, and `macro`. Lacks granular taxonomy (earnings, dividends, IPO, M&A, regulatory). |
| **Date Parsing & Normalization** | **VERIFIED** | `backend/services/rss_service.py:76-85`<br>`backend/services/bse_service.py:112-115` | Parses RFC-2822 and ISO dates using `email.utils.parsedate_to_datetime` and `strptime`, explicitly converting to UTC (`timezone.utc`). Fallback to `now(utc)` on parse error. |
| **URL Handling & Allowlisting** | **PARTIALLY VERIFIED** | `backend/services/rss_service.py:35-74` | Implements domain allowlist (`TRUSTED_DOMAINS`) checking hostname suffix. Lacks canonical URL resolution, query param stripping, or redirection flattening. |
| **Caching & Persistence** | **PARTIALLY VERIFIED** | `backend/services/rss_service.py:13, 147-153` | RSS data is cached in memory for 30 minutes via `cachetools.TTLCache`. **Persistent database storage is completely MISSING.** All data is volatile. |
| **Historical Retrieval** | **MISSING** | `backend/routers/news.py:56-60` | Only filters live feeds within a max window of 2 weeks (`2w`). No historical backfilling, persistent storage, or historical range queries. |
| **Search & Filtering** | **PARTIALLY VERIFIED** | `backend/services/rss_service.py:154-194` | In-memory substring matching against keywords (`_matches()`) and time range cutoff. No full-text search, multi-field querying, or pagination. |
| **Frontend Components** | **VERIFIED** | `frontend/src/App.tsx`<br>`frontend/src/components/*` | Polished React 18 + Vite + Tailwind CSS v4 SPA. Features stock search dropdown, time range buttons, auth modal, and responsive news cards. |
| **Scheduling & Automation** | **MISSING** | `backend/main.py:19-26` | No scheduler or recurring ingestion jobs. Cache is pre-warmed once at startup in `lifespan`; all other collections are triggered on-demand by client requests. |
| **Error Handling & Resilience** | **VERIFIED** | `backend/routers/news.py:103, 113-127` | Uses `asyncio.gather(*tasks, return_exceptions=True)` with exception suppression and warning logs. Downstream API errors do not crash the service. |
| **Automated Tests** | **MISSING** | Entire repository | Zero automated tests found. No test files, pytest fixtures, or frontend test suites exist. |
| **Dependency & Config Mgmt** | **VERIFIED** | `backend/requirements.txt`<br>`backend/.env.example` | Well-scoped dependencies (7 libraries). Safe environment template without secrets. |

---

## 3. Deep Dive: Critical Findings

### 3.1 RSS Data: Cache vs. Persistence
- **Finding:** In StockPulse, RSS data is **merely cached in memory**, never persisted.
- **Evidence:** `rss_service.py:13`: `_rss_cache: TTLCache = TTLCache(maxsize=1, ttl=1800)`. Once the 30-minute TTL expires or the container restarts, all previously collected news articles are discarded.
- **Impact on Borsel Handler:** Borsel Handler requires persistent historical storage. The RSS parsing and domain allowlist logic from `rss_service.py` is reusable, but must be decoupled from `TTLCache` and connected to SQLAlchemy/PostgreSQL persistence.

### 3.2 Ticker & Entity Mapping Viability
- **Finding:** The data in `backend/data/stocks.py` and `backend/data/dependency_map.py` provides high-value curation for Indian financial markets, covering all Nifty 50 stocks with direct ticker keywords, related supply-chain companies, commodity price triggers, and macro keywords.
- **Impact on Borsel Handler:** Highly suitable for reuse in Borsel Handler's entity mapping and classification modules.

### 3.3 Deduplication Weakness
- **Finding:** Deduplication in `routers/news.py:133` computes `hashlib.md5(item["title"].strip().lower().encode()).hexdigest()`.
- **Flaws Identified:**
  1. Compares only lowercase title text; ignores URL, publication timestamp, and source.
  2. Executes independently per category bucket (`direct`, `supply_chain`, `macro`), allowing the same article to appear multiple times across categories.
  3. Slight variations in title wording from syndicated sources (e.g. "TCS Q4 net profit rises 9%" vs "TCS Q4 net up 9%") are treated as separate items.

### 3.4 Missing Official Source Coverage
- StockPulse collects news from 14 RSS feeds and BSE corporate announcements.
- It **does not collect**: NSE announcements, SEBI circulars/regulations, RBI updates, government policy notifications, or SME exchange filings.

---

## 4. Reusability Verdict for Borsel Handler

1. **Adopt & Adapt:**
   - 14 RSS feed sources and `httpx` async fetcher (`services/rss_service.py`).
   - Domain allowlist security check (`rss_service.py:TRUSTED_DOMAINS`).
   - BSE API integration (`services/bse_service.py`).
   - Nifty 50 stocks and dependency taxonomy (`data/stocks.py` and `data/dependency_map.py`).
   - FastAPI structure, CORS middleware, and Pydantic schemas.
   - React 18 / Tailwind frontend architecture.

2. **Replace / Implement New:**
   - Add SQLAlchemy / PostgreSQL persistent storage layer.
   - Replace in-memory title MD5 dedup with multi-tier deduplication engine.
   - Implement automated background scheduler.
   - Add comprehensive unit and integration test suite.
