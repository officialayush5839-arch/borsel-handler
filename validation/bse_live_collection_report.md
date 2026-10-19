# Borsel Handler — BSE Live Collection & Compliant Access Report

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Module:** `borsel_handler/collectors/bse.py`  
**Status:** **COMPLETED; LIVE VALIDATION PENDING (BLOCKED BY UPSTREAM WAF RESTRICTION)**  
**Evaluator:** Application Security Engineer & Financial Data Engineer  

---

## 1. Executive Summary

The Bombay Stock Exchange (BSE) corporate announcements collector has been hardened to enforce ethical, compliant data collection practices. The collector extracts corporate disclosures, scrip codes, company names, publication timestamps, and attachment URLs, with complete offline fixture verification and deduplication. In accordance with strict compliance mandates, the collector does **NOT** employ rotating proxies, stealth headers, or CAPTCHA bypasses to circumvent WAF controls. When upstream WAF protections (HTTP 403) are detected, the collector safely records the access limitation, defers collection, and provides observable health telemetry.

---

## 2. Source Configuration & Access Architecture

- **Authoritative Endpoint:** `https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w`
- **Official Web Portal:** `https://www.bseindia.com/corporates/ann`
- **Attachment Archive Base:** `https://www.bseindia.com/xml-data/corpfiling/AttachLive/`
- **Query Method:** Parameterized REST queries by exchange scrip code (e.g. `strScrip=500209` for Infosys, `500325` for Reliance).

---

## 3. Ethical Compliance & Anti-Evasion Policy

In strict adherence to Section 6 and Section 11 of the project instructions:
1. **Zero Evasion:** Borsel Handler explicitly prohibits the use of rotating residential proxies, headless browser fingerprint spoofing, or unauthorized identity rotation to bypass Akamai WAF controls.
2. **Short-Circuit on Block (No Hammering):** When an initial probe request encounters an HTTP 403 Forbidden or HTTP 429 Too Many Requests response, the collector immediately halts further requests for that collection cycle, rather than repeatedly hammering the server across all 50+ equities.
3. **Transparent Failure Telemetry:** Blocked or rate-limited requests are never silently masked as "successful zero-record runs". The collector sets `self.access_restricted = True`, captures the exact HTTP status code (`last_status_code = 403`), and surfaces error telemetry via `get_health_status()`.

---

## 4. Implementation Details

- **Module:** [`borsel_handler/collectors/bse.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/collectors/bse.py)
- **Extracted Fields:**
  - `title`: Announcement headline (`HEADLINE` or `NewsDesc`).
  - `snippet`: Cleaned announcement description (`NEWSSUB` or attachment text).
  - `published_at`: Parsed from `DissemDT` or `News_dt` into UTC.
  - `original_url`: Direct PDF filing link (`AttachLive/{ATTACHMENTNAME}`) or official announcement page (`ann.html?scrip={scrip}`).
  - `canonical_url`: Normalized canonical URL.
  - `source_record_id`: Unique disclosure ID (`NEWSID`).
  - `symbol` & `company_name`: Scrip code to NSE ticker mapping (`BSE_SCRIP_TO_NSE`) and official name.
  - `category`: Categorized via `classify_event(...)`.
  - `raw_metadata`: Complete raw announcement dictionary preserved.
- **Probe Architecture:**
  The `fetch()` method executes a single probe request on the first symbol. If HTTP 403 or 429 is encountered, the run is aborted immediately without further requests. If HTTP 200 is returned, remaining symbols are queried politely with a 0.5-second inter-request delay.

---

## 5. Verification Evidence

### 5.1 Automated Deterministic Tests
- **Test File:** [`tests/test_bse_compliant.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/tests/test_bse_compliant.py)
- **Results:** **6 passed, 0 failed** in 1.27s:
  - `test_parse_bse_date`: Verified date parsing and UTC conversion.
  - `test_parse_announcement_table`: Verified JSON parsing, scrip code mapping, attachment URLs, and category classification.
  - `test_bse_attachment_url_fallback`: Verified fallback to official portal URL when attachment filename is missing.
  - `test_bse_short_circuit_on_403_access_restricted`: Verified that on HTTP 403, `access_restricted` is set to `True`, error message is captured, and `httpx.get` is called exactly **once** (no hammering).
  - `test_bse_rate_limit_429_handling`: Verified graceful deferral on HTTP 429.
  - `test_bse_database_persistence_and_deduplication`: Verified SQLite storage and duplicate detection.
- **Regression Suite:** `tests/test_collectors.py::test_bse_collector_with_fixture` passes 100%.

### 5.2 Bounded Live Request Verification
- **Execution Command:**
  ```python
  import asyncio
  from borsel_handler.collectors.bse import BSEAnnouncementCollector
  c = BSEAnnouncementCollector()
  recs = asyncio.run(c.fetch())
  ```
- **Live Output:**
  ```
  [WARNING] BSE collection restricted for ADANIENT: HTTP 403
  [WARNING] BSE live collection deferred: BSE returned HTTP 403 (Access Restricted/Rate Limited). Halting further requests to respect source restrictions.
  ```
  - `recs`: `0`
  - `health_status`:
    ```json
    {
      "source_name": "BSE Corporate Announcements",
      "access_restricted": true,
      "last_status_code": 403,
      "last_error": "BSE returned HTTP 403 (Access Restricted/Rate Limited)",
      "last_attempt_at": "2026-10-19T13:35:30.547961+00:00",
      "last_successful_at": null
    }
    ```

---

## 6. Acceptance Status & External Dependency

- **Acceptance Status:** **COMPLETED; LIVE VALIDATION PENDING (BLOCKED BY UPSTREAM WAF RESTRICTION)**.
- **Required External Prerequisite:** In production environments, authorized automated access to `api.bseindia.com` requires an enterprise IP whitelisting agreement or commercial BSE corporate feeds subscription.
- **Compliance Guarantee:** The codebase remains completely free of unauthorized proxy rotation or evasive circumvention techniques.
