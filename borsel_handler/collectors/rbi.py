"""
Reserve Bank of India (RBI) Official Collector — Modernized
Collects monetary policy announcements, regulatory circulars, and official press releases
from the official RBI website (HTML archives and feeds).
Fulfills Category C of Section 6 and Section 3 of Partial Completion Mega Prompt.
"""
import asyncio
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional
from urllib.parse import urljoin

import feedparser
import httpx
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.resolver import CompanyResolver

logger = logging.getLogger(__name__)

RBI_BASE_URL = "https://www.rbi.org.in"
RBI_PRESS_RELEASE_URL = "https://www.rbi.org.in/Scripts/BS_PressReleaseDisplay.aspx"
RBI_NOTIFICATIONS_URL = "https://www.rbi.org.in/Scripts/NotificationUser.aspx"

# Legacy feeds retained for backward compatibility and fixture tests
RBI_LEGACY_FEEDS = [
    ("RBI Press Releases", "https://www.rbi.org.in/rss/rss_pressrelease.xml"),
    ("RBI Circulars", "https://www.rbi.org.in/rss/rss_circular.xml"),
]

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 BorselHandler/1.0"
)

HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


from borsel_handler.core.html_utils import clean_html_to_text


def _clean_text(text: str, max_chars: int = 450) -> str:
    """Cleans HTML tags and truncates text cleanly using robust HTML extraction."""
    return clean_html_to_text(text, max_chars=max_chars)


def parse_rbi_date(date_str: str) -> datetime:
    """Parses date string into timezone-aware UTC datetime."""
    if not date_str:
        return datetime.now(timezone.utc)
    try:
        dt = date_parser.parse(date_str.strip())
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


class RBICollector(BaseCollector):
    """
    Collector for official Reserve Bank of India announcements,
    supporting both modernized HTML web archives and legacy XML feeds.
    """

    def __init__(
        self,
        html_urls: Optional[List[str]] = None,
        feeds: Optional[List[tuple[str, str]]] = None,
        request_timeout: float = 20.0,
    ):
        self._html_urls = html_urls or [RBI_PRESS_RELEASE_URL, RBI_NOTIFICATIONS_URL]
        self._feeds = feeds or RBI_LEGACY_FEEDS
        self._timeout = request_timeout

    @property
    def source_name(self) -> str:
        return "Reserve Bank of India"

    @property
    def source_type(self) -> str:
        return "rbi_circular"

    def parse_html_archive(
        self, html_content: str, source_url: str = RBI_PRESS_RELEASE_URL, cutoff: Optional[datetime] = None
    ) -> List[NormalizedNewsRecord]:
        """
        Parses official RBI press releases and notifications HTML table structure.
        Extracts publication dates, titles, links, PDF attachments, and source IDs.
        """
        records: List[NormalizedNewsRecord] = []
        if not html_content:
            return records

        import warnings
        from bs4 import XMLParsedAsHTMLWarning
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

        soup = BeautifulSoup(html_content, "html.parser")
        current_date = datetime.now(timezone.utc)

        # Iterate through table rows
        rows = soup.find_all("tr")
        for row in rows:
            # Check for date header row: <td class="tableheader" ...><b>Oct 19, 2026</b></td>
            th_cell = row.find("td", class_=lambda c: c and "tableheader" in c)
            if th_cell:
                date_text = th_cell.get_text(strip=True)
                if date_text:
                    current_date = parse_rbi_date(date_text)
                continue

            # Look for article link
            link_tag = row.find(
                "a",
                href=lambda h: h and any(
                    pattern in h for pattern in (
                        "BS_PressReleaseDisplay.aspx?prid=",
                        "NotificationUser.aspx?Id=",
                        "BS_CircularsDisplay.aspx?Id="
                    )
                )
            )

            if not link_tag:
                continue

            title = link_tag.get_text(strip=True)
            if not title:
                continue

            # Apply date cutoff filter if provided
            if cutoff and current_date < cutoff:
                continue

            href = link_tag["href"]
            full_url = urljoin(RBI_BASE_URL, f"/Scripts/{href}" if not href.startswith("http") and not href.startswith("/") else href)
            canon_url = normalize_url(full_url)

            # Extract source record ID from query parameter
            prid_match = re.search(r"prid=(\d+)", href, re.IGNORECASE)
            id_match = re.search(r"Id=([a-zA-Z0-9_\-]+)", href, re.IGNORECASE)
            if prid_match:
                source_rec_id = f"RBI_PR_{prid_match.group(1)}"
            elif id_match:
                source_rec_id = f"RBI_NOTIF_{id_match.group(1)}"
            else:
                source_rec_id = f"RBI_{current_date.strftime('%Y%m%d')}_{abs(hash(title)) % 1000000}"

            # Check for PDF attachment link
            pdf_tag = row.find("a", href=lambda h: h and h.lower().endswith(".pdf"))
            pdf_url = pdf_tag["href"] if pdf_tag else None

            # Entity resolution for banks/financial institutions mentioned
            resolved = CompanyResolver.resolve_primary(title)
            symbol = resolved.symbol if resolved else None
            company_name = resolved.name if resolved else None
            sector = resolved.sector if resolved else "Banking & Financial Services"

            # Event classification
            cat, conf, tags = classify_event(title, title, source_category="rbi")
            if cat == "general_financial_news":
                cat = "rbi_update"

            record = NormalizedNewsRecord(
                title=title,
                snippet=_clean_text(title),
                original_url=full_url,
                canonical_url=canon_url,
                published_at=current_date,
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id=source_rec_id,
                company_name=company_name,
                symbol=symbol,
                sector=sector,
                category=cat,
                tags=tags,
                confidence_score=conf,
                raw_metadata={
                    "page_url": source_url,
                    "pdf_url": pdf_url,
                    "source_id": source_rec_id,
                },
            )
            records.append(record)

        return records

    def parse_rss_feed(self, feed_text: str, feed_name: str, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """Parses legacy or fixture-supplied RSS feeds."""
        records: List[NormalizedNewsRecord] = []
        if not feed_text:
            return records

        parsed = feedparser.parse(feed_text)
        for entry in parsed.entries:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            if not title or not link:
                continue

            pub_dt = datetime.now(timezone.utc)
            for attr in ("published", "updated", "pubDate"):
                raw = getattr(entry, attr, None) or entry.get(attr)
                if raw:
                    try:
                        pub_dt = parsedate_to_datetime(raw).astimezone(timezone.utc)
                        break
                    except Exception:
                        pass

            if cutoff and pub_dt < cutoff:
                continue

            summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            snippet = _clean_text(summary or title)
            guid = getattr(entry, "id", None) or getattr(entry, "guid", None) or link

            resolved = CompanyResolver.resolve_primary(f"{title} {snippet}")
            symbol = resolved.symbol if resolved else None
            company_name = resolved.name if resolved else None
            sector = resolved.sector if resolved else "Banking & Financial Services"

            cat, conf, tags = classify_event(title, snippet, source_category="rbi")
            if cat == "general_financial_news":
                cat = "rbi_update"

            record = NormalizedNewsRecord(
                title=title,
                snippet=snippet,
                original_url=link,
                canonical_url=normalize_url(link),
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
                raw_metadata={"feed_name": feed_name, "guid": str(guid)},
            )
            records.append(record)

        return records

    async def _fetch_url(self, client: httpx.AsyncClient, url: str) -> Optional[httpx.Response]:
        """Safely fetches a URL handling retries, timeouts, and status codes."""
        for attempt in range(3):
            try:
                resp = await client.get(url, headers=HEADERS, timeout=self._timeout, follow_redirects=True)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in (404, 403, 500, 502, 503):
                    logger.warning("RBI endpoint %s returned HTTP %d", url, resp.status_code)
                    return resp
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt == 2:
                    logger.warning("Network failure fetching RBI %s: %s", url, exc)
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """
        Executes RBI collection. First attempts official HTML archive pages;
        if HTML fails, falls back to XML feeds.
        """
        all_records: List[NormalizedNewsRecord] = []
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            # 1. Fetch HTML archives
            for url in self._html_urls:
                resp = await self._fetch_url(client, url)
                if resp and resp.status_code == 200:
                    recs = self.parse_html_archive(resp.text, source_url=url, cutoff=cutoff)
                    all_records.extend(recs)

            # 2. If no records collected from HTML, attempt legacy/feed fallback
            if not all_records and self._feeds:
                for name, feed_url in self._feeds:
                    resp = await self._fetch_url(client, feed_url)
                    if resp and resp.status_code == 200:
                        recs = self.parse_rss_feed(resp.text, feed_name=name, cutoff=cutoff)
                        all_records.extend(recs)

        logger.info("RBICollector fetched %d normalized records", len(all_records))
        return all_records
