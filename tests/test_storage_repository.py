"""
Integration tests for database persistence and repository queries.
"""
from datetime import datetime, timezone, timedelta
from borsel_handler.core.models import SearchQuery
from borsel_handler.storage.models import NewsRecord, CollectionLog
from borsel_handler.storage.repository import NewsRepository


def test_insert_and_retrieve_record(in_memory_db, sample_record):
    entity, inserted, reason = NewsRepository.insert_record(in_memory_db, sample_record)
    assert inserted is True
    assert entity.id is not None
    assert entity.symbol == "TCS"
    assert entity.category == "earnings"

    # Query directly from DB
    retrieved = in_memory_db.query(NewsRecord).filter(NewsRecord.id == entity.id).first()
    assert retrieved is not None
    assert retrieved.title == sample_record.title
    assert retrieved.record_hash is not None


def test_search_filtering(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    rec2 = sample_record.model_copy(
        update={
            "source_record_id": "infy_order_01",
            "title": "Infosys Secures Major AI Contract in Europe",
            "original_url": "https://economictimes.indiatimes.com/infy-ai-contract",
            "canonical_url": "https://economictimes.indiatimes.com/infy-ai-contract",
            "symbol": "INFY",
            "company_name": "Infosys",
            "category": "order_win",
            "published_at": sample_record.published_at - timedelta(days=1),
        }
    )
    NewsRepository.insert_record(in_memory_db, rec2)

    # Filter by symbol
    items, total = NewsRepository.search_records(in_memory_db, SearchQuery(symbol="INFY"))
    assert total == 1
    assert items[0].symbol == "INFY"

    # Filter by category
    items, total = NewsRepository.search_records(in_memory_db, SearchQuery(category="earnings"))
    assert total == 1
    assert items[0].symbol == "TCS"

    # Keyword search across title
    items, total = NewsRepository.search_records(in_memory_db, SearchQuery(query="Contract"))
    assert total == 1
    assert items[0].symbol == "INFY"


def test_pagination(in_memory_db, sample_record):
    for i in range(15):
        rec = sample_record.model_copy(
            update={
                "source_record_id": f"rec_{i}",
                "title": f"Financial Event Headline {i}",
                "canonical_url": f"https://example.com/article/{i}",
                "published_at": sample_record.published_at - timedelta(hours=i),
            }
        )
        NewsRepository.insert_record(in_memory_db, rec)

    # Page 1, size 10
    items, total = NewsRepository.search_records(in_memory_db, SearchQuery(page=1, page_size=10))
    assert total == 15
    assert len(items) == 10

    # Page 2, size 10
    items_p2, total_p2 = NewsRepository.search_records(in_memory_db, SearchQuery(page=2, page_size=10))
    assert total_p2 == 15
    assert len(items_p2) == 5


def test_collection_log_lifecycle(in_memory_db):
    log = NewsRepository.start_log(in_memory_db, "Test Exchange Source")
    assert log.id is not None
    assert log.status == "running"

    NewsRepository.finish_log(
        in_memory_db,
        log_id=log.id,
        status="success",
        found=50,
        inserted=45,
        duplicates=5,
    )

    updated = in_memory_db.query(CollectionLog).filter(CollectionLog.id == log.id).first()
    assert updated.status == "success"
    assert updated.items_found == 50
    assert updated.items_inserted == 45
    assert updated.items_duplicate == 5
    assert updated.finished_at is not None


def test_get_record_by_id_and_relational_entities(in_memory_db, sample_record):
    from borsel_handler.storage.models import SourceRecord, ArticleCompany, ArticleCategory

    entity, inserted, _ = NewsRepository.insert_record(in_memory_db, sample_record)
    assert inserted is True

    record = NewsRepository.get_record_by_id(in_memory_db, entity.id)
    assert record is not None
    assert record.title == sample_record.title
    assert record.symbol == "TCS"

    # Verify relational entities were populated
    src_recs = in_memory_db.query(SourceRecord).filter(SourceRecord.article_id == entity.id).all()
    assert len(src_recs) == 1
    assert src_recs[0].source_name == sample_record.source_name

    companies = in_memory_db.query(ArticleCompany).filter(ArticleCompany.article_id == entity.id).all()
    assert len(companies) == 1
    assert companies[0].symbol == "TCS"

    categories = in_memory_db.query(ArticleCategory).filter(ArticleCategory.article_id == entity.id).all()
    assert len(categories) == 1
    assert categories[0].category_code == sample_record.category


def test_get_stats_and_sources_status(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    stats = NewsRepository.get_stats(in_memory_db)
    assert stats["total_articles"] == 1
    assert "category_distribution" in stats
    assert "source_distribution" in stats

    sources = NewsRepository.get_sources_status(in_memory_db)
    assert len(sources) >= 5
    assert any("BSE" in s["source_name"] for s in sources)

