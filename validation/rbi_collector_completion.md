# Borsel Handler — RBI Collector Modernization Report

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Module:** `borsel_handler/collectors/rbi.py`  
**Status:** **COMPLETED AND LIVE-TESTED**  
**Evaluator:** Senior Backend & Financial Data Engineer  

---

## 1. Executive Summary

The Reserve Bank of India (RBI) updates collector has been successfully modernized from broken legacy RSS endpoints to the official, live RBI web publication archives. The collector extracts monetary policy announcements, auction results, and regulatory circulars, normalizes them into `NormalizedNewsRecord`, performs entity resolution for regulated banks, and stores them via the centralized deduplication pipeline.

---

## 2. Baseline Problem & Verified Failure

- **Previous Implementation:** Targeted legacy XML feeds (`https://www.rbi.org.in/rss/rss_pressrelease.xml` and `https://www.rbi.org.in/rss/rss_circular.xml`).
- **Verified Failure:** On the live web, the RBI portal retired these legacy RSS endpoints, returning HTTP 404. Consequently, no live records could be fetched through the RSS collector.

---

## 3. Verified Official Source & Page Structure

Investigation of the live Reserve Bank of India website identified the active, authoritative endpoints:
1. **Press Releases Archive:** `https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx`
2. **Regulatory Notifications / Circulars:** `https://www.rbi.org.in/Scripts/NotificationUser.aspx`

### HTML Structure Analysis
The official pages render a structured HTML table:
- **Date Header Row:** `<td class="tableheader" colspan="4"><b>Oct 19, 2026</b></td>`
- **Announcement Link:** `<a class="link2" href="BS_PressReleaseDisplay.aspx?prid=63832">...</a>`
- **PDF Attachment Link:** `<a href="https://rbidocs.rbi.org.in/rdocs/PressRelease/PDFs/PR...PDF">...</a>`
- **Unique Primary Key:** Extracted from query string (`prid=63832` $\to$ `RBI_PR_63832`).

---

## 4. Implementation Details

- **Module:** [`borsel_handler/collectors/rbi.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/collectors/rbi.py)
- **Parser Engine:** `BeautifulSoup4` with `html.parser` for tag cleaning, entity decoding, and table traversal.
- **Normalization & Mapping:**
  - `title`: Extracted from announcement link text.
  - `published_at`: Parsed from table date headers (`parse_rbi_date`), converted to timezone-aware UTC.
  - `original_url`: Synthesized absolute RBI URL (`https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx?prid=...`).
  - `canonical_url`: Normalized via `normalize_url`.
  - `source_record_id`: `RBI_PR_{prid}` or `RBI_NOTIF_{id}`.
  - `source_name`: `"Reserve Bank of India"`.
  - `source_type`: `"rbi_circular"`.
  - `category`: Categorized via `classify_event(...)`, defaulting to `"rbi_update"`.
  - `company_name` & `symbol`: Resolved via `CompanyResolver.resolve_primary(...)` for referenced banks (e.g. RBL Bank, SBI).
  - `sector`: Automatically tagged as `"Banking & Financial Services"`.
  - `raw_metadata`: Stores `pdf_url`, `page_url`, and raw query parameters.
- **Resilience:** Polite HTTP headers, 20-second timeouts, exponential backoff retries, and safe handling of HTTP 404/429/5xx status codes.
- **Backward Compatibility:** Preserves `parse_rss_feed` to support fixture-based testing and XML fallback.

---

## 5. Verification Evidence

### 5.1 Automated Deterministic Tests
- **Test File:** [`tests/test_rbi_modern.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/tests/test_rbi_modern.py)
- **Fixture:** `tests/fixtures/rbi_press_releases.html`
- **Results:** **6 passed, 0 failed** in 6.03s:
  - `test_parse_rbi_date`: Date parsing and UTC conversion verified.
  - `test_parse_html_archive_from_fixture`: 5 records parsed with accurate fields, links, and source IDs.
  - `test_date_cutoff_filtering`: Historical date filtering verified.
  - `test_empty_and_malformed_html`: Malformed HTML handling verified.
  - `test_rbi_fetch_resilience_http_errors`: HTTP 404 and network timeout resilience verified.
  - `test_rbi_database_persistence_and_deduplication`: SQLite storage and duplicate prevention verified.
- **Regression Suite:** `tests/test_collectors.py::test_rbi_collector_with_fixture` passes 100%.

### 5.2 Bounded Live Verification
- **Execution Command:**
  ```python
  import asyncio
  from borsel_handler.collectors.rbi import RBICollector
  c = RBICollector()
  recs = asyncio.run(c.fetch())
  ```
- **Live Output:** **77 live records fetched** directly from `rbi.org.in`:
  - `RBI_PR_63832`: *Auction of Government of India Dated Securities* (Oct 19, 2026)
  - `RBI_PR_63831`: *Directions under Section 35A read with Section 56 of Banking Regulation Act*
  - `RBI_PR_63830`: *State Government Securities - Full Auction Result*
- **Live Status:** **Fully Operational**.

---

## 6. Operational Limits & Acceptance Status

- **Acceptance Status:** **COMPLETED AND TESTED (LIVE OPERATIONAL)**.
- **Rate-Limiting Guidance:** Configured for polite collection (minimum 2.0s delay between page traversals).
