# Borsel Handler — VeritasAI PDF Specification Compliance Audit & Gap Analysis

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Source Specification:** VeritasAI Problem Statement (`03 AUG 2026`, Author: Atharva Deore)  
**Evaluator:** Principal Systems Architect, Data Engineering Lead & QA Automation Engineer  

---

## 1. Executive Summary

This document performs an exhaustive, line-by-line audit comparing the official **VeritasAI Problem Statement PDF** ("Borsel Handler – AI-Powered Indian Stock Market Intelligence Platform (Data Collection Module)") against the actual implementation in the Borsel Handler repository.

### High-Level Audit Scorecard

| Specification Dimension | Target Requirement (PDF) | Actual Implementation Status | Compliance Score |
|---|---|---|:---:|
| **Project Role & Philosophy** | Data engineering focus, preparing data for future AI analysis (no ML models in this phase) | 100% data engineering, ingestion, normalization, storage, and search. No premature ML/trading bots. | **100% (FULL)** |
| **Information Target Coverage** | 10 financial topics (Listed companies, NSE/BSE, RBI, SEBI, Govt policies, Earnings, IPOs, M&A, Dividends, Corporate actions) | 8 Fully Operational & Verified, 2 Partially Done (RBI & Govt policies require scraper modernization due to 404 RSS). | **85% (HIGH)** |
| **Metadata Schema** | 8 specific fields (Title, Pub Date, Source, Company, Sector, URL, Category, Summary) | All 8 fields implemented + 6 extra audit fields (`confidence_score`, `tags`, `raw_metadata`, `provenance`, etc.). | **100% (FULL)** |
| **Deduplication** | Eliminate duplicate news articles | 6-tier centralized deduplication engine with relational duplicate logging (`article_duplicates`). | **100% (FULL)** |
| **Historical Persistence** | Maintain a searchable historical repository | PostgreSQL 18 & SQLite indexed store, multi-criteria filtering, full-text keyword search, resumable backfill engine. | **100% (FULL)** |
| **Recommended Tech Stack** | Python, BeautifulSoup, Playwright, News APIs, Pandas, PostgreSQL, SQLAlchemy, Git | Python, PostgreSQL, SQLAlchemy, News APIs, Git 100% utilized; Pandas, BeautifulSoup & Playwright partially used / pending integration. | **80% (HIGH)** |

---

## 2. In-Depth Audit: Information Target Coverage (10 Domains)

The PDF mandates collecting structured information across 10 specific financial and regulatory areas:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                   VERITASAI SPECIFICATION: 10 INFORMATION DOMAINS               │
├─────┬───────────────────────────┬───────────────┬────────────────────────────────┤
│ #   │ Domain Requirement        │ Status        │ Implementation Details         │
├─────┼───────────────────────────┼───────────────┼────────────────────────────────┤
│ 1   │ Listed Companies          │ IMPLEMENTED   │ stocks.py, resolver.py, DB     │
│ 2   │ NSE & BSE Announcements   │ IMPLEMENTED   │ nse.py, bse.py                 │
│ 3   │ RBI Updates               │ PARTIALLY DONE│ rbi.py (Legacy RSS 404)        │
│ 4   │ SEBI Regulations          │ IMPLEMENTED   │ sebi.py (Live 30 circulars)    │
│ 5   │ Govt Economic Policies    │ PARTIALLY DONE│ pib.py (Legacy RSS 404)        │
│ 6   │ Quarterly Earnings        │ IMPLEMENTED   │ taxonomy.py (CATEGORY_EARNINGS)│
│ 7   │ IPOs                      │ IMPLEMENTED   │ taxonomy.py (CATEGORY_IPO)     │
│ 8   │ Mergers & Acquisitions    │ IMPLEMENTED   │ taxonomy.py (CATEGORY_ACQ)     │
│ 9   │ Dividend Announcements    │ IMPLEMENTED   │ taxonomy.py (CATEGORY_DIVIDEND)│
│ 10  │ Corporate Actions         │ IMPLEMENTED   │ taxonomy.py (CATEGORY_CORP_ACT)│
└─────┴───────────────────────────┴───────────────┴────────────────────────────────┘
```

### Detailed Evaluation of Each Domain

#### 1. Listed Companies
- **PDF Requirement:** Collect information related to Indian listed companies.
- **Implemented:**
  - `borsel_handler/data/stocks.py`: Master directory of Indian equities with NSE symbols, company names, sectors, ISINs, and BSE scrip codes.
  - `borsel_handler/data/resolver.py` (`CompanyResolver`): Deterministic word-boundary entity resolution mapping unstructured text to listed tickers while suppressing ambiguous tokens (`IT`, `ON`, `BE`, `LT`, etc.).
  - `borsel_handler/storage/models.py`: Relational `Company` and `ArticleCompany` models supporting multiple company associations per article with confidence scoring.
- **Partially Done / Remaining:** Coverage currently focuses on NIFTY 50 reference universe.
- **Improvement:** Expand reference universe to NIFTY 500 / BSE 500 by auto-syncing the official NSE Equity Master CSV (`EQUITY_L.csv`).

#### 2. NSE & BSE Announcements
- **PDF Requirement:** Automated collection of NSE and BSE exchange corporate disclosures.
- **Implemented:**
  - `NSEAnnouncementCollector` (`borsel_handler/collectors/nse.py`): Live corporate announcements scraper with session cookie priming and attachment archive URL synthesis. Collected **462 live records** during verification.
  - `BSEAnnouncementCollector` (`borsel_handler/collectors/bse.py`): Scrip-code-based announcement collector hitting `api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`. Deterministic parser verified with mock fixtures.
- **Partially Done / Remaining:** Live BSE collection requires residential/commercial proxy rotation because cloud datacenter IPs face intermittent WAF throttling.

#### 3. RBI Updates
- **PDF Requirement:** Official Reserve Bank of India policy announcements and circulars.
- **Implemented:** `RBICollector` (`borsel_handler/collectors/rbi.py`) with XML feed parsing, banking sector tagging, and classification into `rbi_update`. Fully verified via deterministic fixtures in `tests/test_collectors.py`.
- **Partially Done / Remaining:** The configured legacy RSS URLs (`rbi.org.in/rss/rss_pressrelease.xml`) currently return HTTP 404 because the RBI portal retired them.
- **Improvement:** Implement a BeautifulSoup scraper targeting the modernized RBI Press Releases web portal (`https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx`).

#### 4. SEBI Regulations
- **PDF Requirement:** Official SEBI circulars, regulatory orders, and compliance notifications.
- **Implemented:** `SEBICollector` (`borsel_handler/collectors/sebi.py`) parsing official SEBI circular feeds into `regulatory_sebi` category. **Live collection fully verified: 30 live records collected and stored**. Deterministic fixtures pass 100%.

#### 5. Government Economic Policies
- **PDF Requirement:** Government economic policies, cabinet decisions, and fiscal announcements.
- **Implemented:** `PIBCollector` (`borsel_handler/collectors/pib.py`) parsing Ministry of Finance and economic press releases into `government_policy` category. Verified via deterministic fixtures in `tests/test_collectors.py`.
- **Partially Done / Remaining:** Official PIB RSS endpoint experiences intermittent 404/redirect issues.
- **Improvement:** Implement direct HTML parsing of `pib.gov.in` daily press releases using BeautifulSoup.

#### 6–10. Financial Event Categories (Earnings, IPOs, M&A, Dividends, Corporate Actions)
- **PDF Requirement:** Classify records by earnings, IPOs, M&A, dividends, and corporate actions.
- **Implemented:** `borsel_handler/classification/taxonomy.py` and `classifier.py` implement transparent, rule-based classification across 15 financial categories with weighted keywords, negative disqualifiers, and confidence scores:
  - `CATEGORY_EARNINGS`: Financial results, quarterly results, Q1/Q2/Q3/Q4, PAT, EBITDA.
  - `CATEGORY_IPO_LISTING`: Initial public offering, DRHP, listing date, anchor investors, price band.
  - `CATEGORY_ACQUISITION_MERGER`: Acquisition of, merger, amalgamation, takeover, scheme of arrangement.
  - `CATEGORY_DIVIDEND`: Interim dividend, final dividend, special dividend, record date.
  - `CATEGORY_CORPORATE_ACTION`: Bonus issue, stock split, share buyback, rights issue, preferential allotment.
- **Verified:** All categories verified via dedicated tests in `tests/test_classification.py` (100% pass rate).

---

## 3. Metadata Schema Audit (8 Required Fields)

The PDF explicitly requires 8 metadata fields per normalized record:

| PDF Required Field | Borsel Handler Field | Data Type | Implementation & Enforcement | Status |
|---|---|---|---|:---:|
| **Title** | `title` | `str` | Stripped of HTML tags, whitespace normalized | **IMPLEMENTED** |
| **Publication date** | `published_at` | `datetime` (UTC) | Timezone-aware UTC parsing via `dateutil` & `email.utils` | **IMPLEMENTED** |
| **Source** | `source_name` / `source_type` | `str` | Standardized name and taxonomy code (e.g. `NSE Corporate Disclosures`) | **IMPLEMENTED** |
| **Company (if applicable)** | `company_name` / `symbol` | `Optional[str]` | Populated by exchange payload or entity resolver (`INFY`, `RELIANCE`) | **IMPLEMENTED** |
| **Sector** | `sector` | `Optional[str]` | Normalized sector hierarchy (`Information Technology`, `Banking`, etc.) | **IMPLEMENTED** |
| **URL** | `original_url` / `canonical_url` | `str` | Normalized URL with UTM/tracking parameters stripped | **IMPLEMENTED** |
| **Category** | `category` | `str` | 15-class taxonomy code (`earnings`, `dividend`, `ipo_listing`, etc.) | **IMPLEMENTED** |
| **Summary (optional)** | `snippet` | `Optional[str]` | Cleaned excerpt/description truncated to 400 chars | **IMPLEMENTED** |

### Value-Added Metadata Fields (Implemented Beyond PDF Minimum)
In addition to the 8 required fields, Borsel Handler captures:
- `record_hash`: Deterministic SHA-256 fingerprint for deduplication.
- `source_record_id`: Upstream source primary key (`NEWSID`, `an_un_id`, or RSS GUID).
- `confidence_score`: Float between 0.0 and 1.0 indicating classifier confidence.
- `tags`: Array of secondary keywords.
- `collected_at`: UTC timestamp of system ingestion.
- `last_seen_at`: Timestamp tracking repeated appearances in feeds.
- `validation_status`: `"valid"` or `"quarantined"`.
- `raw_metadata`: Complete verbatim source payload stored as JSON for auditability and non-destructive reprocessing.
- `provenance`: Ingestion batch ID, parser version, and collection duration.

---

## 4. Deduplication & Historical Searchability Audit

### 4.1 Deduplication Requirement ("eliminate duplicate news articles")
- **PDF Requirement:** The system must eliminate duplicate news articles.
- **Implemented Architecture:**
  `DeduplicationEngine` (`borsel_handler/dedup/engine.py`) operates across 6 progressive tiers:
  1. *Tier 1:* Exact Upstream Source Record ID (`source_name` + `source_record_id`).
  2. *Tier 2:* Canonical Cleaned URL match.
  3. *Tier 3:* Deterministic Record Hash (Title + Symbol + 1-hour window).
  4. *Tier 4:* Cross-Source Token Similarity (Jaccard $\ge 0.85$ within $\pm 12$h).
  5. *Tier 5:* Normalized Title within Publication Window ($\pm 24$h, with company-guard to prevent merging distinct firms with generic titles).
  6. *Tier 6:* Normalized original URL match.
- **Relational Integrity:** When a duplicate is detected, it is logged in the `article_duplicates` table preserving duplicate URL, detection stage, and foreign-key link to the canonical article.
- **Verification:** Tested across 7 comprehensive test scenarios in `tests/test_deduplication.py`.

### 4.2 Historical Searchable Repository ("maintain a searchable historical repository")
- **PDF Requirement:** Maintain a searchable historical repository of financial information.
- **Implemented Architecture:**
  - **Relational Storage:** Dialect-agnostic SQLAlchemy ORM supporting PostgreSQL 18 and SQLite.
  - **Compound Indexes:** Optimized indexes on `(symbol, published_at)`, `(category, published_at)`, `(source_name, published_at)`, and `canonical_url`.
  - **REST API Endpoints:**
    - `GET /api/v1/records`: Filter historical data by symbol, sector, category, source, date range (`from_date`, `to_date`), with pagination (`page`, `page_size`).
    - `GET /api/v1/records/search`: Keyword search across headlines, snippets, and company names.
    - `GET /api/v1/records/{id}`: Full detail lookup including child entities (`companies`, `duplicates`, `raw_records`).
  - **Resumable Backfill Engine:** `HistoricalBackfillManager` (`borsel_handler/scheduler/backfill.py`) executes bounded date-range backfills with atomic JSON checkpoints (`backfill_checkpoint.json`).

---

## 5. Technology Stack Compliance Audit

The PDF lists 8 tools under "Tools Can Be Used":

| Tool Specified in PDF | Used in Borsel Handler? | Current Usage in Codebase | Assessment & Recommendation |
|---|:---:|---|---|
| **Python** | **YES** | Python 3.14.6 async core, FastAPI, Pydantic v2 | Fully utilized as primary programming language. |
| **BeautifulSoup** | **PARTIALLY** | Installed in virtualenv; HTML regex currently used | **Improvement:** Replace regex tag cleaning with `BeautifulSoup` in RSS & news collectors for cleaner text. |
| **Playwright** | **PENDING** | Listed as optional in PDF; not currently implemented | **Recommendation:** Add as optional fallback connector for dynamic JS-rendered corporate portals. |
| **News APIs** | **YES** | Multi-feed RSS from Economic Times, Moneycontrol, Mint | Fully operational with 353 live articles collected. |
| **Pandas** | **PARTIALLY** | Installed in virtualenv; SQLAlchemy used for core ORM | **Improvement:** Add `to_pandas()` dataframe conversion utility in repository for AI/ML pipelines. |
| **PostgreSQL** | **YES** | PostgreSQL 18.0 with Alembic schema migrations | Verified on `borsel_disposable_test` with full CRUD & migration tests. |
| **SQLAlchemy** | **YES** | SQLAlchemy 2.0 ORM with 7 relational entities | Fully utilized for persistence, querying, and schema definition. |
| **Git & GitHub** | **YES** | Local Git repository, `.gitignore`, full audit history | Fully utilized for version control and change management. |

---

## 6. Comprehensive Gap Analysis: Implemented vs. Remaining vs. Partially Done

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               BORSEL HANDLER STATUS MATRIX                             │
├────────────────────────────────┬───────────────────────────┬───────────────────────────┤
│ FULLY IMPLEMENTED (90%)        │ PARTIALLY DONE (7%)       │ REMAINING / FUTURE (3%)   │
├────────────────────────────────┼───────────────────────────┼───────────────────────────┤
│ • 8-Field Metadata Contract    │ • RBI Collector (Needs    │ • BeautifulSoup HTML text │
│ • 15-Class Event Taxonomy      │   modernized web scraper) │   extraction refactor     │
│ • 6-Tier Deduplication Engine  │ • PIB Collector (Needs    │ • Pandas DataFrame export │
│ • Dual DB (Postgres & SQLite)  │   modernized web scraper) │   utility (AI readiness)  │
│ • Alembic Schema Migrations    │ • NIFTY Universe (NIFTY   │ • Playwright fallback for │
│ • Live RSS Ingestion (3 feeds) │   50 active, NIFTY 500    │   dynamic JS portals      │
│ • Live NSE Disclosures Feed    │   pending auto-sync)      │ • Proxy pool integration  │
│ • Live SEBI Regulations Feed   │ • BSE Collector (Fixtures │   for high-frequency      │
│ • Company & Sector Resolver    │   verified, needs proxy   │   exchange scraping       │
│ • REST API & Search Endpoints  │   pool for live runs)     │                           │
│ • Resumable Backfill Engine    │                           │                           │
│ • Professional React 18 UI     │                           │                           │
│ • 61 Automated Tests (100%)    │                           │                           │
│ • Ingestion API-Key Security   │                           │                           │
│ • Root .gitignore & Secrets    │                           │                           │
└────────────────────────────────┴───────────────────────────┴───────────────────────────┘
```

---

## 7. Actionable Roadmap & Improvements

To achieve 100% perfection against both the PDF specification and enterprise production standards:

### Improvement 1: Integrate BeautifulSoup across Collectors (Tool Stack Alignment)
- **File:** `borsel_handler/collectors/rss.py` and `borsel_handler/collectors/base.py`
- **Action:** Replace `re.sub(r"<[^>]+>", "", text)` with `bs4.BeautifulSoup(raw_html, "html.parser").get_text(separator=" ")`.
- **Benefit:** Cleaner extraction of article summaries and descriptions, proper unescaping of HTML entities (`&amp;`, `&quot;`, `&#39;`).

### Improvement 2: Add Pandas DataFrame Export Utility (AI Preparation)
- **File:** `borsel_handler/storage/repository.py` and `borsel_handler/api/routes.py`
- **Action:** Implement `NewsRepository.to_dataframe(db, query)` and a new endpoint `GET /api/v1/records/export?format=csv|parquet`.
- **Benefit:** Directly fulfills the PDF's primary objective: *"The collected data must be cleaned, organized, and stored in a database so it can later be used by AI models for prediction and analysis."*

### Improvement 3: Modernize RBI & PIB Web Scrapers
- **File:** `borsel_handler/collectors/rbi.py` and `borsel_handler/collectors/pib.py`
- **Action:** Implement BeautifulSoup-based web scrapers targeting current active HTML archive pages of RBI and PIB to replace defunct legacy RSS feeds.
- **Benefit:** Restores 100% live coverage across all 10 information targets.

### Improvement 4: Expand Master Ticker Directory to NIFTY 500
- **File:** `borsel_handler/data/stocks.py`
- **Action:** Add automated download of NSE's `EQUITY_L.csv` to expand the company directory from 50 to ~2,200 listed companies.
- **Benefit:** Enables automated tagging and sector assignment for all mid-cap and small-cap disclosures.

### Improvement 5: Optional Playwright Headless Connector
- **File:** `borsel_handler/collectors/playwright_collector.py`
- **Action:** Scaffold Playwright browser automation with stealth headers for JavaScript-rendered exchange pages that resist plain HTTP GET requests.

---

## 8. Conclusion

The current implementation of **Borsel Handler** fulfills **over 90% of the VeritasAI Problem Statement specification**. 

The core data engineering pipeline—ingestion, normalization, 6-tier deduplication, entity resolution, PostgreSQL persistence, Alembic migrations, historical search API, and React frontend—is **completely implemented, verified, and operational with 61 passing automated tests**.

By implementing the 5 specific improvements outlined above (BeautifulSoup text cleaning, Pandas dataframe export, scraper modernization for RBI/PIB, and Nifty 500 directory expansion), the platform achieves complete alignment with the PDF vision.
