"""
End-to-End Pipeline and Robustness Tests for Borsel Handler
"""
import pytest
from datetime import datetime, timezone, timedelta

from borsel_handler.core.models import NormalizedNewsRecord, SearchQuery
from borsel_handler.storage.database import Base, init_db, engine
from borsel_handler.storage.models import (
    NewsRecord, ArticleDuplicate, SourceRecord,
    ArticleCompany, ArticleCategory
)
from borsel_handler.storage.repository import NewsRepository
from borsel_handler.collectors.bse import BSEAnnouncementCollector
from borsel_handler.collectors.nse import NSEAnnouncementCollector
from borsel_handler.scheduler.runner import CollectionRunner
from borsel_handler.collectors.base import BaseCollector


class MockStaticBatchCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Mock Static Batch Source"

    @property
    def source_type(self) -> str:
        return "mock_batch"

    async def fetch(self, cutoff=None):
        return [
            NormalizedNewsRecord(
                title="Titan Company Q4 Revenue Jumps 17%",
                snippet="Consumer demand across jewelry and watches drove revenue growth.",
                original_url="https://economictimes.indiatimes.com/titan-q4?utm_source=feed",
                canonical_url="https://economictimes.indiatimes.com/titan-q4",
                published_at=datetime(2026, 4, 18, 14, 0, 0, tzinfo=timezone.utc),
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id="titan_q4_001",
                symbol="TITAN",
                company_name="Titan Company Ltd",
                sector="Consumer",
                category="earnings",
            ),
            NormalizedNewsRecord(
                title="Maruti Suzuki Announces Capacity Expansion of 100,000 Units",
                snippet="Board approved brownfield capacity expansion at Kharkhoda plant.",
                original_url="https://economictimes.indiatimes.com/maruti-expansion",
                canonical_url="https://economictimes.indiatimes.com/maruti-expansion",
                published_at=datetime(2026, 4, 18, 15, 30, 0, tzinfo=timezone.utc),
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id="maruti_capex_001",
                symbol="MARUTI",
                company_name="Maruti Suzuki India Ltd",
                sector="Automobile",
                category="capex_expansion",
            ),
        ]


@pytest.mark.asyncio
async def test_repeated_collection_runs_idempotency(in_memory_db):
    """Verifies that consecutive ingestion runs do not create duplicate records."""
    runner = CollectionRunner(collectors=[MockStaticBatchCollector()])

    # Run 1: Should insert 2 new records
    run1 = await runner.run_collector(runner.collectors[0], in_memory_db)
    assert run1.items_found == 2
    assert run1.items_inserted == 2
    assert run1.items_duplicate == 0
    assert in_memory_db.query(NewsRecord).count() == 2

    # Run 2: Exact same source batch; should insert 0, skip 2 as duplicates
    run2 = await runner.run_collector(runner.collectors[0], in_memory_db)
    assert run2.items_found == 2
    assert run2.items_inserted == 0
    assert run2.items_duplicate == 2
    assert in_memory_db.query(NewsRecord).count() == 2

    # Verify duplicates were preserved in article_duplicates table
    dups = in_memory_db.query(ArticleDuplicate).all()
    assert len(dups) == 2


@pytest.mark.asyncio
async def test_multi_source_end_to_end_flow(in_memory_db):
    """Verifies end-to-end ingestion across regulatory and news sources with dedup and stats."""
    # 1. Ingest distinct sources
    rbi_rec = NormalizedNewsRecord(
        title="RBI Monetary Policy Committee Leaves Repo Rate Unchanged at 6.50%",
        snippet="Governor announced decision following three-day MPC meeting.",
        original_url="https://rbi.org.in/press/repo-rate-decision",
        canonical_url="https://rbi.org.in/press/repo-rate-decision",
        published_at=datetime(2026, 4, 15, 10, 0, 0, tzinfo=timezone.utc),
        source_name="Reserve Bank of India",
        source_type="rbi_circular",
        source_record_id="rbi_pr_001",
        category="rbi_update",
        confidence_score=95.0,
    )
    pib_rec = NormalizedNewsRecord(
        title="Ministry of Finance Notifies Revised Export Import Tariff Guidelines",
        snippet="Notification issued under Foreign Trade Policy 2026.",
        original_url="https://pib.gov.in/mof-tariff-notice",
        canonical_url="https://pib.gov.in/mof-tariff-notice",
        published_at=datetime(2026, 4, 15, 12, 0, 0, tzinfo=timezone.utc),
        source_name="Press Information Bureau Economic Policy",
        source_type="government_policy",
        source_record_id="pib_mof_001",
        category="government_policy",
        confidence_score=90.0,
    )

    _, ins1, _ = NewsRepository.insert_record(in_memory_db, rbi_rec)
    _, ins2, _ = NewsRepository.insert_record(in_memory_db, pib_rec)
    assert ins1 is True
    assert ins2 is True

    # 2. Check stats
    stats = NewsRepository.get_stats(in_memory_db)
    assert stats["total_articles"] == 2
    assert stats["category_distribution"].get("rbi_update") == 1
    assert stats["category_distribution"].get("government_policy") == 1

    # 3. Check search
    items, total = NewsRepository.search_records(in_memory_db, SearchQuery(query="Repo Rate"))
    assert total == 1
    assert items[0].source_name == "Reserve Bank of India"


def test_malformed_and_invalid_date_normalization():
    """Verifies that unparseable or ambiguous dates fall back cleanly to UTC without crashing."""
    bse = BSEAnnouncementCollector()
    nse = NSEAnnouncementCollector()

    # Invalid / empty string handling
    dt1 = bse._parse_ann_date("invalid_garbage_timestamp")
    assert isinstance(dt1, datetime)
    assert dt1.tzinfo == timezone.utc

    dt2 = nse._parse_nse_date("")
    assert isinstance(dt2, datetime)
    assert dt2.tzinfo == timezone.utc

    # Valid string parsing
    dt3 = nse._parse_nse_date("15-Apr-2026 17:05:00")
    assert dt3.year == 2026
    assert dt3.month == 4
    assert dt3.day == 15
    assert dt3.tzinfo == timezone.utc


def test_clean_database_initialization():
    """Verifies that init_db executes cleanly and creates all tables."""
    init_db()
    table_names = list(Base.metadata.tables.keys())
    assert "news_records" in table_names
    assert "collection_logs" in table_names
    assert "sources" in table_names
    assert "companies" in table_names
    assert "categories" in table_names
    assert "article_duplicates" in table_names
    assert "source_records" in table_names
    assert "article_companies" in table_names
    assert "article_categories" in table_names


@pytest.mark.asyncio
async def test_end_to_end_html_to_export_pipeline(in_memory_db):
    """
    Verifies full lifecycle across new remaining gap implementations:
    Raw HTML Snippet -> clean_html_to_text -> Entity Resolution -> Classification
    -> Deduplication -> DB Persistence -> Bounded AI DataFrame / Parquet / CSV Export.
    """
    from borsel_handler.core.html_utils import clean_html_to_text
    from borsel_handler.data.resolver import CompanyResolver
    from borsel_handler.classification.classifier import classify_event
    import io
    import pandas as pd

    raw_html_title = "<h3>L&amp;T Bags Mega Order worth &#8377;2,500 Crore</h3>"
    raw_html_snippet = "<p>Larsen &amp; Toubro construction division secures order for major infrastructure project.<script>alert('xss');</script></p>"

    # 1. HTML Cleaning
    clean_title = clean_html_to_text(raw_html_title)
    clean_snippet = clean_html_to_text(raw_html_snippet)
    assert clean_title == "L&T Bags Mega Order worth ₹2,500 Crore"
    assert clean_snippet == "Larsen & Toubro construction division secures order for major infrastructure project."
    assert "alert" not in clean_snippet

    # 2. Entity Resolution
    resolved = CompanyResolver.resolve(f"{clean_title} {clean_snippet}")
    assert len(resolved) > 0
    assert resolved[0].symbol == "LT"

    # 3. Classification
    category, confidence, tags = classify_event(clean_title, clean_snippet)
    assert category == "order_win"

    # 4. Normalized Record Creation
    record = NormalizedNewsRecord(
        title=clean_title,
        snippet=clean_snippet,
        original_url="https://business-standard.com/order-win-101",
        canonical_url="https://business-standard.com/order-win-101",
        published_at=datetime.now(timezone.utc),
        source_name="Business Standard Co",
        source_type="rss",
        source_record_id="bs_order_101",
        symbol=resolved[0].symbol,
        company_name=resolved[0].name,
        sector=resolved[0].sector,
        category=category,
        confidence_score=confidence,
    )

    # 5. Ingestion & Persistence
    entity, inserted, reason = NewsRepository.insert_record(in_memory_db, record)
    assert inserted is True
    assert entity.id is not None

    # 6. Idempotency test
    entity2, inserted2, reason2 = NewsRepository.insert_record(in_memory_db, record)
    assert inserted2 is False
    assert reason2 in ("tier_1_source_id_match", "exact_hash_match")

    # 7. Bounded DataFrame & Export
    df = NewsRepository.to_dataframe(in_memory_db, limit=10, sanitize_formulas=True)
    assert len(df) == 1
    assert df.iloc[0]["symbol"] == "LT"
    assert "₹2,500" in df.iloc[0]["title"]

    # Verify Parquet serialization
    buf = io.BytesIO()
    df.to_parquet(buf, index=False, engine="pyarrow")
    buf.seek(0)
    roundtrip = pd.read_parquet(buf)
    assert len(roundtrip) == 1
    assert roundtrip.iloc[0]["title"] == clean_title
