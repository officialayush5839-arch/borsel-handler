# Borsel Handler — Ingestion Pipeline and Data Quality Audit Report
**Document ID:** DPA-2026-006  
**Date:** 2026-10-19  
**Platform:** Python 3.14.6, Pydantic V2, SQLAlchemy 2.0.51  
**Auditor:** Senior Data Quality & Ingestion Systems Engineer  

---

## 1. Executive Summary

This report delivers a rigorous audit of the normalization, entity resolution, classification, deduplication, and data quarantine pipelines of the Borsel Handler platform.

---

## 2. Ingestion Pipeline Stages

```
   Raw Source Payload (RSS / BSE JSON / NSE Disclosures / SEBI Feeds)
                               │
                               ▼
               1. URL & Text Normalization Layer
         (Strip UTM/tracking parameters, normalize slashes, decode HTML)
                               │
                               ▼
               2. Schema Validation (Pydantic V2)
             (Enforce UTC datetime, mandatory title/URL)
                               │
                               ▼
               3. Entity Resolution & Disambiguation
         (Resolve Nifty 50 tickers, sectors, alias & word boundary)
                               │
                               ▼
               4. Rule-Based Classification Engine
             (Score across 14 financial & regulatory categories)
                               │
                               ▼
               5. Multi-Tier Deduplication Engine
     (Tier 1: Source ID -> Tier 2: URL -> Tier 3: Hash -> Tier 4: Jaccard)
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       [DUPLICATE DETECTED]              [UNIQUE RECORD]
                │                             │
    Stage into `article_duplicates`  Stage into `news_records`
    (Link to primary canonical ID)   (Stage raw payload into `source_records`,
                                      link `article_companies`, `article_categories`)
```

---

## 3. Entity Resolution & Disambiguation Verification

The entity resolution system (`borsel_handler/data/resolver.py`) features sophisticated dictionary and word-boundary regex matching against 50 Indian benchmark equities, incorporating negative lookaheads and common-word disambiguation:

| Challenge | Example Input Headline | Expected Behavior | Empirical Test Result |
| :--- | :--- | :--- | :--- |
| **Common Word Clashes** | *"India boosts thermal coal import to meet rising power demand"* | Must NOT resolve to `COALINDIA` | **PASSED** (`test_common_word_and_negative_disambiguation`) |
| **Mythology / Generic Titan** | *"Clash of the titans in world chess championship"* | Must NOT resolve to `TITAN` | **PASSED** (`test_common_word_and_negative_disambiguation`) |
| **Subword False Positives** | *"The ongoing revolution in digital connectivity"* | Must NOT resolve to `ONGC` (inside 'ongoing') | **PASSED** (`test_subword_false_positive_prevention`) |
| **Alias Resolution** | *"Maruti Suzuki reports record vehicle dispatches in Q3"* | Must resolve to `MARUTI` | **PASSED** (`test_alias_resolution`) |
| **Multi-Company Resolution**| *"TCS and Infosys report divergent Q2 margins"* | Must resolve both `TCS` and `INFY` | **PASSED** (`test_multi_company_resolution`) |

---

## 4. Multi-Tier Deduplication Audit

The deduplication engine implements 6 tiers with company-boundary guards:

1. **Tier 1 (Exact Source Record ID):** Matches identical upstream disclosure identifiers from the same publisher.
2. **Tier 2 (Canonical Cleaned URL):** Matches identical URLs after stripping `utm_*`, `fbclid`, session tokens, and lowercasing domain.
3. **Tier 3 (Record Hash Match):** SHA-256 fingerprint generated from normalized title, symbol, and hour window.
4. **Tier 4 (Cross-Source Near-Duplicate Jaccard Similarity):** Computes token overlap for syndicated reporting (threshold $\ge 0.85$ within $\pm 12$h).
5. **Tier 5 (Normalized Title Window):** Matches normalized headlines within $\pm 24$h.
6. **Tier 6 (Normalized Original URL):** Matches fallback links.

### False-Positive Collision Prevention (Verified)
Generic corporate announcements such as *"Notice of Board Meeting to consider financial results"* filed by two different companies (e.g. `INFY` and `TCS`) on the same day are intentionally **not** collapsed into duplicates because Tiers 4 and 5 enforce company/symbol mismatch rejection guards.

---

## 5. Data Quality, Provenance, & Quarantine

1. **UTC Enforced:** Ingestion pipeline validates and converts all publication timestamps to UTC. Naive datetimes are safely stamped with `timezone.utc`.
2. **Provenance Preservation:** Every inserted record captures full source metadata, original URL, canonical URL, and raw payload in `source_records`.
3. **Audit Duplicate Table:** Secondary duplicates are not silently dropped; their URLs, hashes, and detection tiers are stored in `article_duplicates` referencing the canonical article.

---

## 6. Audit Verdict

**Phase 6 Status:** **VERIFIED**
Data pipeline demonstrates complete integrity, rigorous disambiguation, and zero data loss on duplicate detection. Proceed to Phase 7 Historical Storage and Query Audit.
