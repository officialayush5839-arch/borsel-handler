import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx
from cachetools import TTLCache

logger = logging.getLogger(__name__)

_rss_cache: TTLCache = TTLCache(maxsize=1, ttl=1800)
_cache_lock = asyncio.Lock()

RSS_FEEDS = [
    ("Economic Times Markets",   "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"),
    ("Economic Times Markets",   "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Economic Times Economy",   "https://economictimes.indiatimes.com/economy/rssfeeds/1373380680.cms"),
    ("Business Standard",        "https://www.business-standard.com/rss/markets-106.rss"),
    ("Business Standard",        "https://www.business-standard.com/rss/economy-policy-101.rss"),
    ("Business Standard",        "https://www.business-standard.com/rss/companies-101.rss"),
    ("Mint",                     "https://www.livemint.com/rss/markets"),
    ("Mint",                     "https://www.livemint.com/rss/companies"),
    ("NDTV Profit",              "https://www.ndtvprofit.com/rss"),
    ("BusinessLine",             "https://www.thehindubusinessline.com/markets/?service=rss"),
    ("BusinessLine",             "https://www.thehindubusinessline.com/economy/?service=rss"),
    ("Reuters India",            "https://feeds.reuters.com/reuters/INbusinessNews"),
    ("Financial Express",        "https://www.financialexpress.com/feed/"),
    ("CNBC TV18",                "https://www.cnbctv18.com/rss/market.xml"),
]

# Hard allowlist — only URLs from these domains are accepted.
# This is the safety net that prevents junk from slipping through.
TRUSTED_DOMAINS = {
    "economictimes.indiatimes.com",
    "business-standard.com",
    "livemint.com",
    "ndtvprofit.com",
    "thehindubusinessline.com",
    "reuters.com",
    "financialexpress.com",
    "cnbctv18.com",
    "moneycontrol.com",
    "thehindu.com",
    "bseindia.com",
    "nseindia.com",
    "sebi.gov.in",
    "rbi.org.in",
    "fortuneindia.com",
    "businesstoday.in",
    "inc42.com",
    "bloombergquint.com",
    "ndtv.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _is_trusted_url(url: str) -> bool:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or ""
        # Accept if host exactly matches or is a subdomain of a trusted domain
        return any(host == d or host.endswith("." + d) for d in TRUSTED_DOMAINS)
    except Exception:
        return False


def _parse_published(entry) -> datetime:
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw).astimezone(timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _clean_snippet(text: str, max_chars: int = 450) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "..."
    return text


async def _fetch_one(client: httpx.AsyncClient, source_name: str, url: str) -> list[dict]:
    try:
        resp = await client.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        items = []
        for entry in feed.entries:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()

            if not title or not link:
                continue
            if not _is_trusted_url(link):
                logger.debug("Dropping untrusted URL: %s", link)
                continue

            raw_snippet = entry.get("summary") or entry.get("description") or ""
            snippet = _clean_snippet(raw_snippet)

            items.append({
                "title": title,
                "snippet": snippet or title,
                "url": link,
                "source": source_name,
                "published_at": _parse_published(entry),
            })
        return items
    except Exception as exc:
        logger.warning("RSS fetch failed for %s (%s): %s", source_name, url, exc)
        return []


async def _load_all_feeds() -> list[dict]:
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[_fetch_one(client, name, url) for name, url in RSS_FEEDS]
        )
    all_items = [item for sublist in results for item in sublist]

    # Global dedup by URL across all feeds
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for item in all_items:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            unique.append(item)

    logger.info("RSS cache loaded: %d unique items from %d feeds", len(unique), len(RSS_FEEDS))
    return unique


async def _get_cached_feeds() -> list[dict]:
    async with _cache_lock:
        if "feeds" not in _rss_cache:
            _rss_cache["feeds"] = await _load_all_feeds()
        return _rss_cache["feeds"]


def _matches(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


async def fetch_and_filter(
    keywords: list[str],
    category: str,
    why_it_matters: str,
    cutoff: datetime,
) -> list[dict]:
    if not keywords:
        return []

    all_items = await _get_cached_feeds()
    results = []
    seen: set[str] = set()

    for item in all_items:
        pub = item["published_at"]
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        if pub < cutoff:
            continue

        combined = item["title"] + " " + item["snippet"]
        if not _matches(combined, keywords):
            continue

        key = hashlib.md5(item["title"].lower().encode()).hexdigest()
        if key in seen:
            continue
        seen.add(key)

        results.append({
            **item,
            "category": category,
            "why_it_matters": why_it_matters,
        })

    return results
