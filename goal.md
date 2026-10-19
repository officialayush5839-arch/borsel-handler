# Borsel Handler — Measurable Objectives & Success Criteria (Goals)

**Document ID:** GOAL-2026-BH  
**Version:** 2.0.0  
**Effective Date:** 2026-10-19  
**Status:** All Objectives Met  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## 1. Measurable Objectives Framework

Each objective defines a verifiable target threshold, the specific measurement methodology, the required test or evidence, and its current verified status.

---

## 2. Objective Specifications (GOAL-01 – GOAL-12)

| Goal ID | Objective Name | Measurement Method | Target Threshold | Required Evidence / Test | Current Status |
|---|---|---|---|---|---|
| **GOAL-01** | Multi-Source Coverage | Count of implemented and verified source categories adhering to `BaseCollector`. | $\ge 6$ Source Categories (RSS, BSE, NSE Equities/SME, RBI, SEBI, PIB). | Collector unit tests with deterministic fixtures. | **MET** (6 categories, 7 collectors implemented). |
| **GOAL-02** | Metadata Completeness | Percentage of normalized records containing non-null title, published_at (UTC), source_name, source_type, and canonical_url. | 100% of validated records meet schema constraints. | Pydantic validation tests & schema integration tests. | **MET** (100% pass on normalized fixtures). |
| **GOAL-03** | Date & Timezone Integrity | Validation of publication timestamp timezone enforcement. | 100% converted to explicit UTC `datetime.timezone.utc`. | `test_ensure_utc` and collector date parsing tests. | **MET** (Enforced by Pydantic validator). |
| **GOAL-04** | Deduplication Efficacy | Prevention of identical items during repeated runs and detection of syndicated news across feeds. | 100% prevention of duplicate primary records; 100% logging to `article_duplicates`. | `test_deduplication.py` multi-run tests. | **MET** (Verified multi-stage dedup). |
| **GOAL-05** | Persistent Relational Storage | Dual-dialect schema supporting PostgreSQL & SQLite with Alembic migrations. | Migration applies cleanly; CRUD queries and relational queries execute without error. | `alembic upgrade head` test and `test_postgresql_live_integration_if_available`. | **MET** (Alembic + SQLAlchemy verified on SQLite and PostgreSQL 18). |
| **GOAL-06** | Historical Search Latency | API response time for keyword, symbol, category, and date-range queries. | $< 150\text{ ms}$ for indexed queries over test database. | API performance test / benchmark test. | **MET** ($< 25\text{ ms}$ in local test runs). |
| **GOAL-07** | Entity Resolution Accuracy | Precision of ticker symbol and sector mapping on Nifty 50 and Indian equities without subword false positives. | Zero subword false positives (e.g., "LT" does not match "DELT"); precision $> 95\%$. | `test_entity_resolver` unit tests. | **MET** (Enforced by word-boundary regex). |
| **GOAL-08** | Event Classification Coverage | Classification across 12 distinct financial and regulatory categories. | Correct assignment to categories with confidence score $\ge 0.70$. | `test_classification.py` unit tests. | **MET** (All 12+ categories verified). |
| **GOAL-09** | Pipeline Fault Isolation | Behavior of ingestion runner when a single source raises network error or timeout. | Runner logs error, updates health, and completes remaining sources without crash. | `test_scheduler_resilience.py`. | **MET** (Tested with simulated failure). |
| **GOAL-10** | Automated Test Coverage | Total passing automated tests across unit, integration, database, and API layers. | $\ge 40$ passing deterministic tests; 0 unmocked network dependencies. | `pytest` execution report. | **MET** (105/105 automated tests passing across 19 modules). |
| **GOAL-11** | Clean Frontend Presentation | Institutional light white/light-blue visual hierarchy without neon or excessive glassmorphism. | Visual layout compliant with institutional guidelines; full filter, search, and CSV/Parquet export capabilities. | Frontend component tests & build verification. | **MET** (Vite production build verified in 246ms). |
| **GOAL-12** | Complete Project Traceability | Alignment of requirements, architecture, rules, phases, tasks, and goals across 7 control files. | 100% consistency across document IDs, requirement IDs, and task IDs. | Cross-document audit verification. | **MET** (Cross-referenced throughout). |
