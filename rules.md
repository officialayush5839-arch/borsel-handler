# Borsel Handler — Engineering & Project Rules

**Document ID:** RULES-2026-BH  
**Version:** 2.0.0  
**Effective Date:** 2026-10-19  
**Status:** Mandatory Enforceable Standard  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## 1. Fundamental Principles

1. **Reality Over Assertion:** Never claim a feature is implemented, tested, or operational without tangible, executable code and reproducible test evidence.
2. **Zero Fabricated Data:** Never generate or insert synthetic or hardcoded financial news items or announcements masquerading as real market data.
3. **Preservation of Provenance:** Every ingested item must retain traceable origins: source venue, original URL, canonical URL, publication timestamp, and raw payload.
4. **Clean Decoupling:** Ingestion collectors must remain completely decoupled from persistence mechanisms, API presentation, and UI components.

---

## 2. Code Organization & Architecture

1. **Package Hierarchy:** All backend Python code must reside strictly within `borsel_handler/`:
   - `borsel_handler/core/`: Data contracts, Pydantic schemas, and URL/text utilities.
   - `borsel_handler/collectors/`: Source-specific collectors implementing `BaseCollector`.
   - `borsel_handler/classification/`: Event classification rules and category taxonomies.
   - `borsel_handler/data/`: Reference data (Nifty 50, sector maps, entity resolver).
   - `borsel_handler/dedup/`: Multi-tier deduplication engine and duplicate candidate tracking.
   - `borsel_handler/storage/`: SQLAlchemy ORM models, session providers, and repository queries.
   - `borsel_handler/scheduler/`: Background runner and retry coordination.
   - `borsel_handler/api/`: FastAPI route handlers, dependencies, and middleware.
2. **Frontend Hierarchy:** All frontend code must reside within `frontend/src/` with clear component boundaries (`components/`, `api/`, `types/`).
3. **Database Migrations:** Schema evolution scripts must reside under `alembic/versions/`.

---

## 3. Naming & Style Conventions

1. **Python:** PEP 8 compliance is mandatory.
   - Classes: `PascalCase` (e.g., `NormalizedNewsRecord`, `DeduplicationEngine`, `BSEAnnouncementCollector`).
   - Functions & Methods: `snake_case` (e.g., `insert_record`, `normalize_url`, `check_duplicate`).
   - Constants: `UPPER_SNAKE_CASE` (e.g., `NIFTY_50`, `DEFAULT_TIMEOUT`, `TAXONOMY_CATEGORIES`).
   - Type hints: Mandatory on all public functions, methods, and model fields.
2. **TypeScript / React:**
   - Components & Interfaces: `PascalCase` (e.g., `NewsCard.tsx`, `NewsRecordResponse`).
   - Utility functions & hooks: `camelCase` (e.g., `fetchNews`, `useDebounce`).
3. **SQL & Database:**
   - Table names: Plural `snake_case` (e.g., `articles`, `sources`, `companies`, `collection_runs`, `article_duplicates`).
   - Primary keys: `id` (autoincrementing integer).
   - Foreign keys: `<singular_table>_id` (e.g., `canonical_article_id`, `company_id`).

---

## 4. Source Connector Implementation Rules

1. Every collector must subclass `borsel_handler.collectors.base.BaseCollector` and implement `source_name`, `source_type`, and `fetch(cutoff)`.
2. Collectors must handle network timeouts, HTTP 4xx/5xx status codes, and malformed responses locally without bubbling unhandled exceptions to the scheduler.
3. Every collector must parse upstream dates and guarantee conversion to UTC `datetime` objects.
4. Collectors must never perform direct database inserts or deduplication checks. Collectors strictly emit `List[NormalizedNewsRecord]`.
5. Collectors must supply an informative, compliant `User-Agent` header identifying the application.

---

## 5. Deduplication & Data Quality Rules

1. Deduplication must execute across all 6 standardized stages:
   - Stage 1: Exact `(source_name, source_record_id)` match.
   - Stage 2: Exact `canonical_url` match.
   - Stage 3: Deterministic record hash match (`SHA-256(canonical_url + title)`).
   - Stage 4: Normalized title match (lowercased, stripped punctuation, collapsed whitespace).
   - Stage 5: Normalized title match within a 48-hour publication window.
   - Stage 6: Jaccard word-set similarity ($\ge 0.85$) within a 24-hour publication window.
2. When a duplicate is detected, it must NOT be inserted into `articles`. The duplicate occurrence must be logged to `article_duplicates` preserving duplicate source, duplicate URL, detection stage, and timestamp.
3. Repeated execution of the collection pipeline against the same source data must be completely idempotent.

---

## 6. Database & Persistence Rules

1. **Dual-Dialect Compatibility:** All models and queries must execute without error on both PostgreSQL (production) and SQLite (development/test). Avoid PostgreSQL-only extensions without SQLite conditional fallbacks.
2. **Transaction Safety:** Every database mutation must be wrapped in a transaction. Rollbacks must be explicitly executed on exception before raising.
3. **Schema Evolution:** No table or column may be altered or added without a corresponding Alembic migration script.
4. **Index Hygiene:** Critical query paths (`published_at`, `symbol`, `category`, `source_name`, `record_hash`) must be explicitly indexed.

---

## 7. API Conventions & Error Handling

1. All REST endpoints must follow RESTful URL naming standards under `/api/v1/`.
2. Endpoints returning collections must support pagination (`page`, `page_size`) with capped maximum limits (`page_size <= 500`).
3. Status codes:
   - `200 OK`: Successful retrieval or idempotent operation.
   - `201 Created`: Successful entity creation.
   - `400 Bad Request`: Invalid parameters or malformed input.
   - `404 Not Found`: Resource does not exist.
   - `422 Unprocessable Entity`: Schema validation failure.
   - `500 Internal Server Error`: Server failure with sanitized message (no raw stack traces exposed to client).
4. Interactive OpenAPI documentation (`/docs` and `/redoc`) must be maintained and accurate.

---

## 8. Security & Secret Management

1. **Zero Hardcoded Secrets:** No API keys, passwords, bearer tokens, or database connection strings containing credentials may be committed to source control.
2. **Template Provisioning:** All required configuration keys must be documented with safe placeholder values in `.env.example`.
3. **Input Sanitization:** All incoming user input and raw HTML payloads must be sanitized to prevent XSS and SQL injection.

---

## 9. Testing & Verification Rules

1. Every pull request or milestone must maintain 100% test pass rate with `pytest`.
2. Collector unit tests must execute deterministically using offline fixtures in `tests/fixtures/`. Live network calls are strictly prohibited during normal test suite execution.
3. Regression tests must be written for every resolved bug or edge case.
4. Tests must verify both the happy path and negative/failure paths (e.g., malformed XML, missing dates, database rollbacks, rate limit retries).

---

## 10. Agent & Developer Behavior Standards

1. Inspect the workspace and read existing code before making modifications.
2. Update all seven project-control documents whenever architectural, requirement, or implementation state changes occur.
3. Never weaken or delete existing tests to force a passing status.
4. Present transparent, honest skepticism disclaimers in all task completion reports.

---

## 11. GitHub CI/CD Pipeline Verification & Auto-Remediation

1. **Mandatory Post-Push Pipeline Check:** Whenever code is committed and pushed to GitHub, the developer/agent MUST immediately monitor and verify the remote GitHub Actions pipeline (`gh run list`, `gh run watch`).
2. **Zero Toleration of Broken Pipelines:** Never end a development turn, declare an issue fixed, or mark a task complete while the remote pipeline is in a failing or red state.
3. **Immediate Remediation Cycle:** If the remote pipeline fails or reports errors:
   - Immediately inspect the failure logs (`gh run view <run-id> --log-failed`).
   - Diagnose the root cause and implement the corrective fix.
   - Commit and push the fix (adhering to separate commits per file where requested).
   - Re-verify until the remote pipeline passes 100% green.
