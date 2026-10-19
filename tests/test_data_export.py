"""
Unit & Integration tests for Bounded DataFrame, CSV, and Parquet Export (Task B).
Tests bounds enforcement, spreadsheet formula sanitization (CWE-1236), and format serialization.
"""

import io
from datetime import datetime, timezone
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from borsel_handler.api.app import app
from borsel_handler.api.dependencies import get_db_session
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.storage.models import Base, NewsRecord
from borsel_handler.storage.repository import NewsRepository


@pytest.fixture
def test_db_session():
    """In-memory SQLite database with StaticPool for deterministic multi-threaded tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Populate sample records with benign and formula injection test strings
    records = [
        NormalizedNewsRecord(
            title="=HYPERLINK(\"http://malicious.com\", \"Click Here\")",
            snippet="+12345 malicious formula injection snippet",
            original_url="https://example.com/item1",
            canonical_url="https://example.com/item1",
            published_at=datetime(2026, 10, 19, 10, 0, tzinfo=timezone.utc),
            source_name="@EvilCorp News",
            source_type="rss",
            source_record_id="rec-1",
            company_name="-Risky Holdings",
            symbol="TCS",
            sector="Information Technology",
            category="earnings",
            confidence_score=95.0,
        ),
        NormalizedNewsRecord(
            title="Tata Motors Q2 Net Profit Surges 35% YoY",
            snippet="Tata Motors reported quarterly consolidated net profit growth.",
            original_url="https://example.com/item2",
            canonical_url="https://example.com/item2",
            published_at=datetime(2026, 10, 19, 11, 0, tzinfo=timezone.utc),
            source_name="Economic Times",
            source_type="rss",
            source_record_id="rec-2",
            company_name="Tata Motors Ltd",
            symbol="TATAMOTORS",
            sector="Automotive",
            category="earnings",
            confidence_score=90.0,
        ),
        NormalizedNewsRecord(
            title="RBI Holds Repo Rate Unchanged at 6.50%",
            snippet="The Monetary Policy Committee decided to maintain stance.",
            original_url="https://example.com/item3",
            canonical_url="https://example.com/item3",
            published_at=datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc),
            source_name="Reserve Bank of India",
            source_type="rbi_circular",
            source_record_id="rec-3",
            company_name=None,
            symbol=None,
            sector="Central Banking",
            category="rbi_circular",
            confidence_score=98.0,
        ),
    ]

    for rec in records:
        NewsRepository.insert_record(session, rec)

    yield session
    session.close()


def test_to_dataframe_bounds(test_db_session):
    """Verifies that to_dataframe enforces limits and caps."""
    # Test bounded limit
    df = NewsRepository.to_dataframe(test_db_session, limit=2)
    assert len(df) == 2
    assert isinstance(df, pd.DataFrame)
    assert "title" in df.columns
    assert "symbol" in df.columns

    # Test ceiling capping
    df_all = NewsRepository.to_dataframe(test_db_session, limit=999999, max_limit=5000)
    assert len(df_all) == 3


def test_to_dataframe_formula_sanitization(test_db_session):
    """Verifies CWE-1236 spreadsheet formula injection protection."""
    # Without sanitization (pure analysis / NLP)
    raw_df = NewsRepository.to_dataframe(test_db_session, sanitize_formulas=False)
    rec1_raw = raw_df[raw_df["symbol"] == "TCS"].iloc[0]
    assert rec1_raw["title"].startswith("=")
    assert rec1_raw["snippet"].startswith("+")
    assert rec1_raw["source_name"].startswith("@")
    assert rec1_raw["company_name"].startswith("-")

    # With sanitization (spreadsheet exports)
    clean_df = NewsRepository.to_dataframe(test_db_session, sanitize_formulas=True)
    rec1_clean = clean_df[clean_df["symbol"] == "TCS"].iloc[0]
    assert rec1_clean["title"].startswith("'=")
    assert rec1_clean["snippet"].startswith("'+")
    assert rec1_clean["source_name"].startswith("'@")
    assert rec1_clean["company_name"].startswith("'-")

    # Benign record should remain unsanitized
    rec2_clean = clean_df[clean_df["symbol"] == "TATAMOTORS"].iloc[0]
    assert rec2_clean["title"] == "Tata Motors Q2 Net Profit Surges 35% YoY"

    # Database records must remain canonical and unaltered
    db_rec1 = test_db_session.query(NewsRecord).filter(NewsRecord.source_record_id == "rec-1").first()
    assert db_rec1.title.startswith("=")
    assert not db_rec1.title.startswith("'=")


def test_api_export_csv(test_db_session):
    """Verifies GET /api/v1/export with format=csv."""
    app.dependency_overrides[get_db_session] = lambda: test_db_session
    client = TestClient(app)

    try:
        resp = client.get("/api/v1/export?format=csv&limit=10")
        assert resp.status_code == 200
        assert "text/csv" in resp.headers["content-type"]
        assert 'attachment; filename="borsel_news_export_' in resp.headers["content-disposition"]
        assert resp.headers["content-disposition"].endswith('.csv"')

        # Parse CSV text
        csv_text = resp.text
        assert "id,title,snippet,published_at" in csv_text
        # Verify formula characters are escaped with leading quote
        assert "'=" in csv_text
    finally:
        app.dependency_overrides.clear()


def test_api_export_parquet(test_db_session):
    """Verifies GET /api/v1/export with format=parquet using PyArrow."""
    app.dependency_overrides[get_db_session] = lambda: test_db_session
    client = TestClient(app)

    try:
        resp = client.get("/api/v1/export?format=parquet&limit=10")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/vnd.apache.parquet"
        assert 'attachment; filename="borsel_news_export_' in resp.headers["content-disposition"]
        assert resp.headers["content-disposition"].endswith('.parquet"')

        # Verify Parquet binary can be loaded into Pandas
        parquet_bytes = io.BytesIO(resp.content)
        loaded_df = pd.read_parquet(parquet_bytes)
        assert len(loaded_df) == 3
        assert "title" in loaded_df.columns
        assert "TATAMOTORS" in loaded_df["symbol"].values
    finally:
        app.dependency_overrides.clear()


def test_api_export_validation_bounds(test_db_session):
    """Verifies that invalid export limits (> 5000 or < 1) are rejected."""
    app.dependency_overrides[get_db_session] = lambda: test_db_session
    client = TestClient(app)

    try:
        resp_too_high = client.get("/api/v1/export?limit=6000")
        assert resp_too_high.status_code == 422

        resp_too_low = client.get("/api/v1/export?limit=0")
        assert resp_too_low.status_code == 422
    finally:
        app.dependency_overrides.clear()
