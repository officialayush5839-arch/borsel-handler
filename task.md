# Borsel Handler — Executable Task Tracker (Tasks)

**Document ID:** TASK-2026-BH  
**Version:** 2.0.0  
**Effective Date:** 2026-10-19  
**Status:** Active  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## 1. Task Ledger Overview

This tracker maintains all implementation, verification, database, connector, API, frontend, and testing tasks across the twelve development phases.

Statuses:
- `DONE`: Implementation complete, tests passed, acceptance criteria verified.
- `IN_PROGRESS`: Currently under active development or testing.
- `TODO`: Planned and specified with dependencies identified.
- `BLOCKED`: Work halted due to an external environmental or upstream dependency.
- `DEFERRED`: Intentionally postponed for a subsequent release milestone.

---

## 2. Granular Task List

| Task ID | Phase | Priority | Description | Dependencies | Expected Files | Acceptance Criteria | Status | Evidence |
|---|---|---|---|---|---|---|---|---|
| **TASK-001** | Phase 0 | P0 | Audit StockPulse upstream repository (`upstream/StockPulse`). | None | `reports/stockpulse_audit.md` | Inventory components, commit hashes, license, and entry points. | **DONE** | Commit `e682718` audited in report. |
| **TASK-002** | Phase 0 | P0 | Audit Market Announcements upstream repository (`upstream/market_announcements`). | None | `reports/market_announcements_audit.md` | Inventory components, commit hashes, SQLite tables, and CLI entry points. | **DONE** | Commit `270014b` audited in report. |
| **TASK-003** | Phase 0 | P0 | Verify local Python and test runner runtime environment. | None | Workspace environment | Python 3.11+ detected, pytest operational. | **DONE** | Python 3.14.6 + pytest 9.1.1 verified. |
| **TASK-004** | Phase 1 | P0 | Author `prd.md` specifying institutional requirements (REQ-01 to REQ-25). | TASK-001..003 | `prd.md` | Complete functional and non-functional specifications. | **DONE** | File exists in root with all requirement IDs. |
| **TASK-005** | Phase 1 | P0 | Author `architecture.md`, `rules.md`, `phases.md`. | TASK-004 | `architecture.md`, `rules.md`, `phases.md` | Complete architecture diagrams, engineering rules, and 12-phase roadmap. | **DONE** | Files exist in root. |
| **TASK-006** | Phase 1 | P0 | Author `memory.md`, `goal.md`, `task.md`. | TASK-005 | `memory.md`, `goal.md`, `task.md` | Complete persistent context, measurable goals (GOAL-01..12), and task ledger. | **DONE** | Files exist in root. |
| **TASK-007** | Phase 2 | P0 | Implement normalized relational schema in `borsel_handler/storage/models.py`. | TASK-006 | `borsel_handler/storage/models.py` | Models for `sources`, `articles`, `companies`, `categories`, `collection_runs`, `article_duplicates`. | **DONE** | All 9 entities implemented & tested. |
| **TASK-008** | Phase 2 | P0 | Configure Alembic migration environment (`alembic.ini`, `alembic/env.py`). | TASK-007 | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako` | Alembic correctly detects SQLAlchemy metadata. | **DONE** | Alembic configuration verified. |
| **TASK-009** | Phase 2 | P0 | Generate initial Alembic migration script `001_initial_schema.py` and `002_add_provenance_and_audit_fields.py`. | TASK-008 | `alembic/versions/` | `alembic upgrade head` runs cleanly on clean and upgraded SQLite/PostgreSQL. | **DONE** | `002_audit_fields (head)` verified. |
| **TASK-010** | Phase 3 | P0 | Define `BaseCollector` abstract plugin contract. | TASK-006 | `borsel_handler/collectors/base.py` | Enforces `source_name`, `source_type`, and async `fetch(cutoff)`. | **DONE** | Implemented and verified. |
| **TASK-011** | Phase 3 | P0 | Implement `NormalizedNewsRecord` and API Pydantic schemas. | TASK-010 | `borsel_handler/core/models.py` | Enforces UTC timezone, canonical URL, and metadata dictionary. | **DONE** | Implemented and tested. |
| **TASK-012** | Phase 3 | P1 | Implement URL normalization and tracking parameter stripper. | TASK-010 | `borsel_handler/core/url_utils.py` | Strips `utm_*`, `ref`, standardizes domains and trailing slashes. | **DONE** | Passing tests in `test_url_utils.py`. |
| **TASK-013** | Phase 4 | P0 | Implement `RSSCollector` for 14 Indian business media feeds. | TASK-011 | `borsel_handler/collectors/rss.py` | Parses RSS feeds, sanitizes HTML snippets, enforces UTC publication dates. | **DONE** | Verified in `test_collectors.py`. |
| **TASK-014** | Phase 4 | P1 | Add domain trust validation and sanitization to RSS collector. | TASK-013 | `borsel_handler/collectors/rss.py` | Discards untrusted domains; prevents malicious injections. | **DONE** | Verified in `test_rss_collector_with_fixture`. |
| **TASK-015** | Phase 5 | P0 | Implement `BSEAnnouncementCollector` with attachment link builder. | TASK-011 | `borsel_handler/collectors/bse.py` | Queries BSE API, parses disclosures, resolves PDF attachment URLs. | **DONE** | Verified in `test_bse_collector_with_fixture`. |
| **TASK-016** | Phase 5 | P0 | Implement `NSEAnnouncementCollector` for Equities and SME segments. | TASK-011 | `borsel_handler/collectors/nse.py` | Ingests corporate disclosures with monthly chunking and cookie handling. | **DONE** | Verified in `test_nse_collector_with_fixture`. |
| **TASK-017** | Phase 5 | P1 | Create deterministic mock fixtures for BSE and NSE announcements. | TASK-015..016 | `tests/fixtures/sample_bse.json`, `tests/fixtures/sample_nse.json` | Deterministic offline test fixtures matching real exchange formats. | **DONE** | Fixtures in `tests/fixtures/`. |
| **TASK-018** | Phase 6 | P0 | Implement Reserve Bank of India collector (`RBICollector`). | TASK-010 | `borsel_handler/collectors/rbi.py` | Ingests RBI circulars, press releases, and policy notifications. | **DONE** | Verified in `test_rbi_collector_with_fixture`. |
| **TASK-019** | Phase 6 | P0 | Implement SEBI circulars collector (`SEBICollector`). | TASK-010 | `borsel_handler/collectors/sebi.py` | Ingests SEBI circulars, adjudication orders, and regulatory notices. | **DONE** | Verified in `test_sebi_collector_with_fixture`. |
| **TASK-020** | Phase 6 | P0 | Implement PIB economic policy collector (`PIBCollector`). | TASK-010 | `borsel_handler/collectors/pib.py` | Ingests Ministry of Finance and economic policy press releases from PIB. | **DONE** | Verified in `test_pib_collector_with_fixture`. |
| **TASK-021** | Phase 7 | P0 | Implement institutional company entity resolver (`CompanyResolver`). | TASK-011 | `borsel_handler/data/resolver.py` | Word-boundary regex matching against Indian equities and ticker symbols. | **DONE** | Verified in `tests/test_entity_resolver.py`. |
| **TASK-022** | Phase 7 | P0 | Expand event classification taxonomy to 12+ categories. | TASK-011 | `borsel_handler/classification/classifier.py` | Covers earnings, dividends, M&A, IPOs, RBI, SEBI, Government policy. | **DONE** | Verified in `tests/test_classification.py`. |
| **TASK-023** | Phase 7 | P0 | Implement multi-stage deduplication engine (Stages 1 – 6). | TASK-011 | `borsel_handler/dedup/engine.py` | Checks source ID, canonical URL, hash, normalized title, time window, fuzzy. | **DONE** | Verified in `tests/test_deduplication.py`. |
| **TASK-024** | Phase 7 | P1 | Implement duplicate candidate relationship logging into `article_duplicates`. | TASK-007, 023 | `borsel_handler/storage/repository.py` | Persists duplicate URLs, duplicate sources, and detection stages. | **DONE** | Verified in `test_duplicate_relationship_persistence`. |
| **TASK-025** | Phase 8 | P0 | Implement asynchronous `CollectionRunner` with exponential backoff & jitter. | TASK-013..020 | `borsel_handler/scheduler/runner.py` | Coordinates collectors, catches errors gracefully, prevents overlapping runs. | **DONE** | Verified in `tests/test_scheduler_resilience.py`. |
| **TASK-026** | Phase 8 | P1 | Record execution metrics in `collection_runs` table. | TASK-007, 025 | `borsel_handler/storage/repository.py` | Records items found, inserted, duplicates, errors, duration. | **DONE** | Verified in `test_scheduler_resilience.py`. |
| **TASK-027** | Phase 8 | P2 | Add automated retry helper with configurable attempts and backoff. | TASK-025 | `borsel_handler/scheduler/runner.py` | Handles transient HTTP errors (429, 502, timeouts). | **DONE** | Verified in `runner.py`. |
| **TASK-028** | Phase 9 | P0 | Expose article search and filter REST endpoints (`GET /api/v1/records`). | TASK-007 | `borsel_handler/api/routes.py` | Filtering by symbol, sector, category, source, date range. | **DONE** | Verified in `test_api_endpoints.py`. |
| **TASK-029** | Phase 9 | P0 | Expose single article detail endpoint (`GET /api/v1/records/{id}`). | TASK-007 | `borsel_handler/api/routes.py` | Returns complete metadata, provenance, tags, raw metadata. | **DONE** | Verified in `test_get_record_detail`. |
| **TASK-030** | Phase 9 | P1 | Expose source health and summary stats endpoints (`GET /api/v1/sources`, `/api/v1/stats`). | TASK-007, 026 | `borsel_handler/api/routes.py` | Summarizes collection runs, health status, and category counts. | **DONE** | Verified in `test_platform_stats_and_sources_api`. |
| **TASK-031** | Phase 9 | P0 | Enhance React frontend with light white/light-blue theme and live backend integration. | TASK-028..030 | `frontend/src/` | Responsive UI with search, filter, source health, and stats. | **DONE** | `tsc -b && vite build` passed cleanly. |
| **TASK-032** | Phase 10 | P0 | Create deterministic unit tests for RBI, SEBI, and PIB collectors. | TASK-018..020 | `tests/test_collectors.py`, `tests/fixtures/` | Tests offline mock XML/HTML responses for new collectors. | **DONE** | 6 collector tests passing in pytest. |
| **TASK-033** | Phase 10 | P0 | Add Alembic migration test verifying clean schema upgrade. | TASK-009 | `tests/test_alembic_migrations.py` | Validates `alembic upgrade head` and `downgrade base` run cleanly in pytest. | **DONE** | Verified in `test_alembic_migrations.py`. |
| **TASK-034** | Phase 10 | P0 | Implement comprehensive end-to-end pipeline test with duplicate verification. | TASK-007..031 | `tests/test_end_to_end_pipeline.py` | Ingestion -> Dedup -> Relational DB -> API -> Idempotent rerun. | **DONE** | Verified in `test_end_to_end_pipeline.py`. |
| **TASK-035** | Phase 11 | P1 | Update `README.md` with installation, PostgreSQL setup, Alembic, and API instructions. | All phases | `README.md` | Accurate, verified commands and documentation. | **DONE** | Complete README updated. |
| **TASK-036** | Phase 11 | P1 | Update `.env.example` with all configuration options and safe defaults. | Phase 2 | `.env.example` | Safe placeholder configuration template. | **DONE** | Updated `.env.example`. |
| **TASK-037** | Phase 11 | P0 | Compile final verification report and skeptical engineering assessment. | All phases | Final report via `send_message` | Comprehensive delivery summary per Section 23. | **DONE** | Report compiled. |
| **TASK-038** | Phase 10 | P0 | Expand automated test suite for PostgreSQL live testing, SQL injection, and Unicode. | All phases | `tests/test_expanded_validation.py` | Test suite expanded to 58 automated tests with 100% pass rate. | **DONE** | 58/58 tests passing in `test_execution_report.md`. |
| **TASK-039** | Phase 11 | P0 | Resolve P0/P1 defects (PostgreSQL boolean column default, circular import, Alembic URL override). | TASK-038 | `alembic/versions/`, `dedup/engine.py` | All 5 defects remediated without regressions. | **DONE** | Verified in `validation/defect_register.md`. |
| **TASK-040** | Phase 12 | P0 | Compile Requirements Traceability Matrix (RTM) and synchronize 7 root control files. | All tasks | `validation/requirements_traceability_matrix.md` | 100% of 24 requirements trace to code and tests. | **DONE** | Verified in RTM report. |
| **TASK-041** | Phase 14 | P0 | Author Section 34 Final Acceptance Report. | All tasks | `validation/final_acceptance_report.md` | Comprehensive empirical evaluation across all 15 audit phases. | **DONE** | Verified in final acceptance report. |
| **TASK-042** | Phase 15 | P0 | Modernize RBI dual-date extraction, PIB economic policy filter, 2,619 company master sync, and BSE compliant telemetry. | TASK-041 | `borsel_handler/` collectors & sync | Replaced all partial stubs with robust live/offline parsers and reference directory sync. | **DONE** | Verified in `validation/partial_completion_final_report.md` (85 tests passed). |
| **TASK-043** | Phase 16 | P0 | Implement centralized, robust HTML text extraction utility and refactor legacy collectors. | TASK-042 | `borsel_handler/core/html_utils.py` | Decomposes script/style/svg tags, preserves block spacing, decodes entities, bounded word-truncation. | **DONE** | Verified in `tests/test_html_utils.py` (8 passed). |
| **TASK-044** | Phase 16 | P0 | Implement bounded DataFrame export, formula injection mitigation (CWE-1236), CSV & Parquet APIs, and UI triggers. | TASK-042 | `repository.py`, `routes.py`, `frontend/` | Bounded to max 5000 rows, formula trigger escaping (`'`), PyArrow Parquet support, and React UI controls. | **DONE** | Verified in `tests/test_data_export.py` (5 passed) and `npm run build`. |
| **TASK-045** | Phase 16 | P1 | Implement optional, isolated Playwright collector for JavaScript-hydrated financial sources. | TASK-042 | `borsel_handler/collectors/playwright_collector.py` | Strictly optional import, disabled default, deterministic cleanup in finally blocks, no stealth evasion. | **DONE** | Verified in `tests/test_playwright_collector.py` (6 passed). |
| **TASK-046** | Phase 16 | P0 | Cross-component end-to-end integration and pipeline verification across all modules. | TASK-043..045 | `tests/test_end_to_end_pipeline.py` | HTML -> Entity Resolution -> Dedup -> DB -> Bounded Export end-to-end pipeline. | **DONE** | Verified in `test_end_to_end_html_to_export_pipeline`. |
| **TASK-047** | Phase 16 | P0 | Generate full specification traceability matrix, test execution report, and final gap closure reports. | TASK-042..046 | `validation/` reports | 100% specification coverage with 105 passing automated tests. | **DONE** | Verified in `validation/specification_traceability_matrix.md` & `remaining_gaps_final_report.md`. |

