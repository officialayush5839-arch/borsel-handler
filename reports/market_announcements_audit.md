# Market Announcements Architecture & Capability Audit Report

**Repository:** `upstream/market_announcements`  
**Base Commit:** `270014b24cfae53e546f9fc48ff307ab976a09fd` (Fri Jul 17 11:42:56 2026 +0530)  
**Evaluator:** Borsel Handler Integration Engine  
**Verification Standard:** Five-State Evidence-Based Verification (VERIFIED, PARTIALLY VERIFIED, DOCUMENTED ONLY, MISSING, BLOCKED)

---

## 1. Architectural Overview

Market Announcements is a batch-oriented data ingestion, scoring, and analytics suite for Indian stock exchange disclosures. Its architecture is divided into three functional layers:

1. **Scraping Layer (`market_announcements.py`):** A standalone CLI script that scrapes disclosures from four exchange channels:
   - BSE Equity (via BSE API / `bse` library)
   - BSE SME (via HTML parsing of `bsesme.com`)
   - NSE Equity (via `curl_cffi` session impersonation of Chrome to bypass bot detection)
   - NSE SME (via the same NSE API with SME index parameter)
   Each source writes to its own isolated SQLite database file (`bse_equity.db`, `bse_sme.db`, `nse_equity.db`, `nse_sme.db`).

2. **Classification & Scoring Layer (`announcement_ideas_pipeline.py`, `idea_rules.py`):**
   A rule-based keyword scoring engine that operates on `bse_equity.db`. It maps announcements against 27 distinct event categories across 7 macro groups (Growth & Expansion, Restructuring, Fundraising, etc.), generating weighted match scores (0–100) stored in relational tables (`idea_groups`, `idea_types`, `announcement_idea_scores`).

3. **Dashboard Layer (`bse_market_suite.py`):**
   A Streamlit multi-page web application featuring search/filter views, PDF attachment links, Plotly volume/category visualizations, user authentication (`market_users.db`), and an optional LLM digest using the Anthropic API.

```
[BSE / NSE APIs & HTML]
         │
         ▼
[market_announcements.py]
         │
         ├──▶ bse_equity.db ──▶ [announcement_ideas_pipeline.py] ──▶ (Scores in bse_equity.db)
         ├──▶ bse_sme.db
         ├──▶ nse_equity.db
         └──▶ nse_sme.db
                   │
                   ▼
       [bse_market_suite.py (Streamlit Dashboard)]
```

---

## 2. Capability Audit & Evidence Matrix

| Capability Area | Status | Evidence File(s) & Lines | Detailed Analysis |
|---|---|---|---|
| **NSE Collection Logic** | **VERIFIED** | `market_announcements.py:1441-1525` | Queries `https://www.nseindia.com/api/corporate-announcements`. Uses `curl_cffi.requests.Session(impersonate="chrome124")` to emulate browser TLS handshake and cookies. Supports pagination and monthly chunking. |
| **BSE Collection Logic** | **VERIFIED** | `market_announcements.py:270-360, 480-550` | Fetches corporate announcements using BSE API endpoints. Extracts headline, category, subcategory, scrip code, timestamp, and attachment links. |
| **BSE SME Coverage** | **VERIFIED** | `market_announcements.py:840-980` | Scrapes `bsesme.com` HTML tables with `BeautifulSoup4`. Extracts announcements and corporate actions (ex-date, record date, purpose). |
| **NSE SME Coverage** | **VERIFIED** | `market_announcements.py:1482-1506` | Fetches NSE SME announcements by passing `index="sme"` parameter to the NSE corporate filings endpoint. |
| **Date-Range Chunking** | **VERIFIED** | `market_announcements.py:1482-1506` | Implements `needs_chunking()` and `month_chunks()` to automatically partition multi-month date ranges into 30-day blocks, refreshing session cookies every 3 blocks. |
| **Scheduling Logic** | **PARTIALLY VERIFIED** | `market_announcements.py:1770-1825` | CLI `schedule` command uses the `schedule` library to trigger hourly or daily fetches inside a `while True` loop. Lacks persistence of execution state, restart recovery, or distributed locking. |
| **Database Schemas** | **PARTIALLY VERIFIED** | `market_announcements.py:340-395, 760-806, 1351-1366` | 4 separate SQLite databases with divergent column names (`subject` vs `purpose`, `ann_date` vs `input_timestamp`). No unified foreign keys or shared schema. Data can be migrated without loss to a unified schema. |
| **Event Classification** | **VERIFIED** | `idea_rules.py:27-325`<br>`announcement_ideas_pipeline.py:69-96, 200-290` | Evaluates 27 idea categories with keyword weights, category hints, and negative disqualifiers. High quality financial taxonomy. |
| **Investment Idea Scoring** | **VERIFIED (Rule-based)** | `announcement_ideas_pipeline.py:240-280` | Normalizes keyword weights into a 0–100 integer score. **Important distinction:** This is a deterministic rule-based keyword match score, not an evaluated predictive investment alpha signal. |
| **Company & Symbol Mapping** | **PARTIALLY VERIFIED** | `market_announcements.py:1388-1402` | Captures raw symbol, company name, and scrip code provided by exchanges. Lacks cross-exchange canonical mapping (e.g. mapping BSE `500209` to NSE `INFY`). |
| **Historical Queries** | **VERIFIED** | `market_announcements.py:1408-1430` | Supports date-range and ticker filtering with SQL index acceleration (`idx_symbol`, `idx_ann_date`). |
| **CSV Export** | **VERIFIED** | `market_announcements.py:1700-1765` | CLI `export` command dumps announcements from any of the 4 databases to formatted CSV files. |
| **Streamlit Dashboard** | **VERIFIED** | `bse_market_suite.py:1-2189` | Full-featured multi-page UI: Announcements browser, Plotly charts, Keyword insights, and User authentication (`market_users.db`). |
| **Duplicate Prevention** | **PARTIALLY VERIFIED** | `market_announcements.py:1387-1405` | Prevents intra-source duplicates via `UNIQUE` constraints (`ann_id` in NSE, `script_id + timestamp` in BSE). **Cross-source deduplication is MISSING** (identical disclosures filed on both BSE and NSE are stored as unrelated rows in different DBs). |
| **Retry & Recovery** | **VERIFIED** | `market_announcements.py:86-87, 850-870` | Implements retry loops (`MAX_RETRIES=3`, `RETRY_DELAY_SECONDS=10`) with backoff sleep on network errors. |
| **Error & Audit Logging** | **VERIFIED** | `market_announcements.py:797-806, 1515-1525` | Writes logs to `market_ann.log`. Records audit metadata in `fetch_log` table (rows found, rows new, error message, duration). |
| **Automated Tests** | **MISSING** | Entire repository | Zero automated unit or integration tests exist. Includes only synthetic demo data generation (`--demo` flag). |

---

## 3. Deep Dive: Schema Differences & Migration Feasibility

The 4 SQLite databases store disclosures with heterogeneous structures:

```
BSE Equity (announcements)       BSE SME (announcements)         NSE (announcements)
──────────────────────────       ───────────────────────         ───────────────────
id (INTEGER PK)                  id (INTEGER PK)                 id (INTEGER PK)
script_id (TEXT)                 scrip_code (TEXT)               ann_id (TEXT UNIQUE)
scrip_code (TEXT)                scrip_name (TEXT)               symbol (TEXT)
symbol (TEXT)                    grp (TEXT)                      company_name (TEXT)
company_name (TEXT)              category (TEXT)                 subject (TEXT)
category_id (FK)                 announce_date (TEXT)            description (TEXT)
subcategory_id (FK)              end_date (TEXT)                 ann_date (TEXT)
subject (TEXT)                   purpose (TEXT)                  attachment_url (TEXT)
file_name (TEXT)                 attachment_url (TEXT)           fetched_at (TEXT)
input_timestamp (TEXT)           ann_time (TEXT)                 raw_json (TEXT)
attachment_url (TEXT)            full_text_link (TEXT)
fetched_at (TEXT)                summary (TEXT)
raw_json (TEXT)
```

### Can this data be migrated without loss?
**Yes.** All attributes map cleanly into Borsel Handler's canonical schema:
- `title / headline` ⟵ `subject` (BSE/NSE) or `purpose` (BSE SME)
- `company_name` ⟵ `company_name` (BSE/NSE) or `scrip_name` (BSE SME)
- `symbol` ⟵ `symbol` (NSE/BSE) or scrip code
- `published_at` ⟵ Normalized ISO-8601 UTC timestamp parsed from `ann_date`, `input_timestamp`, or `announce_date + ann_time`
- `source_id` ⟵ `ann_id` (NSE), `script_id` (BSE), or composite SME hash
- `source_type` ⟵ `bse_equity`, `bse_sme`, `nse_equity`, `nse_sme`
- `attachment_url` ⟵ Full qualified PDF URL
- `raw_data` ⟵ Preserved in JSONB column

---

## 4. Evaluation of Classification Rules vs. Predictive Signals

`idea_rules.py` defines 27 announcement categories with positive keywords, weights, negative filters, and category hints.
- **Classification Value:** EXCELLENT. It provides domain-tailored rule sets for detecting acquisitions, capex plans, order wins, management changes, buybacks, and regulatory actions in Indian market disclosures.
- **Investment Signal Caution:** While the repository refers to these as "Idea Board" / "Investment Ideas", in engineering reality they are **rule-based semantic classification scores**. In Borsel Handler, these must be treated as **event classification and metadata extraction**, not validated alpha or investment advice.

---

## 5. Reusability Verdict for Borsel Handler

1. **Adopt & Adapt:**
   - Classification taxonomy and keyword rules (`idea_rules.py`).
   - Scoring algorithm adapted into a deterministic event tagger.
   - NSE and BSE announcement request logic and parsing routines (`market_announcements.py`).
   - Date range chunking logic (`month_chunks()`).
   - Logging audit trail pattern (`fetch_log`).

2. **Replace / Upgrade:**
   - Consolidate 4 SQLite database schemas into a single PostgreSQL / SQLAlchemy schema with unified models.
   - Replace `curl_cffi` dependency with standard `httpx` client where possible, or isolate TLS impersonation behind an adapter to ensure cross-platform compatibility.
   - Replace in-process `schedule` loop with an asynchronous background scheduler.
   - Add centralized cross-source deduplication.
   - Write comprehensive automated tests.
