# Borsel Handler — Scheduler, Reliability, and Error Handling Audit Report
**Document ID:** REL-2026-008  
**Date:** 2026-10-19  
**Platform:** Asyncio, SQLAlchemy Session Pooling, Backoff & Jitter  
**Auditor:** Reliability Engineer & Fault-Tolerance Architect  

---

## 1. Executive Summary

This report evaluates the operational resilience, background task scheduling, retry backoff algorithms, error boundaries, and concurrency safeguards of the Borsel Handler platform.

---

## 2. Scheduling Architecture & Concurrency Safeguards

The scheduling coordinator (`CollectionRunner` in `borsel_handler/scheduler/runner.py`) orchestrates collection across all 7 data sources:

1. **Anti-Overlap Concurrency Lock:**
   - Employs an `asyncio.Lock()` and atomic `_is_running` flag.
   - If a background ingestion job is already active, incoming requests to `/api/v1/ingest/trigger` or automated cron timers are rejected with warning log `Collection job already in progress; skipping overlapping trigger.`
   - Prevents database deadlocks and duplicate network overhead.
2. **Exponential Backoff with Random Jitter:**
   - Network fetches employ exponential backoff with uniformly distributed random jitter:
     $$\Delta t = \min\left(15.0, (\text{base\_delay} \times 2^{\text{attempt}-1}) + \text{Uniform}(0.1, 1.0)\right)$$
   - Prevents thundering-herd synchronization against upstream exchange and regulatory servers.

---

## 3. Fault Isolation & Resiliency Verification

The scheduler guarantees strict component-level fault isolation:

- **Isolated Execution Loop:**
  - Each collector executes within an isolated `try...except` block in `run_collector()`.
  - A fatal exception in one collector (such as a remote HTTP 500, DNS timeout, or HTML parsing error) does **not** terminate the collection run for other collectors.
- **Empirical Test Evidence:**
  - Verified by `tests/test_scheduler_resilience.py::test_scheduler_failure_logged_and_does_not_abort_others`.
  - A deliberately failing mock collector (`FailingCollector`) threw `RuntimeError("Simulated remote server crash")`. The runner cleanly logged status `"failed"` in `collection_logs`, committed the log record, and proceeded to execute subsequent healthy collectors without interruption.

---

## 4. Collection Run Auditing & Health Metrics

Every execution cycle creates an immutable audit trail in the `collection_logs` table:
- `started_at` & `finished_at` (UTC)
- `status` (`'running'`, `'success'`, `'failed'`)
- `items_found`, `items_inserted`, `items_duplicate`, `items_failed`
- `error_message` (truncated diagnostic trace when failed)

These metrics are queried live via `/api/v1/sources/logs` and `/api/v1/stats`, providing operational visibility into source health.

---

## 5. Audit Verdict

**Phase 8 Status:** **VERIFIED**
Scheduler demonstrates full fault isolation, jittered backoff, overlap prevention, and complete audit logging. Proceed to Phase 9 Frontend and End-to-End Integration Audit.
