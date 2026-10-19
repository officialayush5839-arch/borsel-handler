"""
Robust HTML-to-text cleaning and extraction utility for Borsel Handler.
Replaces fragile regex stripping across all financial news and regulatory collectors.
"""

import html
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Non-content tags to strip before text extraction
NON_CONTENT_TAGS = {
    "script",
    "style",
    "noscript",
    "header",
    "footer",
    "svg",
    "nav",
    "iframe",
    "object",
    "embed",
}


def clean_html_to_text(
    html_or_text: Optional[str],
    max_chars: Optional[int] = None,
) -> str:
    """
    Converts raw HTML snippets or unescaped text into clean, normalized plain text.

    Key guarantees:
    - Removes non-content elements (<script>, <style>, <noscript>, <svg>, <nav>, etc.).
    - Preserves spacing around block-level tags (<p>, <br>, <div>, <li>, <tr>).
    - Unescapes all standard and numeric HTML entities (&amp;, &quot;, &#39;, &nbsp;, etc.).
    - Preserves non-ASCII characters, Hindi / Indic scripts, and financial unicode symbols.
    - Normalizes multi-line and irregular whitespace to single spaces.
    - Optionally truncates at word boundaries with an ellipsis ('...') if max_chars is specified.
    """
    if not html_or_text or not isinstance(html_or_text, str):
        return ""

    raw = html_or_text.strip()
    if not raw:
        return ""

    try:
        soup = BeautifulSoup(raw, "html.parser")

        # Decompose non-content elements
        for tag in soup.find_all(NON_CONTENT_TAGS):
            tag.decompose()

        # Extract text with space separator across elements
        extracted = soup.get_text(separator=" ", strip=True)
    except Exception as exc:
        logger.warning("BeautifulSoup parsing failed on snippet (%s); falling back to regex: %s", exc, raw[:50])
        # Fallback: strip script and style blocks first
        cleaned = re.sub(r"<(script|style|noscript|svg|nav)[^>]*>.*?</\1>", " ", raw, flags=re.DOTALL | re.IGNORECASE)
        # Strip remaining HTML tags
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        extracted = cleaned

    # Unescape HTML entities (handles &nbsp;, &#39;, &amp;, &quot;, &lt;, &gt;, &rsquo;, etc.)
    text = html.unescape(extracted)

    # Replace non-breaking spaces and other irregular spaces
    text = text.replace("\xa0", " ").replace("\u200b", "")

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    if max_chars is not None and max_chars > 0 and len(text) > max_chars:
        if max_chars <= 3:
            return text[:max_chars]
        truncated = text[:max_chars]
        if " " in truncated:
            text = truncated.rsplit(" ", 1)[0] + "..."
        else:
            text = truncated[: max_chars - 3] + "..."

    return text
