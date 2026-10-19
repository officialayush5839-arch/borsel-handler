# Borsel Handler — Alembic Database Migration Test Report
**Document ID:** MTR-2026-004  
**Date:** 2026-10-19  
**Platform:** Alembic 1.15.1, PostgreSQL 18.0 (Port 5433), SQLite 3  
**Auditor:** QA Automation & Database Specialist  

---

## 1. Migration History & Revisions

| Revision ID | Down Revision | Description | Created Date |
| :--- | :--- | :--- | :--- |
| `001_initial_schema` | None (Base) | Baseline migration creating all 9 relational entities (`sources`, `companies`, `categories`, `news_records`, `article_duplicates`, `source_records`, `article_companies`, `article_categories`, `collection_logs`) | 2026-10-19 |
| `002_audit_fields` | `001_initial_schema` | Adds audit and provenance fields (`last_seen_at`, `validation_status`, `provenance` to `news_records`, `items_failed` to `collection_logs`) | 2026-10-19 |

---

## 2. Test Execution on PostgreSQL 18

**Command:**
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/borsel_test"
py -m alembic upgrade head
```

**Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, 001_initial_relational_schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_audit_fields, 002_add_provenance_and_audit_fields
Exit Code: 0 (SUCCESS)
```

**Downgrade to Base & Re-Upgrade Cycle:**
```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5433/borsel_test"
py -m alembic downgrade base
py -m alembic upgrade head
```

**Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 002_audit_fields -> 001_initial_schema, 002_add_provenance_and_audit_fields
INFO  [alembic.runtime.migration] Running downgrade 001_initial_schema -> , 001_initial_relational_schema
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001_initial_schema, 001_initial_relational_schema
INFO  [alembic.runtime.migration] Running upgrade 001_initial_schema -> 002_audit_fields, 002_add_provenance_and_audit_fields
Exit Code: 0 (SUCCESS)
```

---

## 3. Test Execution on SQLite

**Command:**
```powershell
py -m alembic current
```

**Output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
002_audit_fields (head)
Exit Code: 0 (SUCCESS)
```

**Automated Pytest Suite Execution:**
`tests/test_alembic_migrations.py::test_alembic_upgrade_head_on_clean_database`
- Creates temporary SQLite database file.
- Executes `command.upgrade(alembic_cfg, "head")`.
- Inspects all 10 tables and composite indexes (`ix_news_records_record_hash`, `idx_pub_sym`).
- Executes `command.downgrade(alembic_cfg, "base")` and verifies complete table cleanup.
- Re-executes `command.upgrade(alembic_cfg, "head")` to confirm idempotency.
- Result: **PASSED (100%)**

---

## 4. Migration Defect Resolution Record

| Defect ID | Defect Description | Severity | Fix Applied | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- |
| **MIG-001** | `alembic.ini` hardcoded SQLite connection string prevented CLI override | High | Modified `alembic/env.py` to prioritize `os.getenv("DATABASE_URL")` over static `.ini` file | PostgreSQL migration switched dynamically and executed cleanly |
| **MIG-002** | Column `is_active` in migration 001 had `server_default=sa.text('1')`, causing PostgreSQL type mismatch error | Critical | Changed `server_default` to `sa.true()`, enabling native boolean literal for PostgreSQL and 1 for SQLite | Successfully executed upgrade, downgrade, and re-upgrade on PostgreSQL 18 |

---

## 5. Conclusion & Verification Verdict

**Migration Test Status:** **VERIFIED**
Alembic migration scripts support full forward upgrades and rollback downgrades on both SQLite and PostgreSQL.
