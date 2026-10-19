"""
Multi-Tier Deduplication Engine for Indian Financial Market Intelligence
Implements 6 distinct verification stages satisfying Section 12 of Mega Prompt 2:
  Tier 1: Exact Source Record ID match
  Tier 2: Canonical URL match
  Tier 3: Record Hash match (Title + 1-hour window)
  Tier 4: Cross-Source Near-Duplicate Token Similarity (Jaccard >= 0.85 within +/- 12h)
  Tier 5: Normalized Title within Publication Time Window (+/- 24h)
  Tier 6: Normalized URL match (Original URL cleaned)
"""
import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url


def normalize_title_text(title: str) -> str:
    """Normalize title for hashing, comparison, and tokenization."""
    if not title:
        return ""
    t = title.lower().strip()
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def compute_record_hash(record: NormalizedNewsRecord) -> str:
    """
    Computes a deterministic SHA-256 fingerprint from:
      - Normalized canonical title
      - Symbol (or empty)
      - Publication timestamp rounded to 1-hour window
    """
    clean_title = normalize_title_text(record.title)
    symbol_str = (record.symbol or "").upper().strip()
    dt_rounded = record.published_at.strftime("%Y-%m-%d-%H")
    seed = f"{clean_title}|{symbol_str}|{dt_rounded}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def title_token_similarity(title1: str, title2: str) -> float:
    """Computes Jaccard token similarity between two titles."""
    t1 = set(normalize_title_text(title1).split())
    t2 = set(normalize_title_text(title2).split())
    if not t1 or not t2:
        return 0.0
    intersection = len(t1.intersection(t2))
    union = len(t1.union(t2))
    return float(intersection) / float(union) if union > 0 else 0.0


class DeduplicationEngine:
    """Centralized multi-stage duplicate detection service."""

    @classmethod
    def check_duplicate(
        cls, db: Session, record: NormalizedNewsRecord
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Evaluates candidate record against persistent storage across 6 stages.
        Returns:
            (is_duplicate: bool, reason: Optional[str], existing_record_id: Optional[int])
        """
        from borsel_handler.storage.models import NewsRecord
        canon_url = normalize_url(record.canonical_url or record.original_url)
        clean_title = normalize_title_text(record.title)

        # Tier 1: Exact Source Record ID match
        if record.source_record_id:
            existing_src = db.query(NewsRecord).filter(
                NewsRecord.source_name == record.source_name,
                NewsRecord.source_record_id == record.source_record_id,
            ).first()
            if existing_src:
                return True, "tier_1_source_id_match", existing_src.id

        # Tier 2: Canonical URL match
        if canon_url:
            existing_url = db.query(NewsRecord).filter(
                NewsRecord.canonical_url == canon_url
            ).first()
            if existing_url:
                return True, "tier_2_canonical_url_match", existing_url.id

        # Tier 6: Normalized URL match (Original URL cleaned)
        if record.original_url:
            norm_orig = normalize_url(record.original_url)
            if norm_orig and norm_orig != canon_url:
                existing_orig = db.query(NewsRecord).filter(
                    NewsRecord.canonical_url == norm_orig
                ).first()
                if existing_orig:
                    return True, "tier_6_normalized_url_match", existing_orig.id

        # Tier 3: Record Hash match (Exact Title + 1-hour window)
        rec_hash = compute_record_hash(record)
        existing_hash = db.query(NewsRecord).filter(
            NewsRecord.record_hash == rec_hash
        ).first()
        if existing_hash:
            return True, "tier_3_record_hash_match", existing_hash.id

        # Tier 5: Title + Publication Time Window (+/- 24h)
        time_lower = record.published_at - timedelta(hours=24)
        time_upper = record.published_at + timedelta(hours=24)

        time_window_candidates = db.query(NewsRecord).filter(
            NewsRecord.published_at >= time_lower,
            NewsRecord.published_at <= time_upper,
        ).all()

        for cand in time_window_candidates:
            cand_clean_title = normalize_title_text(cand.title)
            if clean_title and clean_title == cand_clean_title:
                # Guard against false deduplication of distinct companies filing similar generic titles
                if record.symbol and cand.symbol and record.symbol != cand.symbol:
                    continue
                if record.company_name and cand.company_name and record.company_name.lower().strip() != cand.company_name.lower().strip():
                    continue
                return True, "tier_5_title_window_match", cand.id

        # Tier 4: Cross-Source Near-Duplicate Token Similarity (Jaccard >= 0.85 within +/- 12h)
        sim_lower = record.published_at - timedelta(hours=12)
        sim_upper = record.published_at + timedelta(hours=12)

        near_query = db.query(NewsRecord).filter(
            NewsRecord.published_at >= sim_lower,
            NewsRecord.published_at <= sim_upper,
        )
        if record.symbol:
            near_query = near_query.filter(NewsRecord.symbol == record.symbol)

        candidates = near_query.limit(50).all()
        for cand in candidates:
            sim = title_token_similarity(record.title, cand.title)
            if sim >= 0.85:
                # Guard against false near-duplicate matches across distinct companies
                if record.symbol and cand.symbol and record.symbol != cand.symbol:
                    continue
                if record.company_name and cand.company_name and record.company_name.lower().strip() != cand.company_name.lower().strip():
                    continue
                return True, f"tier_4_cross_source_similarity_{sim:.2f}", cand.id

        return False, None, None
