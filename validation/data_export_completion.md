# Borsel Handler — Data Export Completion Report

**Date:** 19 October 2026  
**Module:** `borsel_handler/storage/repository.py`, `borsel_handler/api/routes.py`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`  
**Test Suite:** `tests/test_data_export.py` (5 passed in 8.39s)  
**Status:** COMPLETE & VERIFIED

---

## 1. Overview and Problem Statement

VeritasAI's PDF specification explicitly stipulates:
> *"The collected data must be cleaned, organized, and stored in a database so it can later be used by AI models for prediction and analysis."*

Previous implementations only supported basic database retrieval or in-memory array responses. Key gaps resolved by this implementation:
1. **Unbounded Data Extraction Risk:** Calling `to_dataframe()` on large production databases risked exhausting worker memory (OOM).
2. **Formula Injection Vulnerability (CWE-1236):** Direct export of unescaped financial titles and snippets (e.g. `=HYPERLINK()`, `+cmd`, `@SUM()`, `-risk`) into CSV files risked arbitrary formula execution when opened in Microsoft Excel or LibreOffice Calc.
3. **Format Limitations:** Modern machine learning workflows require columnar Apache Parquet files for high performance, typed columns, and memory-mapped IO.
4. **UI Disconnect:** The frontend lacked direct controls allowing researchers and analysts to export their filtered datasets.

---

## 2. Technical Implementation

### A. Bounded `to_dataframe` in `NewsRepository`
Located in [`borsel_handler/storage/repository.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/storage/repository.py):
- **Bounded Row Limit:** Enforces `bounded_limit = min(max(1, limit), max_limit)` where default `limit=500` and `max_limit=5000`.
- **Spreadsheet Formula Protection:** When `sanitize_formulas=True`, string fields starting with formula characters (`=`, `+`, `-`, `@`, `\t`, `\r`) are prefixed with `'` in the generated export.
- **Canonical DB Invariance:** The database itself retains the true, untampered canonical text; sanitization applies only at the serialization boundary.

### B. REST API Endpoints: `GET /api/v1/export` & `GET /api/export`
Located in [`borsel_handler/api/routes.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/api/routes.py):
- **Multi-Format Support:** `format: Literal["csv", "parquet"] = "csv"`.
- **Query Filters:** Full support for `symbol`, `sector`, `category`, `source_name`, `source_type`, `query`, `from_date`, `to_date`.
- **Validation Bounds:** `limit: int = Query(500, ge=1, le=5000)`. Invalid limits return HTTP 422.
- **Parquet Engine:** Uses PyArrow (`df.to_parquet(index=False, engine="pyarrow")`) with `application/vnd.apache.parquet`.
- **CSV Engine:** Uses UTF-8 with BOM (`utf-8-sig`) with `text/csv` for native international character rendering in Excel.
- **Content Disposition:** Sets `attachment; filename="borsel_news_export_<timestamp>.<ext>"` for seamless browser downloads.

### C. Frontend Export Controls
- **API Client:** Added `getExportUrl()` in [`frontend/src/api/client.ts`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/frontend/src/api/client.ts).
- **Institutional UI:** Added **CSV** and **Parquet** export buttons directly inside the **Intelligence Feed** control bar and the **Historical Search** results header in [`frontend/src/App.tsx`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/frontend/src/App.tsx).
- **Active State Preservation:** Exports seamlessly inherit the active stock symbol or search query.

---

## 3. Verification Evidence

### Automated Test Suite (`tests/test_data_export.py`)
- `test_to_dataframe_bounds`: PASS (verifies row count clamping to max 5000).
- `test_to_dataframe_formula_sanitization`: PASS (verifies leading `'` prepending on `=, +, -, @` triggers while preserving canonical DB text).
- `test_api_export_csv`: PASS (verifies `text/csv`, headers, and escaped strings).
- `test_api_export_parquet`: PASS (verifies `application/vnd.apache.parquet` binary stream and successful round-trip read by PyArrow).
- `test_api_export_validation_bounds`: PASS (verifies HTTP 422 rejection of out-of-bound limit requests `limit=6000` or `limit=0`).
- Total: 5 passed in 8.39s.

### Frontend Production Build
- `npm run build`: Built cleanly in 495ms (0 errors, 0 warnings).
