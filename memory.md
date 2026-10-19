# Borsel Handler — Persistent Project Context (Memory)

**Document ID:** MEM-2026-BH  
**Version:** 2.0.0  
**Last Updated:** 2026-10-19  
**Status:** Living Document  
**Project:** Borsel Handler — AI-Powered Indian Stock Market Intelligence Platform

---

## 1. Project Purpose & Scope

Borsel Handler is an institutional Indian financial intelligence platform. The primary objective of the current data collection phase is to implement an automated, resilient, multi-source ingestion engine that collects financial news, exchange announcements, corporate filings, and regulatory circulars, normalizes and classifies the data, removes duplicates, and stores records in a relational database with complete provenance.

---

## 2. Upstream Repository Provenance & Commit Identifiers

| Repository Name | Source URL | Local Working Path | Commit Hash | Branch | Import Date | License |
|---|---|---|---|---|---|---|
| **StockPulse** | `https://github.com/ansh-varshney/StockPulse` | `upstream/StockPulse/` | `e68271802c950885c68706b0d5bfe57a05e8ceed` | `main` | 2026-10-19 | None (All Rights Reserved) |
| **Market Announcements** | `https://github.com/Navadhrit/market_announcements` | `upstream/market_announcements/` | `270014b24cfae53e546f9fc48ff307ab976a09fd` | `main` | 2026-10-19 | MIT License (Copyright 2026 Navadhrit) |

---

## 3. Verified Architectural & Technical Decisions

1. **Service Architecture:** Selected StockPulse's asynchronous FastAPI architecture as the application skeleton, refactored into the structured package `borsel_handler/`.
2. **Persistence Strategy:** Rejected ephemeral in-memory `TTLCache` (StockPulse) and fragmented single-file SQLite databases (Market Announcements). Designed a unified third-normal-form relational schema managed by Alembic migrations, compatible with both PostgreSQL and SQLite.
3. **Pluggable Ingestion:** Established `BaseCollector` interface requiring `source_name`, `source_type`, and `fetch(cutoff) -> List[NormalizedNewsRecord]`.
4. **Multi-Stage Deduplication:** Implemented a 6-stage engine to catch duplicates across source record IDs, canonical URLs, normalized URLs, title strings, 24-hour title windows, and Jaccard word-set similarities, logging duplicates to `article_duplicates`.
5. **Entity Resolution:** Implemented `CompanyResolver` with word-boundary regex matching preventing subword false-positives and assigning structured sector classifications.
6. **UI Strategy:** Retained and expanded StockPulse's React 18 + Vite frontend, applying an institutional light white/light-blue visual theme, removing dark neon styling, and adding real-time backend API integration for search, filters, source health, and manual collection triggers.

---

## 4. Implemented Features & Verification Record

- **Test Suite Status:** 105/105 automated unit and integration tests passing cleanly (`py -m pytest` on 2026-10-19, 0 failures, 61 benign upstream deprecation warnings, duration 96.54s across 19 modules).
- **Core Ingestion Connectors:**
  - `RSSCollector`: Ingests from 14 curated Indian business media feeds with domain trust validation and robust HTML text cleaning.
  - `BSEAnnouncementCollector`: Queries BSE India corporate announcements, resolves attachment links, and records non-stealth rate limit telemetry.
  - `NSEAnnouncementCollector`: Ingests Equities and SME corporate announcements from NSE.
  - `PlaywrightCollector`: Optional isolated headless browser collector for JavaScript-rendered corporate portals with deterministic resource cleanup and graceful fallback.
- **Enhanced Official Regulatory & Policy Connectors:**
  - `RBICollector`: Modernized collector for Reserve Bank of India circulars with dual-date parsing and HTML cleaning.
  - `SEBICollector`: Ingests official regulatory circulars, adjudication orders, and notices from SEBI.
  - `PIBCollector`: Modernized collector with economic policy discrimination filtering macroeconomic and financial policy releases.
- **Data Quality, Security & AI Enablement Modules:**
  - `borsel_handler/core/html_utils.py`: Centralized HTML text extraction stripping `<script>`, `<style>`, `<noscript>`, `<svg>`, `<nav>` tags, decoding HTML entities, and preserving block element spacing and Indic scripts.
  - `NewsRepository.to_dataframe()`: Bounded extraction capped at max 5,000 rows to prevent memory exhaustion, with CWE-1236 formula injection protection (prefixing `'` on `=, +, -, @` triggers).
  - Multi-Format Export APIs (`GET /api/v1/export`, `GET /api/export`): Serves sanitized CSV (`utf-8-sig`) and columnar Apache Parquet (`application/vnd.apache.parquet`) via PyArrow.
  - Listed Company Reference Sync: Expanded master reference directory to 2,619 active Indian equities.
- **Relational Schema Entities:** `sources`, `articles` (`news_records`), `source_records`, `companies`, `article_companies`, `categories`, `article_categories`, `collection_runs` (`collection_logs`), `article_duplicates`.
- **Alembic Migrations:** Configured `alembic.ini`, `alembic/env.py`, baseline migration `001_initial_relational_schema.py` (`001_initial_schema`), and `002_add_provenance_and_audit_fields.py` (`002_audit_fields (head)`).
- **Frontend Build Status:** Vite production build passes in 246ms (`dist/` generated with institutional light white/light-blue theme, historical search, live metrics, and CSV/Parquet export triggers).

---

## 5. Known Limitations & Technical Constraints

1. **Network Sandbox & Test Isolation:** Live external connections to Indian financial and government portals (`bseindia.com`, `nseindia.com`, `rbi.org.in`, `sebi.gov.in`, `pib.gov.in`) are subject to dynamic anti-scraping challenges (TLS fingerprinting, cookie generation) and feed endpoint URL changes. While live RSS, NSE, and SEBI feeds yielded 845 records live, all continuous automated CI/CD testing is executed against deterministic offline fixtures.
2. **PostgreSQL Runtime Availability:** Verified on local PostgreSQL 18.0 (port 5433) and SQLite 3. Production deployments can toggle seamlessly between dialects via `DATABASE_URL`.
3. **Scope Exclusions:** Stock price predictions, sentiment trading signals, and portfolio management are strictly excluded from this data collection and engineering module.
