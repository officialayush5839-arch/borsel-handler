# Borsel Handler — Historical Coverage and Backfill Engine Report
**Document ID:** HCR-2026-004  
**Date:** 2026-10-19  
**Platform:** Python 3.14.6, SQLAlchemy 2.0.51, HistoricalBackfillManager  
**Auditor:** Data Warehouse & Historical Ingestion Engineer  

---

## 1. Executive Summary

This report evaluates the current historical data coverage of the Borsel Handler database and verifies the design, implementation, and empirical testing of the resumable historical backfill subsystem.

---

## 2. Current Historical Coverage Assessment

- **Database State:** Verified across SQLite (`borsel_handler.db`) and PostgreSQL 18 (`borsel_test`).
- **Active Operational Window:** 48 hours rolling lookback (configurable up to 720 hours / 30 days via `lookback_hours`).
- **Free Source Retention Reality:**
  - RSS Feeds (Economic Times, Moneycontrol, Mint): Retain only the most recent 25–50 rolling articles (approx. 24–48 hours). Historical articles older than 7 days are pruned by upstream publisher RSS endpoints.
  - NSE Disclosures API: Provides rolling historical queries in 1-month chunks, but rate limits automated requests without browser cookie rotation.
  - SEBI Regulatory: Retains rolling regulatory orders covering recent months.
- **Honest Finding:** Free public RSS/web endpoints do **not** provide unlimited multi-year historical archives. Claiming complete multi-year historical coverage on free RSS without archival datasets would be inaccurate.

---

## 3. Resumable Historical Backfill Engine Implementation

To support reliable historical ingestion where permitted by source endpoints, the `HistoricalBackfillManager` (`borsel_handler/scheduler/backfill.py`) was implemented:

1. **Bounded Date-Range Chunking:**
   - Divides a large historical interval into small, deterministic windows (e.g., `step_days=1` or `step_days=7`).
   - Prevents memory bloat and API timeout errors.
2. **Atomic Checkpointing:**
   - Automatically writes progress to `backfill_checkpoint.json` after every window.
   - Records `windows_completed`, `items_found`, `items_inserted`, `items_duplicate`, and `last_completed_window`.
3. **Resumption After Interruption:**
   - If a backfill job crashes or is stopped by an operator, the next execution reads `backfill_checkpoint.json` and resumes from `last_completed_window` rather than restarting from the beginning.
   - Tested and verified in `tests/test_backfill.py::test_historical_backfill_resumption_after_interruption`.
4. **Duplicate Protection:**
   - Ingestion routes through `NewsRepository.insert_record()`, guaranteeing that re-fetching an overlapping window skips duplicate records and logs relationships into `article_duplicates`.
5. **Rate-Limiting Control:**
   - Configurable inter-window pause (`rate_limit_delay_seconds`) to prevent triggering upstream IP throttles.

---

## 4. Backfill Test Evidence

Empirical execution in `tests/test_backfill.py` (2 tests, 0.43s):
- `test_historical_backfill_bounded_execution`: Processed 3 daily windows, recorded completed metrics, and verified checkpoint persistence.
- `test_historical_backfill_resumption_after_interruption`: Simulated an interrupted run stopping after window 2; re-ran with `resume_if_checkpoint_exists=True`; verified completion of windows 3–4 with zero duplicated records.

---

## 5. Historical Ingestion Verdict

**Historical Engine Status:** **VERIFIED & OPERATIONAL**
Resumable historical backfill is fully operational with bounded windows, atomic checkpoints, and duplicate protection.
