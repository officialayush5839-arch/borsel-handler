# Borsel Handler — Database Architecture and Schema Audit Report
**Document ID:** DBA-2026-004  
**Date:** 2026-10-19  
**Platform:** PostgreSQL 18.0 & SQLite 3.45+ via SQLAlchemy 2.0.51  
**Auditor:** Senior Database Architect & Systems Engineer  

---

## 1. Executive Summary

This report presents a thorough technical evaluation of the database architecture, entity modeling, relationship mappings, constraints, index topologies, and transactional integrity for the Borsel Handler platform.

The system features a dual storage design:
1. **Normalized Enterprise Schema:** High-performance relational tables modeling `sources`, `companies`, `categories`, `articles` (`news_records`), `article_duplicates`, `source_records`, `article_companies`, `article_categories`, and `collection_logs`.
2. **Dual-Dialect SQLAlchemy Engine:** Operates natively on PostgreSQL (production target with transactional DDL and strict types) and SQLite (zero-config local runtime).

---

## 2. Relational Schema & Entity Specifications

```
  ┌──────────────┐          ┌──────────────────────┐          ┌──────────────┐
  │   sources    │──(1:N)──>│    source_records    │<──(1:N)──│ news_records │
  └──────────────┘          └──────────────────────┘          └──────────────┘
                                                                 │      │
                                                               (M:N)  (M:N)
                                                                 │      │
                                                                 ▼      ▼
                                                            companies categories
```

### Table Definitions & Primary Keys

1. **`sources`**
   - Columns: `id` (PK), `code` (Unique), `name`, `source_type`, `base_url`, `is_active`, `rate_limit_rps`, `created_at`, `updated_at`.
   - Indexes: `ix_sources_code` (UNIQUE), `ix_sources_source_type`.

2. **`companies`**
   - Columns: `id` (PK), `symbol` (Unique), `name`, `isin` (Unique), `bse_code`, `sector`, `industry`, `is_active`, `created_at`.
   - Indexes: `ix_companies_symbol` (UNIQUE), `ix_companies_isin` (UNIQUE), `ix_companies_sector`.

3. **`categories`**
   - Columns: `id` (PK), `code` (Unique), `name`, `description`, `parent_category`.
   - Indexes: `ix_categories_code` (UNIQUE).

4. **`news_records` (Articles)**
   - Columns: `id` (PK), `record_hash` (Unique SHA-256), `canonical_url`, `original_url`, `source_name`, `source_type`, `source_record_id`, `company_name`, `symbol`, `sector`, `category`, `confidence_score`, `title`, `snippet`, `tags` (JSON), `raw_metadata` (JSON), `published_at` (TZ), `collected_at` (TZ), `first_seen_at` (TZ), `last_seen_at` (TZ), `validation_status`, `provenance` (JSON).
   - Indexes:
     - `ix_news_records_record_hash` (UNIQUE)
     - `ix_news_records_canonical_url`
     - `idx_pub_sym` (COMPOSITE: `published_at DESC`, `symbol`)
     - `ix_news_records_category`
     - `ix_news_records_source_name`

5. **`article_duplicates`**
   - Columns: `id` (PK), `primary_record_id` (FK -> `news_records.id`), `duplicate_url`, `source_name`, `duplicate_record_hash`, `detection_tier`, `similarity_score`, `detected_at`.
   - Indexes: `ix_article_duplicates_primary_record_id`.

6. **`source_records`**
   - Columns: `id` (PK), `source_id` (FK -> `sources.id`), `source_record_id`, `raw_payload` (JSON), `fetched_at`, `processed_status`.
   - Indexes: `ix_source_records_source_record_id`.

7. **`article_companies` & `article_categories` (Junction Tables)**
   - Normalized association mapping many-to-many relationships with extraction confidence and matching methodology.

8. **`collection_logs`**
   - Columns: `id` (PK), `source_name`, `started_at`, `finished_at`, `status`, `items_found`, `items_inserted`, `items_duplicate`, `items_failed`, `error_message`.
   - Indexes: `ix_collection_logs_source_name`.

---

## 3. PostgreSQL vs SQLite Dialect Compatibility Verification

| Dialect Feature | PostgreSQL 18 Engine | SQLite 3 Engine | Resolution in Borsel Handler |
| :--- | :--- | :--- | :--- |
| **Boolean Column Defaults** | Strict boolean (`TRUE` / `FALSE`) | Integer (`1` / `0`) | Uses `sa.true()`, rendering `TRUE` on PG and `1` on SQLite. |
| **JSON Serialization** | Native `JSONB` / `JSON` | Native JSON text column | SQLAlchemy `sa.JSON()` abstracts type translation. |
| **Timestamp with Timezone** | `TIMESTAMP WITH TIME ZONE` | Text (ISO-8601 strings) | Pydantic and SQLAlchemy UTC coercers enforce clean round-trips. |
| **Transactional DDL** | Supported natively | Partial / Emulated via Batch | Alembic migrations use batch operations for SQLite and native DDL for PG. |
| **Index Creation Safety** | `CREATE INDEX IF NOT EXISTS` | Native conditional indexes | Wrapped with error traps in migration scripts. |

---

## 4. Concurrency, Race Condition, & Integrity Tests

Empirical testing confirmed:
1. **Unique Constraint Enforcement:** Inserting a record with an identical `record_hash` on PostgreSQL generates an `IntegrityError` and is immediately rolled back without dirtying the database state.
2. **Transaction Rollback:** Failed collection runs cleanly abort their database transactions, leaving previously inserted items intact.
3. **Audit Trail Completeness:** Collection run status, items inserted, duplicates detected, and items failed are consistently updated in `collection_logs`.

---

## 5. Audit Verdict

**Phase 4 Database Audit Status:** **VERIFIED**
Both SQLite and PostgreSQL 18 schemas are completely sound, fully indexed, and enforce referential integrity.
