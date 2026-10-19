"""
Core Data Contracts and Pydantic Models for Borsel Handler
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class NormalizedNewsRecord(BaseModel):
    """
    Unified financial news and market announcement data contract.
    Fulfills all requirements of R09 & Section 3.
    """
    title: str = Field(..., description="Headline or announcement subject")
    snippet: str = Field(..., description="Summary, description, or excerpt")
    original_url: str = Field(..., description="Original URL or source link")
    canonical_url: str = Field(..., description="Canonical cleaned URL")
    published_at: datetime = Field(..., description="Publication timestamp in UTC")
    source_name: str = Field(..., description="Human-readable source name e.g. 'Economic Times'")
    source_type: str = Field(..., description="Category: 'rss', 'bse_announcement', 'nse_announcement'")
    source_record_id: Optional[str] = Field(None, description="Unique identifier from upstream source if present")
    company_name: Optional[str] = Field(None, description="Standardized company name if applicable")
    symbol: Optional[str] = Field(None, description="Stock ticker symbol (e.g. 'INFY')")
    sector: Optional[str] = Field(None, description="Industry sector (e.g. 'IT', 'Banking')")
    category: str = Field(default="general_financial_news", description="Taxonomy classification category")
    tags: List[str] = Field(default_factory=list, description="Categorization or metadata tags")
    confidence_score: float = Field(default=1.0, ge=0.0, le=100.0, description="Classification confidence")
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Ingestion UTC timestamp")
    raw_metadata: Dict[str, Any] = Field(default_factory=dict, description="Raw source payload preservation")

    @field_validator("published_at", "collected_at", mode="before")
    @classmethod
    def ensure_utc(cls, v: Any) -> datetime:
        if isinstance(v, str):
            from dateutil import parser
            dt = parser.parse(v)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(timezone.utc)
        return v


class NewsRecordResponse(BaseModel):
    id: int
    record_hash: str
    title: str
    snippet: str
    original_url: str
    canonical_url: str
    published_at: datetime
    collected_at: datetime
    source_name: str
    source_type: str
    source_record_id: Optional[str] = None
    company_name: Optional[str] = None
    symbol: Optional[str] = None
    sector: Optional[str] = None
    category: str
    confidence_score: float
    tags: List[str] = []
    raw_metadata: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)


class SearchQuery(BaseModel):
    query: Optional[str] = None
    symbol: Optional[str] = None
    sector: Optional[str] = None
    category: Optional[str] = None
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=500)


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[NewsRecordResponse]


class CollectionRunSummary(BaseModel):
    source_name: str
    status: str
    items_found: int
    items_inserted: int
    items_duplicate: int
    error_message: Optional[str] = None
    started_at: datetime
    finished_at: datetime
