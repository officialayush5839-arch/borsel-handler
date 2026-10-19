"""
Unit tests for data collectors using local mock fixtures.
Guarantees deterministic execution without depending on live external networks.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import httpx

from borsel_handler.collectors.rss import RSSCollector
from borsel_handler.collectors.bse import BSEAnnouncementCollector
from borsel_handler.collectors.nse import NSEAnnouncementCollector
from borsel_handler.collectors.rbi import RBICollector
from borsel_handler.collectors.sebi import SEBICollector
from borsel_handler.collectors.pib import PIBCollector

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.mark.asyncio
async def test_rss_collector_with_fixture():
    rss_xml = (FIXTURES_DIR / "sample_rss.xml").read_text(encoding="utf-8")

    collector = RSSCollector(feeds=[("Economic Times Markets", "https://economictimes.indiatimes.com/rss")])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = rss_xml
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    # The fixture has 3 items:
    # 1: TCS Q4 earnings (trusted, valid)
    # 2: L&T order win (trusted, valid)
    # 3: Untrusted domain (scamstocksblog.xyz) -> Should be dropped!
    assert len(records) == 2

    r1 = next(r for r in records if "TCS" in r.title)
    assert r1.symbol == "TCS"
    assert r1.source_name == "Economic Times Markets"
    assert r1.category in ("earnings", "dividend")
    assert r1.published_at.tzinfo is not None

    r2 = next(r for r in records if "L&T" in r.title)
    assert r2.category == "order_win"


@pytest.mark.asyncio
async def test_bse_collector_with_fixture():
    bse_data = json.loads((FIXTURES_DIR / "sample_bse.json").read_text(encoding="utf-8"))

    collector = BSEAnnouncementCollector(symbols=["TCS", "LT"])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=bse_data)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    assert len(records) >= 2
    tcs_rec = next(r for r in records if r.symbol == "TCS")
    assert "tcs_financial_results_q4.pdf" in tcs_rec.canonical_url or "tcs_financial_results_q4.pdf" in tcs_rec.original_url
    assert tcs_rec.category in ("earnings", "dividend")


@pytest.mark.asyncio
async def test_nse_collector_with_fixture():
    nse_data = json.loads((FIXTURES_DIR / "sample_nse.json").read_text(encoding="utf-8"))

    collector = NSEAnnouncementCollector(index_tag="equities")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json = MagicMock(return_value=nse_data)

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    assert len(records) == 2
    symbols = {r.symbol for r in records}
    assert "TCS" in symbols
    assert "INFY" in symbols


@pytest.mark.asyncio
async def test_rbi_collector_with_fixture():
    rbi_xml = (FIXTURES_DIR / "sample_rbi.xml").read_text(encoding="utf-8")
    collector = RBICollector(feeds=[("RBI Press Releases", "https://www.rbi.org.in/rss/rss_pressrelease.xml")])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = rbi_xml

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    assert len(records) == 2
    assert records[0].source_name == "Reserve Bank of India"
    assert records[0].source_type == "rbi_circular"
    assert records[0].category in ("rbi_update", "macro_economic")
    assert "Repo Rate" in records[0].title
    assert records[0].published_at.tzinfo is not None

    # Second item mentions HDFC Bank
    r2 = records[1]
    assert r2.symbol == "HDFCBANK" or "HDFC" in (r2.company_name or "")


@pytest.mark.asyncio
async def test_sebi_collector_with_fixture():
    sebi_xml = (FIXTURES_DIR / "sample_sebi.xml").read_text(encoding="utf-8")
    collector = SEBICollector(feeds=[("SEBI Circulars", "https://www.sebi.gov.in/sebirss.xml")])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = sebi_xml

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    assert len(records) == 2
    assert records[0].source_name == "Securities and Exchange Board of India"
    assert records[0].source_type == "sebi_regulation"
    assert records[0].category in ("regulatory_sebi", "corporate_action")
    assert records[0].published_at.tzinfo is not None


@pytest.mark.asyncio
async def test_pib_collector_with_fixture():
    pib_xml = (FIXTURES_DIR / "sample_pib.xml").read_text(encoding="utf-8")
    collector = PIBCollector(feeds=[("PIB MoF", "https://pib.gov.in/RssMain.aspx?ModId=2&MinId=0")])

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = pib_xml

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        records = await collector.fetch()

    assert len(records) == 2
    assert records[0].source_name == "Press Information Bureau Economic Policy"
    assert records[0].source_type == "government_policy"
    assert records[0].category in ("government_policy", "macro_economic")
    assert "PLI Scheme" in records[0].title
    assert records[0].published_at.tzinfo is not None
