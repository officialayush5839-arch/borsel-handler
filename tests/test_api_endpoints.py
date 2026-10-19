"""
Integration tests for FastAPI endpoints.
"""
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy.pool import StaticPool
from borsel_handler.api.app import app
from borsel_handler.api.dependencies import get_db_session
from borsel_handler.storage.database import Base


# Setup in-memory test database override with StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db
client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "total_records_indexed" in data


def test_stocks_endpoint():
    resp = client.get("/api/v1/stocks")
    assert resp.status_code == 200
    stocks = resp.json()
    assert len(stocks) >= 50
    assert any(s["symbol"] == "RELIANCE" for s in stocks)


def test_record_ingestion_and_query():
    payload = {
        "title": "State Bank of India Reports 24% Net Profit Surge",
        "snippet": "Strong credit growth and declining NPAs bolster Q4 earnings.",
        "original_url": "https://economictimes.indiatimes.com/sbi-q4-results?utm_source=rss",
        "canonical_url": "https://economictimes.indiatimes.com/sbi-q4-results",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_name": "Economic Times",
        "source_type": "rss",
        "source_record_id": "sbi_q4_test_01",
        "company_name": "State Bank of India",
        "symbol": "SBIN",
        "sector": "Banking",
        "category": "earnings",
        "confidence_score": 95.0,
        "tags": ["financial results", "banking"],
    }

    # Ingest record
    resp = client.post("/api/v1/records", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "inserted"

    # Ingest duplicate
    dup_resp = client.post("/api/v1/records", json=payload)
    assert dup_resp.status_code == 200
    assert dup_resp.json()["status"] == "duplicate_skipped"

    # Query record by symbol
    q_resp = client.get("/api/v1/records?symbol=SBIN")
    assert q_resp.status_code == 200
    res_data = q_resp.json()
    assert res_data["total"] >= 1
    assert res_data["items"][0]["symbol"] == "SBIN"

    # Search keyword
    search_resp = client.get("/api/v1/records/search?q=Surge")
    assert search_resp.status_code == 200
    assert search_resp.json()["total"] >= 1


def test_react_frontend_compatibility_endpoints():
    # /api/stocks
    resp1 = client.get("/api/stocks")
    assert resp1.status_code == 200

    # /api/auth
    resp2 = client.post("/api/auth", json={"password": "any"})
    assert resp2.status_code == 200
    assert resp2.json()["ok"] is True

    # /api/news
    resp3 = client.get("/api/news?symbol=SBIN&timerange=48h")
    assert resp3.status_code == 200
    news_data = resp3.json()
    assert "stock" in news_data
    assert "categories" in news_data
    assert "direct" in news_data["categories"]


def test_validation_error_on_missing_required_fields():
    bad_payload = {
        "snippet": "Missing title and URL",
    }
    resp = client.post("/api/v1/records", json=bad_payload)
    assert resp.status_code == 422


def test_get_record_detail():
    # Insert a record first
    payload = {
        "title": "HDFC Life Declares Strategic Bancassurance Tie-Up",
        "snippet": "New partnership expands distribution across 1,000 branches.",
        "original_url": "https://economictimes.indiatimes.com/hdfc-life-tieup",
        "canonical_url": "https://economictimes.indiatimes.com/hdfc-life-tieup",
        "published_at": datetime.now(timezone.utc).isoformat(),
        "source_name": "Economic Times",
        "source_type": "rss",
        "source_record_id": "hdfc_life_001",
        "company_name": "HDFC Life Insurance",
        "symbol": "HDFCLIFE",
        "sector": "Insurance",
        "category": "order_win",
        "confidence_score": 90.0,
    }
    ing_resp = client.post("/api/v1/records", json=payload)
    assert ing_resp.status_code == 200
    rec_id = ing_resp.json()["id"]

    # Fetch detail
    detail_resp = client.get(f"/api/v1/records/{rec_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == rec_id
    assert detail_data["symbol"] == "HDFCLIFE"

    # 404 test
    not_found_resp = client.get("/api/v1/records/999999")
    assert not_found_resp.status_code == 404


def test_platform_stats_and_sources_api():
    # Stats endpoint
    stats_resp = client.get("/api/v1/stats")
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert "total_articles" in stats_data
    assert "total_duplicates_prevented" in stats_data
    assert "category_distribution" in stats_data

    # Sources endpoint
    sources_resp = client.get("/api/v1/sources")
    assert sources_resp.status_code == 200
    sources_data = sources_resp.json()
    assert len(sources_data) >= 5
    assert any("Reserve Bank of India" in s["source_name"] for s in sources_data)

    # Companies endpoint
    comp_resp = client.get("/api/v1/companies?q=TCS")
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()
    assert len(comp_data) >= 1
    assert comp_data[0]["symbol"] == "TCS"


def test_trigger_ingestion_security_and_auth(monkeypatch):
    """Verifies that trigger endpoint requires valid X-API-Key when API_SECRET_KEY is configured."""
    from borsel_handler.config import settings

    # 1. When secret key is set, unauthorized requests must receive 401
    monkeypatch.setattr(settings, "API_SECRET_KEY", "prod_admin_secret_99")

    unauthed_resp = client.post("/api/v1/ingest/trigger?lookback_hours=12")
    assert unauthed_resp.status_code == 401
    assert "Unauthorized" in unauthed_resp.json()["detail"]

    bad_key_resp = client.post(
        "/api/v1/ingest/trigger?lookback_hours=12",
        headers={"X-API-Key": "wrong_key"}
    )
    assert bad_key_resp.status_code == 401

    # 2. When valid X-API-Key is provided, request succeeds with 200
    authed_resp = client.post(
        "/api/v1/ingest/trigger?lookback_hours=12",
        headers={"X-API-Key": "prod_admin_secret_99"}
    )
    assert authed_resp.status_code == 200
    assert authed_resp.json()["status"] == "collection_initiated"

    # 3. When API_SECRET_KEY is empty (dev mode), request succeeds without key
    monkeypatch.setattr(settings, "API_SECRET_KEY", "")
    dev_resp = client.post("/api/v1/ingest/trigger?lookback_hours=12")
    assert dev_resp.status_code == 200


def test_pandas_export_endpoint():
    """Verifies that the /api/v1/records/export endpoint returns valid CSV generated by Pandas."""
    resp = client.get("/api/v1/records/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    csv_text = resp.text
    assert "id,title,snippet,published_at,source_name" in csv_text


