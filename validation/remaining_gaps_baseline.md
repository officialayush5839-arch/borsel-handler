# Borsel Handler — Remaining Gaps Baseline Report

**Audit Date:** 19 October 2026  
**Auditor:** Principal Python Engineer & Verification Specialist  
**Target System:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform (Data Collection Module)  
**Baseline Test Execution:** `py -m pytest` -> **85 passed, 0 failed, 61 warnings in 42.75s**  
**Frontend Production Build:** `npm run build` in `frontend/` -> **PASS (652ms, 0 errors, 0 warnings)**

---

## 1. Executive Summary

Following the completion and verification of the 4 partial implementation items (RBI modern collection, PIB economic policy collector, 2,619 company master directory sync, and compliant BSE collection telemetry), this baseline audit establishes the exact entry state for closing the final remaining implementation gaps.

The platform is stable with 85 active tests across 17 test modules. However, specific architectural and data engineering gaps remain between current collector implementations and the long-term production standard:
1. **HTML Extraction Inconsistencies:** Legacy collectors still employ regex stripping (`re.sub(r"<[^>]+>", "", text)`) or fragmented tag parsing rather than a unified, resilient BeautifulSoup utility.
2. **Data Export Limits & Security:** `NewsRepository.to_dataframe()` provides basic Pandas conversion, but lacks bounded row limits, CSV spreadsheet formula injection protection (CWE-1236), format flexibility (`parquet` vs `csv`), and integrated frontend export triggers.
3. **Optional Headless Browser Rendering:** The platform lacks an isolated, resource-bounded Playwright collector for JavaScript-heavy financial sources that fails gracefully when headless environments are unavailable or prohibited.
4. **Cross-Component Integration Traceability:** End-to-end integration requires formalized validation across all unified modules without conflicting rules or redundant execution paths.

---

## 2. Baseline Status by Work Area

| Area / Workstream | Current State | Defect / Gap Identified | Required Remediation |
| :--- | :--- | :--- | :--- |
| **A. HTML Extraction** | Fragmented across `rss.py`, `nse.py`, `bse.py`, `rbi.py`, `pib.py`; some regex fallbacks | Potential script/style leakage, entity corruption, lack of centralized max-length bounds | Implement `borsel_handler/core/html_utils.py` with `clean_html_to_text()`, entity decoding, script/style removal, block formatting. |
| **B. DataFrame & Data Export** | Basic `to_dataframe()` in `storage.py` and CSV route in `routes.py` | Unbounded exports can cause memory exhaustion; CSV text susceptible to formula injection (`=`, `+`, `-`, `@`); no Parquet support; no UI button | Add row bounding (`limit <= 5000`), formula sanitization (`'` prefix on formula triggers), Parquet export via PyArrow, and frontend export UI. |
| **C. JavaScript Rendering** | Requests/feedparser/httpx only | JS-rendered sources cannot be collected; missing fallback connector | Implement `borsel_handler/collectors/playwright_collector.py` as strictly optional fallback with configuration flag, timeout, and resource bounds. |
| **D. Cross-Component Integration** | 85 passing tests; core pipeline verified | Isolated collector changes need end-to-end verification through ingestion, storage, API, and frontend | Comprehensive end-to-end regression and verification test suite. |
| **E. Traceability Matrix** | Previous matrices covered initial integration and partial items | Final closure items need full requirement-to-code traceability | Generate complete specification traceability matrix. |

---

## 3. Environment & Tooling Verification

- **Python Runtime:** Python 3.14.6 (win32)
- **Pytest:** 9.1.1 (85 items collected, 85 passed)
- **Pandas:** 2.3.3 installed
- **PyArrow:** 24.0.0 installed (Parquet engine ready)
- **Playwright:** Present in Python environment (ready for isolated optional wrapper)
- **Frontend:** Node.js / Vite / React 19 (TypeScript compilation passing)
- **Database:** PostgreSQL compatible schema, SQLite in-memory and file test fixtures verified

---

## 4. Remediation Plan

1. **Task A:** Create `borsel_handler/core/html_utils.py`, update collectors (`rss.py`, `nse.py`, `bse.py`, `rbi.py`, `pib.py`), create `tests/test_html_utils.py`.
2. **Task B:** Enhance `NewsRepository.to_dataframe`, update `export_records_for_ai` in `borsel_handler/api/routes.py` with CSV/Parquet, add formula sanitization, add frontend export trigger in `frontend/src/App.tsx`, create `tests/test_data_export.py`.
3. **Task C:** Implement `borsel_handler/collectors/playwright_collector.py` with graceful degradation, create `tests/test_playwright_collector.py`.
4. **Task D & E:** Run full test suite, verify frontend build, generate all required validation reports.
