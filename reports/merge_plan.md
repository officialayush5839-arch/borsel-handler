# Merge Plan: Borsel Handler Data Collection Platform

**Document ID:** MP-2026-001  
**Generated:** 2026-10-19  
**Specification:** Stage E — Borsel Handler Unified Integration

---

## 1. Architectural Foundation Decision

### 1.1 Comparative Evaluation
- **Option 1: Market Announcements CLI/Streamlit as Base**  
  *Pros:* Working NSE/BSE scrapers and comprehensive SQLite storage.  
  *Cons:* Monolithic scripts (1,970 lines in one file, 2,189 in another), fragmented into 4 separate SQLite files, synchronous execution, no REST API for client apps or agentic workflows, tight coupling of Streamlit UI to direct SQL calls.
- **Option 2: StockPulse FastAPI/React as Base (SELECTED & ENHANCED)**  
  *Pros:* Modern asynchronous architecture, clean FastAPI routing, Pydantic type safety, modular services, polished React SPA frontend.  
  *Cons:* Ephemeral in-memory caching without database persistence, lack of NSE scraper, basic deduplication.

### 1.2 Verdict
Use the **FastAPI service architecture (StockPulse pattern)** as the core foundation, refactored into an enterprise-grade package `borsel_handler`. Extract and adapt the exchange scraping logic and taxonomy from Market Announcements into pluggable collectors and classifiers, backed by a persistent SQLAlchemy 2.0 ORM layer supporting PostgreSQL (production) and SQLite (development/testing).

---

## 2. Component Analysis: Reused, Adapted, Excluded, & Newly Implemented

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Borsel Handler Platform                         │
├────────────────────────────────┬───────────────────────────────────────┤
│ Reused & Adapted               │ Source Repository                     │
├────────────────────────────────┼───────────────────────────────────────┤
│ 14 Curated RSS Feeds           │ StockPulse (rss_service.py)           │
│ Nifty 50 Entity & Sector Data  │ StockPulse (stocks.py, dependency_map)│
│ BSE Announcement API Fetcher   │ StockPulse / Market Announcements     │
│ NSE Corporate Disclosures      │ Market Announcements                  │
│ Event Classification Taxonomy  │ Market Announcements (idea_rules.py)  │
│ FastAPI Routing & App Skeleton │ StockPulse (backend/main.py)          │
│ React Frontend UI Components   │ StockPulse (frontend/src/)            │
├────────────────────────────────┼───────────────────────────────────────┤
│ Excluded                       │ Reason                                │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4 Fragmented SQLite DBs        │ Replaced by unified SQLAlchemy schema │
│ Synchronous `schedule` loop    │ Replaced by async background runner   │
│ Speculative "Idea Scoring"     │ Isolated into deterministic tagger    │
│ Streamlit UI as primary        │ Replaced by React SPA + REST API      │
│ In-memory TTLCache for news    │ Replaced by persistent DB storage     │
├────────────────────────────────┼───────────────────────────────────────┤
│ Newly Implemented              │ Purpose                               │
├────────────────────────────────┼───────────────────────────────────────┤
│ `BaseCollector` Interface      │ Standardized plugin contract          │
│ `NormalizedNewsRecord`         │ Unified Pydantic schema               │
│ SQLAlchemy Persistence Layer   │ Dialect-agnostic PostgreSQL/SQLite    │
│ Multi-Tier Deduplication Engine│ Cross-source & intra-source dedup     │
│ Canonical URL Normalizer       │ URL tracking strip & canonicalization │
│ Automated Test Suite           │ Deterministic Pytest coverage         │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 3. Unified Directory Structure (`borsel_handler/`)

```
borsel_handler/
├── __init__.py
├── config.py                          # Pydantic Settings & environment validation
├── core/
│   ├── __init__.py
│   ├── models.py                      # NormalizedNewsRecord & Pydantic schemas
│   └── url_utils.py                   # Canonical URL normalization & allowlisting
├── storage/
│   ├── __init__.py
│   ├── database.py                    # SQLAlchemy engine, session maker, base
│   ├── models.py                      # SQLAlchemy ORM models (NewsRecord, CollectionLog)
│   └── repository.py                  # CRUD repository, transactional persistence
├── dedup/
│   ├── __init__.py
│   └── engine.py                      # Multi-tier deduplication engine
├── classification/
│   ├── __init__.py
│   ├── taxonomy.py                    # 27 event categories and groups
│   └── classifier.py                  # Rule-based weighted classifier
├── collectors/
│   ├── __init__.py
│   ├── base.py                        # BaseCollector abstract base class
│   ├── rss.py                         # 14 RSS feed collector
│   ├── bse.py                         # BSE India announcements collector
│   └── nse.py                         # NSE corporate disclosures collector
├── scheduler/
│   ├── __init__.py
│   └── runner.py                      # Async periodic collection manager
├── api/
│   ├── __init__.py
│   ├── dependencies.py                # Database and config FastAPI dependencies
│   ├── routes.py                      # GET /records, GET /search, POST /ingest
│   └── app.py                         # FastAPI application factory & middleware
└── data/
    ├── __init__.py
    ├── stocks.py                      # Curated Indian stock metadata
    └── dependency_map.py              # Curated supply chain & macro keywords
```

---

## 4. Technical Design Specifications

### 4.1 Common Collector Interface (`BaseCollector`)
All data collectors inherit from `BaseCollector`:
```python
class BaseCollector(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @property
    @abstractmethod
    def source_type(self) -> str: ...

    @abstractmethod
    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """Fetch raw records, parse, normalize, and return validated records."""
        ...
```

### 4.2 Normalized Data Model (`NormalizedNewsRecord`)
```python
class NormalizedNewsRecord(BaseModel):
    title: str
    snippet: str
    original_url: str
    canonical_url: str
    published_at: datetime
    source_name: str
    source_type: str                   # 'rss', 'bse_announcement', 'nse_announcement'
    source_record_id: Optional[str]    # Unique ID from origin
    company_name: Optional[str]
    symbol: Optional[str]              # NSE/BSE ticker symbol
    sector: Optional[str]
    category: str                      # 'earnings', 'corporate_action', 'regulatory', etc.
    tags: List[str] = []
    confidence_score: float = 1.0
    collected_at: datetime
    raw_metadata: Dict[str, Any] = {}
```

### 4.3 Unified Persistence (PostgreSQL & SQLite)
SQLAlchemy declarative model `NewsRecord` uses dialect-agnostic constructs:
- `id`: Integer Primary Key
- `record_hash`: SHA-256 hash string (Unique)
- `canonical_url`: Indexed String
- `source_name` + `source_record_id`: Composite unique constraint
- `published_at`: UTC DateTime (Indexed)
- `symbol`, `company_name`, `sector`, `category`: Indexed Strings
- `raw_metadata`: JSON/JSONB column

### 4.4 Multi-Tier Deduplication Engine
When an ingested record arrives:
1. **Tier 1 (Source Exact ID):** Match `(source_name, source_record_id)` in database.
2. **Tier 2 (Canonical URL):** Match normalized `canonical_url`.
3. **Tier 3 (Exact Title & Date Window):** SHA-256 hash of normalized title + rounded publication date (1-hour window).
4. **Tier 4 (Cross-Source Semantic / Fuzzy Match):**
   - High similarity (Jaro-Winkler score $\ge 0.88$ on normalized title) AND publication times within 6 hours AND matching company/symbol.
   - If match is detected, record is linked or skipped rather than duplicated.

### 4.5 Unified Classification
- Primary Categories: `earnings`, `dividend`, `corporate_action`, `acquisition_merger`, `capex_expansion`, `order_win`, `regulatory_sebi`, `rbi_update`, `board_management`, `credit_rating`, `general_financial_news`.
- Both source-provided category and rule-evaluated classification are stored.

---

## 5. Migration and Execution Strategy

1. **Step 1:** Establish clean package `borsel_handler/` and dependencies.
2. **Step 2:** Build core schemas (`models.py`, `url_utils.py`).
3. **Step 3:** Implement persistent SQLAlchemy layer with transactional session handling.
4. **Step 4:** Implement deduplication engine with confidence thresholds.
5. **Step 5:** Implement classification engine using domain rules.
6. **Step 6:** Implement standardized collectors (`rss.py`, `bse.py`, `nse.py`).
7. **Step 7:** Build FastAPI endpoints (`/health`, `/records`, `/search`, `/collect`).
8. **Step 8:** Add test suite with fixtures and verify 100% pass rate.
