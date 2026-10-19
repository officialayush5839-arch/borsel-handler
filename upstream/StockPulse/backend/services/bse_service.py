import logging
from datetime import datetime, timezone

import httpx

logger = logging.getLogger(__name__)

# BSE corporate announcements via the public BSE API endpoint
# No auth required — this is the same endpoint used by bseindia.com
BSE_ANNOUNCEMENT_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

# Mapping from NSE symbol to BSE scrip code (Nifty 50)
NSE_TO_BSE: dict[str, str] = {
    "ADANIENT":   "512599",
    "ADANIPORTS":  "532921",
    "APOLLOHOSP":  "508869",
    "ASIANPAINT":  "500820",
    "AXISBANK":    "532215",
    "BAJAJ-AUTO":  "532977",
    "BAJFINANCE":  "500034",
    "BAJAJFINSV":  "532978",
    "BPCL":        "500547",
    "BHARTIARTL":  "532454",
    "BRITANNIA":   "500825",
    "CIPLA":       "500087",
    "COALINDIA":   "533278",
    "DRREDDY":     "500124",
    "EICHERMOT":   "505200",
    "GRASIM":      "500300",
    "HCLTECH":     "532281",
    "HDFCBANK":    "500180",
    "HDFCLIFE":    "540777",
    "HEROMOTOCO":  "500182",
    "HINDALCO":    "500440",
    "HINDUNILVR":  "500696",
    "ICICIBANK":   "532174",
    "ITC":         "500875",
    "INDUSINDBK":  "532187",
    "INFY":        "500209",
    "JINDALSTEL":  "532286",
    "JSWSTEEL":    "500228",
    "KOTAKBANK":   "500247",
    "LT":          "500510",
    "M&M":         "500520",
    "MARUTI":      "532500",
    "NTPC":        "532555",
    "NESTLEIND":   "500790",
    "ONGC":        "500312",
    "POWERGRID":   "532898",
    "RELIANCE":    "500325",
    "SBILIFE":     "540719",
    "SHRIRAMFIN":  "511218",
    "SBIN":        "500112",
    "SUNPHARMA":   "524715",
    "TCS":         "532540",
    "TATACONSUM":  "500800",
    "TATAMOTORS":  "500570",
    "TATASTEEL":   "500470",
    "TECHM":       "532755",
    "TITAN":       "500114",
    "TRENT":       "500251",
    "ULTRACEMCO":  "532538",
    "WIPRO":       "507685",
    "ZOMATO":      "543320",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bseindia.com/",
}


def _clean_snippet(text: str, max_chars: int = 400) -> str:
    import re
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "..."
    return text


async def fetch_announcements(symbol: str, cutoff: datetime) -> list[dict]:
    scrip_code = NSE_TO_BSE.get(symbol)
    if not scrip_code:
        return []

    params = {
        "pageno": "1",
        "strCat": "-1",
        "strPrevDate": cutoff.strftime("%Y%m%d"),
        "strScrip": scrip_code,
        "strSearch": "P",
        "strToDate": datetime.now(timezone.utc).strftime("%Y%m%d"),
        "strType": "C",
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                BSE_ANNOUNCEMENT_URL, params=params, headers=HEADERS, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("BSE announcements fetch failed for %s: %s", symbol, exc)
        return []

    results = []
    for ann in data.get("Table", []):
        try:
            dt_raw = ann.get("DissemDT") or ann.get("News_dt") or ""
            try:
                pub = datetime.strptime(dt_raw[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            except Exception:
                pub = datetime.now(timezone.utc)

            if pub < cutoff:
                continue

            headline = (ann.get("HEADLINE") or ann.get("NewsDesc") or "").strip()
            details = _clean_snippet(ann.get("NEWSSUB") or ann.get("ATTACHMENTNAME") or headline)
            url = ann.get("NSURL") or ann.get("ATTACHMENTNAME") or f"https://www.bseindia.com/corporates/ann.html?scrip={scrip_code}"

            if not headline:
                continue

            results.append({
                "title": headline,
                "snippet": details or headline,
                "url": url if url.startswith("http") else f"https://www.bseindia.com/corporates/ann.html?scrip={scrip_code}",
                "source": "BSE Announcements",
                "published_at": pub,
                "category": "direct",
                "why_it_matters": "Official BSE corporate announcement",
            })
        except Exception:
            continue

    return results
