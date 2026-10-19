"""
Pytest Fixtures for Borsel Handler Test Suite
"""
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from borsel_handler.storage.database import Base
from borsel_handler.core.models import NormalizedNewsRecord


@pytest.fixture
def in_memory_db():
    """Provides an isolated in-memory SQLite database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_record():
    return NormalizedNewsRecord(
        title="TCS Q4 Net Profit Rises 9% to Rs 12,434 Crore",
        snippet="Tata Consultancy Services posted solid earnings beat.",
        original_url="https://economictimes.indiatimes.com/tcs-q4-results?utm_source=twitter",
        canonical_url="https://economictimes.indiatimes.com/tcs-q4-results",
        published_at=datetime(2026, 4, 15, 17, 0, 0, tzinfo=timezone.utc),
        source_name="Economic Times",
        source_type="rss",
        source_record_id="et_tcs_q4_01",
        company_name="Tata Consultancy Services",
        symbol="TCS",
        sector="IT",
        category="earnings",
        confidence_score=90.0,
        tags=["financial results", "q4 results"],
    )
