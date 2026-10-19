# Borsel Handler — Product Requirements Document (PRD)

**Document ID:** PRD-2026-BH  
**Version:** 2.0.0  
**Effective Date:** 2026-10-19  
**Status:** Approved for Implementation  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform (Data Collection Module)

---

## 1. Executive Summary & Vision

Borsel Handler is an institutional-grade financial data engineering and market intelligence platform purpose-built for the Indian capital markets ecosystem. 

The core mission of the current phase (**Market Data Collection and Storage System**) is to establish an automated, resilient, multi-source ingestion pipeline that continuously acquires, cleanses, normalizes, classifies, deduplicates, and permanently stores financial news, exchange announcements, corporate filings, and regulatory circulars across Indian financial venues.

The collected repository serves as the authoritative, tamper-evident historical data lake for downstream financial analysis, supply chain graph analysis, and AI reasoning. The system is engineered strictly around data engineering excellence, verifiable provenance, and reproducible automated testing.

---

## 2. Problem Statement

Indian capital markets present several distinct data acquisition challenges:
1. **Source Fragmentation:** Critical market information is split across multiple disparate formats — RSS feeds from news media, JSON APIs from BSE India, session-authenticated REST endpoints from NSE, and HTML/RSS circulars from regulators (RBI, SEBI) and government ministries (PIB).
2. **Duplicate Saturation:** Up to 70% of intraday news items are syndicated duplicates or cross-filed across both BSE and NSE, leading to redundant noise.
3. **Entity Resolution Ambiguity:** Financial news often mentions companies by colloquial names, brand names, or abbreviations without structured stock tickers or ISINs.
4. **Data Volatility:** Exchange APIs frequently change parameters, employ anti-scraping countermeasures, or suffer intermittent latency.
5. **Lack of Provenance:** Aggregators often discard raw payloads, making historical audit or compliance validation impossible.

Borsel Handler resolves these challenges through a unified plugin-based collector framework, a 6-stage deduplication engine, structured entity mapping, and dual-dialect SQLAlchemy storage backed by Alembic migrations.

---

## 3. Scope of Current Phase

### 3.1 In-Scope Capabilities
- Continuous and on-demand data collection across 6 source categories:
  - **Category A:** Curated Indian Financial RSS media feeds (Economic Times, Business Standard, LiveMint, NDTV Profit, Financial Express, CNBC-TV18, Reuters India).
  - **Category B:** Official Stock Exchange Disclosures (BSE India Corporate Announcements and NSE Equities & SME filings).
  - **Category C:** Reserve Bank of India (RBI) notifications, press releases, and circulars.
  - **Category D:** Securities and Exchange Board of India (SEBI) circulars, adjudication orders, and regulations.
  - **Category E:** Press Information Bureau (PIB) / Government Economic Policy releases and Ministry of Finance announcements.
  - **Category F & G:** Corporate Filings & Corporate Events (earnings reports, IPO listings, M&A, dividends, and corporate actions).
- Common normalization layer: whitespace cleaning, HTML entity decoding, sanitization, strict UTC ISO-8601 timestamps, and canonical URL derivation.
- Structured Company and Sector Resolution for Indian equities with word-boundary matching and confidence scoring.
- Comprehensive Event Classification Taxonomy covering 12 distinct financial and regulatory categories.
- Multi-Tier Deduplication Pipeline preserving provenance and recording duplicate candidate relationships in persistent storage.
- Relational schema in PostgreSQL (production) with SQLite compatibility for deterministic local test runs.
- Database versioning and migrations managed via Alembic.
- High-performance FastAPI REST API supporting search, structured filtering, source health monitoring, collection triggers, and system statistics.
- Responsive, clean financial dashboard frontend featuring a light white/light-blue visual hierarchy, search, filter controls, source-health monitors, and article detail inspection.
- 100% deterministic test suite utilizing local fixtures without unmocked live network dependencies.

### 3.2 Explicitly Excluded Functionality
- Automated stock trading or algorithmic order execution.
- Stock price prediction or automated investment recommendations.
- Portfolio accounting and brokerage integration.
- Speculative machine learning or sentiment-based buy/sell signaling.
- Bypassing CAPTCHAs, paywalls, or anti-scraping restrictions on protected sites.
- Synthesizing or hardcoding fabricated financial news records.

---

## 4. User Personas & Core Workflows

### 4.1 Target Personas
1. **Quantitative Researcher & Financial Analyst:** Queries historical company filings, corporate actions, and regulatory circulars with structured ticker and sector filtering.
2. **Data Engineer & Pipeline Administrator:** Monitors source health, inspects collection run logs, tracks duplicate prevention rates, and initiates backfill runs.
3. **Compliance & Audit Officer:** Validates provenance, raw payloads, and original source links for corporate filings.

### 4.2 Key User Workflows
- **Workflow 1: Market Intelligence Exploration:** User opens the Borsel Handler dashboard, selects an equity symbol (e.g., `TCS`), selects a time window, and reviews deduplicated direct announcements, supply-chain news, and macro policy circulars.
- **Workflow 2: Historical Keyword & Regulatory Search:** User executes full-text search for terms such as `"dividend"`, `"merger"`, or `"monetary policy"` across all venues, filtering by category and date range.
- **Workflow 3: Ingestion Health Monitoring & Manual Trigger:** Pipeline admin views `/api/v1/sources` and `/api/v1/stats`, checks error logs for exchange endpoints, and triggers an on-demand refresh for a specific lookback window.

---

## 5. Functional Requirements (Unique IDs)

| Requirement ID | Category | Description | Priority |
|---|---|---|---|
| **REQ-01** | Ingestion | Collector framework implementing `BaseCollector` interface for all sources. | Mandatory |
| **REQ-02** | Ingestion | Financial RSS news collector supporting curated Indian business publications. | Mandatory |
| **REQ-03** | Ingestion | BSE Corporate Announcements collector with attachment URL resolution. | Mandatory |
| **REQ-04** | Ingestion | NSE Corporate Disclosures collector supporting Equities and SME segments. | Mandatory |
| **REQ-05** | Ingestion | RBI collector for press releases, circulars, and monetary policy updates. | Mandatory |
| **REQ-06** | Ingestion | SEBI collector for regulatory circulars, notices, and enforcement orders. | Mandatory |
| **REQ-07** | Ingestion | Government Economic Policy collector (PIB / Ministry of Finance). | Mandatory |
| **REQ-08** | Ingestion | Corporate Action & Earnings extraction from exchange announcement feeds. | Mandatory |
| **REQ-09** | Normalization | Sanitization of HTML, unicode entity decoding, and text truncation limits. | Mandatory |
| **REQ-10** | Normalization | Strict UTC conversion for all publication and collection timestamps. | Mandatory |
| **REQ-11** | Normalization | URL normalization stripping UTM parameters, ref tags, and resolving canonical links. | Mandatory |
| **REQ-12** | Entity Resolution | Company resolution supporting Nifty 50 & broad Indian equities with structured sectors. | Mandatory |
| **REQ-13** | Classification | Taxonomy classifier assigning records to 12 distinct financial and regulatory categories. | Mandatory |
| **REQ-14** | Deduplication | Multi-stage deduplication: Source ID, Canonical URL, Normalized Title, and Near-duplicate matching. | Mandatory |
| **REQ-15** | Persistence | Normalized relational PostgreSQL/SQLite schema: sources, articles, companies, categories, runs, duplicates. | Mandatory |
| **REQ-16** | Migrations | Alembic database migration environment and versioned scripts. | Mandatory |
| **REQ-17** | API | REST API endpoint for listing and filtering articles (`GET /api/v1/records`). | Mandatory |
| **REQ-18** | API | REST API endpoint for full-text search (`GET /api/v1/records/search`). | Mandatory |
| **REQ-19** | API | REST API endpoint for article detail inspection (`GET /api/v1/records/{id}`). | Mandatory |
| **REQ-20** | API | REST API endpoints for source status and run audit logs (`GET /api/v1/sources`, `/api/v1/sources/logs`). | Mandatory |
| **REQ-21** | API | REST API endpoint for platform summary statistics (`GET /api/v1/stats`). | Mandatory |
| **REQ-22** | API | On-demand ingestion trigger endpoint (`POST /api/v1/ingest/trigger`). | Mandatory |
| **REQ-23** | Scheduling | Asynchronous background collection runner with exponential backoff and jitter. | Mandatory |
| **REQ-24** | Frontend | Responsive React dashboard with light white/light-blue theme, search, filters, and health monitoring. | Mandatory |
| **REQ-25** | Testing | Automated pytest suite with local mock fixtures verifying collectors, dedup, db, and API. | Mandatory |

---

## 6. Non-Functional Requirements

1. **Reliability & Fault Isolation:** A failure in one source collector (e.g., NSE network timeout) must not interrupt or fail the collection runs of other sources.
2. **Idempotence:** Re-running the collection runner against the exact same source payloads must insert zero duplicate records and update run audit metrics accurately.
3. **Data Provenance:** Every persisted article must retain its originating source name, original URL, canonical URL, raw metadata dictionary, and ingestion timestamp.
4. **Performance:** Search and filter API queries on indexed columns (`published_at`, `symbol`, `category`, `source_name`) must execute in < 150ms on historical datasets up to 100,000 records.
5. **Dialect Portability:** Storage code must execute transparently on both PostgreSQL 14+ and SQLite 3.35+ without requiring code modifications.
6. **Security & Secrets:** All secrets, database URLs, and API tokens must be configurable via environment variables or `.env`. No plaintext credentials in Git.
7. **Rate Limiting & Politeness:** Collectors must respect source rate limits, implement backoff delays, and supply clear descriptive User-Agent headers.

---

## 7. Supported Data Sources & Status

| Source Name | Category | Access Method | Target URL / Feed | Status |
|---|---|---|---|---|
| **Curated RSS Feeds** | Financial News | HTTP/RSS | 14 Indian business media feeds (ET, BS, Mint, NDTV, FE) | Active / Verified |
| **BSE India Equities** | Exchange Filings | JSON API | `api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w` | Active / Verified |
| **NSE India Equities** | Exchange Filings | REST API | `nseindia.com/api/corporate-announcements` (Equities) | Active / Verified |
| **NSE India SME** | Exchange Filings | REST API | `nseindia.com/api/corporate-announcements` (SME) | Active / Verified |
| **Reserve Bank of India** | Regulatory Updates | RSS / HTTP | `rbi.org.in/rss/rss_pressrelease.xml` | Active / Implemented |
| **SEBI India** | Regulatory Updates | RSS / HTTP | `sebi.gov.in/sebirss.xml` | Active / Implemented |
| **PIB Economic Releases** | Government Policy | RSS / HTTP | `pib.gov.in/RssMain.aspx?ModId=2&MinId=0` (Finance/Economy) | Active / Implemented |

---

## 8. Data Schema & Metadata Requirements

Each normalized article record must capture:
- `id`: Unique integer surrogate primary key.
- `record_hash`: Deterministic SHA-256 fingerprint generated from canonical title, date, and source.
- `title`: Sanitized, non-empty text string.
- `snippet`: Cleaned plain-text summary or excerpt.
- `original_url`: Raw URL from source feed.
- `canonical_url`: Normalized URL stripped of tracking parameters.
- `published_at`: UTC timestamp of original publication.
- `collected_at`: UTC timestamp of ingestion.
- `source_name`: Standardized source identifier.
- `source_type`: Category identifier (`rss`, `bse_announcement`, `nse_announcement`, `rbi_circular`, `sebi_regulation`, `pib_policy`).
- `source_record_id`: Unique identifier from upstream source if provided.
- `company_name`: Standardized corporate entity name.
- `symbol`: NSE/BSE equity ticker symbol (e.g., `INFY`).
- `sector`: Industry sector (e.g., `Information Technology`, `Banking`).
- `category`: Classification tag from taxonomy.
- `confidence_score`: Floating point score (0.0 – 1.0) for classification/extraction confidence.
- `tags`: List of keyword tags.
- `raw_metadata`: Full JSON dictionary of the original upstream payload.
- `validation_status`: Status flag (`valid`, `quarantine`, `provisional`).

---

## 9. Acceptance Criteria & Definition of Done

A deliverable or phase is declared **DONE** only when:
1. All functional requirements tagged for the milestone are implemented in source code.
2. 100% of unit and integration tests pass cleanly with `pytest`.
3. Database migrations successfully apply to clean databases via Alembic.
4. Deterministic fixtures validate edge cases (malformed HTML, missing dates, duplicate payloads, untrusted URLs).
5. Frontend renders live backend data without mock stubs or broken component states.
6. Traceability across all 7 project-control files is verified with no conflicting specifications.
