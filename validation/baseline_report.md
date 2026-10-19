# Borsel Handler — Baseline Environment and Inventory Audit Report
**Date:** 2026-10-19  
**Platform:** Windows 11 (64-bit)  
**Workspace:** `C:\Users\ARYAN - AYUSH\OneDrive\Desktop\borsel handler`  
**Execution Context:** Clean technical audit and baseline verification  

---

## 1. Executive Summary

This report establishes the baseline runtime environment, dependency tree, upstream repository provenance, and inventory of the **Borsel Handler** codebase prior to executing the comprehensive 15-phase audit and stabilization protocol.

The system is configured as an Indian financial-data intelligence and ingestion engine, built on Python 3.14.6, FastAPI, SQLAlchemy 2.0.51, Alembic, SQLite (local verified storage) / PostgreSQL (enterprise ORM target), and a React/TypeScript frontend.

---

## 2. Runtime Environment & Toolchain

| Component | Tool / Runtime | Verified Version | Command Verified | Exit Code / Status |
| :--- | :--- | :--- | :--- | :--- |
| **Python Runtime** | Python (pythoncore-3.14-64) | `3.14.6` | `py --version` | `0` (Passing) |
| **Node.js Runtime** | Node.js Engine | `v26.4.0` | `node --version` | `0` (Passing) |
| **Node Package Mgr**| npm | `11.17.0` | `npm --version` | `0` (Passing) |
| **Test Engine** | Pytest | `9.1.1` | `py -m pytest --version` | `0` (Passing) |
| **Migration Engine**| Alembic | `1.15.1+` | `py -m alembic current` | `0` (Head: `002_audit_fields`) |
| **Frontend Tool** | Vite + TypeScript | Vite `8.0.14`, TS `5.9.3` | `npm run build` | `0` (Passing, 176ms) |

---

## 3. Dependency Inventory & Package Audit

Key Python packages confirmed in the active runtime:

- **FastAPI / Server:** `fastapi 0.135.1`, `uvicorn 0.50.2`, `starlette 1.3.1`
- **Data Modeling & Validation:** `pydantic 2.13.4`, `pydantic-settings 2.14.2`
- **Database & Persistence:** `SQLAlchemy 2.0.51`, `alembic 1.15.1`, `psycopg2-binary 2.9.12`, `sqlite3` (built-in)
- **Ingestion & Parsing:** `feedparser 6.0.14`, `httpx 0.28.1`, `beautifulsoup4 4.14.3`, `requests 2.34.2`
- **Date & String Processing:** `python-dateutil 2.9.0.post0`, `pytz 2026.2`
- **Testing:** `pytest 9.1.1`, `pytest-asyncio 1.4.0`, `pytest-benchmark 5.2.3`, `pytest-mock 3.15.1`

---

## 4. Upstream Repository Provenance & Hashes

Both external upstream repositories were imported into the workspace under `upstream/` and verified:

| Upstream Project | Target Path | Git Commit Hash | Verified Status |
| :--- | :--- | :--- | :--- |
| **StockPulse** | `upstream/StockPulse` | `e68271802c950885c68706b0d5bfe57a05e8ceed` | Cloned & Inspected |
| **Market Announcements** | `upstream/market_announcements` | `270014b24cfae53e546f9fc48ff307ab976a09fd` | Cloned & Inspected |

---

## 5. Directory Structure & File Counts

```
borsel handler/
├── alembic/                         # Alembic database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 001_initial_relational_schema.py
│       └── 002_add_provenance_and_audit_fields.py
├── alembic.ini                      # Alembic configuration
├── borsel_handler/                  # Core unified application package
│   ├── api/                         # FastAPI application, dependencies, routes
│   │   ├── app.py
│   │   ├── dependencies.py
│   │   └── routes.py
│   ├── classification/              # Taxonomy & deterministic rule-based classifier
│   │   ├── classifier.py
│   │   └── taxonomy.py
│   ├── collectors/                  # 7 source connector implementations
│   │   ├── base.py
│   │   ├── bse.py
│   │   ├── nse.py
│   │   ├── pib.py
│   │   ├── rbi.py
│   │   ├── rss.py
│   │   └── sebi.py
│   ├── core/                        # Data models & URL normalization utilities
│   │   ├── models.py
│   │   └── url_utils.py
│   ├── data/                        # Symbol dictionary & company resolver
│   │   ├── dependency_map.py
│   │   ├── resolver.py
│   │   └── stocks.py
│   ├── dedup/                       # 5-tier deduplication engine
│   │   └── engine.py
│   ├── scheduler/                   # Ingestion orchestrator & resilience runner
│   │   └── runner.py
│   ├── storage/                     # SQLAlchemy models, database session, repository
│   │   ├── database.py
│   │   ├── models.py
│   │   └── repository.py
│   └── config.py                    # Pydantic Settings configuration
├── frontend/                        # React + TypeScript frontend
│   ├── src/                         # Application source code
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── reports/                         # Prior audit and merge reports
├── tests/                           # Automated test suite (11 test files, 53 tests)
├── upstream/                        # Upstream cloned repositories
├── validation/                      # Technical validation and audit outputs
├── architecture.md                  # Project Architecture Document
├── goal.md                          # Measurable Objectives & Metrics
├── memory.md                        # Persistent Context & Decisions
├── phases.md                        # 12-Phase Roadmap & Milestones
├── prd.md                           # Product Requirements Document
├── rules.md                         # Architecture & Coding Rules
├── task.md                          # Traceable Task Tracker
├── README.md                        # Setup and operational guide
├── .env.example                     # Environment template
└── borsel_handler.db                # SQLite database (migrated to head)
```

**Total Modules & Test Inventory:**
- Core Python Application Files: 20 source files in `borsel_handler/`
- Test Files: 11 test modules in `tests/`
- Alembic Migration Revisions: 2 migrations (`001`, `002`)
- Frontend Assets: React 19 / Vite 8 / Tailwind CSS client in `frontend/`

---

## 6. Initial Database Baseline

- Database File: `borsel_handler.db`
- Current Alembic Revision: `002_audit_fields (head)`
- Database Tables Detected:
  1. `alembic_version`
  2. `news_records`
  3. `collection_logs`
  4. `sources`
  5. `companies`
  6. `categories`
  7. `article_duplicates`
  8. `source_records`
  9. `article_categories`
  10. `article_companies`
- Verified: Both flat legacy-compatible (`news_records`) and normalized relational entities (`sources`, `companies`, `categories`, `article_duplicates`, `source_records`) are present with foreign keys and unique indexes.

---

## 7. Baseline Verification Verdict

**Phase 1 Status:** **VERIFIED**
All base tools, environments, upstream commits, source trees, and migrations are sound and operational. Proceed to Phase 2 independent verification of completion claims.
