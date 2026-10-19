"""
Unit tests for URL normalization and allowlisting.
"""
from borsel_handler.core.url_utils import normalize_url, is_trusted_url


def test_normalize_url_strips_utm_and_tracking_params():
    raw = "https://economictimes.indiatimes.com/news/article.cms?utm_source=twitter&utm_medium=social&utm_campaign=breaking&real_param=123"
    canonical = normalize_url(raw)
    assert "utm_source" not in canonical
    assert "utm_medium" not in canonical
    assert "utm_campaign" not in canonical
    assert "real_param=123" in canonical


def test_normalize_url_normalizes_case_and_slashes():
    raw = "HTTPS://WWW.LiveMint.com/Market/stocks///?fbclid=xyz#section2"
    canonical = normalize_url(raw)
    assert canonical.startswith("https://www.livemint.com/Market/stocks")
    assert "#section2" not in canonical
    assert "fbclid" not in canonical


def test_trusted_domains():
    assert is_trusted_url("https://economictimes.indiatimes.com/markets") is True
    assert is_trusted_url("https://www.bseindia.com/corporates/ann.html") is True
    assert is_trusted_url("https://api.bseindia.com/BseIndiaAPI") is True
    assert is_trusted_url("https://www.nseindia.com/api/corporate-announcements") is True
    assert is_trusted_url("https://malicious-scam-invest.xyz/pump-and-dump") is False
    assert is_trusted_url("not_a_valid_url") is False
