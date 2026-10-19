"""
Unit tests for optional Playwright collector (Task C).
Tests graceful degradation, disabled mode, DOM parsing, and deterministic resource lifecycle.
"""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from borsel_handler.collectors.playwright_collector import PlaywrightCollector, PLAYWRIGHT_AVAILABLE


@pytest.fixture
def sample_rendered_html():
    return """
    <!DOCTYPE html>
    <html>
      <head><title>Corporate Disclosures Dynamic</title></head>
      <body>
        <div class="announcements-container">
          <div class="announcement-item">
            <h4><a href="/disclosures/equity/infy-q2-2026.html">Infosys Ltd Announces Q2 Results and Dividend of Rs 21</a></h4>
            <p class="snippet-desc">The Board of Directors of Infosys declared an interim dividend and reported YoY profit increase.</p>
          </div>
          <div class="announcement-item">
            <h4><a href="/disclosures/equity/reliance-refinery.html">Reliance Industries commissions new green energy manufacturing plant in Gujarat</a></h4>
            <p class="snippet-desc">Reliance Industries announced operational commencement of its solar module facility.</p>
          </div>
          <div class="announcement-item">
            <span class="no-link">Notice without link tag</span>
          </div>
        </div>
      </body>
    </html>
    """


def test_playwright_collector_init_defaults():
    collector = PlaywrightCollector(enabled=False)
    assert collector.source_name == "JavaScript Dynamic Announcement Collector"
    assert collector.source_type == "js_rendered_source"
    assert not collector.is_enabled
    assert collector.is_available == PLAYWRIGHT_AVAILABLE


@pytest.mark.asyncio
async def test_playwright_collector_disabled_returns_empty():
    """When disabled via config or init, collector returns empty list without launching browser."""
    collector = PlaywrightCollector(target_urls=["https://example.com"], enabled=False)
    records = await collector.fetch()
    assert records == []


@pytest.mark.asyncio
async def test_playwright_collector_unavailable_fallback():
    """When Playwright library is absent, collector degrades gracefully without errors."""
    with patch("borsel_handler.collectors.playwright_collector.PLAYWRIGHT_AVAILABLE", False):
        collector = PlaywrightCollector(target_urls=["https://example.com"], enabled=True)
        records = await collector.fetch()
        assert records == []


def test_playwright_collector_parse_rendered_html(sample_rendered_html):
    """Verifies that parse_rendered_html extracts and normalizes records correctly."""
    collector = PlaywrightCollector()
    records = collector.parse_rendered_html(sample_rendered_html, base_url="https://www.bseindia.com")

    assert len(records) == 2

    infy_rec = records[0]
    assert "Infosys Ltd Announces Q2 Results" in infy_rec.title
    assert "Board of Directors of Infosys" in infy_rec.snippet
    assert infy_rec.canonical_url == "https://www.bseindia.com/disclosures/equity/infy-q2-2026.html"
    assert infy_rec.symbol == "INFY"
    assert infy_rec.category in ("earnings", "dividend")

    ril_rec = records[1]
    assert "Reliance Industries" in ril_rec.title
    assert ril_rec.symbol == "RELIANCE"
    assert ril_rec.canonical_url == "https://www.bseindia.com/disclosures/equity/reliance-refinery.html"


def test_playwright_collector_parse_empty_html():
    collector = PlaywrightCollector()
    assert collector.parse_rendered_html("", "https://example.com") == []
    assert collector.parse_rendered_html(None, "https://example.com") == []


@pytest.mark.asyncio
async def test_playwright_lifecycle_mocked():
    """Verifies that browser, context, and page are cleaned up in finally blocks."""
    mock_page = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    mock_page.content.return_value = "<article><a href='https://news.com/1'>Tata Motors launches EV platform</a></article>"
    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_playwright = AsyncMock()
    mock_playwright.chromium.launch.return_value = mock_browser

    mock_pw_context_manager = MagicMock()
    mock_pw_context_manager.__aenter__.return_value = mock_playwright
    mock_pw_context_manager.__aexit__.return_value = None

    with patch("borsel_handler.collectors.playwright_collector.async_playwright", return_value=mock_pw_context_manager):
        with patch("borsel_handler.collectors.playwright_collector.PLAYWRIGHT_AVAILABLE", True):
            collector = PlaywrightCollector(target_urls=["https://news.com/feed"], enabled=True)
            records = await collector.fetch()

            assert len(records) == 1
            assert "Tata Motors" in records[0].title

            # Ensure cleanup methods were called
            mock_context.close.assert_awaited_once()
            mock_browser.close.assert_awaited_once()
