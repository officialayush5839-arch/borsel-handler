"""
Data Repository and Query Layer
Handles database persistence, deduplication gating, duplicate relationship tracking,
raw provenance staging, and structured queries.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import or_, desc, func
from sqlalchemy.orm import Session

from borsel_handler.core.models import NormalizedNewsRecord, SearchQuery
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.dedup.engine import DeduplicationEngine, compute_record_hash
from borsel_handler.data.stocks import NIFTY_50
from borsel_handler.storage.models import (
    NewsRecord,
    CollectionLog,
    ArticleDuplicate,
    SourceRecord,
    ArticleCompany,
    ArticleCategory,
)


class NewsRepository:
    """Handles database persistence, deduplication gating, and queries."""

    @staticmethod
    def insert_record(
        db: Session, record: NormalizedNewsRecord
    ) -> Tuple[Optional[NewsRecord], bool, Optional[str]]:
        """
        Inserts a normalized record if unique. If duplicate, records relationship in article_duplicates.
        Returns:
            (entity: Optional[NewsRecord], inserted: bool, skip_reason: Optional[str])
        """
        is_dup, reason, existing_id = DeduplicationEngine.check_duplicate(db, record)
        if is_dup:
            # Preserve duplicate provenance evidence in persistent storage
            try:
                dup_hash = compute_record_hash(record)
                dup_entry = ArticleDuplicate(
                    canonical_article_id=existing_id,
                    duplicate_url=record.original_url,
                    duplicate_title=record.title,
                    duplicate_source=record.source_name,
                    duplicate_hash=dup_hash,
                    detection_stage=reason or "unknown_stage",
                    detected_at=datetime.now(timezone.utc),
                )
                db.add(dup_entry)
                db.commit()
            except Exception:
                db.rollback()
            return None, False, reason

        canon_url = normalize_url(record.canonical_url or record.original_url)
        rec_hash = compute_record_hash(record)

        entity = NewsRecord(
            record_hash=rec_hash,
            canonical_url=canon_url,
            original_url=record.original_url,
            source_name=record.source_name,
            source_type=record.source_type,
            source_record_id=record.source_record_id,
            title=record.title,
            snippet=record.snippet,
            published_at=record.published_at,
            collected_at=record.collected_at,
            last_seen_at=datetime.now(timezone.utc),
            validation_status="valid",
            company_name=record.company_name,
            symbol=record.symbol,
            sector=record.sector,
            category=record.category,
            confidence_score=record.confidence_score,
            tags=record.tags,
            raw_metadata=record.raw_metadata,
            provenance={
                "source_name": record.source_name,
                "source_type": record.source_type,
                "original_url": record.original_url,
                "ingestion_utc": record.collected_at.isoformat(),
            },
        )

        try:
            db.add(entity)
            db.flush()

            # 1. Stage raw source record for compliance and audit
            src_record = SourceRecord(
                article_id=entity.id,
                source_name=record.source_name,
                source_record_id=record.source_record_id,
                raw_payload=record.raw_metadata or {},
                fetched_at=record.collected_at,
                processed_status="processed",
            )
            db.add(src_record)

            # 2. Add relational entity mappings
            if record.symbol:
                art_comp = ArticleCompany(
                    article_id=entity.id,
                    symbol=record.symbol,
                    confidence=record.confidence_score / 100.0 if record.confidence_score > 1.0 else record.confidence_score,
                    extraction_method="regex_boundary",
                )
                db.add(art_comp)

            if record.category:
                art_cat = ArticleCategory(
                    article_id=entity.id,
                    category_code=record.category,
                    confidence=record.confidence_score / 100.0 if record.confidence_score > 1.0 else record.confidence_score,
                )
                db.add(art_cat)

            db.commit()
            db.refresh(entity)
            return entity, True, None
        except Exception as exc:
            db.rollback()
            return None, False, f"db_error: {str(exc)}"

    @staticmethod
    def get_record_by_id(db: Session, record_id: int) -> Optional[NewsRecord]:
        """Retrieves a single news article with all relationships."""
        return db.query(NewsRecord).filter(NewsRecord.id == record_id).first()

    @staticmethod
    def search_records(
        db: Session, query: SearchQuery
    ) -> Tuple[List[NewsRecord], int]:
        """Performs indexed search and filtering with pagination."""
        q = db.query(NewsRecord)

        if query.symbol:
            q = q.filter(NewsRecord.symbol == query.symbol.upper())

        if query.sector:
            q = q.filter(NewsRecord.sector.ilike(f"%{query.sector}%"))

        if query.category:
            q = q.filter(NewsRecord.category == query.category)

        if query.source_name:
            q = q.filter(NewsRecord.source_name.ilike(f"%{query.source_name}%"))

        if query.source_type:
            q = q.filter(NewsRecord.source_type == query.source_type)

        if query.from_date:
            q = q.filter(NewsRecord.published_at >= query.from_date)

        if query.to_date:
            q = q.filter(NewsRecord.published_at <= query.to_date)

        if query.query:
            pattern = f"%{query.query}%"
            q = q.filter(
                or_(
                    NewsRecord.title.ilike(pattern),
                    NewsRecord.snippet.ilike(pattern),
                    NewsRecord.company_name.ilike(pattern),
                )
            )

        total = q.count()
        offset = (query.page - 1) * query.page_size
        items = q.order_by(desc(NewsRecord.published_at)).offset(offset).limit(query.page_size).all()
        return items, total

    @staticmethod
    def get_stats(db: Session) -> Dict[str, Any]:
        """Aggregates platform intelligence statistics."""
        total_articles = db.query(NewsRecord).count()
        total_duplicates = db.query(ArticleDuplicate).count()
        total_runs = db.query(CollectionLog).count()

        # Category breakdown
        cat_counts = (
            db.query(NewsRecord.category, func.count(NewsRecord.id))
            .group_by(NewsRecord.category)
            .all()
        )
        category_distribution = {cat: count for cat, count in cat_counts}

        # Source breakdown
        src_counts = (
            db.query(NewsRecord.source_name, func.count(NewsRecord.id))
            .group_by(NewsRecord.source_name)
            .all()
        )
        source_distribution = {src: count for src, count in src_counts}

        # Last collection run
        last_run = (
            db.query(CollectionLog)
            .order_by(desc(CollectionLog.started_at))
            .first()
        )

        return {
            "total_articles": total_articles,
            "total_duplicates_prevented": total_duplicates,
            "total_collection_runs": total_runs,
            "category_distribution": category_distribution,
            "source_distribution": source_distribution,
            "last_collection_run": {
                "source_name": last_run.source_name if last_run else None,
                "status": last_run.status if last_run else None,
                "finished_at": last_run.finished_at.isoformat() if last_run and last_run.finished_at else None,
            } if last_run else None,
        }

    @staticmethod
    def get_sources_status(db: Session) -> List[Dict[str, Any]]:
        """Returns health status and stats for each known source."""
        # Standard source catalogue
        known_sources = [
            ("Indian Financial RSS Aggregator", "rss", "Active", "14 Curated Indian Feeds"),
            ("BSE Corporate Disclosures", "bse_announcement", "Active", "BSE India API"),
            ("NSE Corporate Disclosures (Equities)", "nse_announcement", "Active", "NSE Equities API"),
            ("NSE Corporate Disclosures (SME)", "nse_announcement", "Active", "NSE SME API"),
            ("Reserve Bank of India", "rbi_circular", "Active", "RBI Official RSS/Web"),
            ("Securities and Exchange Board of India", "sebi_regulation", "Active", "SEBI Official Circulars"),
            ("Press Information Bureau Economic Policy", "government_policy", "Active", "PIB / Ministry of Finance"),
        ]

        result = []
        for name, src_type, default_status, endpoint_desc in known_sources:
            # Query last run log for this source
            log = (
                db.query(CollectionLog)
                .filter(CollectionLog.source_name == name)
                .order_by(desc(CollectionLog.id))
                .first()
            )
            article_count = db.query(NewsRecord).filter(NewsRecord.source_name == name).count()

            result.append({
                "source_name": name,
                "source_type": src_type,
                "status": log.status if log else "idle",
                "last_run": log.started_at.isoformat() if log else None,
                "last_finished": log.finished_at.isoformat() if log and log.finished_at else None,
                "items_indexed": article_count,
                "last_error": log.error_message if log else None,
                "description": endpoint_desc,
            })
        return result

    @staticmethod
    def start_log(db: Session, source_name: str) -> CollectionLog:
        log = CollectionLog(
            source_name=source_name,
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def finish_log(
        db: Session,
        log_id: int,
        status: str,
        found: int,
        inserted: int,
        duplicates: int,
        error_msg: Optional[str] = None,
    ):
        log = db.query(CollectionLog).filter(CollectionLog.id == log_id).first()
        if log:
            log.finished_at = datetime.now(timezone.utc)
            log.status = status
            log.items_found = found
            log.items_inserted = inserted
            log.items_duplicate = duplicates
            log.items_failed = found - (inserted + duplicates) if found > (inserted + duplicates) else 0
            log.error_message = error_msg
            db.commit()

    @staticmethod
    def to_dataframe(
        db: Session,
        query: Optional[SearchQuery] = None,
        limit: int = 500,
        max_limit: int = 5000,
        sanitize_formulas: bool = False,
    ):
        """
        Exports news records to a Pandas DataFrame for downstream AI/ML modeling.
        Directly fulfills the VeritasAI PDF requirement:
        'The collected data must be cleaned, organized, and stored in a database
        so it can later be used by AI models for prediction and analysis.'

        Guarantees:
        - Bounded row count (default 500, capped at max_limit) to prevent memory exhaustion.
        - Optional spreadsheet formula sanitization (CWE-1236) to prevent code execution in Excel/Calc.
        """
        import pandas as pd
        bounded_limit = min(max(1, limit), max_limit)

        q = db.query(NewsRecord)
        if query:
            if query.symbol:
                q = q.filter(NewsRecord.symbol == query.symbol.upper())
            if query.sector:
                q = q.filter(NewsRecord.sector.ilike(f"%{query.sector}%"))
            if query.category:
                q = q.filter(NewsRecord.category == query.category)
            if query.source_name:
                q = q.filter(NewsRecord.source_name.ilike(f"%{query.source_name}%"))
            if query.source_type:
                q = q.filter(NewsRecord.source_type == query.source_type)
            if query.from_date:
                q = q.filter(NewsRecord.published_at >= query.from_date)
            if query.to_date:
                q = q.filter(NewsRecord.published_at <= query.to_date)
            if query.query:
                pattern = f"%{query.query}%"
                q = q.filter(
                    or_(
                        NewsRecord.title.ilike(pattern),
                        NewsRecord.snippet.ilike(pattern),
                        NewsRecord.company_name.ilike(pattern),
                    )
                )

        records = q.order_by(desc(NewsRecord.published_at)).limit(bounded_limit).all()

        formula_triggers = ("=", "+", "-", "@", "\t", "\r")

        def _clean_val(val):
            if sanitize_formulas and isinstance(val, str) and val.startswith(formula_triggers):
                return f"'{val}"
            return val

        data = [
            {
                "id": r.id,
                "title": _clean_val(r.title),
                "snippet": _clean_val(r.snippet),
                "published_at": r.published_at,
                "source_name": _clean_val(r.source_name),
                "source_type": r.source_type,
                "company_name": _clean_val(r.company_name),
                "symbol": _clean_val(r.symbol),
                "sector": r.sector,
                "category": r.category,
                "canonical_url": r.canonical_url,
                "original_url": r.original_url,
                "confidence_score": r.confidence_score,
                "collected_at": r.collected_at,
            }
            for r in records
        ]
        return pd.DataFrame(data)
