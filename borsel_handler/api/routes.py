"""
FastAPI Routes for Borsel Handler Platform
Implements complete REST API suite satisfying Section 14 of Mega Prompt 2.
"""
import io
from datetime import datetime, timezone
from typing import List, Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Header, Response
from sqlalchemy.orm import Session

from borsel_handler.config import settings
from borsel_handler.api.dependencies import get_db_session
from borsel_handler.core.models import (
    NormalizedNewsRecord, NewsRecordResponse, SearchQuery,
    SearchResponse, CollectionRunSummary
)
from borsel_handler.data.stocks import NIFTY_50
from borsel_handler.data.resolver import CompanyResolver, SECTORS
from borsel_handler.scheduler.runner import CollectionRunner
from borsel_handler.storage.models import CollectionLog, NewsRecord
from borsel_handler.storage.repository import NewsRepository

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db_session)):
    """Health check validating application and database connectivity."""
    try:
        count = db.query(NewsRecord).count()
        return {
            "status": "healthy",
            "database": "connected",
            "total_records_indexed": count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Database check failed: {exc}")


@router.get("/api/v1/stats")
def get_platform_stats(db: Session = Depends(get_db_session)):
    """Returns aggregated platform metrics including duplicate prevention counts."""
    return NewsRepository.get_stats(db)


@router.get("/api/v1/sources", response_model=List[dict])
def get_sources(db: Session = Depends(get_db_session)):
    """Returns active monitored sources, their health status, and run logs."""
    return NewsRepository.get_sources_status(db)


@router.get("/api/v1/sources/logs", response_model=List[dict])
def get_collection_logs(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db_session),
):
    """Retrieve audit history and health logs of collection runs."""
    logs = db.query(CollectionLog).order_by(CollectionLog.id.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "source_name": l.source_name,
            "started_at": l.started_at,
            "finished_at": l.finished_at,
            "status": l.status,
            "items_found": l.items_found,
            "items_inserted": l.items_inserted,
            "items_duplicate": l.items_duplicate,
            "items_failed": l.items_failed,
            "error_message": l.error_message,
        }
        for l in logs
    ]


@router.get("/api/v1/companies", response_model=List[dict])
def get_companies(
    q: Optional[str] = Query(None, description="Search ticker or name"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
):
    """Returns reference directory of Indian listed equities and sectors."""
    results = NIFTY_50
    if sector:
        results = [s for s in results if s.get("sector", "").lower() == sector.lower()]
    if q:
        query_str = q.lower()
        results = [
            s for s in results
            if query_str in s["symbol"].lower() or query_str in s["name"].lower()
        ]
    return results


@router.get("/api/v1/records", response_model=SearchResponse)
def get_records(
    symbol: Optional[str] = Query(None, description="Stock ticker symbol (e.g. INFY)"),
    sector: Optional[str] = Query(None, description="Industry sector"),
    category: Optional[str] = Query(None, description="Event category"),
    source_name: Optional[str] = Query(None, description="Source name"),
    source_type: Optional[str] = Query(None, description="Source type (rss, bse_announcement, nse_announcement, rbi_circular, etc.)"),
    from_date: Optional[datetime] = Query(None, description="Start date (ISO-8601)"),
    to_date: Optional[datetime] = Query(None, description="End date (ISO-8601)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db_session),
):
    """Retrieve historical news and announcement records with structured filtering."""
    query = SearchQuery(
        symbol=symbol,
        sector=sector,
        category=category,
        source_name=source_name,
        source_type=source_type,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size,
    )
    items, total = NewsRepository.search_records(db, query)
    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[NewsRecordResponse.model_validate(item) for item in items],
    )


@router.get("/api/v1/records/search", response_model=SearchResponse)
def search_records(
    q: str = Query(..., description="Keyword query across title, snippet, and company"),
    symbol: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db_session),
):
    """Full-text search on historical news and announcements."""
    query = SearchQuery(
        query=q,
        symbol=symbol,
        category=category,
        page=page,
        page_size=page_size,
    )
    items, total = NewsRepository.search_records(db, query)
    return SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[NewsRecordResponse.model_validate(item) for item in items],
    )


@router.get("/api/v1/records/export")
def export_records_for_ai(
    symbol: Optional[str] = Query(None, description="Filter by stock ticker symbol"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db_session),
):
    """
    Exports clean, normalized financial intelligence dataset as CSV via Pandas.
    Fulfills VeritasAI mandate: preparing structured data for downstream AI models.
    """
    query = SearchQuery(symbol=symbol, category=category, page=1, page_size=500)
    df = NewsRepository.to_dataframe(db, query)
    csv_bytes = df.to_csv(index=False)
    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=borsel_ai_training_data.csv"},
    )


@router.get("/api/v1/records/{id}", response_model=NewsRecordResponse)
def get_record_detail(
    id: int,
    db: Session = Depends(get_db_session),
):
    """Retrieves single article detail by primary key id."""
    record = NewsRepository.get_record_by_id(db, id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Record #{id} not found")
    return NewsRecordResponse.model_validate(record)


@router.post("/api/v1/records", response_model=dict)
def ingest_record(
    record: NormalizedNewsRecord,
    db: Session = Depends(get_db_session),
):
    """Ingests a normalized record through the multi-stage deduplication engine."""
    entity, inserted, reason = NewsRepository.insert_record(db, record)
    if not inserted:
        return {
            "status": "duplicate_skipped",
            "reason": reason,
        }
    return {
        "status": "inserted",
        "id": entity.id,
        "record_hash": entity.record_hash,
    }


@router.post("/api/v1/ingest/trigger", response_model=dict)
async def trigger_ingestion(
    background_tasks: BackgroundTasks,
    lookback_hours: int = Query(48, ge=1, le=720),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    """
    Asynchronously triggers data collection across all configured sources.
    Secured: Requires valid X-API-Key header when API_SECRET_KEY is configured.
    """
    if settings.API_SECRET_KEY:
        if not x_api_key or x_api_key != settings.API_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Valid X-API-Key header required to trigger collection."
            )

    runner = CollectionRunner()
    background_tasks.add_task(runner.run_all, cutoff_hours=lookback_hours)
    return {
        "status": "collection_initiated",
        "lookback_hours": lookback_hours,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================================
# Frontend Compatibility Endpoints (StockPulse Contract)
# =========================================================================

@router.get("/api/v1/stocks", response_model=List[dict])
@router.get("/api/stocks", response_model=List[dict])
def get_stocks_compat():
    """Returns curated list of Nifty 50 Indian companies."""
    return NIFTY_50


@router.post("/api/auth")
def auth_compat():
    """Compatibility auth endpoint."""
    return {"ok": True}


@router.get("/api/news")
def get_news_compat(
    symbol: str = Query(..., description="NSE ticker symbol e.g. MARUTI"),
    timerange: str = Query("48h", description="One of: 24h, 48h, 72h, 1w, 2w, all"),
    db: Session = Depends(get_db_session),
):
    """Compatibility endpoint for React frontend backed by persistent DB."""
    from datetime import timedelta
    sym = symbol.upper()
    stock_meta = next((s for s in NIFTY_50 if s["symbol"] == sym), None)
    if not stock_meta:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not found")

    deltas = {
        "24h": timedelta(hours=24),
        "48h": timedelta(hours=48),
        "72h": timedelta(hours=72),
        "1w": timedelta(weeks=1),
        "2w": timedelta(weeks=2),
    }

    q = db.query(NewsRecord)
    if timerange in deltas:
        cutoff = datetime.now(timezone.utc) - deltas[timerange]
        q = q.filter(NewsRecord.published_at >= cutoff)

    records = q.all()

    direct_items = []
    supply_items = []
    macro_items = []

    for r in records:
        item_dict = {
            "id": r.id,
            "title": r.title,
            "snippet": r.snippet or r.title,
            "url": r.canonical_url or r.original_url,
            "source": r.source_name,
            "source_type": r.source_type,
            "published_at": r.published_at.isoformat(),
            "category": "direct" if r.symbol == sym else ("supply_chain" if r.category in ("order_win", "capex_expansion") else "macro"),
            "why_it_matters": f"{r.category.replace('_', ' ').title()} - {r.source_name}",
        }
        if r.symbol == sym:
            direct_items.append(item_dict)
        elif r.sector == stock_meta.get("sector"):
            macro_items.append(item_dict)
        else:
            supply_items.append(item_dict)

    total = len(direct_items) + len(supply_items) + len(macro_items)

    return {
        "stock": stock_meta,
        "timerange": timerange,
        "categories": {
            "direct": direct_items,
            "supply_chain": supply_items,
            "macro": macro_items,
        },
        "total": total,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


# =========================================================================
# Data Export Endpoints for AI Modeling & Quantitative Research
# =========================================================================

@router.get("/api/v1/export")
@router.get("/api/export")
def export_records_for_ai(
    format: Literal["csv", "parquet"] = Query("csv", description="Export format ('csv' or 'parquet')"),
    limit: int = Query(500, ge=1, le=5000, description="Max rows to export (up to 5000)"),
    symbol: Optional[str] = Query(None, description="Filter by stock ticker symbol"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    category: Optional[str] = Query(None, description="Filter by category code"),
    source_name: Optional[str] = Query(None, description="Filter by source name"),
    source_type: Optional[str] = Query(None, description="Filter by source type"),
    query: Optional[str] = Query(None, description="Keyword search pattern"),
    from_date: Optional[datetime] = Query(None, description="Filter records published on or after"),
    to_date: Optional[datetime] = Query(None, description="Filter records published on or before"),
    sanitize_formulas: bool = Query(True, description="Prefix leading spreadsheet formula characters to prevent CSV injection (CWE-1236)"),
    db: Session = Depends(get_db_session),
):
    """
    Exports clean, structured financial intelligence records as CSV or Apache Parquet.
    Directly satisfies the VeritasAI requirement for downstream AI/ML training and quantitative data analysis.

    Security & Reliability:
    - Bounded: Strictly limited to max 5000 rows per request to protect backend memory.
    - Sanitized: CSV strings with leading formula triggers (=, +, -, @, \\t, \\r) are sanitized with a single-quote prefix.
    """
    search_q = SearchQuery(
        query=query,
        symbol=symbol,
        sector=sector,
        category=category,
        source_name=source_name,
        source_type=source_type,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
    )

    df = NewsRepository.to_dataframe(
        db,
        query=search_q,
        limit=limit,
        max_limit=5000,
        sanitize_formulas=sanitize_formulas if format == "csv" else False,
    )

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if format == "parquet":
        buf = io.BytesIO()
        df.to_parquet(buf, index=False, engine="pyarrow")
        content = buf.getvalue()
        filename = f"borsel_news_export_{timestamp_str}.parquet"
        return Response(
            content=content,
            media_type="application/vnd.apache.parquet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    else:
        csv_str = df.to_csv(index=False, encoding="utf-8-sig")
        filename = f"borsel_news_export_{timestamp_str}.csv"
        return Response(
            content=csv_str,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
