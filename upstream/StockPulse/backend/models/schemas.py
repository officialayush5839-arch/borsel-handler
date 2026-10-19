from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: str


class NewsItem(BaseModel):
    title: str
    snippet: str
    url: str
    source: str
    published_at: datetime
    category: Literal["direct", "supply_chain", "macro"]
    why_it_matters: str


class NewsCategories(BaseModel):
    direct: list[NewsItem]
    supply_chain: list[NewsItem]
    macro: list[NewsItem]


class NewsResponse(BaseModel):
    stock: StockInfo
    timerange: str
    categories: NewsCategories
    total: int
    fetched_at: datetime
