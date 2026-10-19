import logging
import os
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.marketaux.com/v1/news/all"


def _clean_snippet(text: str, max_chars: int = 400) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "..."
    return text


async def fetch(symbol: str, cutoff: datetime) -> list[dict]:
    api_key = os.getenv("MARKETAUX_API_KEY", "")
    if not api_key:
        logger.info("MARKETAUX_API_KEY not set — skipping Marketaux fetch")
        return []

    # Marketaux uses NSE: prefix for Indian stocks
    symbols = f"NSE:{symbol}"
    params = {
        "symbols": symbols,
        "filter_entities": "true",
        "language": "en",
        "api_token": api_key,
        "limit": 50,
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(BASE_URL, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("Marketaux fetch failed for %s: %s", symbol, exc)
        return []

    results = []
    for article in data.get("data", []):
        try:
            pub_raw = article.get("published_at", "")
            pub = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            if pub.tzinfo is None:
                pub = pub.replace(tzinfo=timezone.utc)
            if pub < cutoff:
                continue

            title = (article.get("title") or "").strip()
            snippet = _clean_snippet(article.get("description") or article.get("snippet") or title)
            url = (article.get("url") or "").strip()
            source = article.get("source", "Marketaux")

            if not title or not url:
                continue

            results.append({
                "title": title,
                "snippet": snippet,
                "url": url,
                "source": source,
                "published_at": pub,
                "category": "direct",
                "why_it_matters": "Direct company news",
            })
        except Exception:
            continue

    return results
