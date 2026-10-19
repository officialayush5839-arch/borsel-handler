"""
Unit and Integration Tests for Company Directory Synchronization Engine
Verifies CSV parsing, BOM handling, transactional upsert, rollback, and resolver integration.
"""
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borsel_handler.data.sync import CompanyDirectorySync
from borsel_handler.data.resolver import CompanyResolver
from borsel_handler.storage.database import Base
from borsel_handler.storage.models import Company

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "equity_l_sample.csv"


@pytest.fixture
def sample_csv_text():
    return FIXTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_parse_csv_content_from_fixture(sample_csv_text):
    records, rejected = CompanyDirectorySync.parse_csv_content(sample_csv_text)

    assert len(records) == 10
    assert rejected == 0

    first = records[0]
    assert first["symbol"] == "20MICRONS"
    assert first["name"] == "20 Microns Limited"
    assert first["isin"] == "INE144J01027"

    tcs = next(r for r in records if r["symbol"] == "TCS")
    assert tcs["name"] == "Tata Consultancy Services Limited"
    assert tcs["isin"] == "INE467B01029"


def test_parse_csv_bom_and_whitespace():
    csv_with_bom = (
        "\ufeffSYMBOL , NAME OF COMPANY , ISIN NUMBER \n"
        "ABC , ABC Corp Limited , INE123456789 \n"
        "XYZ,XYZ Technologies Ltd,INE987654321\n"
    )
    records, rejected = CompanyDirectorySync.parse_csv_content(csv_with_bom)
    assert len(records) == 2
    assert rejected == 0
    assert records[0]["symbol"] == "ABC"
    assert records[0]["name"] == "ABC Corp Limited"
    assert records[0]["isin"] == "INE123456789"


def test_parse_csv_missing_required_columns():
    bad_csv = "COL1,COL2,COL3\n1,2,3\n"
    records, rejected = CompanyDirectorySync.parse_csv_content(bad_csv)
    assert records == []


def test_sync_to_database_idempotency_and_updates(sample_csv_text, in_memory_db):
    records, _ = CompanyDirectorySync.parse_csv_content(sample_csv_text)

    # Initial sync
    res1 = CompanyDirectorySync.sync_to_database(in_memory_db, records)
    assert res1["status"] == "success"
    assert res1["imported_count"] == 10
    assert res1["updated_count"] == 0

    total_companies = in_memory_db.query(Company).count()
    assert total_companies == 10

    # Repeat sync with exact same data
    res2 = CompanyDirectorySync.sync_to_database(in_memory_db, records)
    assert res2["status"] == "success"
    assert res2["imported_count"] == 0
    assert res2["updated_count"] == 0
    assert in_memory_db.query(Company).count() == 10

    # Repeat sync with updated company name
    updated_records = list(records)
    updated_records[0] = {
        "symbol": "20MICRONS",
        "name": "20 Microns Advanced Materials Ltd",
        "isin": "INE144J01027",
    }
    res3 = CompanyDirectorySync.sync_to_database(in_memory_db, updated_records)
    assert res3["status"] == "success"
    assert res3["imported_count"] == 0
    assert res3["updated_count"] == 1

    comp = in_memory_db.query(Company).filter(Company.symbol == "20MICRONS").first()
    assert comp.name == "20 Microns Advanced Materials Ltd"


def test_resolver_integration_with_synced_directory(sample_csv_text, in_memory_db):
    records, _ = CompanyDirectorySync.parse_csv_content(sample_csv_text)
    CompanyDirectorySync.sync_to_database(in_memory_db, records)

    # Load from DB into CompanyResolver registry
    CompanyResolver.load_from_db(in_memory_db)

    # Resolve a newly synced stock that was NOT in the initial NIFTY 50
    text = "20 Microns Limited announced a new minerals processing facility in Gujarat."
    resolved = CompanyResolver.resolve(text)

    assert any(r.symbol == "20MICRONS" for r in resolved)
    match_20m = next(r for r in resolved if r.symbol == "20MICRONS")
    assert match_20m.name == "20 Microns Limited"


def test_ambiguous_symbol_safeguard_remains_active():
    # 'IT' or 'ON' in lowercase should not resolve
    resolved_ambiguous = CompanyResolver.resolve("Information on the economic trends in it industry.")
    assert not any(r.symbol in ("IT", "ON", "IN") for r in resolved_ambiguous)


@pytest.mark.asyncio
async def test_live_sync_error_handling(in_memory_db):
    # Mock download failure
    mock_resp_500 = httpx.Response(status_code=500, request=httpx.Request("GET", "https://test.nse/csv"))
    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp_500)):
        res = await CompanyDirectorySync.sync_live(in_memory_db, url="https://test.nse/csv")
        assert res["status"] == "download_failed"
        assert res["imported_count"] == 0
