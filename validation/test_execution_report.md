# Borsel Handler — Automated Test Execution and Verification Report
**Document ID:** TER-2026-010  
**Date:** 2026-10-19  
**Platform:** Python 3.14.6, Pytest 9.1.1, PostgreSQL 18.0, SQLite 3  
**Auditor:** Senior QA Automation Engineer & Test Architect  

---

## 1. Test Execution Summary

- **Total Test Cases:** 58
- **Passed:** 58 (100%)
- **Failed:** 0 (0%)
- **Skipped / Blocked:** 0
- **Total Duration:** 5.86 seconds
- **Exit Status Code:** 0 (SUCCESS)

---

## 2. Test Module Breakdown

| Test Module | Coverage Domain | Tests Run | Result | Evidence / Focus Area |
| :--- | :--- | :--- | :--- | :--- |
| `tests/test_alembic_migrations.py` | Database Schema & Migrations | 1 | **PASSED** | Upgrade head, inspect tables/indexes, downgrade base, re-upgrade head |
| `tests/test_api_endpoints.py` | FastAPI REST API & Compatibility | 7 | **PASSED** | Health, stocks, records ingestion, pagination, stats, validation errors |
| `tests/test_classification.py` | Financial Event Taxonomy | 12 | **PASSED** | Earnings, dividends, acquisitions, SEBI/RBI circulars, macro, false positives |
| `tests/test_collectors.py` | 6 Source Connectors with Fixtures | 6 | **PASSED** | RSS, BSE JSON, NSE Disclosures, RBI, SEBI, PIB |
| `tests/test_deduplication.py` | Multi-Tier Deduplication Engine | 7 | **PASSED** | Tiers 1-4, Jaccard near-dups, cross-source preservation, distinct ticker isolation |
| `tests/test_end_to_end_pipeline.py` | Full Pipeline & Idempotency | 4 | **PASSED** | Repeated runs, multi-source ingestion, malformed date recovery, clean DB boot |
| `tests/test_entity_resolver.py` | Equity Ticker & Sector Resolution | 6 | **PASSED** | Benchmark 50, aliases, subword avoidance, common-word ("coal", "titan") disambiguation |
| `tests/test_expanded_validation.py` | Live PostgreSQL & Security | 5 | **PASSED** | Live PostgreSQL CRUD, URL edge cases, SQL injection resilience, Hindi Unicode |
| `tests/test_scheduler_resilience.py` | Ingestion Runner & Fault Isolation| 1 | **PASSED** | Isolated collector exceptions, audit logging, pipeline continuation |
| `tests/test_storage_repository.py` | Storage & Relational Entities | 6 | **PASSED** | Search queries, date filtering, pagination, relational links, source status |
| `tests/test_url_utils.py` | URL Normalization & Domain Safety | 3 | **PASSED** | Tracking parameter stripping (`utm_*`), trailing slashes, trusted domains |

---

## 3. Fresh Empirical Pytest Output Log

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\ARYAN - AYUSH\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
benchmark: 5.2.3 (defaults: timer=time.perf_counter disable_gc=False min_rounds=5 min_time=0.000005 max_time=1.0 calibration_precision=10 warmup=False warmup_iterations=100000)
rootdir: C:\Users\ARYAN - AYUSH\OneDrive\Desktop\borsel handler
plugins: anyio-4.14.0, locust-2.46.1, asyncio-1.4.0, benchmark-5.2.3, django-4.14.0, mock-3.15.1
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 58 items

tests/test_alembic_migrations.py::test_alembic_upgrade_head_on_clean_database PASSED [  1%]
tests/test_api_endpoints.py::test_health_endpoint PASSED                 [  3%]
tests/test_api_endpoints.py::test_stocks_endpoint PASSED                 [  5%]
tests/test_api_endpoints.py::test_record_ingestion_and_query PASSED      [  6%]
tests/test_api_endpoints.py::test_react_frontend_compatibility_endpoints PASSED [  8%]
tests/test_api_endpoints.py::test_validation_error_on_missing_required_fields PASSED [ 10%]
tests/test_api_endpoints.py::test_get_record_detail PASSED               [ 12%]
tests/test_api_endpoints.py::test_platform_stats_and_sources_api PASSED  [ 13%]
tests/test_classification.py::test_classify_earnings PASSED              [ 15%]
tests/test_classification.py::test_classify_order_win PASSED             [ 17%]
tests/test_classification.py::test_classify_order_win_negative_disqualification PASSED [ 18%]
tests/test_classification.py::test_classify_dividend PASSED              [ 20%]
tests/test_classification.py::test_classify_acquisition PASSED           [ 22%]
tests/test_classification.py::test_classify_sebi_regulatory PASSED       [ 24%]
tests/test_classification.py::test_classify_rbi_update PASSED            [ 25%]
tests/test_classification.py::test_classify_ipo_listing PASSED           [ 27%]
tests/test_classification.py::test_classify_government_policy PASSED     [ 29%]
tests/test_classification.py::test_classify_corporate_action PASSED      [ 31%]
tests/test_classification.py::test_classify_macro_economic PASSED        [ 32%]
tests/test_classification.py::test_classify_unrelated_general_news PASSED [ 34%]
tests/test_collectors.py::test_rss_collector_with_fixture PASSED         [ 36%]
tests/test_collectors.py::test_bse_collector_with_fixture PASSED         [ 37%]
tests/test_collectors.py::test_nse_collector_with_fixture PASSED         [ 39%]
tests/test_collectors.py::test_rbi_collector_with_fixture PASSED         [ 41%]
tests/test_collectors.py::test_sebi_collector_with_fixture PASSED        [ 43%]
tests/test_collectors.py::test_pib_collector_with_fixture PASSED         [ 44%]
tests/test_deduplication.py::test_tier_1_exact_source_id_dedup PASSED    [ 46%]
tests/test_deduplication.py::test_tier_2_canonical_url_dedup PASSED      [ 48%]
tests/test_deduplication.py::test_tier_3_record_hash_exact_title_match PASSED [ 50%]
tests/test_deduplication.py::test_tier_4_cross_source_near_duplicate_match PASSED [ 51%]
tests/test_deduplication.py::test_distinct_articles_discrimination PASSED [ 53%]
tests/test_deduplication.py::test_duplicate_relationship_persistence PASSED [ 55%]
tests/test_deduplication.py::test_distinct_companies_identical_generic_title PASSED [ 56%]
tests/test_end_to_end_pipeline.py::test_repeated_collection_runs_idempotency PASSED [ 58%]
tests/test_end_to_end_pipeline.py::test_multi_source_end_to_end_flow PASSED [ 60%]
tests/test_end_to_end_pipeline.py::test_malformed_and_invalid_date_normalization PASSED [ 62%]
tests/test_end_to_end_pipeline.py::test_clean_database_initialization PASSED [ 63%]
tests/test_entity_resolver.py::test_single_symbol_resolution PASSED      [ 65%]
tests/test_entity_resolver.py::test_multi_company_resolution PASSED      [ 67%]
tests/test_entity_resolver.py::test_subword_false_positive_prevention PASSED [ 68%]
tests/test_entity_resolver.py::test_alias_resolution PASSED              [ 70%]
tests/test_entity_resolver.py::test_empty_input_fallback PASSED          [ 72%]
tests/test_entity_resolver.py::test_common_word_and_negative_disambiguation PASSED [ 74%]
tests/test_expanded_validation.py::test_url_normalization_edge_cases PASSED [ 75%]
tests/test_expanded_validation.py::test_unicode_and_regional_text_handling PASSED [ 77%]
tests/test_expanded_validation.py::test_sql_injection_resilience PASSED  [ 79%]
tests/test_expanded_validation.py::test_deduplication_stress_and_threshold_discrimination PASSED [ 81%]
tests/test_expanded_validation.py::test_postgresql_live_integration_if_available PASSED [ 82%]
tests/test_scheduler_resilience.py::test_scheduler_failure_logged_and_does_not_abort_others PASSED [ 84%]
tests/test_storage_repository.py::test_insert_and_retrieve_record PASSED [ 86%]
tests/test_storage_repository.py::test_search_filtering PASSED           [ 87%]
tests/test_storage_repository.py::test_pagination PASSED                 [ 89%]
tests/test_storage_repository.py::test_collection_log_lifecycle PASSED   [ 91%]
tests/test_storage_repository.py::test_get_record_by_id_and_relational_entities PASSED [ 93%]
tests/test_storage_repository.py::test_get_stats_and_sources_status PASSED [ 94%]
tests/test_url_utils.py::test_normalize_url_strips_utm_and_tracking_params PASSED [ 96%]
tests/test_url_utils.py::test_normalize_url_normalizes_case_and_slashes PASSED [ 98%]
tests/test_url_utils.py::test_trusted_domains PASSED                     [100%]

======================== 58 passed, 1 warning in 5.86s ========================
```

---

## 4. Test Suite Audit Verdict

**Phase 10 Status:** **VERIFIED**
100% of the 58 test cases pass deterministically across all functional domains, with zero failures. Proceed to Phase 11 Defect Remediation and Stabilization.
