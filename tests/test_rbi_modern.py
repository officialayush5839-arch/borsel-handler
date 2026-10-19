"""
Unit and Integration Tests for Modernized RBI Collector
Verifies HTML archive parsing, dates, entity resolution, deduplication, and resilience.
"""
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borsel_handler.collectors.rbi import RBICollector, parse_rbi_date
from borsel_handler.storage.database import Base
from borsel_handler.storage.repository import NewsRepository

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "rbi_press_releases.html"


@pytest.fixture
def rbi_html_content():
    return FIXTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_parse_rbi_date():
    dt = parse_rbi_date("Oct 19, 2026")
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 19
    assert dt.tzinfo == timezone.utc

    # Fallback on empty or garbage
    dt_fallback = parse_rbi_date("")
    assert dt_fallback.tzinfo == timezone.utc


def test_parse_html_archive_from_fixture(rbi_html_content):
    collector = RBICollector()
    records = collector.parse_html_archive(rbi_html_content)

    assert len(records) == 5

    # Check first record
    rec1 = records[0]
    assert "Auction of Government of India Dated Securities" in rec1.title
    assert rec1.published_at.year == 2026
    assert rec1.published_at.month == 10
    assert rec1.published_at.day == 19
    assert rec1.source_record_id == "RBI_PR_63832"
    assert "BS_PressReleaseDisplay.aspx?prid=63832" in rec1.canonical_url
    assert rec1.category == "rbi_update"
    assert rec1.source_name == "Reserve Bank of India"
    assert rec1.source_type == "rbi_circular"

    # Check monetary policy record
    rec_policy = next(r for r in records if "Repo Rate" in r.title)
    assert rec_policy.source_record_id == "RBI_PR_63830"
    assert rec_policy.category in ("rbi_update", "macro_economic")

    # Check banking entity resolution
    rec_bank = next(r for r in records if "RBL Bank" in r.title)
    assert rec_bank.sector == "Banking & Financial Services"


def test_date_cutoff_filtering(rbi_html_content):
    collector = RBICollector()
    # Cutoff set to Oct 18, 2026 should exclude the two Oct 16 records
    cutoff = datetime(2026, 10, 18, tzinfo=timezone.utc)
    records = collector.parse_html_archive(rbi_html_content, cutoff=cutoff)

    assert len(records) == 3
    for r in records:
        assert r.published_at >= cutoff


def test_empty_and_malformed_html():
    collector = RBICollector()
    assert collector.parse_html_archive("") == []
    assert collector.parse_html_archive("<html><body><p>No table</p></body></html>") == []


@pytest.mark.asyncio
async def test_rbi_fetch_resilience_http_errors():
    collector = RBICollector(html_urls=["https://test.rbi.org/404"], feeds=[])

    # Mock 404 response
    mock_resp_404 = httpx.Response(status_code=404, request=httpx.Request("GET", "https://test.rbi.org/404"))
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp_404)):
        records = await collector.fetch()
        assert records == []

    # Mock timeout exception
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("Connection timed out")):
        records = await collector.fetch()
        assert records == []


def test_rbi_database_persistence_and_deduplication(rbi_html_content, in_memory_db):
    collector = RBICollector()
    records = collector.parse_html_archive(rbi_html_content)

    # First insertion batch
    inserted_count = 0
    for r in records:
        _, inserted, _ = NewsRepository.insert_record(in_memory_db, r)
        if inserted:
            inserted_count += 1

    assert inserted_count == 5

    # Second insertion batch (should all be skipped as duplicates)
    dup_count = 0
    for r in records:
        _, inserted, reason = NewsRepository.insert_record(in_memory_db, r)
        if not inserted:
            dup_count += 1
            assert "match" in reason or "tier" in reason

    assert dup_count == 5
