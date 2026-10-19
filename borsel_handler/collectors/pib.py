"""
Press Information Bureau (PIB) Government Economic Policy Collector — Modernized
Collects official economic releases, Cabinet approvals, GST Council updates, and
Ministry of Finance announcements from the official PIB portal.
Fulfills Category E of Section 6 and Section 4 of Partial Completion Mega Prompt.
"""
import asyncio
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Optional, Set
from urllib.parse import urljoin

import feedparser
import httpx
from bs4 import BeautifulSoup

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.classification.taxonomy import CATEGORY_GOVERNMENT_POLICY, CATEGORY_MACRO_ECONOMIC
from borsel_handler.data.resolver import CompanyResolver

logger = logging.getLogger(__name__)

PIB_BASE_URL = "https://www.pib.gov.in"
PIB_ALL_RELEASE_URL = "https://www.pib.gov.in/AllRelease.aspx?reg=3&lang=1"

ECONOMIC_MINISTRIES: Set[str] = {
    "Ministry of Finance",
    "Cabinet Committee on Economic Affairs (CCEA)",
    "Cabinet",
    "Ministry of Commerce & Industry",
    "Ministry of Corporate Affairs",
    "Ministry of Petroleum & Natural Gas",
    "Ministry of Heavy Industries",
    "Ministry of Statistics and Programme Implementation",
}

ECONOMIC_KEYWORDS = [
    "tax", "gst", "budget", "customs", "duty", "revenue", "fiscal", "inflation",
    "gdp", "growth", "policy", "scheme", "pli", "incentive", "disinvestment",
    "export", "import", "trade", "investment", "fdi", "economic", "semiconductor",
    "manufacturing", "cabinet approves", "ccea approves", "subsidy", "procurement",
]

# Legacy RSS feeds preserved for backward compatibility and offline fixtures
PIB_LEGACY_FEEDS = [
    ("PIB Ministry of Finance", "https://pib.gov.in/RssMain.aspx?ModId=2&MinId=0"),
    ("PIB Ministry of Commerce", "https://pib.gov.in/RssMain.aspx?ModId=2&MinId=12"),
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


def is_economic_content(title: str, ministry: str) -> bool:
    """
    Discriminates economic and financial policy releases from general/ceremonial releases.
    Returns True only if issued by an economic ministry or matches economic policy keywords.
    """
    t_lower = title.lower()
    m_clean = ministry.strip()

    # Direct match for known economic ministries
    if any(em.lower() in m_clean.lower() for em in ECONOMIC_MINISTRIES):
        return True

    # Keyword match for economic policy content from other ministries
    return any(kw in t_lower for kw in ECONOMIC_KEYWORDS)


class PIBCollector(BaseCollector):
    """
    Collector for official Government Economic Policy announcements via PIB.
    Supports official HTML release listings and legacy XML feeds.
    """

    def __init__(
        self,
        html_url: str = PIB_ALL_RELEASE_URL,
        feeds: Optional[List[tuple[str, str]]] = None,
        request_timeout: float = 20.0,
    ):
        self._html_url = html_url
        self._feeds = feeds or PIB_LEGACY_FEEDS
        self._timeout = request_timeout

    @property
    def source_name(self) -> str:
        return "Press Information Bureau Economic Policy"

    @property
    def source_type(self) -> str:
        return "government_policy"

    def parse_html_releases(
        self, html_content: str, cutoff: Optional[datetime] = None
    ) -> List[NormalizedNewsRecord]:
        """
        Parses official PIB release listings with strict economic policy discrimination.
        Extracts headlines, ministries, links, and PRIDs.
        """
        records: List[NormalizedNewsRecord] = []
        if not html_content:
            return records

        import warnings
        from bs4 import XMLParsedAsHTMLWarning
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

        soup = BeautifulSoup(html_content, "html.parser")
        current_dt = datetime.now(timezone.utc)

        # PIB groups releases under <h3> headings for each Ministry
        ministry_headers = soup.find_all("h3")
        for header in ministry_headers:
            ministry_name = header.get_text(strip=True)
            if not ministry_name:
                continue

            # Find following sibling container (ul, div, or individual lis)
            container = header.find_next_sibling()
            if not container:
                continue

            # Collect release links under this ministry
            links = container.find_all("a", href=lambda h: h and "PRID=" in h)
            for link in links:
                title = link.get_text(strip=True)
                if not title:
                    continue

                # Apply economic policy discrimination
                if not is_economic_content(title, ministry_name):
                    continue

                if cutoff and current_dt < cutoff:
                    continue

                href = link["href"]
                full_url = urljoin(PIB_BASE_URL, href)
                canon_url = normalize_url(full_url)

                # Extract PRID for deterministic record ID
                prid_match = re.search(r"PRID=(\d+)", href, re.IGNORECASE)
                source_rec_id = f"PIB_{prid_match.group(1)}" if prid_match else f"PIB_{abs(hash(title)) % 1000000}"

                # Entity resolution for corporate entities mentioned in policy
                resolved = CompanyResolver.resolve_primary(title)
                symbol = resolved.symbol if resolved else None
                company_name = resolved.name if resolved else None
                sector = resolved.sector if resolved else "Macroeconomic & Fiscal Policy"

                # Classify
                cat, conf, tags = classify_event(title, title, source_category="pib")
                if cat == "general_financial_news":
                    cat = CATEGORY_GOVERNMENT_POLICY

                record = NormalizedNewsRecord(
                    title=title,
                    snippet=_clean_text(f"[{ministry_name}] {title}"),
                    original_url=full_url,
                    canonical_url=canon_url,
                    published_at=current_dt,
                    source_name=self.source_name,
                    source_type=self.source_type,
                    source_record_id=source_rec_id,
                    company_name=company_name,
                    symbol=symbol,
                    sector=sector,
                    category=cat,
                    tags=list(set(tags + [ministry_name.lower().replace(" ", "_")])),
                    confidence_score=conf,
                    raw_metadata={
                        "ministry": ministry_name,
                        "source_id": source_rec_id,
                        "href": href,
                    },
                )
                records.append(record)

        return records

    def parse_rss_feed(
        self, feed_text: str, feed_name: str, cutoff: Optional[datetime] = None
    ) -> List[NormalizedNewsRecord]:
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
            sector = resolved.sector if resolved else "Macroeconomic Policy"

            cat, conf, tags = classify_event(title, snippet, source_category="pib")
            if cat == "general_financial_news":
                cat = CATEGORY_GOVERNMENT_POLICY

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
                    logger.warning("PIB endpoint %s returned HTTP %d", url, resp.status_code)
                    return resp
            except (httpx.TimeoutException, httpx.RequestError) as exc:
                if attempt == 2:
                    logger.warning("Network failure fetching PIB %s: %s", url, exc)
                    return None
                await asyncio.sleep(0.5 * (2 ** attempt))
        return None

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """
        Executes PIB collection. First attempts official HTML releases portal;
        if HTML fails, falls back to XML feeds.
        """
        all_records: List[NormalizedNewsRecord] = []
        async with httpx.AsyncClient(timeout=self._timeout, follow_redirects=True) as client:
            # 1. Fetch HTML portal
            resp = await self._fetch_url(client, self._html_url)
            if resp and resp.status_code == 200:
                recs = self.parse_html_releases(resp.text, cutoff=cutoff)
                all_records.extend(recs)

            # 2. If no records from HTML, fall back to RSS feeds
            if not all_records and self._feeds:
                for name, feed_url in self._feeds:
                    resp = await self._fetch_url(client, feed_url)
                    if resp and resp.status_code == 200:
                        recs = self.parse_rss_feed(resp.text, feed_name=name, cutoff=cutoff)
                        all_records.extend(recs)

        logger.info("PIBCollector fetched %d normalized economic policy records", len(all_records))
        return all_records
