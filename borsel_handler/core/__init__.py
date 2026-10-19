from .models import NormalizedNewsRecord, NewsRecordResponse, SearchQuery, SearchResponse
from .url_utils import normalize_url, is_trusted_url

__all__ = [
    "NormalizedNewsRecord",
    "NewsRecordResponse",
    "SearchQuery",
    "SearchResponse",
    "normalize_url",
    "is_trusted_url",
]
