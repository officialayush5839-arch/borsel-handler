# Borsel Handler — Live Source Health and Operational Report
**Document ID:** LSH-2026-003  
**Date:** 2026-10-19  
**Platform:** Async HTTPX, Feedparser, BeautifulSoup4, Borsel Handler Ingestion Engine  
**Auditor:** Data Ingestion Engineer & Feeds Specialist  

---

## 1. Executive Summary

This report documents the empirical operational status, rate limits, access restrictions, latest retrieval statistics, and failure recovery behaviors for all seven configured market data and regulatory sources.

---

## 2. Source Operational Roster & Empirical Metrics

| Source Connector | Source Type | Access Method | Rate Limit / Polling Interval | Live Records Fetched | Records Normalized | Duplicates Skipped | Latest Error / Limitation | Health Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSS Financial Aggregator** | `rss` | Asynchronous RSS parsing | 2.0 RPS / 60 min | **353** | 353 | Evaluated via Dedup | Discontinued legacy feeds (Reuters DNS, NDTV 403, CNBC 404, FE 410) trapped safely | **OPERATIONAL (HEALTHY)** |
| **NSE Announcements (Equities)** | `nse_announcement` | Direct REST with Session Headers | 1.0 RPS / 30 min | **462** | 462 | Evaluated via Dedup | Periodic Akamai WAF challenges on long date-range backfills | **OPERATIONAL (HEALTHY)** |
| **NSE Announcements (SME)** | `nse_announcement` | Direct REST with Session Headers | 1.0 RPS / 30 min | Bounded batch | Bounded batch | Evaluated via Dedup | Subject to same header/session requirements as Equities | **OPERATIONAL (HEALTHY)** |
| **SEBI Regulatory Updates** | `sebi_regulation` | Official Circulars & Orders RSS | 1.0 RPS / 120 min | **30** | 30 | Evaluated via Dedup | None. Official XML feeds responding normally | **OPERATIONAL (HEALTHY)** |
| **BSE Announcements** | `bse_announcement` | JSON Disclosures API with attachment URLs | 2.0 RPS / 30 min | 0 (Window filter) | 0 | 0 | Live endpoint returned 0 announcements in active 48h filter; fixture passed 100% | **STANDBY / FIXTURE VERIFIED** |
| **RBI Official Releases** | `rbi_circular` | Official Press Releases RSS | 1.0 RPS / 120 min | 0 (HTTP 404) | 0 | 0 | Legacy XML feed links moved to HTML press release portal | **MAINTENANCE REQUIRED / FIXTURE VERIFIED** |
| **PIB Economic Policies** | `government_policy` | Ministry of Finance RSS | 1.0 RPS / 120 min | 0 (HTTP 404) | 0 | 0 | Legacy XML feed links moved to gov press portal | **MAINTENANCE REQUIRED / FIXTURE VERIFIED** |

---

## 3. Network Fault Isolation & Feed Error Handling

Empirical testing confirmed that the ingestion pipeline implements isolated feed execution:
- When an individual feed within a multi-feed collector encounters a network error (e.g., DNS resolution failure on legacy Reuters feed, or 403 on NDTV Profit), the error is logged as a warning.
- The pipeline **does not abort**. It continues retrieving and normalizing records from the remaining healthy endpoints.
- Total live records successfully acquired during the audit probe: **845 records** across RSS, NSE, and SEBI in $< 15$ seconds.

---

## 4. Recovery & Next Actions for Maintenance Feeds

1. **RBI Updates:** Migrate feed URL from legacy `rss_pressrelease.xml` to RBI's modern HTML table scraper or updated XML syndicate endpoint.
2. **PIB Press Releases:** Update PIB Ministry of Finance feed to the current Press Information Bureau JSON/HTML release API.
3. **NSE Rotation:** For multi-month backfills in non-mock production, configure rotated user-agent headers and proxy gateways to prevent rate limiting.
