"""
BSE India Corporate Announcement Collector — Compliant & Resilient
Collects corporate announcements from BSE India with strict compliance,
polite request handling, and explicit access restriction / WAF telemetry.
Fulfills Section 6 (Task D) of Partial Completion Mega Prompt.
"""
import asyncio
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.stocks import TICKER_TO_NAME, TICKER_TO_SECTOR

logger = logging.getLogger(__name__)

BSE_API_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
BSE_ATTACH_BASE = "https://www.bseindia.com/xml-data/corpfiling/AttachLive/"

NSE_TO_BSE_SCRIP: Dict[str, str] = {
    "ADANIENT": "512599", "ADANIPORTS": "532921", "APOLLOHOSP": "508869",
    "ASIANPAINT": "500820", "AXISBANK": "532215", "BAJAJ-AUTO": "532977",
    "BAJFINANCE": "500034", "BAJAJFINSV": "532978", "BPCL": "500547",
    "BHARTIARTL": "532454", "BRITANNIA": "500825", "CIPLA": "500087",
    "COALINDIA": "533278", "DRREDDY": "500124", "EICHERMOT": "505200",
    "GRASIM": "500300", "HCLTECH": "532281", "HDFCBANK": "500180",
    "HDFCLIFE": "540777", "HEROMOTOCO": "500182", "HINDALCO": "500440",
    "HINDUNILVR": "500696", "ICICIBANK": "532174", "ITC": "500875",
    "INDUSINDBK": "532187", "INFY": "500209", "JINDALSTEL": "532286",
    "JSWSTEEL": "500228", "KOTAKBANK": "500247", "LT": "500510",
    "M&M": "500520", "MARUTI": "532500", "NTPC": "532555",
    "NESTLEIND": "500790", "ONGC": "500312", "POWERGRID": "532898",
    "RELIANCE": "500325", "SBILIFE": "540719", "SHRIRAMFIN": "511218",
    "SBIN": "500112", "SUNPHARMA": "524715", "TCS": "532540",
    "TATACONSUM": "500800", "TATAMOTORS": "500570", "TATASTEEL": "500470",
    "TECHM": "532755", "TITAN": "500114", "TRENT": "500251",
    "ULTRACEMCO": "532538", "WIPRO": "507685", "ZOMATO": "543320",
}
BSE_SCRIP_TO_NSE = {v: k for k, v in NSE_TO_BSE_SCRIP.items()}

# Compliant standard browser headers without stealth evasion
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.bseindia.com/corporates/ann",
}


from borsel_handler.core.html_utils import clean_html_to_text


def _clean_text(text: str, max_chars: int = 400) -> str:
    """Cleans HTML tags and truncates text cleanly using robust HTML extraction."""
    return clean_html_to_text(text, max_chars=max_chars)


def parse_bse_date(dt_raw: str) -> datetime:
    """Parses BSE date format into timezone-aware UTC datetime."""
    if not dt_raw:
        return datetime.now(timezone.utc)
    try:
        return datetime.strptime(dt_raw[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except Exception:
        try:
            from dateutil import parser
            return parser.parse(dt_raw).astimezone(timezone.utc)
        except Exception:
            return datetime.now(timezone.utc)


class BSEAnnouncementCollector(BaseCollector):
    """
    Collects official corporate announcements from BSE India.
    Implements ethical collection: respects access restrictions (HTTP 403 / 429),
    avoids repeated retries on blocked endpoints, and provides accurate telemetry.
    """

    def __init__(self, symbols: Optional[List[str]] = None, request_timeout: float = 15.0):
        self._symbols = symbols or list(NSE_TO_BSE_SCRIP.keys())
        self._timeout = request_timeout

        # Observability state
        self.access_restricted: bool = False
        self.last_status_code: Optional[int] = None
        self.last_error: Optional[str] = None
        self.last_attempt_at: Optional[datetime] = None
        self.last_successful_at: Optional[datetime] = None

    @property
    def source_name(self) -> str:
        return "BSE Corporate Announcements"

    @property
    def source_type(self) -> str:
        return "bse_announcement"

    def _parse_ann_date(self, dt_raw: str) -> datetime:
        """Parses BSE date format into timezone-aware UTC datetime."""
        return parse_bse_date(dt_raw)

    def parse_announcement_table(
        self,
        table: List[Dict[str, Any]],
        symbol: Optional[str] = None,
        cutoff: Optional[datetime] = None,
    ) -> List[NormalizedNewsRecord]:
        """
        Parses JSON list of BSE announcements into NormalizedNewsRecord items.
        Extracts scrip codes, headlines, dates, categories, and attachment URLs.
        """
        records: List[NormalizedNewsRecord] = []
        for ann in table:
            dt_raw = ann.get("DissemDT") or ann.get("News_dt") or ""
            pub_date = parse_bse_date(dt_raw)
            if cutoff and pub_date < cutoff:
                continue

            headline = (ann.get("HEADLINE") or ann.get("NewsDesc") or "").strip()
            if not headline:
                continue

            sub_desc = ann.get("NEWSSUB") or ann.get("ATTACHMENTNAME") or headline
            snippet = _clean_text(sub_desc)

            scrip_code = str(ann.get("SCRIP_CD") or "").strip()
            resolved_symbol = symbol or BSE_SCRIP_TO_NSE.get(scrip_code)

            attach_file = ann.get("ATTACHMENTNAME") or ""
            if attach_file and not attach_file.startswith("http"):
                attach_url = f"{BSE_ATTACH_BASE}{attach_file}"
            elif attach_file:
                attach_url = attach_file
            else:
                attach_url = f"https://www.bseindia.com/corporates/ann.html?scrip={scrip_code}"

            canonical_url = normalize_url(attach_url)
            script_id = str(ann.get("NEWSID") or f"{scrip_code}_{dt_raw}")

            category, confidence, tags = classify_event(
                headline, snippet, source_category=ann.get("CATEGORYNAME", "")
            )

            company_name = TICKER_TO_NAME.get(resolved_symbol, ann.get("SLONGNAME"))

            rec = NormalizedNewsRecord(
                title=headline,
                snippet=snippet,
                original_url=attach_url,
                canonical_url=canonical_url,
                published_at=pub_date,
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id=script_id,
                company_name=company_name,
                symbol=resolved_symbol or None,
                sector=TICKER_TO_SECTOR.get(resolved_symbol) if resolved_symbol else None,
                category=category,
                tags=tags,
                confidence_score=confidence,
                collected_at=datetime.now(timezone.utc),
                raw_metadata=ann,
            )
            records.append(rec)

        return records

    async def _fetch_for_symbol(
        self, client: httpx.AsyncClient, symbol: str, cutoff: Optional[datetime]
    ) -> Tuple[List[NormalizedNewsRecord], Optional[int], Optional[str]]:
        """
        Executes compliant request for a single scrip.
        Returns: (records, status_code, error_message)
        """
        scrip_code = NSE_TO_BSE_SCRIP.get(symbol)
        if not scrip_code:
            return [], None, f"Unknown symbol {symbol}"

        start_dt = cutoff or (datetime.now(timezone.utc))
        params = {
            "pageno": "1",
            "strCat": "-1",
            "strPrevDate": start_dt.strftime("%Y%m%d"),
            "strScrip": scrip_code,
            "strSearch": "P",
            "strToDate": datetime.now(timezone.utc).strftime("%Y%m%d"),
            "strType": "C",
        }

        try:
            resp = await client.get(BSE_API_URL, params=params, headers=HEADERS, timeout=self._timeout)
            if resp.status_code == 200:
                data = resp.json()
                table = data.get("Table", [])
                records = self.parse_announcement_table(table, symbol=symbol, cutoff=cutoff)
                return records, 200, None

            if resp.status_code in (403, 429):
                err = f"BSE returned HTTP {resp.status_code} (Access Restricted/Rate Limited)"
                logger.warning("BSE collection restricted for %s: HTTP %d", symbol, resp.status_code)
                return [], resp.status_code, err

            logger.warning("BSE request for %s returned HTTP %d", symbol, resp.status_code)
            return [], resp.status_code, f"HTTP {resp.status_code}"

        except (httpx.TimeoutException, httpx.RequestError) as exc:
            logger.warning("Network failure querying BSE for %s: %s", symbol, exc)
            return [], None, str(exc)
        except Exception as exc:
            logger.warning("Unexpected error querying BSE for %s: %s", symbol, exc)
            return [], None, str(exc)

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """
        Fetches announcements across configured equities.
        Implements short-circuiting on HTTP 403 / 429 to avoid repeatedly hammering blocked endpoints.
        """
        self.last_attempt_at = datetime.now(timezone.utc)
        self.access_restricted = False
        self.last_error = None
        all_records: List[NormalizedNewsRecord] = []

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            # Probe first symbol to determine whether endpoint is accessible from this network environment
            probe_symbol = self._symbols[0] if self._symbols else "INFY"
            probe_records, probe_status, probe_err = await self._fetch_for_symbol(client, probe_symbol, cutoff)
            self.last_status_code = probe_status

            if probe_status in (403, 429):
                self.access_restricted = True
                self.last_error = probe_err
                logger.warning(
                    "BSE live collection deferred: %s. Halting further requests to respect source restrictions.",
                    probe_err,
                )
                return []

            if probe_status == 200:
                all_records.extend(probe_records)
                self.last_successful_at = datetime.now(timezone.utc)

                # Process remaining symbols politely with rate limiting delays
                remaining_symbols = self._symbols[1:]
                for sym in remaining_symbols:
                    await asyncio.sleep(0.5)  # Politeness delay
                    recs, st, err = await self._fetch_for_symbol(client, sym, cutoff)
                    if st in (403, 429):
                        self.access_restricted = True
                        self.last_error = err
                        break
                    all_records.extend(recs)

        logger.info("BSEAnnouncementCollector completed run: fetched %d records", len(all_records))
        return all_records

    def get_health_status(self) -> Dict[str, Any]:
        """Returns observable source health metrics for monitoring and API."""
        return {
            "source_name": self.source_name,
            "access_restricted": self.access_restricted,
            "last_status_code": self.last_status_code,
            "last_error": self.last_error,
            "last_attempt_at": self.last_attempt_at.isoformat() if self.last_attempt_at else None,
            "last_successful_at": self.last_successful_at.isoformat() if self.last_successful_at else None,
        }
