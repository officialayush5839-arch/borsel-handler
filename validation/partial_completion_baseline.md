# Borsel Handler — Partial Implementation Completion Baseline

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Module:** Borsel Handler (Data Collection & Intelligence Platform)  
**Evaluator:** Senior Backend & Data Engineering Lead  

---

## 1. Executive Summary

This baseline document records the state of Borsel Handler immediately prior to beginning the completion of the 4 areas identified as **PARTIALLY DONE** in the VeritasAI PDF Specification Compliance Audit:

1. **Task A:** RBI updates collector modernization.
2. **Task B:** Government economic policy / PIB collector modernization.
3. **Task C:** Expansion and automated synchronization of the listed-company reference directory.
4. **Task D:** Live BSE announcements collection and compliant access handling.

---

## 2. Baseline Test Suite Status

- **Execution Command:** `py -m pytest -v`
- **Result:** **62 passed, 0 failed, 61 warnings** in 21.65s across 13 test files.
- **Frontend Build:** `npm run build` in `frontend/` succeeds cleanly in **249ms** (0 errors, 0 warnings).
- **Database Status:** Dual compatibility (SQLite `borsel_handler.db` and PostgreSQL 18.0 `borsel_disposable_test`), Alembic revision `002_audit_fields (head)`.

---

## 3. Current Implementation Status of the 4 Target Areas

### Task A: RBI Updates Collector (`borsel_handler/collectors/rbi.py`)
- **Current State:** Implemented for XML RSS parsing (`/rss/rss_pressrelease.xml`, `/rss/rss_circular.xml`). Categorizes events into `rbi_update`. Tests pass against static RSS fixture (`tests/test_collectors.py::test_rbi_collector_with_fixture`).
- **Deficiency:** The configured legacy RSS endpoints return HTTP 404 on the live web because the Reserve Bank of India portal retired them.
- **Required Work:**
  - Modernize the collector to extract from official RBI publication archive pages (`https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx` and Notification/Circular archives).
  - Use BeautifulSoup for HTML table parsing with robust date normalization, summary extraction, and entity resolution for regulated banks.
  - Support bounded historical traversal and pagination.
  - Implement resilience (timeouts, retries with backoff, safe HTTP 404/429/5xx handling).
  - Provide deterministic HTML fixtures and test suite.

### Task B: PIB / Government Economic Policy Collector (`borsel_handler/collectors/pib.py`)
- **Current State:** Implemented for RSS parsing of Ministry of Finance releases into `government_policy`. Tests pass against static fixture (`tests/test_collectors.py::test_pib_collector_with_fixture`).
- **Deficiency:** Legacy RSS URL has intermittent 404/redirect failures on the live network.
- **Required Work:**
  - Modernize to extract from the official Press Information Bureau releases portal (`https://pib.gov.in/AllRelease.aspx` / Ministry of Finance / Cabinet Economic decisions).
  - Maintain strict discrimination so only economic/financial policy announcements are classified into `government_policy`, leaving unrelated announcements appropriately filtered.
  - Extract headline, date, ministry, description, and canonical URL.
  - Implement bounded historical/date-based navigation.
  - Provide deterministic HTML fixtures and comprehensive unit tests.

### Task C: Listed-Company Directory Expansion & Sync (`borsel_handler/data/stocks.py`, `resolver.py`)
- **Current State:** Hardcoded static directory of 50 companies (NIFTY 50) in `stocks.py`. `CompanyResolver` uses word-boundary regex with suppression of ambiguous tokens (`IT`, `ON`, `LT`, etc.). Relational `Company` and `ArticleCompany` models exist in database.
- **Deficiency:** Covers only 50 large-cap stocks; does not cover the wider universe of listed Indian equities (~2,200 NSE listed companies).
- **Required Work:**
  - Implement official master data ingestion from NSE's official equity master (`https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv`).
  - Implement robust CSV parsing: BOM handling, whitespace cleaning, column-order independence, validation of symbol, name, ISIN, series, listing date.
  - Implement safe, idempotent synchronization service (`CompanyDirectorySync`): transactional staging/upsert, preserving existing valid directory if download fails, preventing duplicate symbols.
  - Update `CompanyResolver` to leverage the expanded universe while preserving protections against short ambiguous tokens.
  - Provide deterministic CSV fixtures and unit tests for corrupted downloads, encoding edge cases, and repeat synchronization.

### Task D: Live BSE Announcements Collection (`borsel_handler/collectors/bse.py`)
- **Current State:** Scrip-code based query to `api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`. Tested via fixtures.
- **Deficiency:** Live collection encounters WAF / HTTP 403 / 429 restrictions from cloud/datacenter IPs.
- **Required Work:**
  - Audit and modernize BSE collection strategy strictly following ethical, compliant methods (no proxy evasion or stealth bypasses).
  - Implement compliant session priming, polite rate-limiting, and graceful handling of 403/429 responses with accurate source health reporting.
  - Verify record extraction: scrip code, company name, headline, date, announcement URL, attachment links, category.
  - Execute bounded live validation if authorized access succeeds; otherwise, clearly document the exact environmental access limitation without misrepresentation.
  - Provide deterministic fixtures and tests covering 403, 429, 5xx, and malformed responses.

---

## 4. Relevant File Map

| Subsystem | Existing Files | Planned Files / Modifications |
|---|---|---|
| **RBI Collector** | `borsel_handler/collectors/rbi.py`<br>`tests/test_collectors.py` | Modernized HTML parser in `rbi.py`<br>Fixture `tests/fixtures/rbi_archive.html`<br>Tests `tests/test_rbi_modern.py` |
| **PIB Collector** | `borsel_handler/collectors/pib.py`<br>`tests/test_collectors.py` | Modernized HTML parser in `pib.py`<br>Fixture `tests/fixtures/pib_archive.html`<br>Tests `tests/test_pib_modern.py` |
| **Stock Directory & Sync** | `borsel_handler/data/stocks.py`<br>`borsel_handler/data/resolver.py`<br>`borsel_handler/storage/models.py` | `borsel_handler/data/sync.py`<br>Fixture `tests/fixtures/equity_l_sample.csv`<br>Tests `tests/test_company_sync.py` |
| **BSE Collector** | `borsel_handler/collectors/bse.py`<br>`tests/test_collectors.py` | Hardened compliant collector in `bse.py`<br>Tests `tests/test_bse_compliant.py` |
| **Reporting** | `validation/` | 7 required reports under `validation/` |

---

## 5. Verification Gate & Safety Rules
- Zero regressions: Baseline 62 tests must continue passing.
- No credential or secret hardcoding.
- No anti-WAF bypasses or rotating proxies.
- Deterministic offline tests must not depend on live network availability.
