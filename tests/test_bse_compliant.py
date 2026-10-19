"""
Unit and Integration Tests for Compliant BSE Announcement Collector
Verifies JSON parsing, attachment URLs, access restriction short-circuiting (HTTP 403/429), and deduplication.
"""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borsel_handler.collectors.bse import BSEAnnouncementCollector, parse_bse_date
from borsel_handler.storage.database import Base
from borsel_handler.storage.repository import NewsRepository

SAMPLE_BSE_TABLE = [
    {
        "NEWSID": "BSE_ANN_001",
        "SCRIP_CD": 500209,
        "SLONGNAME": "Infosys Ltd",
        "HEADLINE": "Infosys announces strategic collaboration with global cloud provider",
        "NEWSSUB": "Infosys expands global presence through enterprise cloud alliance",
        "ATTACHMENTNAME": "infosys_announcement_001.pdf",
        "DissemDT": "2026-10-19T14:30:00",
        "CATEGORYNAME": "Company Update",
    },
    {
        "NEWSID": "BSE_ANN_002",
        "SCRIP_CD": 500209,
        "SLONGNAME": "Infosys Ltd",
        "HEADLINE": "Outcome of Board Meeting - Financial Results for Q2 FY27",
        "NEWSSUB": "Board approves unaudited financial results and declares interim dividend of Rs 20",
        "ATTACHMENTNAME": "https://www.bseindia.com/direct/financials.pdf",
        "DissemDT": "2026-10-18T16:00:00",
        "CATEGORYNAME": "Financial Results",
    },
]


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_parse_bse_date():
    dt = parse_bse_date("2026-10-19T14:30:00")
    assert dt.year == 2026
    assert dt.month == 10
    assert dt.day == 19
    assert dt.hour == 14
    assert dt.tzinfo == timezone.utc

    # Fallback
    assert parse_bse_date("").tzinfo == timezone.utc


def test_parse_announcement_table():
    collector = BSEAnnouncementCollector(symbols=["INFY"])
    records = collector.parse_announcement_table(SAMPLE_BSE_TABLE, symbol="INFY")

    assert len(records) == 2

    # Record 1
    rec1 = records[0]
    assert rec1.title == "Infosys announces strategic collaboration with global cloud provider"
    assert rec1.symbol == "INFY"
    assert rec1.source_record_id == "BSE_ANN_001"
    assert "https://www.bseindia.com/xml-data/corpfiling/AttachLive/infosys_announcement_001.pdf" == rec1.original_url
    assert rec1.source_name == "BSE Corporate Announcements"
    assert rec1.source_type == "bse_announcement"

    # Record 2 (Earnings / Dividend)
    rec2 = records[1]
    assert "Financial Results" in rec2.title
    assert rec2.category in ("earnings", "dividend")
    assert rec2.original_url == "https://www.bseindia.com/direct/financials.pdf"


def test_bse_attachment_url_fallback():
    table_no_attach = [{
        "NEWSID": "BSE_NO_ATT",
        "SCRIP_CD": 500209,
        "HEADLINE": "General Intimation",
        "ATTACHMENTNAME": "",
        "DissemDT": "2026-10-19T10:00:00",
    }]
    collector = BSEAnnouncementCollector(symbols=["INFY"])
    records = collector.parse_announcement_table(table_no_attach, symbol="INFY")
    assert len(records) == 1
    assert "ann.html?scrip=500209" in records[0].original_url


@pytest.mark.asyncio
async def test_bse_short_circuit_on_403_access_restricted():
    """
    Verifies ethical compliance: when BSE returns HTTP 403 Forbidden (Akamai WAF),
    the collector records the limitation and immediately halts without hammering all 50 symbols.
    """
    collector = BSEAnnouncementCollector(symbols=["INFY", "TCS", "RELIANCE", "SBIN"])

    mock_resp_403 = httpx.Response(
        status_code=403,
        content=b"<HTML><TITLE>Access Denied</TITLE></HTML>",
        request=httpx.Request("GET", "https://api.bseindia.com/probe"),
    )

    get_mock = AsyncMock(return_value=mock_resp_403)
    with patch("httpx.AsyncClient.get", new=get_mock):
        records = await collector.fetch()

        # Must return empty list gracefully
        assert records == []

        # Must record access restriction state
        assert collector.access_restricted is True
        assert collector.last_status_code == 403
        assert "Access Restricted" in collector.last_error

        # CRITICAL ETHICAL CHECK: Must only call get once for the probe, NOT 4 times!
        assert get_mock.call_count == 1

        health = collector.get_health_status()
        assert health["access_restricted"] is True
        assert health["last_status_code"] == 403


@pytest.mark.asyncio
async def test_bse_rate_limit_429_handling():
    """Verifies graceful handling of HTTP 429 Too Many Requests."""
    collector = BSEAnnouncementCollector(symbols=["INFY"])

    mock_resp_429 = httpx.Response(
        status_code=429,
        content=b"Too Many Requests",
        request=httpx.Request("GET", "https://api.bseindia.com/probe"),
    )

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp_429)):
        records = await collector.fetch()
        assert records == []
        assert collector.access_restricted is True
        assert collector.last_status_code == 429


def test_bse_database_persistence_and_deduplication(in_memory_db):
    collector = BSEAnnouncementCollector(symbols=["INFY"])
    records = collector.parse_announcement_table(SAMPLE_BSE_TABLE, symbol="INFY")

    # Initial insertion
    inserted = 0
    for r in records:
        _, ins, _ = NewsRepository.insert_record(in_memory_db, r)
        if ins:
            inserted += 1
    assert inserted == 2

    # Repeated insertion (idempotent duplicate prevention)
    dup = 0
    for r in records:
        _, ins, _ = NewsRepository.insert_record(in_memory_db, r)
        if not ins:
            dup += 1
    assert dup == 2
