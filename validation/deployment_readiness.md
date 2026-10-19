# Borsel Handler — Deployment Readiness Report

**Date:** 2026-10-19  
**Module:** Borsel Handler (Data Collection & Intelligence Platform)  
**Evaluator:** Senior Software Architect & DevOps Lead  
**Document Status:** Approved for Development & Staging  

---

## 1. Executive Summary

This report defines the operational and deployment readiness criteria for **Borsel Handler**. It documents exact configuration variables, database initialization and migration steps, repeatable application startup commands, observability endpoints, backup and recovery procedures, and operational limitations for deployment across development and staging environments.

---

## 2. Environment Configuration

Borsel Handler relies on environment-based configuration loaded via `pydantic-settings` in `borsel_handler/config.py`. All configuration parameters provide safe defaults while strictly enforcing production security requirements.

### 2.1 Configuration Matrix

| Environment Variable | Description | Default / Development Value | Recommended Staging/Production Value |
|----------------------|-------------|-----------------------------|--------------------------------------|
| `ENVIRONMENT` | Deployment environment label | `development` | `staging` / `production` |
| `DEBUG` | Verbose debug logs & OpenAPI UI | `true` | `false` |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./borsel_handler.db` | `postgresql://borsel_user:secure_pwd@db_host:5432/borsel_db` |
| `API_SECRET_KEY` | Secret key for protected ingestion endpoints | `dev_secret_key_change_in_production` | Strong random 256-bit hexadecimal string |
| `ALLOWED_ORIGINS` | Permitted CORS origins | `http://localhost:5173,http://localhost:3000` | Strict comma-separated domain list (e.g. `https://borsel.internal.domain`) |
| `COLLECTION_INTERVAL_MINUTES` | Scheduler interval between collection runs | `15` | `15` to `60` depending on source rate limits |
| `REQUEST_TIMEOUT_SECONDS` | HTTP request timeout for collectors | `30` | `30` |
| `MAX_RETRIES` | Max HTTP retry attempts per collector | `3` | `3` |
| `RATE_LIMIT_DELAY` | Politeness delay between external requests | `1.5` | `2.0` to `5.0` |

### 2.2 Template Configuration File (`.env.example`)
A clean, secure `.env.example` is maintained in the project root. Root `.gitignore` prevents real `.env` or credential files from being tracked in version control.

---

## 3. Database Initialization & Migration

Borsel Handler supports dual database targets:
- **Zero-Dependency Local Dev / CI:** SQLite (`sqlite:///./borsel_handler.db`)
- **Staging / High-Throughput Production:** PostgreSQL 16+ (tested on PostgreSQL 18.0)

### 3.1 Initial Setup Steps (PostgreSQL)

1. **Create Database and User:**
   ```sql
   CREATE USER borsel_user WITH PASSWORD 'replace_with_strong_password';
   CREATE DATABASE borsel_db OWNER borsel_user;
   GRANT ALL PRIVILEGES ON DATABASE borsel_db TO borsel_user;
   ```

2. **Execute Alembic Migrations:**
   ```bash
   # Set the database URL
   export DATABASE_URL="postgresql://borsel_user:replace_with_strong_password@db_host:5432/borsel_db"

   # Apply all migrations to head
   alembic upgrade head
   ```

3. **Verify Schema Status:**
   ```bash
   alembic current
   # Expected output: 002_audit_fields (head)
   ```

---

## 4. Application Startup Commands

### 4.1 Backend API Server (FastAPI + Uvicorn)

- **Development Mode (with auto-reload):**
  ```bash
  py -m uvicorn borsel_handler.api.app:app --host 127.0.0.1 --port 8000 --reload
  ```

- **Staging / Production Mode (multi-worker):**
  ```bash
  py -m uvicorn borsel_handler.api.app:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'
  ```

### 4.2 Frontend Application (React 18 + Vite)

- **Development Server:**
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

- **Production Static Build:**
  ```bash
  cd frontend
  npm run build
  # Generates optimized static assets into frontend/dist/
  ```
  The built assets in `frontend/dist/` can be served directly via Nginx, Caddy, AWS S3 + CloudFront, or FastAPI static file mount.

### 4.3 Scheduled Collection Worker

The ingestion scheduler is configured as an async background task or independent CLI worker:
```bash
py -m borsel_handler.scheduler.runner
```

---

## 5. Health Checks & Observability

### 5.1 Service Endpoints

1. **Liveness & Readiness Probe:**
   - **Endpoint:** `GET /health`
   - **Success Response (HTTP 200):**
     ```json
     {
       "status": "healthy",
       "database": "connected",
       "version": "1.0.0",
       "timestamp": "2026-10-19T12:00:00Z"
     }
     ```
   - **Failure Response (HTTP 503):** Returns `"database": "disconnected"` if database ping fails.

2. **Source Status Probe:**
   - **Endpoint:** `GET /api/v1/sources`
   - **Response:** Array of all 7 registered sources with collector type, health status, and metadata.

3. **Collection Statistics:**
   - **Endpoint:** `GET /api/v1/stats`
   - **Response:** Total records, source distribution, category distribution, and duplicate counts.

### 5.2 Structured Logging

- Borsel Handler utilizes standard library `logging` configured in `borsel_handler/utils/logger.py` with structured format:
  `%(asctime)s [%(levelname)s] [%(name)s]: %(message)s`
- Log levels are controlled via `LOG_LEVEL` environment variable (`INFO` default, `DEBUG` for troubleshooting).
- For containerized deployments, logs stream directly to `stdout`/`stderr` for collection by Docker logging drivers, Fluentbit, or Datadog.

---

## 6. Database Backup & Disaster Recovery

### 6.1 PostgreSQL Backup Procedure

- **Daily Logical Dump:**
  ```bash
  pg_dump -h db_host -U borsel_user -F c -b -v -f "/backups/borsel_db_$(date +%Y%m%d_%H%M%S).dump" borsel_db
  ```
- **Automated Cron Schedule (e.g. 02:00 AM daily):**
  ```cron
  0 2 * * * /usr/bin/pg_dump -h localhost -U borsel_user -F c -b -f "/backups/borsel_db_$(date +\%Y\%m\%d).dump" borsel_db
  ```

### 6.2 Restoration Procedure

To restore from a backup file:
```bash
# 1. Terminate active connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'borsel_db';"

# 2. Re-create database
dropdb -U postgres borsel_db
createdb -U postgres -O borsel_user borsel_db

# 3. Restore data
pg_restore -h db_host -U borsel_user -d borsel_db -v "/backups/borsel_db_target.dump"
```

---

## 7. Graceful Shutdown & Timeouts

- **HTTP Request Timeouts:** All external collector calls via `httpx.AsyncClient` enforce an explicit 30.0-second timeout to prevent hung connections.
- **Signal Handling:** FastAPI / Uvicorn captures `SIGINT` and `SIGTERM` signals, completing in-flight HTTP requests before releasing database connection pools.
- **Scheduler Interruption:** The `HistoricalBackfillManager` writes an atomic `backfill_checkpoint.json` on each batch completion, ensuring graceful shutdown without data loss or duplicate records upon restart.

---

## 8. Deployment Prerequisites & Operational Limitations

1. **Proxy Rotation for Real-Time Exchange Collectors:**  
   NSE and BSE public corporate announcement endpoints enforce Akamai/rate-limit protections. In high-frequency staging/production deployments, configure an egress residential/datacenter proxy pool.
2. **Regulatory Portal Notice:**  
   SEBI circulars RSS feed is stable. RBI and PIB legacy endpoints have migrated and require maintenance updates to their new REST/HTML endpoints before production activation.
3. **Historical Backfill Window:**  
   Free RSS feeds only retain rolling 24–48 hours of announcements. Long-term backfilling (> 90 days) requires archival data imports via historical CSV/JSON dumps.
