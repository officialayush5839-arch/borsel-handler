# Borsel Handler — HTML Extraction Completion Report

**Date:** 19 October 2026  
**Module:** `borsel_handler/core/html_utils.py`  
**Test Suite:** `tests/test_html_utils.py` (8 passed) + Collector Regression (30 passed)  
**Status:** COMPLETE & VERIFIED

---

## 1. Overview and Problem Statement

Earlier collector implementations used fragile regular expressions (`re.sub(r"<[^>]+>", "", text)`) or fragmented BeautifulSoup snippets to clean raw HTML descriptions and titles. This legacy approach caused multiple defects:
1. `<script>` and `<style>` contents were leaked directly into text snippets if present in raw feeds or scraped markup.
2. Words in adjacent block elements (e.g. `<p>A</p><p>B</p>`) were mashed together without whitespace separators (`AB`).
3. HTML entities (`&amp;`, `&#39;`, `&quot;`, `&nbsp;`, `&#8377;`) were partially or inconsistently decoded.
4. Non-English and Indic scripts (e.g., Hindi updates from PIB or RBI) suffered encoding or truncation corruptions.
5. Inconsistent max-length slicing caused mid-word breaks or truncated sentences abruptly.

---

## 2. Technical Implementation

A centralized HTML processing module was implemented at [`borsel_handler/core/html_utils.py`](file:///c:/Users/ARYAN%20-%20AYUSH/OneDrive/Desktop/borsel%20handler/borsel_handler/core/html_utils.py):

### Core Function: `clean_html_to_text(html_or_text: Optional[str], max_chars: Optional[int] = None) -> str`
- **Non-Content Tag Removal:** Explicitly decomposes `<script>`, `<style>`, `<noscript>`, `<header>`, `<footer>`, `<svg>`, `<nav>`, `<iframe>`, `<object>`, and `<embed>` tags via BeautifulSoup before textual extraction.
- **Block Spacing Preservation:** Employs `soup.get_text(separator=" ", strip=True)` to ensure clean boundaries between paragraphs, table cells, and list items.
- **Entity Decoding:** Leverages Python's standard `html.unescape()` to decode all named and numeric entities cleanly.
- **Whitespace Normalization:** Standardizes multi-line breaks, non-breaking spaces (`\xa0`), and zero-width spaces (`\u200b`) into canonical single-space prose.
- **Word-Boundary Truncation:** If `max_chars` is specified and text exceeds this length, it truncates on word boundaries without chopping words, appending `...`.
- **Fault-Tolerant Fallback:** In the unlikely event BeautifulSoup encounters an unrecoverable exception, a regex-based fallback safely decomposes script/style blocks and cleans tags without crashing ingestion pipelines.

---

## 3. Collector Refactoring

All collectors were updated to consume `clean_html_to_text`:
- `borsel_handler/collectors/rss.py`: Title and snippet extraction refactored.
- `borsel_handler/collectors/nse.py`: `_clean_text` refactored to wrap `clean_html_to_text(text, max_chars=400)`.
- `borsel_handler/collectors/bse.py`: `_clean_text` refactored to wrap `clean_html_to_text(text, max_chars=400)`.
- `borsel_handler/collectors/rbi.py`: `_clean_text` refactored to wrap `clean_html_to_text(text, max_chars=450)`.
- `borsel_handler/collectors/pib.py`: `_clean_text` refactored to wrap `clean_html_to_text(text, max_chars=450)`.
- `borsel_handler/collectors/sebi.py`: `_clean_text` refactored to wrap `clean_html_to_text(text, max_chars=450)`.

---

## 4. Verification Evidence

### Test Suite Execution
`py -m pytest tests/test_html_utils.py tests/test_collectors.py tests/test_rbi_modern.py tests/test_pib_modern.py tests/test_bse_compliant.py`
- `tests/test_html_utils.py`: 8 passed
  - `test_clean_html_none_and_empty`
  - `test_clean_html_plain_text`
  - `test_clean_html_strips_scripts_and_styles`
  - `test_clean_html_block_separators`
  - `test_clean_html_entity_decoding`
  - `test_clean_html_indic_scripts`
  - `test_clean_html_truncation`
  - `test_clean_html_malformed_html`
- Regression suite: 22 collector tests passed.
- Total: 30 passed in 12.65s (0 failures, 0 errors).
