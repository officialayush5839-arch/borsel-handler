# Borsel Handler — Data Quality and Deduplication Audit Report
**Document ID:** DQR-2026-005  
**Date:** 2026-10-19  
**Platform:** Python 3.14.6, Pydantic V2, SQLAlchemy 2.0.51  
**Auditor:** Lead Data Quality Engineer & Ingestion Specialist  

---

## 1. Executive Summary

This report evaluates the data fidelity, entity resolution accuracy, deduplication idempotency, and provenance preservation of the Borsel Handler data pipeline.

---

## 2. Verification Against Data Quality Criteria

| Quality Criterion | Architectural Safeguard | Empirical Test Result | Status |
| :--- | :--- | :--- | :--- |
| **1. Repeated Collection Idempotency** | 6-Tier Deduplication Engine (`DeduplicationEngine.check_duplicate()`) | `test_repeated_collection_runs_idempotency` PASSED (2 inserted on run 1; 0 inserted, 2 skipped on run 2). | **VERIFIED** |
| **2. Distinct Announcements Preservation** | Distinct headlines and timestamps are not collapsed | `test_distinct_articles_discrimination` PASSED. Distinct corporate events preserved. | **VERIFIED** |
| **3. Source ID & Canonical URL Retention** | Stored in `news_records.source_record_id` & `canonical_url` | Verified in database schema inspection and API detail endpoints. | **VERIFIED** |
| **4. Consistent Publication Timestamps** | Pydantic V2 `@field_validator` coerces strings & datetimes to UTC | `test_ensure_utc` & `test_malformed_and_invalid_date_normalization` PASSED. | **VERIFIED** |
| **5. Ambiguity-Free Entity Resolution** | Word-boundary regex with negative lookaheads | `test_common_word_and_negative_disambiguation` PASSED ("coal" does not resolve to Coal India; "titan" does not resolve to Titan). | **VERIFIED** |
| **6. Traceable Unclassified Records** | Fallback to `general_financial_news` category with raw payload preserved | Verified: Unclassified articles retain raw payload and are retrievable via full-text search. | **VERIFIED** |
| **7. Source Provenance Preservation** | Every unique article writes raw source payload to `source_records` table | `test_get_record_by_id_and_relational_entities` PASSED. Raw JSON payload staged. | **VERIFIED** |
| **8. Database Race Condition Protection** | Unique index on `news_records.record_hash` | Verified in PostgreSQL live test: concurrent duplicate attempt triggers `IntegrityError` and transaction rollback. | **VERIFIED** |

---

## 3. Deduplication Discrimination & Collision Prevention

A potential vulnerability in simple deduplication engines is false-positive matching:
- When two different companies (e.g. `INFY` and `TCS`) file an identical generic regulatory title on the same day (e.g., *"Notice of Board Meeting to consider financial results"*), naive text-similarity engines merge them into one.
- **Borsel Handler Guard:** Tiers 4 and 5 in `DeduplicationEngine` verify `record.symbol != cand.symbol` and `record.company_name != cand.company_name`. If the symbols or company names differ, deduplication is bypassed, ensuring both announcements are stored independently.
- **Empirically Verified:** `tests/test_deduplication.py::test_distinct_companies_identical_generic_title` PASSED.

---

## 4. Data Quality Verdict

**Data Quality Status:** **VERIFIED & SOUND**
The pipeline satisfies all 8 data quality gates with zero data loss and zero synthetic record generation.
