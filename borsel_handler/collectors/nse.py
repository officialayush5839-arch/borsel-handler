"""
NSE India Corporate Disclosures Collector
Adapted from Market Announcements market_announcements.py.
"""
import logging
import re
from datetime import datetime, timezone
from typing import List, Optional

import httpx

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.stocks import TICKER_TO_NAME, TICKER_TO_SECTOR

logger = logging.getLogger(__name__)

NSE_BASE_URL = "https://www.nseindia.com"
NSE_API_URL = "https://www.nseindia.com/api/corporate-announcements"
NSE_ARCHIVE_ATTACH = "https://nsearchives.nseindia.com/corporate/"

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/companies-listing/corporate-filings-announcements",
}


from borsel_handler.core.html_utils import clean_html_to_text


def _clean_text(text: str, max_chars: int = 400) -> str:
    """Cleans HTML tags and truncates text cleanly using robust HTML extraction."""
    return clean_html_to_text(text, max_chars=max_chars)


class NSEAnnouncementCollector(BaseCollector):
    """Collects official disclosures from National Stock Exchange of India (NSE)."""

    def __init__(self, index_tag: str = "equities"):
        self._index_tag = index_tag

    @property
    def source_name(self) -> str:
        return f"NSE Corporate Disclosures ({self._index_tag.capitalize()})"

    @property
    def source_type(self) -> str:
        return "nse_announcement"

    def _parse_nse_date(self, dt_str: str) -> datetime:
        if not dt_str:
            return datetime.now(timezone.utc)
        # Formats common in NSE: "28-Jun-2026 15:30:00" or ISO format
        for fmt in ("%d-%b-%Y %H:%M:%S", "%d-%m-%Y %H:%M:%S", "%d-%b-%Y", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(dt_str.strip(), fmt).replace(tzinfo=timezone.utc)
            except Exception:
                pass
        try:
            from dateutil import parser
            return parser.parse(dt_str).astimezone(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        records: List[NormalizedNewsRecord] = []
        now = datetime.now(timezone.utc)
        start_date = cutoff or now

        # NSE accepts DD-MM-YYYY
        from_str = start_date.strftime("%d-%m-%Y")
        to_str = now.strftime("%d-%m-%Y")

        params = {
            "index": self._index_tag,
            "from_date": from_str,
            "to_date": to_str,
        }

        try:
            async with httpx.AsyncClient(headers=NSE_HEADERS, follow_redirects=True, timeout=20) as client:
                # Prime session cookies
                try:
                    await client.get(NSE_BASE_URL, timeout=10)
                except Exception:
                    pass

                resp = await client.get(NSE_API_URL, params=params)
                if resp.status_code != 200:
                    logger.warning("NSE API returned HTTP %d", resp.status_code)
                    return []

                raw_data = resp.json()
                items = []
                if isinstance(raw_data, list):
                    items = raw_data
                elif isinstance(raw_data, dict):
                    items = raw_data.get("data") or raw_data.get("announcements") or []

                for item in items:
                    symbol = (item.get("symbol") or "").upper().strip()
                    company = item.get("sm_name") or item.get("companyName") or TICKER_TO_NAME.get(symbol)
                    subject = (item.get("subject") or item.get("desc") or "").strip()
                    if not subject:
                        continue

                    desc = _clean_text(item.get("attchmntText") or item.get("description") or subject)
                    dt_raw = item.get("bfDissTime") or item.get("an_dt") or item.get("dissemTime") or ""
                    pub_date = self._parse_nse_date(dt_raw)

                    if cutoff and pub_date < cutoff:
                        continue

                    ann_id = str(item.get("an_un_id") or item.get("ann_id") or f"NSE_{symbol}_{dt_raw}")

                    file_name = item.get("attchmntFile") or ""
                    if file_name and file_name.startswith("http"):
                        attach_url = file_name
                    elif file_name:
                        attach_url = f"{NSE_ARCHIVE_ATTACH}{file_name}"
                    else:
                        attach_url = f"https://www.nseindia.com/companies-listing/corporate-filings-announcements?symbol={symbol}"

                    canonical_url = normalize_url(attach_url)

                    # Classify event
                    category, confidence, tags = classify_event(subject, desc)

                    rec = NormalizedNewsRecord(
                        title=subject,
                        snippet=desc,
                        original_url=attach_url,
                        canonical_url=canonical_url,
                        published_at=pub_date,
                        source_name=self.source_name,
                        source_type=self.source_type,
                        source_record_id=ann_id,
                        company_name=company,
                        symbol=symbol or None,
                        sector=TICKER_TO_SECTOR.get(symbol),
                        category=category,
                        tags=tags,
                        confidence_score=confidence,
                        collected_at=datetime.now(timezone.utc),
                        raw_metadata=item,
                    )
                    records.append(rec)

        except Exception as exc:
            logger.warning("Error collecting NSE announcements: %s", exc)

        return records
