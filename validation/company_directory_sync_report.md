# Borsel Handler — Listed-Company Reference Directory Synchronization Report

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Module:** `borsel_handler/data/sync.py`  
**Status:** **COMPLETED AND LIVE-TESTED**  
**Evaluator:** Senior Database Architect & Financial Data Engineer  

---

## 1. Executive Summary

The listed-company reference directory has been expanded from a hardcoded 50-stock list (NIFTY 50) to the comprehensive universe of Indian listed equities by ingesting the official National Stock Exchange of India (NSE) equity master file (`EQUITY_L.csv`). A transactional, idempotent synchronization service ([`CompanyDirectorySync`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/data/sync.py)) now synchronizes **2,619 listed companies** into persistent storage, powering the entity resolution engine while strictly preserving disambiguation safeguards.

---

## 2. Baseline Condition & Deficiency

- **Previous Implementation:** Static dictionary of 50 Nifty equities in `borsel_handler/data/stocks.py`.
- **Deficiency:** Failed to resolve announcements and news concerning thousands of mid-cap, small-cap, and newly listed equities across Indian capital markets.

---

## 3. Official Master-Data Source

- **Authoritative Source:** National Stock Exchange of India (NSE) Official Archives
- **Download Endpoint:** `https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv`
- **File Schema:**
  - `SYMBOL`: Unique exchange ticker symbol (e.g. `20MICRONS`, `INFY`, `RELIANCE`).
  - `NAME OF COMPANY`: Full corporate entity name (e.g. `20 Microns Limited`).
  - `SERIES`: Trading series category (`EQ`, `BE`, `SM`).
  - `DATE OF LISTING`: Official date of exchange admission (`DD-MMM-YYYY`).
  - `ISIN NUMBER`: International Securities Identification Number (`INE...`).
  - `PAID UP VALUE` & `FACE VALUE`: Par value of shares.

---

## 4. Implementation Details

- **Module:** [`borsel_handler/data/sync.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/data/sync.py)
- **Robust CSV Parsing:**
  - Handles byte-order marks (`\ufeff` UTF-8 BOM) and trailing whitespace.
  - Case-insensitive, whitespace-stripped column mapping (`clean_field_map`).
  - Rejects empty symbols, missing company names, and malformed records.
  - Validates 12-character ISIN identifiers.
- **Transactional Database Upsert:**
  - Reuses existing [`Company`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/storage/models.py#L46-L61) SQLAlchemy ORM model without requiring schema migrations.
  - Queries existing records by unique `symbol`.
  - Updates changed names, ISINs, or activation flags.
  - Inserts new companies safely.
  - Wraps all operations in an atomic database transaction (`db.commit()`), executing full rollback (`db.rollback()`) on any error to prevent partial corruption.
- **Entity Resolver Integration:**
  - Enhanced [`CompanyResolver`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/data/resolver.py) with dynamic registry support (`CompanyResolver.load_from_db(db)`).
  - Resolves corporate entities across the expanded 2,600+ company universe.
  - Strictly preserves `AMBIGUOUS_SYMBOLS` suppression (`IT`, `ON`, `BE`, `AT`, `OR`, `IN`, `LT`, `TITAN`, `TRENT`) to prevent false-positive ticker matches in free-form prose.

---

## 5. Verification Evidence

### 5.1 Automated Deterministic Tests
- **Test File:** [`tests/test_company_sync.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/tests/test_company_sync.py)
- **Fixture:** `tests/fixtures/equity_l_sample.csv`
- **Results:** **7 passed, 0 failed** in 0.98s:
  - `test_parse_csv_content_from_fixture`: 10 valid records parsed cleanly.
  - `test_parse_csv_bom_and_whitespace`: Handled `\ufeff` BOM and whitespace.
  - `test_parse_csv_missing_required_columns`: Safely rejected CSV missing `SYMBOL`.
  - `test_sync_to_database_idempotency_and_updates`: Verified idempotent repeated synchronization (10 imported $\to$ 0 new, 0 duplicates) and field update.
  - `test_resolver_integration_with_synced_directory`: Verified newly synced stock `20MICRONS` resolved from prose.
  - `test_ambiguous_symbol_safeguard_remains_active`: Confirmed ambiguous tokens (`it`, `on`) remain suppressed.
  - `test_live_sync_error_handling`: Verified graceful failure reporting and existing data preservation on network/HTTP 500 error.

### 5.2 Bounded Live Verification
- **Execution Command:**
  ```python
  import asyncio
  from borsel_handler.data.sync import CompanyDirectorySync
  res = asyncio.run(CompanyDirectorySync.sync_live(db))
  ```
- **Live Output:**
  ```json
  {
    "status": "success",
    "source": "NSE_EQUITY_L_LIVE",
    "total_parsed": 2619,
    "imported_count": 2619,
    "updated_count": 0,
    "rejected_count": 0,
    "total_active_companies": 2619
  }
  ```
- **Live Status:** **Fully Operational**.

---

## 6. Acceptance Status

- **Acceptance Status:** **COMPLETED AND TESTED (LIVE OPERATIONAL)**.
- **Universe Coverage:** Expanded from 50 to 2,619 listed Indian equities with verified ISINs.
