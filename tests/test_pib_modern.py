"""
Unit and Integration Tests for Modernized PIB Collector
Verifies HTML release extraction, economic discrimination, deduplication, and resilience.
"""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borsel_handler.collectors.pib import PIBCollector, is_economic_content
from borsel_handler.storage.database import Base
from borsel_handler.storage.repository import NewsRepository

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "pib_releases.html"


@pytest.fixture
def pib_html_content():
    return FIXTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_is_economic_content_discrimination():
    # Economic ministries should pass
    assert is_economic_content("Meeting held", "Ministry of Finance") is True
    assert is_economic_content("Approvals granted", "Cabinet Committee on Economic Affairs (CCEA)") is True
    assert is_economic_content("Trade report", "Ministry of Commerce & Industry") is True

    # Keyword match from non-economic ministry should pass
    assert is_economic_content("New PLI incentive scheme announced", "Ministry of Electronics") is True
    assert is_economic_content("Budget allocation for highway projects", "Ministry of Road Transport") is True

    # Non-economic content from non-economic ministry should be filtered
    assert is_economic_content("Cultural festival organized in New Delhi", "Ministry of Culture") is False
    assert is_economic_content("Annual sports day held", "Ministry of Youth Affairs") is False


def test_parse_html_releases_from_fixture(pib_html_content):
    collector = PIBCollector()
    records = collector.parse_html_releases(pib_html_content)

    # 5 economic releases from Finance, CCEA, Commerce should be extracted; Culture should be filtered
    assert len(records) == 5

    # Check Ministry of Finance record
    rec_tax = next(r for r in records if "Transfer Pricing" in r.title)
    assert rec_tax.source_record_id == "PIB_2325126"
    assert "PressReleseDetail.aspx?PRID=2325126" in rec_tax.canonical_url
    assert rec_tax.category == "government_policy"
    assert rec_tax.source_name == "Press Information Bureau Economic Policy"
    assert rec_tax.source_type == "government_policy"
    assert "ministry_of_finance" in rec_tax.tags

    # Check CCEA PLI scheme record
    rec_pli = next(r for r in records if "PLI" in r.title)
    assert rec_pli.source_record_id == "PIB_2324900"
    assert rec_pli.category == "government_policy"

    # Verify that the culture festival release was NOT included
    assert not any("Cultural festival" in r.title for r in records)


@pytest.mark.asyncio
async def test_pib_fetch_resilience_http_errors():
    collector = PIBCollector(html_url="https://test.pib.gov/404", feeds=[])

    # Mock 404 response
    mock_resp_404 = httpx.Response(status_code=404, request=httpx.Request("GET", "https://test.pib.gov/404"))
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp_404)):
        records = await collector.fetch()
        assert records == []

    # Mock timeout exception
    with patch("httpx.AsyncClient.get", side_effect=httpx.TimeoutException("PIB connection timeout")):
        records = await collector.fetch()
        assert records == []


def test_pib_database_persistence_and_deduplication(pib_html_content, in_memory_db):
    collector = PIBCollector()
    records = collector.parse_html_releases(pib_html_content)

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
