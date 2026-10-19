# Borsel Handler — Optional Playwright Collector Integration Report

**Date:** 19 October 2026  
**Module:** `borsel_handler/collectors/playwright_collector.py`  
**Configuration:** `borsel_handler/config.py` (`ENABLE_PLAYWRIGHT=False`, `PLAYWRIGHT_TIMEOUT_SECONDS=30`)  
**Test Suite:** `tests/test_playwright_collector.py` (6 passed in 0.46s)  
**Status:** COMPLETE & VERIFIED

---

## 1. Architectural Strategy & Design Principles

Borsel Handler prioritizes lightweight, deterministic, and network-efficient data extraction via official APIs and RSS feeds. However, certain regulatory portals or corporate investor portals rely heavily on client-side JavaScript hydration (SPAs).

To address this without creating architectural brittleness or violating data collection guidelines:
1. **Strictly Optional Dependency:** Playwright is wrapped inside `try: ... except ImportError:` blocks. The platform runs normally and all standard collectors operate even if browser binaries are uninstalled or unsupported.
2. **Configuration Gating:** Playwright execution is disabled by default (`ENABLE_PLAYWRIGHT=False`). It can be selectively toggled on via `.env` or constructor flags for specific targets.
3. **No Stealth Evasion / Compliant Browsing:** Operates transparently with explicit Borsel Handler institutional user-agent identifiers without evasion plugins, residential proxies, or anti-captcha tools.
4. **Deterministic Resource Management:** Headless browser contexts and pages are strictly scoped inside `try: ... finally:` blocks, guaranteeing closure upon success or exception and preventing background process leaks.
5. **Decoupled DOM Parsing:** DOM extraction is isolated in `parse_rendered_html()`, consuming `clean_html_to_text()` from `borsel_handler.core.html_utils` and integrating with `CompanyResolver` and `classify_event`.

---

## 2. Technical Implementation Details

Located at [`borsel_handler/collectors/playwright_collector.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/collectors/playwright_collector.py):

### Class: `PlaywrightCollector(BaseCollector)`
- **Interface Conformance:** Implements `source_name` ("JavaScript Dynamic Announcement Collector"), `source_type` ("js_rendered_source"), and `async def fetch(cutoff)`.
- **Runtime Availability Check:** Exposes `is_available` to report environment status and `is_enabled` to reflect operational mode.
- **Resource Limits:** Configurable page timeout (default 30 seconds), headless execution flags (`--no-sandbox`, `--disable-gpu`, `--disable-dev-shm-usage`).
- **Normalized Data Generation:** Produces canonical `NormalizedNewsRecord` instances with extracted URLs, cleaned titles/snippets, resolved stock tickers, and categorized event tags.

---

## 3. Verification Evidence

### Automated Test Suite (`tests/test_playwright_collector.py`)
- `test_playwright_collector_init_defaults`: PASS (verifies disabled default state and proper metadata).
- `test_playwright_collector_disabled_returns_empty`: PASS (verifies zero overhead when disabled via config).
- `test_playwright_collector_unavailable_fallback`: PASS (verifies graceful degradation if library is missing).
- `test_playwright_collector_parse_rendered_html`: PASS (verifies DOM parsing of candidate articles into INFY and RELIANCE records with clean titles, canonical URLs, and categories).
- `test_playwright_collector_parse_empty_html`: PASS (verifies empty/None resilience).
- `test_playwright_lifecycle_mocked`: PASS (verifies deterministic invocation of `context.close()` and `browser.close()` in cleanup blocks).
- Result: 6 passed in 0.46s (0 failures, 0 errors).
