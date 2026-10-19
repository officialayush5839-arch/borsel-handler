"""
SQLAlchemy ORM Models for Borsel Handler Platform
Implements complete normalized relational schema satisfying Section 8 of Mega Prompt 2:
- sources
- articles / news_records
- source_records
- companies
- article_companies
- categories
- article_categories
- collection_runs / collection_logs
- article_duplicates
Fully dialect-agnostic: operates seamlessly on PostgreSQL and SQLite.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, JSON, Boolean,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from borsel_handler.storage.database import Base


def utc_now() -> datetime:
    """Current UTC datetime factory."""
    return datetime.now(timezone.utc)


class Source(Base):
    """
    Registry of all monitored data sources and their operational parameters.
    """
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    source_type = Column(String(64), index=True, nullable=False)
    base_url = Column(String(1024), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    rate_limit_rps = Column(Float, default=2.0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class Company(Base):
    """
    Curated reference database of Indian listed companies.
    """
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String(32), unique=True, index=True, nullable=False)
    name = Column(String(256), nullable=False)
    isin = Column(String(32), unique=True, index=True, nullable=True)
    bse_code = Column(String(32), index=True, nullable=True)
    sector = Column(String(128), index=True, nullable=True)
    industry = Column(String(128), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)


class Category(Base):
    """
    Financial event and regulatory classification taxonomy.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    parent_category = Column(String(64), nullable=True)


class NewsRecord(Base):
    """
    Persistent normalized financial news and corporate announcement entity.
    Also aliased as Article.
    Fulfills all requirements of Section 8:
    - Article ID
    - Title
    - Publication timestamp
    - Source name & Source type
    - Company, symbol, sector
    - Original URL & Canonical URL
    - Category & snippet
    - First-seen & last-seen timestamps
    - Validation status & Provenance
    - Raw metadata & tags
    """
    __tablename__ = "news_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_hash = Column(String(64), unique=True, index=True, nullable=False)
    canonical_url = Column(String(1024), index=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    source_name = Column(String(128), index=True, nullable=False)
    source_type = Column(String(64), index=True, nullable=False)
    source_record_id = Column(String(256), nullable=True)

    title = Column(String(1024), nullable=False)
    snippet = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), index=True, nullable=False)
    collected_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), default=utc_now, nullable=True)
    validation_status = Column(String(32), default="valid", nullable=False)

    company_name = Column(String(256), index=True, nullable=True)
    symbol = Column(String(32), index=True, nullable=True)
    sector = Column(String(128), index=True, nullable=True)
    category = Column(String(128), index=True, default="general_financial_news", nullable=False)
    confidence_score = Column(Float, default=1.0, nullable=False)

    tags = Column(JSON, default=list, nullable=False)
    raw_metadata = Column(JSON, default=dict, nullable=False)
    provenance = Column(JSON, default=dict, nullable=False)

    # Relational associations
    duplicates = relationship("ArticleDuplicate", back_populates="canonical_article", cascade="all, delete-orphan")
    raw_records = relationship("SourceRecord", back_populates="article", cascade="all, delete-orphan")
    companies = relationship("ArticleCompany", back_populates="article", cascade="all, delete-orphan")
    categories = relationship("ArticleCategory", back_populates="article", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("source_name", "source_record_id", name="uq_source_record_id"),
        Index("idx_pub_sym", "symbol", "published_at"),
        Index("idx_cat_pub", "category", "published_at"),
        Index("idx_src_pub", "source_name", "published_at"),
    )


# Entity alias for Article
Article = NewsRecord


class ArticleDuplicate(Base):
    """
    Preserves relationship and provenance evidence for duplicate items.
    """
    __tablename__ = "article_duplicates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    canonical_article_id = Column(Integer, ForeignKey("news_records.id", ondelete="CASCADE"), nullable=True, index=True)
    duplicate_url = Column(String(2048), nullable=False)
    duplicate_title = Column(String(1024), nullable=False)
    duplicate_source = Column(String(128), nullable=False)
    duplicate_hash = Column(String(64), index=True, nullable=False)
    detection_stage = Column(String(64), nullable=False)  # exact_source_id, canonical_url, record_hash, normalized_title, title_window, fuzzy_jaccard
    detected_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    canonical_article = relationship("NewsRecord", back_populates="duplicates")


class SourceRecord(Base):
    """
    Raw payload staging table for auditing and non-destructive reprocessing.
    """
    __tablename__ = "source_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("news_records.id", ondelete="SET NULL"), nullable=True, index=True)
    source_name = Column(String(128), index=True, nullable=False)
    source_record_id = Column(String(256), nullable=True)
    raw_payload = Column(JSON, nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    processed_status = Column(String(32), default="processed", nullable=False)

    article = relationship("NewsRecord", back_populates="raw_records")


class ArticleCompany(Base):
    """
    Many-to-many relationship supporting multiple companies per article.
    """
    __tablename__ = "article_companies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("news_records.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True)
    symbol = Column(String(32), index=True, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    extraction_method = Column(String(64), default="regex_boundary", nullable=False)

    article = relationship("NewsRecord", back_populates="companies")
    company = relationship("Company")


class ArticleCategory(Base):
    """
    Many-to-many relationship supporting multi-category taxonomy tagging.
    """
    __tablename__ = "article_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("news_records.id", ondelete="CASCADE"), nullable=False, index=True)
    category_code = Column(String(64), index=True, nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)

    article = relationship("NewsRecord", back_populates="categories")


class CollectionLog(Base):
    """
    Ingestion audit log tracking source health, volume, and errors.
    Also aliased as CollectionRun.
    """
    __tablename__ = "collection_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_name = Column(String(128), index=True, nullable=False)
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), default="running", nullable=False)  # running, success, failed, partial
    items_found = Column(Integer, default=0, nullable=False)
    items_inserted = Column(Integer, default=0, nullable=False)
    items_duplicate = Column(Integer, default=0, nullable=False)
    items_failed = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)


# Entity alias for CollectionRun
CollectionRun = CollectionLog
