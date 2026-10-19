import asyncio
import hashlib
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from data.dependency_map import DEPENDENCY_MAP
from data.stocks import NIFTY_50
from models.schemas import NewsCategories, NewsItem, NewsResponse, StockInfo
from services import bse_service, marketaux_service, newsapi_service, rss_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/auth")
async def auth(request: Request):
    body = await request.json()
    password = body.get("password", "")
    site_password = os.getenv("SITE_PASSWORD", "")
    if site_password and password != site_password:
        return JSONResponse({"ok": False}, status_code=401)
    return {"ok": True}

TIME_RANGE_MAP: dict[str, timedelta] = {
    "24h":  timedelta(hours=24),
    "48h":  timedelta(hours=48),
    "72h":  timedelta(hours=72),
    "1w":   timedelta(weeks=1),
    "2w":   timedelta(weeks=2),
}

_STOCK_LOOKUP: dict[str, dict] = {s["symbol"]: s for s in NIFTY_50}


@router.get("/stocks")
async def get_stocks() -> list[dict]:
    return NIFTY_50


@router.get("/news", response_model=NewsResponse)
async def get_news(
    symbol: str = Query(..., description="NSE ticker symbol e.g. MARUTI"),
    timerange: str = Query("48h", description="One of: 24h, 48h, 72h, 1w, 2w"),
) -> NewsResponse:
    symbol = symbol.upper()

    stock = _STOCK_LOOKUP.get(symbol)
    if not stock:
        raise HTTPException(status_code=404, detail=f"Stock '{symbol}' not found in Nifty 50 list")

    delta = TIME_RANGE_MAP.get(timerange)
    if not delta:
        raise HTTPException(status_code=400, detail=f"Invalid timerange '{timerange}'. Use: 24h, 48h, 72h, 1w, 2w")

    cutoff = datetime.now(timezone.utc) - delta
    dep = DEPENDENCY_MAP.get(symbol, {})

    direct_keywords: list[str] = dep.get("direct_keywords", [stock["name"], symbol])
    related_companies: dict[str, str] = dep.get("related_companies", {})
    commodity_keywords: list[str] = dep.get("commodity_keywords", [])
    macro_keywords: list[str] = dep.get("macro_keywords", [])

    # Build supply chain keyword groups: one group per related company
    related_kw_groups: list[tuple[list[str], str]] = [
        ([name], label) for name, label in related_companies.items()
    ]
    # Commodity keywords as one combined supply chain group
    if commodity_keywords:
        related_kw_groups.append((commodity_keywords, "Commodity input affecting production cost"))

    # Fire all fetches in parallel
    tasks: list[Any] = [
        # Direct: Marketaux (ticker-tagged)
        marketaux_service.fetch(symbol, cutoff),
        # Direct: RSS filtered by company name
        rss_service.fetch_and_filter(
            direct_keywords, "direct", "Direct company news", cutoff
        ),
        # Direct: BSE announcements
        bse_service.fetch_announcements(symbol, cutoff),
        # Macro: RSS
        rss_service.fetch_and_filter(
            macro_keywords, "macro", f"{stock['sector']} sector & macro news", cutoff
        ),
        # Macro: NewsAPI
        newsapi_service.fetch(
            macro_keywords, cutoff, f"{stock['sector']} sector & macro news"
        ),
    ]

    # Supply chain: one RSS task per related company + one for commodities
    supply_chain_tasks: list[Any] = [
        rss_service.fetch_and_filter(kws, "supply_chain", label, cutoff)
        for kws, label in related_kw_groups
    ]

    all_tasks = tasks + supply_chain_tasks
    results = await asyncio.gather(*all_tasks, return_exceptions=True)

    # Separate fixed task results from supply chain results
    fixed_results = results[:5]
    supply_results = results[5:]

    raw_direct: list[dict] = []
    raw_supply: list[dict] = []
    raw_macro: list[dict] = []

    for i, res in enumerate(fixed_results):
        if isinstance(res, Exception):
            logger.warning("Task %d failed: %s", i, res)
            continue
        items: list[dict] = res  # type: ignore[assignment]
        if i in (0, 1, 2):   # marketaux, rss direct, bse
            raw_direct.extend(items)
        elif i in (3, 4):    # rss macro, newsapi macro
            raw_macro.extend(items)

    for res in supply_results:
        if isinstance(res, Exception):
            logger.warning("Supply chain task failed: %s", res)
            continue
        raw_supply.extend(res)  # type: ignore[arg-type]

    def dedupe_and_sort(items: list[dict]) -> list[NewsItem]:
        seen: set[str] = set()
        unique: list[NewsItem] = []
        for item in sorted(items, key=lambda x: x["published_at"], reverse=True):
            key = hashlib.md5(item["title"].strip().lower().encode()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            try:
                unique.append(NewsItem(**item))
            except Exception as exc:
                logger.debug("Skipping malformed item: %s", exc)
        return unique

    direct_items = dedupe_and_sort(raw_direct)
    supply_items = dedupe_and_sort(raw_supply)
    macro_items = dedupe_and_sort(raw_macro)

    total = len(direct_items) + len(supply_items) + len(macro_items)

    return NewsResponse(
        stock=StockInfo(**stock),
        timerange=timerange,
        categories=NewsCategories(
            direct=direct_items,
            supply_chain=supply_items,
            macro=macro_items,
        ),
        total=total,
        fetched_at=datetime.now(timezone.utc),
    )
