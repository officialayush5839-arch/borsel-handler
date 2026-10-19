"""
Financial RSS News Collector
Adapted from StockPulse rss_service.py.
Ingests from 14 curated Indian financial media RSS feeds.
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
from borsel_handler.core.url_utils import normalize_url, is_trusted_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.stocks import NIFTY_50

logger = logging.getLogger(__name__)

CURATED_RSS_FEEDS = [
    ("Economic Times Markets",   "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"),
    ("Economic Times Markets 2", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Economic Times Economy",   "https://economictimes.indiatimes.com/economy/rssfeeds/1373380680.cms"),
    ("Business Standard Markets","https://www.business-standard.com/rss/markets-106.rss"),
    ("Business Standard Economy","https://www.business-standard.com/rss/economy-policy-101.rss"),
    ("Business Standard Co",     "https://www.business-standard.com/rss/companies-101.rss"),
    ("Mint Markets",             "https://www.livemint.com/rss/markets"),
    ("Mint Companies",           "https://www.livemint.com/rss/companies"),
    ("NDTV Profit",              "https://www.ndtvprofit.com/rss"),
    ("BusinessLine Markets",     "https://www.thehindubusinessline.com/markets/?service=rss"),
    ("BusinessLine Economy",     "https://www.thehindubusinessline.com/economy/?service=rss"),
    ("Reuters India",            "https://feeds.reuters.com/reuters/INbusinessNews"),
    ("Financial Express",        "https://www.financialexpress.com/feed/"),
    ("CNBC TV18",                "https://www.cnbctv18.com/rss/market.xml"),
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 BorselHandler/1.0"
)


from borsel_handler.core.html_utils import clean_html_to_text


def _clean_snippet(text: str, max_chars: int = 450) -> str:
    """Cleans HTML tags and truncates snippet cleanly."""
    return clean_html_to_text(text, max_chars=max_chars)


def _detect_nifty_company(text: str) -> Optional[dict]:
    """Check if any Nifty 50 stock is mentioned in text using word boundaries."""
    t_lower = text.lower()
    for s in NIFTY_50:
        sym = s["symbol"].lower()
        name = s["name"].lower().replace("ltd", "").replace("limited", "").strip()
        # Ensure exact word boundary match for symbol
        if re.search(r"\b" + re.escape(sym) + r"\b", t_lower):
            return s
        # Ensure exact word boundary match for company name
        if len(name) > 3 and re.search(r"\b" + re.escape(name) + r"\b", t_lower):
            return s
    return None


class RSSCollector(BaseCollector):
    """Collector for Indian Financial RSS Feeds."""

    def __init__(self, feeds: List[tuple[str, str]] = None):
        self._feeds = feeds or CURATED_RSS_FEEDS

    @property
    def source_name(self) -> str:
        return "Indian Financial RSS Aggregator"

    @property
    def source_type(self) -> str:
        return "rss"

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
            resp.raise_for_status()
            parsed = feedparser.parse(resp.text)

            for entry in parsed.entries:
                title = clean_html_to_text(entry.get("title") or "")
                link = (entry.get("link") or "").strip()
                if not title or not link:
                    continue

                if not is_trusted_url(link):
                    continue

                pub_date = self._parse_entry_date(entry)
                if cutoff and pub_date < cutoff:
                    continue

                raw_summary = entry.get("summary") or entry.get("description") or title
                snippet = _clean_snippet(raw_summary)
                canonical_link = normalize_url(link)

                # Entity linking
                matched_stock = _detect_nifty_company(f"{title} {snippet}")
                symbol = matched_stock["symbol"] if matched_stock else None
                company_name = matched_stock["name"] if matched_stock else None
                sector = matched_stock["sector"] if matched_stock else None

                # Classification
                category, confidence, tags = classify_event(title, snippet)

                record = NormalizedNewsRecord(
                    title=title,
                    snippet=snippet,
                    original_url=link,
                    canonical_url=canonical_link,
                    published_at=pub_date,
                    source_name=name,
                    source_type=self.source_type,
                    source_record_id=canonical_link,
                    company_name=company_name,
                    symbol=symbol,
                    sector=sector,
                    category=category,
                    tags=tags,
                    confidence_score=confidence,
                    collected_at=datetime.now(timezone.utc),
                    raw_metadata={"feed_url": url},
                )
                records.append(record)

        except Exception as exc:
            logger.warning("Error fetching RSS feed %s (%s): %s", name, url, exc)

        return records

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        all_records: List[NormalizedNewsRecord] = []
        async with httpx.AsyncClient() as client:
            tasks = [
                self._fetch_feed(client, name, url, cutoff)
                for name, url in self._feeds
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    all_records.extend(res)
        return all_records
