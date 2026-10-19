from datetime import datetime

# NewsAPI.org removed — its /v2/everything endpoint pulls from ~80k sources
# including shopping/deal sites (dealnews.com etc.) that match financial keywords.
# Macro news is now covered entirely by the curated RSS feeds in rss_service.py.

async def fetch(keywords: list[str], cutoff: datetime, why_it_matters: str) -> list[dict]:
    return []
