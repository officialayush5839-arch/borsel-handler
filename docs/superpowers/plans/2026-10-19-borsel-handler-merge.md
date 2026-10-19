# Borsel Handler Dual-Repo Integration & Audit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Import, rigorously audit, merge, test, and document StockPulse and Market Announcements into Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform (Data Collection Module).

**Architecture:** A decoupled, asynchronous data ingestion pipeline featuring a standardized Collector interface, multi-tier deduplication engine (Exact, Canonical, Normalized URL, Title/Date fuzzy matching), unified SQLAlchemy persistence layer supporting PostgreSQL with SQLite fallback, unified financial event taxonomy classifier, and REST API for historical query and filtering.

**Tech Stack:** Python 3.14+, FastAPI, SQLAlchemy, Alembic, Pydantic, HTTPX/Requests, SQLite/PostgreSQL, Pytest.

**Spec:** Borsel Handler Specification and MEGA PROMPT 1 Requirements (Stages A through H).

## Global Constraints
- Preserve upstream repositories unchanged in dedicated directories (`upstream/StockPulse`, `upstream/market_announcements`).
- Never claim execution, testing, or functionality without direct evidence.
- No stock-price forecasting, portfolio recommendations, or speculative trading signals; pure data engineering.
- Deterministic automated tests using mock fixtures and local test databases.
- All 7 integration artifacts must be written to `reports/`.

## Review Focus
1. Upstream network endpoints changing or being rate-limited: Mock all external HTTP requests in tests.
2. Timezone conversion ambiguities between UTC and IST (Asia/Kolkata): Pin datetime normalization to ISO-8601 with explicit timezone handling.
3. False positive deduplication merging distinct financial news items with identical headlines: Require confidence threshold and distinct company/symbol check.
4. SQLite vs PostgreSQL type differences (JSON, UUID, DateTime): Use SQLAlchemy generic types and dialect-agnostic constructs.
5. Incomplete upstream dependencies on Python 3.14: Audit third-party packages for Python 3.14 compatibility and provide fallback shims where needed.

---

### Task 1: Stage A — Import Both Repositories & Build Import Manifest
- Clone `https://github.com/ansh-varshney/StockPulse` and `https://github.com/Navadhrit/market_announcements` into `upstream/`.
- Inspect commits, branches, licenses, directory trees, runtime requirements, entry points, and dependencies.
- Compile and verify `reports/repository_import_manifest.md`.

### Task 2: Stage B — Deep Codebase Audit of StockPulse
- Inspect StockPulse collectors, schemas, APIs, caching, ticker mappings, and test coverage.
- Classify all capabilities (VERIFIED, PARTIALLY VERIFIED, DOCUMENTED ONLY, MISSING, BLOCKED) with file and line evidence.
- Compile and verify `reports/stockpulse_audit.md`.

### Task 3: Stage C — Deep Codebase Audit of Market Announcements
- Inspect Market Announcements collectors (NSE/BSE, Equity/SME), SQLite schemas, classification logic, historical query logic, and tests.
- Classify all capabilities with exact file and line evidence.
- Compile and verify `reports/market_announcements_audit.md`.

### Task 4: Stage D — Requirement Coverage Matrix
- Evaluate requirements R01 to R24 against both codebases.
- Document selected implementation, planned modifications, missing work, and required verification.
- Compile and verify `reports/requirement_coverage_matrix.md`.

### Task 5: Stage E — Integration Architecture & Merge Plan
- Design unified package structure in `borsel_handler/`.
- Define common collector interface (`BaseCollector`), normalized record schema (`NormalizedNewsRecord`), deduplication engine, database schema, and API contracts.
- Compile and verify `reports/merge_plan.md`.

### Task 6: Stage F — Implement Unified Borsel Handler Core
- Implement `borsel_handler/core/models.py` (Pydantic models and metadata).
- Implement `borsel_handler/storage/` (SQLAlchemy models, dialect-agnostic PostgreSQL/SQLite engine, repository layer).
- Implement `borsel_handler/dedup/` (multi-tier deduplication engine).
- Implement `borsel_handler/classification/` (taxonomy and rule-based classifier).
- Implement `borsel_handler/collectors/` (BaseCollector, RSS collector adapted from StockPulse, Exchange Announcement collector adapted from Market Announcements).
- Implement `borsel_handler/api/` (FastAPI routes for search, filtering, health, ingestion trigger).
- Implement `borsel_handler/config.py` and safe `.env.example`.

### Task 7: Stage G — Deterministic Integration & Unit Test Suite
- Write comprehensive Pytest test suite covering collectors, malformed payloads, date/timezone parsing, URL canonicalization, deduplication tiers, database transactions, API endpoints, and error handling.
- Execute test suite and capture output into `reports/test_execution_report.md`.

### Task 8: Stage H — Verification Report & Final Delivery
- Verify component-by-component merge status against requirements.
- Compile `reports/merge_verification_report.md` with full evidence, verdicts, and remaining roadmap.
