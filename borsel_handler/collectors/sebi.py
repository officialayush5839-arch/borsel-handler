"""
Securities and Exchange Board of India (SEBI) Collector
Collects regulatory circulars, adjudication orders, notices, and policy frameworks.
Fulfills Category D of Section 6 of Mega Prompt 2.
"""
import asyncio
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional

import feedparser
import httpx

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.resolver import CompanyResolver

logger = logging.getLogger(__name__)

SEBI_FEEDS = [
    ("SEBI Circulars & Orders", "https://www.sebi.gov.in/sebirss.xml"),
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 BorselHandler/1.0"
)


from borsel_handler.core.html_utils import clean_html_to_text


def _clean_text(text: str, max_chars: int = 450) -> str:
    """Cleans HTML tags and truncates text cleanly using robust HTML extraction."""
    return clean_html_to_text(text, max_chars=max_chars)


class SEBICollector(BaseCollector):
    """Collector for official SEBI regulatory releases."""

    def __init__(self, feeds: Optional[List[tuple[str, str]]] = None):
        self._feeds = feeds or SEBI_FEEDS

    @property
    def source_name(self) -> str:
        return "Securities and Exchange Board of India"

    @property
    def source_type(self) -> str:
        return "sebi_regulation"

    def _parse_entry_date(self, entry) -> datetime:
        for attr in ("published", "updated", "pubDate"):
            raw = getattr(entry, attr, None) or entry.get(attr)
            if raw:
                try:
                    return parsedate_to_datetime(raw).astimezone(timezone.utc)
                except Exception:
                    pass
        return datetime.now(timezone.utc)

    async def _fetch_feed(
        self, client: httpx.AsyncClient, name: str, url: str, cutoff: Optional[datetime]
    ) -> List[NormalizedNewsRecord]:
        records: List[NormalizedNewsRecord] = []
        try:
            resp = await client.get(url, headers={"User-Agent": USER_AGENT}, timeout=15, follow_redirects=True)
            if resp.status_code != 200:
                logger.warning("SEBI feed %s returned status %s", name, resp.status_code)
                return []

            parsed = feedparser.parse(resp.text)
            for entry in parsed.entries:
                title = getattr(entry, "title", "").strip()
                link = getattr(entry, "link", "").strip()
                if not title or not link:
                    continue

                pub_dt = self._parse_entry_date(entry)
                if cutoff and pub_dt < cutoff:
                    continue

                summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
                snippet = _clean_text(summary)
                guid = getattr(entry, "id", None) or getattr(entry, "guid", None) or link

                # Company entity resolution if specific corporate entities are referenced
                resolved = CompanyResolver.resolve_primary(f"{title} {snippet}")
                symbol = resolved.symbol if resolved else None
                company_name = resolved.name if resolved else None
                sector = resolved.sector if resolved else "Capital Markets & Regulatory"

                cat, conf, tags = classify_event(title, snippet, source_category="sebi")
                if cat == "general_financial_news":
                    cat = "regulatory_sebi"

                canon_url = normalize_url(link)
                record = NormalizedNewsRecord(
                    title=title,
                    snippet=snippet,
                    original_url=link,
                    canonical_url=canon_url,
                    published_at=pub_dt,
                    source_name=self.source_name,
                    source_type=self.source_type,
                    source_record_id=str(guid),
                    company_name=company_name,
                    symbol=symbol,
                    sector=sector,
                    category=cat,
                    tags=tags,
                    confidence_score=conf,
                    raw_metadata={"feed_name": name, "guid": str(guid)},
                )
                records.append(record)

        except Exception as exc:
            logger.error("Error fetching SEBI feed %s: %s", name, exc)

        return records

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        all_records: List[NormalizedNewsRecord] = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            tasks = [self._fetch_feed(client, name, url, cutoff) for name, url in self._feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    all_records.extend(res)
        return all_records
