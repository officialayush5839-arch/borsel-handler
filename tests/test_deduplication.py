"""
Unit tests for multi-tier deduplication engine.
"""
from datetime import datetime, timezone, timedelta
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.dedup.engine import DeduplicationEngine
from borsel_handler.storage.repository import NewsRepository


def test_tier_1_exact_source_id_dedup(in_memory_db, sample_record):
    # Insert first
    NewsRepository.insert_record(in_memory_db, sample_record)

    # Second record with identical source_record_id and source_name
    dup = sample_record.model_copy(
        update={
            "title": "TCS Q4 Profit Beats Estimates with 9% Growth",
            "canonical_url": "https://economictimes.indiatimes.com/different-url",
        }
    )
    is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(in_memory_db, dup)
    assert is_dup is True
    assert reason == "tier_1_source_id_match"


def test_tier_2_canonical_url_dedup(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    dup = sample_record.model_copy(
        update={
            "source_record_id": "totally_different_id_999",
            "title": "Different Headline Same URL",
            "original_url": "https://economictimes.indiatimes.com/tcs-q4-results?utm_medium=email",
            "canonical_url": "https://economictimes.indiatimes.com/tcs-q4-results",
        }
    )
    is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(in_memory_db, dup)
    assert is_dup is True
    assert reason == "tier_2_canonical_url_match"


def test_tier_3_record_hash_exact_title_match(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    dup = sample_record.model_copy(
        update={
            "source_record_id": "new_id_123",
            "original_url": "https://different-source.com/article1",
            "canonical_url": "https://different-source.com/article1",
            "source_name": "Different Publisher",
            "title": "TCS Q4 Net Profit Rises 9% to Rs 12,434 Crore",
            "published_at": sample_record.published_at + timedelta(minutes=15),
        }
    )
    is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(in_memory_db, dup)
    assert is_dup is True
    assert reason == "tier_3_record_hash_match"


def test_tier_4_cross_source_near_duplicate_match(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    # Syndicated article with nearly identical wording from another publisher
    syndicated = sample_record.model_copy(
        update={
            "source_record_id": "reuters_tcs_01",
            "original_url": "https://reuters.com/markets/tcs-q4-profit-up",
            "canonical_url": "https://reuters.com/markets/tcs-q4-profit-up",
            "source_name": "Reuters India",
            "title": "TCS Q4 net profit rises 9% to Rs 12,434 crore reported",
            "published_at": sample_record.published_at + timedelta(hours=2),
        }
    )
    is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(in_memory_db, syndicated)
    assert is_dup is True
    assert "tier_4_cross_source_similarity" in reason


def test_distinct_articles_discrimination(in_memory_db, sample_record):
    NewsRepository.insert_record(in_memory_db, sample_record)

    # Distinct article about a different event for TCS
    distinct_article = sample_record.model_copy(
        update={
            "source_record_id": "tcs_new_order_01",
            "original_url": "https://economictimes.indiatimes.com/tcs-bags-deal",
            "canonical_url": "https://economictimes.indiatimes.com/tcs-bags-deal",
            "title": "TCS Bags $1 Billion Strategic Contract From UK Life Insurance Giant",
            "published_at": sample_record.published_at + timedelta(hours=1),
        }
    )
    is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(in_memory_db, distinct_article)
    assert is_dup is False
    assert reason is None


def test_duplicate_relationship_persistence(in_memory_db, sample_record):
    from borsel_handler.storage.models import ArticleDuplicate

    entity, inserted, _ = NewsRepository.insert_record(in_memory_db, sample_record)
    assert inserted is True

    # Re-attempt insertion of identical record
    dup_entity, inserted_dup, reason = NewsRepository.insert_record(in_memory_db, sample_record)
    assert inserted_dup is False
    assert dup_entity is None

    # Verify duplicate record is logged to article_duplicates
    dups = in_memory_db.query(ArticleDuplicate).all()
    assert len(dups) == 1
    assert dups[0].canonical_article_id == entity.id
    assert dups[0].duplicate_url == sample_record.original_url
    assert dups[0].duplicate_source == sample_record.source_name


def test_distinct_companies_identical_generic_title(in_memory_db, sample_record):
    """
    Verifies Section 12 rule: 'Do not merge two different events merely because their titles are similar.'
    Two distinct companies filing 'Outcome of Board Meeting' must NOT be deduplicated.
    """
    rec_tcs = sample_record.model_copy(
        update={
            "source_record_id": "BSE_ANN_TCS_001",
            "title": "Outcome of Board Meeting",
            "snippet": "Board meeting concluded at 14:30 hrs",
            "original_url": "https://bseindia.com/filing_tcs_1",
            "canonical_url": "https://bseindia.com/filing_tcs_1",
            "symbol": "TCS",
            "company_name": "Tata Consultancy Services",
        }
    )
    rec_infy = sample_record.model_copy(
        update={
            "source_record_id": "BSE_ANN_INFY_002",
            "title": "Outcome of Board Meeting",
            "snippet": "Board meeting concluded at 16:00 hrs",
            "original_url": "https://bseindia.com/filing_infy_1",
            "canonical_url": "https://bseindia.com/filing_infy_1",
            "symbol": "INFY",
            "company_name": "Infosys Ltd",
        }
    )

    ent_tcs, ins_tcs, _ = NewsRepository.insert_record(in_memory_db, rec_tcs)
    assert ins_tcs is True
    assert ent_tcs is not None

    # INFY record with same generic title on same day must be inserted as a distinct record
    is_dup, reason, _ = DeduplicationEngine.check_duplicate(in_memory_db, rec_infy)
    assert is_dup is False, f"Expected distinct companies to not match as duplicates, got reason: {reason}"

    ent_infy, ins_infy, reason = NewsRepository.insert_record(in_memory_db, rec_infy)
    assert ins_infy is True
    assert ent_infy is not None
    assert ent_infy.id != ent_tcs.id

