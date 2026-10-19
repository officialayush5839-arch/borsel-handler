"""
URL Canonicalization and Validation Utilities
"""
import re
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_QUERY_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "fbclid", "gclid", "ref", "source", "ref_src", "soc_src",
    "mc_cid", "mc_eid"
}

TRUSTED_FINANCIAL_DOMAINS = {
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


def normalize_url(raw_url: str) -> str:
    """
    Transforms any raw article URL into a canonical format:
    - Lowercases scheme and netloc.
    - Strips tracking and session parameters (UTM, fbclid, etc.).
    - Removes fragments / anchor tags.
    - Preserves semantic query parameters sorted alphabetically.
    - Normalizes trailing slashes.
    """
    if not raw_url:
        return ""
    
    url = raw_url.strip()
    try:
        parsed = urlparse(url)
        scheme = (parsed.scheme or "https").lower()
        netloc = parsed.netloc.lower()

        # Remove default port if explicit
        if netloc.endswith(":80") and scheme == "http":
            netloc = netloc[:-3]
        elif netloc.endswith(":443") and scheme == "https":
            netloc = netloc[:-4]

        path = parsed.path or "/"
        # Normalize multiple slashes in path
        path = re.sub(r"/+", "/", path)
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]

        # Filter out tracking query parameters
        filtered_params = []
        if parsed.query:
            query_tuples = parse_qsl(parsed.query, keep_blank_values=False)
            filtered_params = [
                (k, v) for k, v in query_tuples
                if k.lower() not in TRACKING_QUERY_PARAMS
            ]
            filtered_params.sort(key=lambda x: x[0])

        new_query = urlencode(filtered_params) if filtered_params else ""
        canonical = urlunparse((scheme, netloc, path, "", new_query, ""))
        return canonical
    except Exception:
        return url


def is_trusted_url(url: str, allowlist: set[str] = None) -> bool:
    """Checks whether URL belongs to an approved trusted domain."""
    if allowlist is None:
        allowlist = TRUSTED_FINANCIAL_DOMAINS
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            return False
        return any(host == d or host.endswith("." + d) for d in allowlist)
    except Exception:
        return False
