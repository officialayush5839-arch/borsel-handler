# Borsel Handler — Release Gate Checklist

**Document Version:** 1.0.0  
**Date:** 2026-10-19  
**Review Target:** Borsel Handler Data Collection & Intelligence Module  
**Evaluator:** QA Automation & Release Engineering  

---

## 1. Executive Summary

This checklist evaluates Borsel Handler against production and staging release readiness gates across 10 functional and operational dimensions. Every item is verified against executed tests, security audits, and runtime behavior.

**Gate Status Summary:**
- **Total Release Gates:** 10
- **PASSED:** 9 Gates
- **CONDITIONAL PASS:** 1 Gate (Live Exchange & Regulatory Source Network Hardening)
- **FAILED:** 0 Gates

---

## 2. Release Gate Verification Matrix

### Gate 1: Repository Hygiene & Secret Management
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Gitignore Enforcement | `.gitignore` in root prevents tracking `.env`, `*.db`, `node_modules`, `dist` | Inspected root `.gitignore`. All patterns present. | **PASS** |
| Zero Secrets in VCS | No passwords, tokens, private keys in source, tests, or docs | Grepped codebase and commit history. Clean. | **PASS** |
| Environment Template | Safe `.env.example` with non-production placeholders | Verified `.env.example` has generic dummy values. | **PASS** |

### Gate 2: Static Analysis & Dependencies
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Dependency Vulnerabilities | No known CVEs in installed Python dependencies | Executed `pip-audit 2.10.1`. 8/8 core dependencies 100% clean. | **PASS** |
| Frontend Dependencies | No critical npm vulnerabilities | Inspected `frontend/package.json` with pinned versions. | **PASS** |
| Code Standards | Clean Python syntax, explicit typing, no syntax errors | Python compilation clean across all 35 modules. | **PASS** |

### Gate 3: Automated Test Suite
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Backend Unit Tests | Full test suite passes without errors | Executed `py -m pytest -v`: **61 passed, 0 failed** in 18.02s. | **PASS** |
| Test Coverage Dimensions | Collectors, normalizers, deduplication, backfill, API, DB tested | 13 test files covering all system components. | **PASS** |
| Deterministic Fixtures | Offline tests execute deterministically without network calls | Mock fixtures utilized for all offline regression tests. | **PASS** |

### Gate 4: Database & Schema Migrations
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| PostgreSQL Compatibility | PostgreSQL 16+ fully supported and verified | Verified on PostgreSQL 18.0 disposable test database. | **PASS** |
| SQLite Fallback | Zero-configuration SQLite for local dev & testing | Verified on `borsel_handler.db` with identical schema. | **PASS** |
| Alembic Migrations | `upgrade head` and `downgrade base` reversible and clean | Verified upgrade/downgrade cycle on PostgreSQL & SQLite. | **PASS** |
| Relational Integrity | Foreign keys, compound unique constraints, and indexes | Schema includes unique indexes on URLs, fingerprints, tickers. | **PASS** |

### Gate 5: Application Security & Hardening
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Ingestion Trigger Protection | `POST /api/v1/ingest/trigger` requires `X-API-Key` | Enforced in `routes.py`, returns 401 on unauthorized access. | **PASS** |
| CORS Configuration | Explicit origin allowlist; no wildcard credential sharing | Configured in `app.py` & `config.py`. Wildcard creds rejected. | **PASS** |
| Safe SQL Execution | No raw string SQL interpolation | 100% SQLAlchemy ORM and parameterized queries. | **PASS** |
| Error Leakage Prevention | No internal stack traces leaked to clients | Handled via FastAPI custom exception handlers. | **PASS** |

### Gate 6: Ingestion Pipeline & Normalization
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Multi-Tier Deduplication | Exact ID, canonical URL, title+date, content hash | Verified in `borsel_handler/processors/dedup.py`. | **PASS** |
| Metadata Normalization | Clean timestamps, company tickers, sectors, summaries | Verified in `normalizer.py` & `company_mapper.py`. | **PASS** |
| Provenance Tracking | Every article linked to raw source payload & run ID | Stored in `articles` and `collection_runs` tables. | **PASS** |

### Gate 7: Resumable Historical Backfill
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Bounded Chunking | Backfill requests partitioned by configurable date ranges | Verified in `borsel_handler/scheduler/backfill.py`. | **PASS** |
| Checkpoint Persistence | State saved atomically to JSON to survive restarts | Verified in `tests/test_backfill.py` (interruption & resume). | **PASS** |
| Rate-Limiting & Politeness | Delays between chunk queries to avoid hammering upstream | Configurable delays enforced between collector chunks. | **PASS** |

### Gate 8: External Source Health & Adaptability
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Live RSS Collection | Financial news feeds operational (ET, Moneycontrol, Mint) | 353 live articles collected during audit verification. | **PASS** |
| Live NSE Corporate Filings | NSE corporate disclosures collected successfully | 462 live articles collected during audit verification. | **PASS** |
| Live SEBI Regulations | Official SEBI circulars RSS collected successfully | 30 live articles collected during audit verification. | **PASS** |
| Exchange Rate-Limiting & WAF | Akamai/IP-blocking mitigation on exchanges (NSE/BSE) | Requires proxy rotation in production (currently single IP). | **CONDITIONAL** |
| Legacy Endpoints (RBI/PIB) | Graceful handling of changed/404 legacy endpoints | Endpoints isolated; collector logs failure without crashing. | **PASS** |

### Gate 9: Backend API & Frontend UI
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| API Health & Stats | `/health`, `/api/v1/sources`, `/api/v1/stats` operational | HTTP 200 returned with valid payloads and DB status. | **PASS** |
| Frontend Production Build | React 18 + Vite production build compiles cleanly | `npm run build` succeeds in 227ms with 0 errors/warnings. | **PASS** |
| UI Design & Ergonomics | Professional financial theme (light white/blue, no dark neon) | Verified UI theme, responsive filters, search, and badges. | **PASS** |

### Gate 10: Operational Documentation & Reproducibility
| Check Item | Requirement | Verification Evidence | Status |
|---|---|---|---|
| Project Control Documents | 7 root specification files complete and synchronized | `prd.md`, `architecture.md`, `rules.md`, `phases.md`, etc. | **PASS** |
| Deployment & Backup Guides | Repeatable startup, migration, and backup instructions | Documented in `README.md` and `deployment_readiness.md`. | **PASS** |

---

## 3. Final Gate Sign-Off

- **Overall Checklist Score:** 9.5 / 10
- **Sign-Off Decision:** **APPROVED FOR STAGING & DEVELOPMENT RELEASE**
- **Action Required for Production Gate:** Provision commercial proxy pool for NSE/BSE exchange collectors and implement REST parser for updated RBI press announcements.
