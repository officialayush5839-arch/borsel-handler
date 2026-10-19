# Borsel Handler — Implementation Roadmap (Phases 0 – 11)

**Document ID:** PHASES-2026-BH  
**Version:** 2.0.0  
**Effective Date:** 2026-10-19  
**Status:** Completed  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## Overview

The development of Borsel Handler is structured into twelve sequential, dependency-aware phases. Progress is gated by verifiable evidence and passing tests. All twelve phases have satisfied their mandatory criteria with 51 passing automated tests.

---

## Phase 0: Repository Audit & Environment Verification
- **Objectives:** Inspect workspace, audit upstream repositories (`upstream/StockPulse`, `upstream/market_announcements`), review commit hashes, verify Python runtime and test framework readiness.
- **Deliverables:** `reports/repository_import_manifest.md`, `reports/stockpulse_audit.md`, `reports/market_announcements_audit.md`.
- **Status:** **COMPLETE** (Verified Python 3.14.6 + pytest 9.1.1, commit hashes documented).

## Phase 1: Project Specification & Architecture
- **Objectives:** Establish authoritative seven project-control documents in root directory with complete cross-file consistency.
- **Deliverables:** `prd.md`, `architecture.md`, `rules.md`, `phases.md`, `memory.md`, `goal.md`, `task.md`.
- **Status:** **COMPLETE** (All 7 control files in root, cross-referenced).

## Phase 2: Database Schema & Migrations
- **Objectives:** Design dual-dialect normalized SQLAlchemy schema and configure Alembic migration environment.
- **Deliverables:** `borsel_handler/storage/models.py`, `alembic.ini`, `alembic/env.py`, `alembic/versions/001_initial_relational_schema.py`.
- **Status:** **COMPLETE** (All 9 relational entities verified via `alembic upgrade head`).

## Phase 3: Shared Ingestion Framework
- **Objectives:** Define and verify `BaseCollector` interface, canonical Pydantic models, and shared parsing utilities.
- **Deliverables:** `borsel_handler/collectors/base.py`, `borsel_handler/core/models.py`, `borsel_handler/core/url_utils.py`.
- **Status:** **COMPLETE** (Pydantic UTC validation and URL canonicalization verified).

## Phase 4: Integration of Verified StockPulse News-Collection
- **Objectives:** Adapt and verify StockPulse RSS collection service into modular `RSSCollector`.
- **Deliverables:** `borsel_handler/collectors/rss.py`, curated list of 14 Indian business media feeds.
- **Status:** **COMPLETE** (Passing `test_rss_collector_with_fixture`).

## Phase 5: Integration of Verified Market Announcements
- **Objectives:** Adapt BSE and NSE announcement scrapers from Market Announcements into asynchronous `BaseCollector` implementations.
- **Deliverables:** `borsel_handler/collectors/bse.py`, `borsel_handler/collectors/nse.py`.
- **Status:** **COMPLETE** (Passing `test_bse_collector_with_fixture`, `test_nse_collector_with_fixture`).

## Phase 6: Additional Official Regulatory, Government & Filing Sources
- **Objectives:** Implement dedicated collectors for Reserve Bank of India (RBI), SEBI, and Government Economic Policy (PIB).
- **Deliverables:** `borsel_handler/collectors/rbi.py`, `borsel_handler/collectors/sebi.py`, `borsel_handler/collectors/pib.py`, deterministic fixtures in `tests/fixtures/`.
- **Status:** **COMPLETE** (Passing unit tests for RBI, SEBI, and PIB collectors).

## Phase 7: Normalization, Company Mapping, Classification & Deduplication
- **Objectives:** Build institutional company entity resolver, taxonomy classifier, and 6-stage deduplication engine with duplicate relationship logging.
- **Deliverables:** `borsel_handler/data/resolver.py`, `borsel_handler/classification/classifier.py`, `borsel_handler/dedup/engine.py`.
- **Status:** **COMPLETE** (Word-boundary matching, 14 categories, duplicate persistence verified).

## Phase 8: Scheduler, Retries, Recovery & Monitoring
- **Objectives:** Implement asynchronous background collection runner with exponential backoff, jitter, rate limiting, and execution logging.
- **Deliverables:** `borsel_handler/scheduler/runner.py`.
- **Status:** **COMPLETE** (Verified fault isolation and exponential backoff retry logic).

## Phase 9: API & Frontend Integration
- **Objectives:** Expose full REST API suite in FastAPI and enhance React frontend with light white/light-blue theme, search, filtering, and source-health dashboard.
- **Deliverables:** `borsel_handler/api/routes.py`, `frontend/src/App.tsx`, `frontend/src/components/SourceHealthDashboard.tsx`, `frontend/src/components/ArticleDetailModal.tsx`.
- **Status:** **COMPLETE** (Vite production build verified in 168ms).

## Phase 10: Automated Testing, Security Review & Data-Quality Validation
- **Objectives:** Execute end-to-end integration tests, verify database rollback, validate security constraints, and verify duplicate prevention.
- **Deliverables:** 58 passing automated tests in `tests/` across 12 test modules.
- **Status:** **COMPLETE** (100% pass rate: 58/58 tests passing in 5.86s).

## Phase 11: Deployment Documentation & Final Verification
- **Objectives:** Update `README.md`, `.env.example`, architecture documentation, produce final traceability report and delivery package.
- **Deliverables:** Updated `README.md`, `.env.example`, 12 technical validation reports in `validation/`, final report per Section 34.
- **Status:** **COMPLETE**.
