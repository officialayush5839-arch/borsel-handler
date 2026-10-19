# Borsel Handler — API Surface and Architecture Audit Report
**Document ID:** API-2026-003  
**Date:** 2026-10-19  
**Platform:** FastAPI 0.135.1, Pydantic V2 (2.13.4), Uvicorn 0.50.2  
**Auditor:** Senior Software Architect & API Specialist  

---

## 1. Executive Summary

This report delivers a rigorous audit of the FastAPI application structure, routing, serialization contracts, input validation, CORS configuration, dependency injection, and error boundaries for the Borsel Handler platform.

The API exposes a dual interface:
1. **Modern RESTful Data Platform API (`/api/v1/*`):** Structured querying, historical search, source status, collection logging, and ingestion triggering.
2. **Backward-Compatible UI Contract (`/api/stocks`, `/api/news`, `/api/auth`):** Direct drop-in compatibility for the React/TypeScript frontend.

---

## 2. API Routes & Endpoint Inventory

| Endpoint | Method | Input Parameters / Body | Response Schema / Type | HTTP Status Codes | Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/health` | `GET` | None | `{"status": str, "database": str, "total_records_indexed": int, "timestamp": str}` | 200, 500 | **VERIFIED** |
| `/api/v1/stats` | `GET` | None | `{"total_records": int, "unique_canonical_urls": int, "duplicates_prevented": int, "total_collection_runs": int, "distinct_sources": int, "last_collection_timestamp": str}` | 200 | **VERIFIED** |
| `/api/v1/sources` | `GET` | None | `List[dict]` (Source operational parameters, health status, last run) | 200 | **VERIFIED** |
| `/api/v1/sources/logs` | `GET` | `limit: int` (1-100, default 20) | `List[dict]` (Chronological collection run audit trail) | 200, 422 | **VERIFIED** |
| `/api/v1/companies` | `GET` | `q: Optional[str]`, `sector: Optional[str]` | `List[dict]` (Curated reference directory of Indian equities) | 200 | **VERIFIED** |
| `/api/v1/records` | `GET` | `symbol`, `sector`, `category`, `source_name`, `source_type`, `from_date`, `to_date`, `page`, `page_size` | `SearchResponse` | 200, 422 | **VERIFIED** |
| `/api/v1/records/search` | `GET` | `q: str` (required), `symbol`, `category`, `page`, `page_size` | `SearchResponse` | 200, 422 | **VERIFIED** |
| `/api/v1/records/{id}` | `GET` | `id: int` (path param) | `NewsRecordResponse` | 200, 404, 422 | **VERIFIED** |
| `/api/v1/records` | `POST` | `record: NormalizedNewsRecord` (JSON body) | `{"status": str, "id": Optional[int], "record_hash": Optional[str], "reason": Optional[str]}` | 200, 422 | **VERIFIED** |
| `/api/v1/ingest/trigger`| `POST` | `lookback_hours: int` (1-720, default 48) | `{"status": "collection_initiated", "lookback_hours": int, "timestamp": str}` | 200, 422 | **VERIFIED** |
| `/api/stocks` | `GET` | None | `List[dict]` (Nifty 50 catalog) | 200 | **VERIFIED** |
| `/api/news` | `GET` | `symbol: str` (required), `timerange: str` (default "48h") | `{"stock": dict, "timerange": str, "categories": {"direct": [], "supply_chain": [], "macro": []}, "total": int}` | 200, 404, 422 | **VERIFIED** |
| `/api/auth` | `POST` | Empty | `{"ok": True}` | 200 | **VERIFIED** |

---

## 3. Data Contracts & Schema Validation

- **Pydantic V2 Compliance:** Uses `pydantic.BaseModel` with `ConfigDict(from_attributes=True)` for seamless SQLAlchemy ORM serialization.
- **Strict Timezone Normalization:** `@field_validator("published_at", "collected_at", mode="before")` intercepts naive string and datetime inputs and coerces them into standard UTC datetime objects.
- **Input Boundaries:**
  - `page >= 1`
  - `1 <= page_size <= 500`
  - `1 <= lookback_hours <= 720`
  - URL format validation handled by `url_utils`
  - Ticker case-insensitivity supported across query endpoints

---

## 4. Security, Middleware, and CORS

- **CORS Configuration:** `CORSMiddleware` mounted with configurable `ALLOWED_ORIGINS` loaded from `Settings`.
- **Database Connection Safety:** Scoped database sessions managed through FastAPI dependency injection (`get_db_session()`), ensuring automatic session termination and connection pooling cleanup on every request.
- **Sanitized Error Payloads:** Database errors produce structured JSON HTTP 500/404 messages without leaking raw database stack traces or credentials to clients.

---

## 5. Architectural Findings & Verdict

The backend API cleanly isolates transport concerns from business and storage logic. No direct database access or scraping operations occur in route handlers; all data interactions route through `NewsRepository` or `CollectionRunner`.

**Phase 3 Status:** **VERIFIED**
Proceed to Phase 4 Database and Migration Audit.
