# Repository Import Manifest: Borsel Handler Data Ingestion Foundations

**Document ID:** RIM-2026-001  
**Generated:** 2026-10-19  
**Platform:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform (Data Collection Module)

---

## 1. Executive Summary

This manifest documents the initial acquisition, provenance, file structure, runtime dependencies, license posture, and security inspection of the two source repositories imported into the Borsel Handler workspace:
1. **Repository A — StockPulse** (`upstream/StockPulse`)
2. **Repository B — Market Announcements** (`upstream/market_announcements`)

Both repositories were cloned cleanly without loss or modification into dedicated directories under `upstream/`. Both repositories exhibit characteristics of early-stage, experimental prototypes with low commit counts, missing automated test suites, and differing runtime architectures.

---

## 2. Repository A: StockPulse

### 2.1 Provenance and Git Metadata
- **Source URL:** `https://github.com/ansh-varshney/StockPulse`
- **Local Clone Target:** `upstream/StockPulse/`
- **Current Branch:** `main` (tracking `origin/main`)
- **Commit Hash:** `e68271802c950885c68706b0d5bfe57a05e8ceed`
- **Commit Date:** Thu May 21 17:56:28 2026 +0530
- **Author:** Ansh Varshney `<your-email@example.com>`
- **Commit Message:** `pin Python to 3.11.9 for Render deployment`
- **Total Commit Count:** 2 commits
- **Maintenance Status:** Stagnant / Prototype. Contains only initial feature dump and a deployment patch. No issues/PRs tracked, no CI/CD pipelines configured.

### 2.2 License and Attribution
- **License File:** NONE present in repository.
- **Legal Assessment:** Under default copyright laws, source code published to GitHub without an open-source license remains the intellectual property of the author ("All Rights Reserved"). Fair use permits inspection and reverse engineering of concepts, but direct distribution requires formal licensing or independent reimplementation. Code adapted from StockPulse must either be reimplemented or clearly isolated with appropriate attribution notes pending formal license granting.

### 2.3 Directory Structure & Inventory
```
upstream/StockPulse/
├── .claude/
│   └── settings.json                  # Anthropic Claude assistant settings
├── backend/
│   ├── .env.example                   # Template with MARKETAUX_API_KEY
│   ├── .python-version                # Pinned to 3.11.9
│   ├── main.py                        # FastAPI entry point, CORS, password middleware
│   ├── requirements.txt               # Backend dependencies
│   ├── data/
│   │   ├── __init__.py
│   │   ├── dependency_map.py          # Static supply chain graph for Nifty 50
│   │   └── stocks.py                  # Nifty 50 ticker and company list
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                 # Pydantic news models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── news.py                    # API routes (/api/stocks, /api/news, /api/auth)
│   └── services/
│       ├── __init__.py
│       ├── bse_service.py             # BSE announcements via bseindia API
│       ├── marketaux_service.py       # Marketaux commercial news API
│       ├── newsapi_service.py         # Disabled stub returning empty list
│       └── rss_service.py             # 14 financial RSS feeds with TTLCache
├── frontend/
│   ├── public/                        # Static assets (favicons, SVGs)
│   ├── src/
│   │   ├── App.css / App.tsx          # Root layout and authentication gate
│   │   ├── index.css / main.tsx       # Tailwind CSS v4 setup and DOM bootstrap
│   │   ├── api/client.ts              # Fetch wrapper with x-site-password header
│   │   ├── assets/                    # Images (hero.png, logos)
│   │   ├── components/                # UI components (NewsCard, StockSelector, etc.)
│   │   └── types/news.ts              # TypeScript interfaces
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json                   # React 18, Vite, Tailwind CSS v4
│   ├── package-lock.json
│   ├── tsconfig.json / app / node
│   └── vercel.json                    # Vercel deployment rewrite rules
├── .gitignore
├── README.md                          # Architecture and usage documentation
└── render.yaml                        # Render.com deployment manifest
```

### 2.4 Languages, Frameworks, and Runtime
- **Backend Language:** Python (pins 3.11.9 in `.python-version`, compatible with 3.11+)
- **Backend Framework:** FastAPI 0.115.5, Uvicorn 0.32.1, Pydantic 2.10.3
- **HTTP Client & Parsing:** `httpx 0.27.2`, `feedparser 6.0.11`
- **Cache:** `cachetools 5.5.0` (`TTLCache` in-memory 30-min window)
- **Frontend Language & Framework:** TypeScript, React 18, Vite 5, Tailwind CSS 4
- **Database:** None. No relational database, no ORM, no persistent storage. Everything is cached in memory for 30 minutes.
- **Tests:** None. No `test_*.py` files, no Jest/Vitest test files.

### 2.5 Entry Points & External Services
- **Backend Entry:** `uvicorn main:app --reload --port 8000` (from `backend/`)
- **Frontend Entry:** `npm run dev` (Vite dev server on port 5173)
- **External Dependencies:**
  - RSS Feeds (14 Indian news feeds: Economic Times, Mint, Business Standard, NDTV Profit, Financial Express, CNBC TV18, Reuters India, BusinessLine)
  - BSE India Corporate Announcements API (`https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`)
  - Marketaux News API (`https://api.marketaux.com/v1/news/all` - free tier 100 req/day)

### 2.6 Environment Variables & Security
- `MARKETAUX_API_KEY`: API key for Marketaux. Optional (fails gracefully if missing).
- `SITE_PASSWORD`: Optional shared password for API access gate. If omitted, auth check passes unconditionally.
- `VITE_API_URL`: Frontend configuration pointing to backend.
- **Security Audit:** No hardcoded secrets found. Password check uses simple string comparison (not constant-time `hmac.compare_digest`), vulnerable to timing attacks if deployed in security-sensitive contexts.

---

## 3. Repository B: Market Announcements

### 3.1 Provenance and Git Metadata
- **Source URL:** `https://github.com/Navadhrit/market_announcements`
- **Local Clone Target:** `upstream/market_announcements/`
- **Current Branch:** `main` (tracking `origin/main`)
- **Commit Hash:** `270014b24cfae53e546f9fc48ff307ab976a09fd`
- **Commit Date:** Fri Jul 17 11:42:56 2026 +0530
- **Author:** Navadhrit `<navadhritm@gmail.com>`
- **Commit Message:** `Ver 0.0.0.0.4`
- **Total Commit Count:** 5 commits
- **Maintenance Status:** Prototype / Active author development. 5 iterative versions tracking early alpha releases (`0.0.0.0.1` to `0.0.0.0.4`).

### 3.2 License and Attribution
- **License File:** `LICENSE` (MIT License, Copyright 2026 Navadhrit).
- **Legal Assessment:** Full permissive MIT license allows reuse, modification, and integration into Borsel Handler, provided copyright notice is preserved.

### 3.3 Directory Structure & Inventory
```
upstream/market_announcements/
├── .env.example                       # Template for ANTHROPIC_API_KEY
├── .gitattributes
├── .gitignore                         # Excludes *.db, .venv, etc.
├── LICENSE                            # MIT License
├── README.md                          # Comprehensive documentation
├── quickstart.sh                      # Shell script for setup and synthetic demo
├── requirements.txt                   # Scraper and dashboard dependencies
├── announcement_ideas_pipeline.py     # Rule-based scoring engine for BSE Equity (22 KB)
├── idea_rules.py                      # Keyword taxonomy & scoring weights (15 KB)
├── market_announcements.py            # CLI scraper for 4 exchange sources (87 KB)
└── bse_market_suite.py                # Streamlit multi-tab analytical dashboard (116 KB)
```

### 3.4 Languages, Frameworks, and Runtime
- **Language:** Python 3.10+
- **Frontend / UI:** Streamlit (`bse_market_suite.py`) with Plotly, `streamlit-option-menu`, `streamlit-authenticator`
- **Data Collection / Scraper:** `requests`, `curl_cffi` (for NSE browser TLS fingerprint spoofing), `beautifulsoup4`, `lxml`, `bse` (third-party wrapper)
- **Scheduling:** `schedule` library for recurring execution
- **Database:** Local SQLite files:
  - `bse_equity.db`
  - `bse_sme.db`
  - `nse_equity.db`
  - `nse_sme.db`
  - `market_users.db`
- **Tests:** None. No automated test suite included. Relies on synthetic demo generation (`--demo` flag in `announcement_ideas_pipeline.py`) for manual verification.

### 3.5 Entry Points & External Services
- **CLI Ingestion Entry:** `python market_announcements.py fetch [--source <src>] [--from DD-MM-YYYY] [--to DD-MM-YYYY]`
- **Scoring Pipeline Entry:** `python announcement_ideas_pipeline.py --db bse_equity.db run`
- **Dashboard Entry:** `streamlit run bse_market_suite.py`
- **External Dependencies:**
  - NSE Official Website (`https://www.nseindia.com/api/corporate-announcements`) via `curl_cffi` Impersonate
  - BSE Official Website (`https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w`)
  - BSE SME HTML Pages via `beautifulsoup4`
  - Optional Anthropic Claude API for narrative summaries (`ANTHROPIC_API_KEY`)

### 3.6 Environment Variables & Security
- `ANTHROPIC_API_KEY`: Optional key for AI digest tab.
- **Security Audit:** Contains hardcoded default credentials (`admin` / `admin@123`) for Streamlit dashboard seeding. Uses raw SQL strings with `sqlite3` parameterization in some queries, but string formatting in others. `curl_cffi` is used to impersonate Chrome TLS fingerprints to bypass NSE anti-scraping protections.

---

## 4. Comparative Runtime & Conflict Analysis

| Parameter | StockPulse | Market Announcements | Borsel Handler Target |
|---|---|---|---|
| **Primary Focus** | Nifty 50 News & RSS Aggregation | Exchange Corporate Announcements | Unified Financial News & Regulatory Ingestion |
| **Backend Framework** | FastAPI (REST API) | None (CLI scripts) | FastAPI + Service Layer |
| **UI Framework** | React 18 + Vite (SPA) | Streamlit (Data Dashboard) | React 18 SPA (Primary) + Streamlit (Optional Analytics) |
| **Persistence** | None (In-memory TTLCache) | SQLite (4 separate databases) | PostgreSQL + SQLAlchemy ORM (SQLite test/dev fallback) |
| **Deduplication** | URL allowlist + in-memory dict | SQLite `INSERT OR IGNORE` on id | Centralized Multi-Tier Deduplication Engine |
| **Data Schema** | Pydantic schemas (`NewsItem`) | Ad-hoc SQLite table definitions | Unified SQLAlchemy & Pydantic Data Contract |
| **Testing** | 0 tests | 0 tests | Comprehensive Automated Test Suite |

---

## 5. Import Status Verdict

Both repositories were successfully imported, checked out, and inventoried.
- **StockPulse Import Status:** SUCCESSFUL (`upstream/StockPulse`, commit `e682718`).
- **Market Announcements Import Status:** SUCCESSFUL (`upstream/market_announcements`, commit `270014b`).
- **Blockers:** None encountered during git clone and inventory stages.
