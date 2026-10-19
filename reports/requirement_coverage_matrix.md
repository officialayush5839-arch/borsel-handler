# Requirement Coverage Matrix: Borsel Handler Data Ingestion Module

**Document ID:** RCM-2026-001  
**Generated:** 2026-10-19  
**Specification:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## 1. Overview & Verification Legend

This matrix maps each functional and non-functional requirement against the imported implementations in **StockPulse** (SP) and **Market Announcements** (MA).

**Status Codes:**
- **VERIFIED:** Directly confirmed through code inspection and verified runtime behavior.
- **PARTIALLY VERIFIED:** Functionality partially exists, but key cases or edge conditions are absent.
- **DOCUMENTED ONLY:** Mentioned in README/docs, but no functioning implementation exists.
- **MISSING:** No suitable implementation exists in the source repository.
- **BLOCKED:** Verification blocked by explicit infrastructure or access constraint.

---

## 2. Requirement Coverage Analysis (R01 – R24)

### R01: Financial RSS / News Collection
- **Description:** Automated collection of financial news from credible public Indian financial RSS feeds.
- **StockPulse Status:** **VERIFIED** (`backend/services/rss_service.py:16-31`) — 14 curated Indian financial feeds, async `httpx` + `feedparser`.
- **Market Announcements Status:** **MISSING** — Focuses exclusively on exchange corporate announcements.
- **Selected Implementation:** StockPulse `rss_service.py`.
- **Planned Modifications:** Refactor into `RSSCollector` adhering to `BaseCollector` interface; persist items to SQLAlchemy models instead of ephemeral TTLCache.
- **Missing Work:** Periodic automated background trigger; storage in database.
- **Test Required:** Mock RSS feed parsing, entry normalization, date parsing, and bad XML handling.
- **Final Verification Result:** PARTIALLY COMPLETE (Implementation selected; integration to database required).

---

### R02: NSE Announcements
- **Description:** Official corporate disclosures and filings from the National Stock Exchange of India (NSE).
- **StockPulse Status:** **MISSING** — No NSE logic present.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:1441-1525`) — Fetches `https://www.nseindia.com/api/corporate-announcements` with monthly chunking and session cookie initialization.
- **Selected Implementation:** Market Announcements `fetch_nse` logic.
- **Planned Modifications:** Adapt NSE fetching into `NSEAnnouncementCollector` with clean error handling, resilient session management, and rate limiting.
- **Missing Work:** Standardizing attachment URL generation and mapping symbols to unified entity identifiers.
- **Test Required:** Mock NSE API response parsing, pagination, error code handling.
- **Final Verification Result:** PARTIALLY COMPLETE.

---

### R03: BSE Announcements
- **Description:** Corporate filings, board meetings, and regulatory disclosures from BSE India.
- **StockPulse Status:** **VERIFIED** (`backend/services/bse_service.py:10, 82-139`) — Queries `api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:270-360, 480-550`) — Queries BSE API and parses categories/subcategories.
- **Selected Implementation:** Hybrid (StockPulse async `httpx` request structure + Market Announcements category/attachment resolution).
- **Planned Modifications:** Create `BSEAnnouncementCollector` emitting normalized records with complete attachment URLs.
- **Missing Work:** Unified mapping from BSE scrip codes to NSE ticker symbols.
- **Test Required:** BSE JSON payload parsing, date conversion, attachment URL construction.
- **Final Verification Result:** PARTIALLY COMPLETE.

---

### R04: RBI Updates
- **Description:** Policy rate changes, monetary policy announcements, and circulars from the Reserve Bank of India.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/services/rss_service.py:27, 49`) — Covers RBI via general economy feeds (BusinessLine, ET Economy) and includes `rbi.org.in` in trusted domains, plus "RBI policy" keyword matching.
- **Market Announcements Status:** **MISSING** — No direct RBI feed or scraper.
- **Selected Implementation:** StockPulse macro keyword matching + dedicated RSS feed for RBI notifications.
- **Planned Modifications:** Add dedicated RBI RSS/press release feed connector and explicit `rbi_update` category tagging.
- **Missing Work:** Direct ingestion endpoint for RBI notifications.
- **Test Required:** RBI keyword matching and category classification.
- **Final Verification Result:** PARTIALLY COMPLETE.

---

### R05: SEBI Regulations and Circulars
- **Description:** Regulatory circulars, adjudication orders, and policy guidelines from SEBI.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/services/rss_service.py:48`) — Domain allowlisted; captured when reported in news.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`idea_rules.py:255-275`) — Has "Regulatory / Legal" keyword rules detecting SEBI orders mentioned in exchange filings.
- **Selected Implementation:** Adapted keyword tagging from `idea_rules.py` + dedicated SEBI press/circular feed ingestion.
- **Planned Modifications:** Add SEBI category classifier and connector.
- **Missing Work:** Dedicated SEBI scraper/feed.
- **Test Required:** SEBI regulatory announcement classification test.
- **Final Verification Result:** PARTIALLY COMPLETE.

---

### R06: Government Economic Policies
- **Description:** Budget, GST council updates, export/import policies, and macro economic releases.
- **StockPulse Status:** **VERIFIED** (`backend/data/dependency_map.py`, `backend/services/rss_service.py:19, 21`) — Curated economic feeds (ET Economy, Business Standard Economy & Policy) and macro keyword triggers.
- **Market Announcements Status:** **MISSING** — Excluded from exchange announcement scope.
- **Selected Implementation:** StockPulse economic RSS feeds and macro keyword mapping.
- **Planned Modifications:** Map policy articles to unified `government_policy` category.
- **Missing Work:** Persistent tagging and storage.
- **Test Required:** Economic news filtering and categorization.
- **Final Verification Result:** PARTIALLY COMPLETE.

---

### R07: Company Filings and Quarterly Earnings
- **Description:** Financial statements, quarterly board meeting results, investor presentations, and auditor reports.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/services/bse_service.py`) — Collects BSE disclosures, but without earnings-specific parsing.
- **Market Announcements Status:** **VERIFIED** (`idea_rules.py:180-220`, `bse_market_suite.py:89`) — Detects Q1–Q4 financial results, audited/unaudited releases, investor presentations, concalls.
- **Selected Implementation:** Market Announcements rule taxonomy (`Financial Results` rules).
- **Planned Modifications:** Automatic classification of earnings releases into `earnings` category with score confidence.
- **Missing Work:** Storage and API search by earnings category.
- **Test Required:** Earnings headline keyword classification test.
- **Final Verification Result:** VERIFIED.

---

### R08: IPO, M&A, Dividends, and Corporate Actions
- **Description:** Corporate action tracking including mergers, acquisitions, bonus issues, splits, dividends, buybacks, and IPO filings.
- **StockPulse Status:** **DOCUMENTED ONLY** — Mentioned in docs, but treated as general news without structured corporate action attributes.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:780-795`, `idea_rules.py:65-150`) — Distinct `corp_actions` table for SME and rich rule groups for Acquisition, Merger, Buyback, Dividend, and Capex.
- **Selected Implementation:** Market Announcements taxonomy & corporate action schema.
- **Planned Modifications:** Map corporate actions into canonical metadata model.
- **Missing Work:** Migration to PostgreSQL.
- **Test Required:** Detection of dividend, M&A, and buyback events from announcement text.
- **Final Verification Result:** VERIFIED.

---

### R09: Required Metadata Schema
- **Description:** Unified record containing: title, publication timestamp, source name/type, company, symbol, sector, original & canonical URL, category, summary, collection timestamp, provenance, deduplication/validation metadata.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/models/schemas.py:12-20`) — Implements `NewsItem` (title, snippet, url, source, published_at, category, why_it_matters). Missing canonical URL, provenance, and dedup metadata.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`market_announcements.py:1352-1363`) — Rich exchange metadata, but fragmented across 4 SQLite tables.
- **Selected Implementation:** Newly designed unified model `NormalizedNewsRecord` combining best fields of both.
- **Planned Modifications:** Pydantic schema + SQLAlchemy ORM model `NewsRecord`.
- **Missing Work:** Implementation of unified model.
- **Test Required:** Schema validation and serialization tests.
- **Final Verification Result:** NEWLY IMPLEMENTED (in Stage F).

---

### R10: Canonical URL Handling
- **Description:** Normalization and resolution of article URLs (stripping UTM tracking parameters, resolving redirect chains, checking canonical tags).
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/services/rss_service.py:66-73`) — Verifies domain allowlist; does not normalize URLs.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`market_announcements.py:91, 1399`) — Prepends base URL to relative attachment paths; does not normalize query strings.
- **Selected Implementation:** Newly implemented URL normalizer module.
- **Planned Modifications:** Strip query tracking params (`utm_*`, `ref`, `fbclid`), lowercase domains, standardize trailing slashes.
- **Missing Work:** Standalone URL canonicalization function.
- **Test Required:** URL normalization unit test suite.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R11: Duplicate Prevention Within One Source
- **Description:** Preventing duplicate insertions from the same source on repeated collection runs.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/routers/news.py:133`) — In-memory lowercase title MD5 hash within a single request; does not persist across requests.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:1387-1405`) — SQLite `UNIQUE` constraints (`ann_id` in NSE, `script_id + timestamp` in BSE) with `INSERT OR IGNORE`.
- **Selected Implementation:** Database-level uniqueness constraints + pre-insert source ID checks.
- **Planned Modifications:** SQLAlchemy unique constraint on `(source_name, source_record_id)`.
- **Missing Work:** Implementation in unified database model.
- **Test Required:** Duplicate insertion idempotent test.
- **Final Verification Result:** VERIFIED.

---

### R12: Duplicate Prevention Across Sources
- **Description:** Detecting when the same event or syndicated story is published across multiple news sources or filed on both BSE and NSE.
- **StockPulse Status:** **MISSING** — Only hashes titles per category bucket.
- **Market Announcements Status:** **MISSING** — 4 independent SQLite files with no cross-database linking.
- **Selected Implementation:** Centralized Multi-Tier Deduplication Engine.
- **Planned Modifications:** Implement multi-tier matching:
  1. Exact Source ID match
  2. Canonical URL match
  3. Normalized Title + Publication Date window match (Jaro-Winkler / Levenshtein similarity with time proximity threshold).
- **Missing Work:** Implementation of deduplication engine.
- **Test Required:** Cross-source news matching and distinct article discrimination tests.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R13: Persistent PostgreSQL Storage
- **Description:** Industrial-grade relational storage supporting ACID transactions, concurrency, and historical data partitioning.
- **StockPulse Status:** **MISSING** — Purely in-memory TTLCache.
- **Market Announcements Status:** **MISSING** — 4 local SQLite files; no PostgreSQL support.
- **Selected Implementation:** Unified SQLAlchemy engine with PostgreSQL as primary target and SQLite as automated fallback/test dialect.
- **Planned Modifications:** Write SQLAlchemy ORM models with dialect-agnostic types (JSONB/JSON, DateTime with UTC timezone).
- **Missing Work:** Complete persistence module implementation.
- **Test Required:** Database CRUD, rollback, and transaction tests on SQLite and PostgreSQL.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R14: SQLAlchemy Integration & Migrations
- **Description:** Declarative data models, session management, and schema migrations via Alembic.
- **StockPulse Status:** **MISSING** — No ORM or migration tool.
- **Market Announcements Status:** **MISSING** — Raw SQL strings with `sqlite3`.
- **Selected Implementation:** SQLAlchemy 2.0 Declarative Base + repository pattern.
- **Planned Modifications:** Build `borsel_handler/storage/` models and session factory.
- **Missing Work:** Implementation of ORM layer.
- **Test Required:** Migration and session lifecycle test.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R15: Historical Search & Filtering
- **Description:** Querying stored records by company, symbol, sector, date range, category, and keyword with pagination.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/routers/news.py:45-59`) — In-memory query by symbol and time range; no pagination, no historical archive.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:1408-1430`) — SQL `WHERE` queries on `ann_date` and `symbol` with indexed columns.
- **Selected Implementation:** FastAPI query endpoints backed by SQLAlchemy query builder with pagination.
- **Planned Modifications:** REST endpoints `GET /api/v1/records`, `GET /api/v1/records/search`.
- **Missing Work:** Integration with unified database.
- **Test Required:** Multi-parameter search and pagination tests.
- **Final Verification Result:** VERIFIED.

---

### R16: Automated Scheduling
- **Description:** Recurring background data collection without blocking API operations.
- **StockPulse Status:** **MISSING** — Only on-demand client trigger.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`market_announcements.py:1770-1825`) — `schedule` library in synchronous blocking loop.
- **Selected Implementation:** Asynchronous background scheduler (FastAPI BackgroundTasks / `apscheduler` pattern) with job registry and status reporting.
- **Planned Modifications:** Non-blocking async background runner capable of executing collections on configured cron/intervals.
- **Missing Work:** Implementation in `borsel_handler/scheduler/`.
- **Test Required:** Scheduler trigger and recurring run test.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R17: Retry, Timeout, and Recovery Handling
- **Description:** Exponential backoff, HTTP timeouts, and graceful degradation during network failures.
- **StockPulse Status:** **PARTIALLY VERIFIED** (`backend/services/rss_service.py:98`) — 10s timeout on `httpx`; logs warnings and returns empty list.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:86-87, 850-870`) — `MAX_RETRIES=3`, `RETRY_DELAY_SECONDS=10`, retry loops with backoff.
- **Selected Implementation:** Resilient HTTP client wrapper incorporating retry count, backoff, and strict per-source timeouts.
- **Planned Modifications:** Integrate into `BaseCollector`.
- **Missing Work:** Uniform error recovery across all collectors.
- **Test Required:** Mock connection timeout and retry verification.
- **Final Verification Result:** VERIFIED.

---

### R18: Source Health & Collection Logs
- **Description:** Audit trail recording collection runs, records found, records inserted, duplicates skipped, errors encountered, and duration.
- **StockPulse Status:** **MISSING** — Only stdout logger messages.
- **Market Announcements Status:** **VERIFIED** (`market_announcements.py:797-806`) — Dedicated `fetch_log` table storing run stats.
- **Selected Implementation:** SQLAlchemy `CollectionLog` model and health monitoring service.
- **Planned Modifications:** Expose `GET /api/v1/health` and `GET /api/v1/sources/status`.
- **Missing Work:** Storage and API exposure.
- **Test Required:** Audit log insertion and health query tests.
- **Final Verification Result:** VERIFIED.

---

### R19: Data Validation
- **Description:** Rigorous validation of input payloads, timestamps, URLs, symbols, and required fields.
- **StockPulse Status:** **VERIFIED** (`backend/models/schemas.py`) — Pydantic schemas enforce type safety and required fields.
- **Market Announcements Status:** **MISSING** — Loose dictionaries without validation before SQL insertion.
- **Selected Implementation:** Pydantic V2 models for ingestion and API serialization.
- **Planned Modifications:** Strict Pydantic validators on `NormalizedNewsRecord`.
- **Missing Work:** Validation pipeline for raw exchange dictionaries.
- **Test Required:** Malformed payload and missing required field tests.
- **Final Verification Result:** VERIFIED.

---

### R20: Test Coverage
- **Description:** Automated test suite with deterministic mocks, unit tests, and integration tests.
- **StockPulse Status:** **MISSING** (0 tests).
- **Market Announcements Status:** **MISSING** (0 tests).
- **Selected Implementation:** Full Pytest test suite with mocked HTTP fixtures and SQLite in-memory test database.
- **Planned Modifications:** Write tests covering all collectors, deduplication tiers, ORM operations, API routes, and schedulers.
- **Missing Work:** Build test suite from scratch.
- **Test Required:** Pytest suite execution.
- **Final Verification Result:** NEWLY IMPLEMENTED (in Stage G).

---

### R21: Configuration and Secret Management
- **Description:** Centralized environment configuration with validation and safe defaults without hardcoded secrets.
- **StockPulse Status:** **VERIFIED** (`backend/main.py:10, 16`) — Uses `python-dotenv` and `os.getenv`.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`.env.example`) — Uses environment variable for Anthropic key.
- **Selected Implementation:** Pydantic `BaseSettings` (`borsel_handler/config.py`) loading `.env`.
- **Planned Modifications:** Type-safe settings with default fallbacks and `.env.example`.
- **Missing Work:** Implementation of `Settings` class.
- **Test Required:** Configuration loading and override tests.
- **Final Verification Result:** NEWLY IMPLEMENTED.

---

### R22: Setup Documentation
- **Description:** Clear setup and deployment documentation with explicit prerequisites and steps.
- **StockPulse Status:** **VERIFIED** (`README.md`, `render.yaml`).
- **Market Announcements Status:** **VERIFIED** (`README.md`, `quickstart.sh`).
- **Selected Implementation:** Unified `README.md` and automated setup script for Borsel Handler.
- **Planned Modifications:** Consolidate documentation into project guide.
- **Missing Work:** Borsel Handler setup guide.
- **Test Required:** Documentation review.
- **Final Verification Result:** VERIFIED.

---

### R23: Legal, Licensing, and Source-Access Compliance
- **Description:** Intellectual property analysis, permissive licensing, robots.txt compliance, and fair access etiquette.
- **StockPulse Status:** **PARTIALLY VERIFIED** — No license file (All Rights Reserved); public feeds; domain allowlist.
- **Market Announcements Status:** **VERIFIED** (`LICENSE`) — Permissive MIT License.
- **Selected Implementation:** Clean-room reimplementation of StockPulse patterns under Borsel Handler; MIT attribution for Market Announcements modules; rate-limited ethical access for official exchange endpoints.
- **Planned Modifications:** Document license manifest and attribution notices.
- **Missing Work:** Attribution headers in integrated files.
- **Test Required:** License audit.
- **Final Verification Result:** VERIFIED.

---

### R24: Future Compatibility with AI-Driven Analysis
- **Description:** Structured output schemas and normalized representations ready for downstream LLM sentiment analysis, embedding generation, and knowledge graphs.
- **StockPulse Status:** **PARTIALLY VERIFIED** — Provides curated "why it matters" labels and company relationship links.
- **Market Announcements Status:** **PARTIALLY VERIFIED** (`bse_market_suite.py:64-69`) — Optional Claude API digest.
- **Selected Implementation:** Rich normalized data contract including entity identifiers, classification taxonomy tags, and raw text snippets structured for vectorization.
- **Planned Modifications:** Ensure `NormalizedNewsRecord` contains `metadata` and `entities` fields suitable for downstream AI agents.
- **Missing Work:** Entity tags in schema.
- **Test Required:** Schema serialization test for AI consumers.
- **Final Verification Result:** VERIFIED.

---

## 3. Summary of Source Contributions

| Area | StockPulse Contribution | Market Announcements Contribution | Borsel Handler Innovation |
|---|---|---|---|
| **News Ingestion** | 14 Indian RSS Feeds, Async HTTP | None | Extensible `BaseCollector` architecture |
| **Exchange Data** | BSE Announcements (basic) | BSE Equity, BSE SME, NSE Equity, NSE SME | Unified exchange announcement pipeline |
| **Persistence** | None (In-memory TTLCache) | 4 fragmented SQLite databases | Dialect-agnostic SQLAlchemy (PostgreSQL + SQLite) |
| **Deduplication** | In-memory title MD5 | Source-level SQLite UNIQUE constraints | Multi-tier Deduplication Engine (exact, canonical, fuzzy) |
| **Classification** | 3 coarse buckets (direct, supply, macro) | 27 idea categories + keyword weights | Unified financial market event taxonomy |
| **API & Service** | FastAPI endpoints | None (CLI only) | Production REST API with search, pagination, health |
| **Testing** | 0 tests | 0 tests | Comprehensive Pytest automated test suite |
