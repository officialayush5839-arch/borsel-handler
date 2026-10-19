# Borsel Handler — AI-Powered Indian Financial Intelligence Platform

Borsel Handler is an institutional-grade financial data engineering and market intelligence platform for the Indian capital markets ecosystem. It integrates financial media news aggregation, stock exchange corporate announcements (BSE & NSE), regulatory updates (RBI & SEBI), and official government economic policies (PIB), backed by a 6-stage deduplication pipeline, dual-dialect SQLAlchemy persistence, Alembic database migrations, and a modern light white/light-blue financial dashboard.

---

## 1. What Borsel Handler Does

1. **Multi-Source Ingestion:** Acquires financial disclosures, news stories, circulars, and policy announcements across 7 distinct channels.
2. **Deterministic Normalization:** Cleanses HTML, decodes Unicode entities, strips UTM tracking parameters, derives canonical URLs, and enforces strict UTC ISO-8601 timestamps.
3. **Institutional Entity Resolution:** Maps mentioned Indian corporations to stock ticker symbols (e.g., `TCS`, `INFY`, `HDFCBANK`, `LT`) and structured sectors using word-boundary matching without subword false positives.
4. **14-Category Event Taxonomy:** Classifies records into earnings, dividends, IPO listings, M&A, corporate actions, RBI circulars, SEBI regulations, PIB government economic policies, and contracts.
5. **6-Stage Deduplication Engine:** Detects and prevents exact duplicates and cross-source syndicated duplicates, preserving duplicate relationships in persistent storage (`article_duplicates`).
6. **Relational Storage & Versioned Migrations:** Stores records in a normalized schema (`sources`, `articles`, `companies`, `categories`, `collection_runs`, `article_duplicates`) managed via Alembic migrations.
7. **REST APIs & Financial Frontend:** Serves indexed queries, article detail modals, source health status, platform statistics, and an on-demand collection trigger via FastAPI and React 18.

---

## 2. Supported Data Sources & Status

| Source Channel | Source Type | Category Covered | Target Endpoint / Feed | Verification Status |
|---|---|---|---|---|
| **Curated RSS Feeds** | `rss` | Category A: Financial News | 14 Indian media feeds (ET, BS, Mint, NDTV, FE, CNBC) | Verified with Fixtures & Live Code |
| **BSE India Announcements** | `bse_announcement` | Category B: Exchange Filings | BSE India Corporate Disclosures API | Verified with Fixtures & Live Code |
| **NSE India Equities** | `nse_announcement` | Category B: Exchange Filings | NSE Equities Corporate Announcements API | Verified with Fixtures & Live Code |
| **NSE India SME** | `nse_announcement` | Category B: SME Filings | NSE SME Corporate Announcements API | Verified with Fixtures & Live Code |
| **Reserve Bank of India** | `rbi_circular` | Category C: RBI Policy & Circulars | Official RBI Press Releases & Circulars RSS | Verified with Fixtures & Live Code |
| **SEBI India** | `sebi_regulation` | Category D: SEBI Regulatory Updates | Official SEBI Circulars & Orders RSS | Verified with Fixtures & Live Code |
| **PIB Economic Policies** | `government_policy` | Category E: Government Policy | PIB Ministry of Finance & Economic Policy Feeds | Verified with Fixtures & Live Code |

---

## 3. System Prerequisites

- **Python:** Python 3.11+ (Python 3.14 compatible).
- **Node.js:** Node.js v20+ / v26+ and npm 10+.
- **Database:** PostgreSQL 14+ (recommended for production) or SQLite 3.35+ (default for local development and tests).
- **Operating System:** Windows, Linux, or macOS.

---

## 4. Installation & Setup

### 4.1 Clone and Environment Setup
```bash
# Navigate to the project root
cd "borsel handler"

# Configure environment variables
copy .env.example .env
```

### 4.2 Python Dependencies
```bash
py -m pip install -r requirements.txt
```

### 4.3 Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## 5. PostgreSQL & Database Migrations

### 5.1 Configuring PostgreSQL (Production)
In `.env`:
```ini
DATABASE_URL=postgresql://borsel_user:secure_password@localhost:5432/borsel_db
```

### 5.2 Running Alembic Migrations
```bash
# Apply all schema migrations to target database
py -m alembic upgrade head

# Inspect current migration version
py -m alembic current
```

---

## 6. How to Start the Application

### 6.1 Start FastAPI Backend Server
```bash
py -m uvicorn borsel_handler.api.app:app --reload --host 0.0.0.0 --port 8000
```
- API Server: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Platform Summary Stats: `http://localhost:8000/api/v1/stats`
- Source Health Status: `http://localhost:8000/api/v1/sources`

### 6.2 Start React 18 Frontend
```bash
cd frontend
npm run dev
```
- Dashboard URL: `http://localhost:5173`
- Light white/light-blue institutional financial theme
- Features Intelligence Feed, Historical Search & Archive, and Source Health & Operations Dashboard.

---

## 7. How to Execute Ingestion Collectors

### 7.1 Manual CLI Execution
```bash
py -c "import asyncio; from borsel_handler.scheduler.runner import CollectionRunner; asyncio.run(CollectionRunner().run_all(cutoff_hours=48))"
```

### 7.2 On-Demand Ingestion Trigger via REST API
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/trigger?lookback_hours=48"
```

---

## 8. How to Run the Automated Test Suite

All tests use deterministic offline fixtures in `tests/fixtures/` without unmocked live external network dependencies.

```bash
# Run complete test suite (58 tests)
py -m pytest -v

# Run collector tests only
py -m pytest tests/test_collectors.py -v

# Run deduplication tests only
py -m pytest tests/test_deduplication.py -v

# Run Alembic migration tests
py -m pytest tests/test_alembic_migrations.py -v

# Run expanded PostgreSQL & security tests
py -m pytest tests/test_expanded_validation.py -v

# Run end-to-end pipeline tests
py -m pytest tests/test_end_to_end_pipeline.py -v
```

---

## 9. Seven Essential Project-Control Documents

The authoritative specification and tracking documents are located in the project root:

1. `prd.md` — Product Requirements Document (REQ-01 to REQ-25).
2. `architecture.md` — Technical Architecture & Component Specifications.
3. `rules.md` — Mandatory Engineering & Project Rules.
4. `phases.md` — Implementation Roadmap across Phases 0 to 11.
5. `memory.md` — Persistent Factual Project Context & Commit Provenance.
6. `goal.md` — Measurable Objectives & Target Thresholds (GOAL-01 to GOAL-12).
7. `task.md` — Granular Executable Task Ledger (TASK-001 to TASK-041).

---

## 10. Known Limitations

1. **Network Sandbox & Rate Limits:** Production execution against live exchange endpoints (`nseindia.com`, `bseindia.com`) requires compliance with source rate limits and header conventions. Test execution is strictly offline and deterministic.
2. **Relational Dialect:** SQLite is used for local offline test execution; PostgreSQL 14+ is the targeted production persistence engine, verified via dialect-agnostic SQLAlchemy abstractions and Alembic migrations.
3. **Scope Exclusions:** Stock price predictions, sentiment trading signals, and portfolio management are strictly excluded from this data collection and engineering module.
