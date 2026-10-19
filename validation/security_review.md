# Borsel Handler — Application Security Review & Hardening Report
**Document ID:** SEC-2026-002  
**Date:** 2026-10-19  
**Platform:** FastAPI, Pydantic V2, SQLAlchemy 2.0.51, PostgreSQL 18.0  
**Auditor:** Application Security Engineer & Systems Architect  

---

## 1. Executive Summary

This report documents the security posture, vulnerability assessment, credential audit, authorization boundaries, and hardening remediations implemented for the Borsel Handler platform.

---

## 2. Credential & Secret Management Audit

| Review Item | Inspection Target | Audit Finding | Hardening Action Taken |
| :--- | :--- | :--- | :--- |
| **Database Credentials in Code** | `borsel_handler/` Python files | Zero hardcoded passwords found in application source code. | Verified: `DATABASE_URL` loaded exclusively via `pydantic-settings` from environment variables. |
| **`postgres:postgres` Analysis** | Previous report & test scripts | The `postgres:postgres` string is a default local development superuser credential on Windows port 5433. | Replaced in example strings; confirmed `.env.example` contains safe generic placeholder `borsel_user:secure_password`. |
| **Root `.gitignore` Exclusions** | Project Root | **VULNERABILITY FOUND:** Root directory lacked `.gitignore`, risking accidental commit of `.env` or SQLite DB files. | **REMEDIATED:** Created root `.gitignore` explicitly excluding `.env`, `*.db`, `frontend/dist/`, `frontend/node_modules/`, `*.pyc`. |
| **API Keys & External Secrets** | `MARKETAUX_API_KEY`, `ANTHROPIC_API_KEY` | Placeholder empty strings `""` defined in `config.py`. | Verified: No live 3rd-party vendor API keys are embedded in source or repository history. |

---

## 3. Network, CORS, & Endpoint Authorization Hardening

### 3.1 CORS Hardening
- **Initial Vulnerability:** `ALLOWED_ORIGINS` was configured as `["*"]` with `allow_credentials=True`. Modern browsers reject credentialed requests with wildcard origins, and wildcard access exposes internal endpoints to cross-origin abuse.
- **Remediation Applied:** 
  1. Updated default `ALLOWED_ORIGINS` in `borsel_handler/config.py` to explicit local development origins: `["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]`.
  2. In `borsel_handler/api/app.py`, conditionally set `allow_credentials = False if "*" in settings.ALLOWED_ORIGINS else True`.

### 3.2 Ingestion Trigger Route Authorization
- **Initial Vulnerability:** `POST /api/v1/ingest/trigger` was unauthenticated, allowing anonymous callers to spawn arbitrary background ingestion workloads.
- **Remediation Applied:**
  1. Updated `trigger_ingestion` in `borsel_handler/api/routes.py` to inspect the `X-API-Key` header.
  2. If `settings.API_SECRET_KEY` is configured in production/staging, requests lacking a valid matching key are immediately rejected with **HTTP 401 Unauthorized**.
  3. Verified via automated test `test_trigger_ingestion_security_and_auth` in `tests/test_api_endpoints.py`.

---

## 4. SQL Injection & Input Validation

- **SQLAlchemy Parameterization:** All database queries in `NewsRepository.search_records()` use parameterized ORM expressions (`filter()`, `ilike()`), ensuring safe variable binding.
- **Empirical Injection Testing:** Tested hostile inputs including `'; DROP TABLE news_records; --`, `' OR 1=1 --`, and `UNION SELECT` in `tests/test_expanded_validation.py::test_sql_injection_resilience`. All attacks were parameterized safely with zero data leakage or schema corruption.
- **Pydantic V2 Request Gating:** Strong schema validation rejects malformed datetimes, invalid query bounds (`page_size` limited to 1–500, `lookback_hours` limited to 1–720), and invalid URLs.

---

## 5. Dependency Vulnerability Audit (`pip-audit`)

A full dependency audit was executed using `pip-audit 2.10.1` against the active Python runtime environment:

- **Borsel Handler Core Dependencies:**
  - `fastapi 0.135.1` — **CLEAN** (0 vulnerabilities)
  - `uvicorn 0.50.2` — **CLEAN** (0 vulnerabilities)
  - `pydantic 2.13.4` — **CLEAN** (0 vulnerabilities)
  - `sqlalchemy 2.0.51` — **CLEAN** (0 vulnerabilities)
  - `alembic 1.15.1` — **CLEAN** (0 vulnerabilities)
  - `httpx 0.28.1` — **CLEAN** (0 vulnerabilities)
  - `feedparser 6.0.14` — **CLEAN** (0 vulnerabilities)
  - `psycopg2-binary 2.9.12` — **CLEAN** (0 vulnerabilities)
- **External Environment Tooling Findings:**
  - Vulnerabilities identified by `pip-audit` (`gitpython`, `mlflow`, `aiohttp`, `twisted`) belong to auxiliary system tools and CLI packages outside Borsel Handler's application runtime.
  - Recommendation for deployment: Isolate Borsel Handler in a clean virtual environment or container containing exclusively the pinned requirements.

---

## 6. Security Hardening Verdict

**Security Status:** **HARDENED & VERIFIED**
The codebase contains zero hardcoded production credentials, enforces authorization on ingestion triggers, restricts CORS origins, prevents credential leakages, and resists SQL injection attacks.
