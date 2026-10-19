"""
Optional Headless Browser Collector (Playwright) for JavaScript-Rendered Sources.

Key architectural properties:
- Strictly optional: does not break standard execution or CI if Playwright is uninstalled.
- Bounded execution: strict timeout (default 30s) and memory bounding.
- Deterministic cleanup: closes browser instances and contexts in finally blocks.
- Non-evasive compliance: standard browser user agent without WAF evasion or rotating proxies.
- Robust HTML parsing: utilizes clean_html_to_text for text normalization and sanitization.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from bs4 import BeautifulSoup

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.config import settings
from borsel_handler.core.html_utils import clean_html_to_text
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.core.url_utils import normalize_url
from borsel_handler.classification.classifier import classify_event
from borsel_handler.data.resolver import CompanyResolver

logger = logging.getLogger(__name__)

# Safe optional import of Playwright
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 BorselHandler-Playwright/1.0"
)


class PlaywrightCollector(BaseCollector):
    """
    Isolated collector for dynamic single-page applications (SPAs) or JS-hydrated
    regulatory and market announcement pages.
    """

    def __init__(
        self,
        target_urls: Optional[List[str]] = None,
        enabled: Optional[bool] = None,
        timeout_seconds: Optional[int] = None,
    ):
        self._target_urls = target_urls or []
        self._enabled = enabled if enabled is not None else settings.ENABLE_PLAYWRIGHT
        self._timeout_seconds = timeout_seconds or settings.PLAYWRIGHT_TIMEOUT_SECONDS

    @property
    def source_name(self) -> str:
        return "JavaScript Dynamic Announcement Collector"

    @property
    def source_type(self) -> str:
        return "js_rendered_source"

    @property
    def is_available(self) -> bool:
        """Indicates if Playwright library is present in the Python environment."""
        return PLAYWRIGHT_AVAILABLE

    @property
    def is_enabled(self) -> bool:
        """Indicates if Playwright execution is enabled in configuration."""
        return self._enabled

    def parse_rendered_html(self, html_content: str, base_url: str) -> List[NormalizedNewsRecord]:
        """
        Parses rendered DOM HTML into normalized news records.
        Decoupled from network requests to enable deterministic testing.
        """
        if not html_content:
            return []

        records: List[NormalizedNewsRecord] = []
        soup = BeautifulSoup(html_content, "html.parser")

        # Candidate item selectors commonly used on news and announcement portals
        items = soup.select("article, .announcement-item, .news-card, .disclosure-row, tr.announcement")
        if not items:
            # Fallback: find elements with headline links
            items = soup.select(".title a, h2 a, h3 a, h4 a")

        for item in items:
            link_tag = item if item.name == "a" else item.find("a")
            if not link_tag:
                continue

            raw_title = link_tag.get_text() or ""
            title = clean_html_to_text(raw_title, max_chars=300)
            if not title or len(title) < 10:
                continue

            href = link_tag.get("href") or ""
            if href.startswith("/"):
                from urllib.parse import urljoin
                full_url = urljoin(base_url, href)
            elif href.startswith("http"):
                full_url = href
            else:
                continue

            canonical_url = normalize_url(full_url)

            # Extract snippet
            snippet_tag = item.find(["p", "span", "div"], class_=lambda c: c and any(k in str(c).lower() for k in ["desc", "snippet", "summary", "text"]))
            raw_snippet = snippet_tag.get_text() if snippet_tag else ""
            snippet = clean_html_to_text(raw_snippet or title, max_chars=450)

            # Entity resolution
            resolved = CompanyResolver.resolve(f"{title} {snippet}")
            symbol = resolved[0].symbol if resolved else None
            company_name = resolved[0].name if resolved else None
            sector = resolved[0].sector if resolved else None

            category, confidence, tags = classify_event(title, snippet)

            rec = NormalizedNewsRecord(
                title=title,
                snippet=snippet,
                original_url=full_url,
                canonical_url=canonical_url,
                published_at=datetime.now(timezone.utc),
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id=canonical_url,
                company_name=company_name,
                symbol=symbol,
                sector=sector,
                category=category,
                tags=tags,
                confidence_score=confidence,
                collected_at=datetime.now(timezone.utc),
                raw_metadata={"base_url": base_url, "render_engine": "playwright_headless"},
            )
            records.append(rec)

        return records

    async def fetch(self, cutoff: Optional[datetime] = None) -> List[NormalizedNewsRecord]:
        """
        Renders target pages in a headless Chromium browser and extracts records.
        Exits gracefully if Playwright is disabled or not installed.
        """
        if not self.is_available:
            logger.info("Playwright library is not installed; skipping JS-rendered collection.")
            return []

        if not self.is_enabled:
            logger.info("Playwright collection is disabled (ENABLE_PLAYWRIGHT=False); skipping.")
            return []

        if not self._target_urls:
            logger.debug("No target URLs specified for Playwright dynamic collection.")
            return []

        all_records: List[NormalizedNewsRecord] = []

        try:
            async with async_playwright() as p:
                browser: Browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"]
                )
                try:
                    context: BrowserContext = await browser.new_context(
                        user_agent=USER_AGENT,
                        viewport={"width": 1280, "height": 800},
                        java_script_enabled=True,
                    )
                    try:
                        page: Page = await context.new_page()
                        page.set_default_timeout(self._timeout_seconds * 1000)

                        for url in self._target_urls:
                            try:
                                logger.info("Playwright navigating to %s", url)
                                await page.goto(url, wait_until="networkidle", timeout=self._timeout_seconds * 1000)
                                content = await page.content()
                                parsed = self.parse_rendered_html(content, url)
                                for rec in parsed:
                                    if cutoff and rec.published_at < cutoff:
                                        continue
                                    all_records.append(rec)
                            except Exception as nav_exc:
                                logger.warning("Playwright navigation error for %s: %s", url, nav_exc)
                    finally:
                        await context.close()
                finally:
                    await browser.close()

        except Exception as exc:
            logger.error("Playwright browser execution encountered an error: %s", exc)

        return all_records
