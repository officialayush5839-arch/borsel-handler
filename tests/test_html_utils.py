"""
Unit tests for robust HTML-to-text extraction in borsel_handler/core/html_utils.py.
"""

import pytest
from borsel_handler.core.html_utils import clean_html_to_text


def test_clean_html_none_and_empty():
    assert clean_html_to_text(None) == ""
    assert clean_html_to_text("") == ""
    assert clean_html_to_text("   \n\t  ") == ""


def test_clean_html_plain_text():
    raw = "Reserve Bank of India maintains repo rate at 6.50%."
    assert clean_html_to_text(raw) == raw


def test_clean_html_strips_scripts_and_styles():
    html_doc = """
    <html>
      <head>
        <style>body { background: #fff; } .hide { display: none; }</style>
        <script>console.log("analytics tracking code"); alert('xss');</script>
      </head>
      <body>
        <noscript>Please enable JavaScript</noscript>
        <h1>Tata Motors Reports Q2 Results</h1>
        <script>var x = 10;</script>
        <p>Consolidated net profit surged 35% YoY.</p>
        <svg><text>Ignored vector</text></svg>
      </body>
    </html>
    """
    cleaned = clean_html_to_text(html_doc)
    assert "Tata Motors Reports Q2 Results Consolidated net profit surged 35% YoY." == cleaned
    assert "analytics" not in cleaned
    assert "background" not in cleaned
    assert "JavaScript" not in cleaned
    assert "vector" not in cleaned


def test_clean_html_block_separators():
    html_doc = "<p>First paragraph.</p><p>Second paragraph.</p><div>Next div block.</div>"
    cleaned = clean_html_to_text(html_doc)
    assert cleaned == "First paragraph. Second paragraph. Next div block."
    # Ensure words are not concatenated
    assert "paragraph.Second" not in cleaned


def test_clean_html_entity_decoding():
    raw = "Reliance &amp; Adani &quot;Infra&quot; deal: &#39;Special&#39; dividend &gt; &lt; &euro;100 &amp; &#8377;500 &nbsp; crore"
    cleaned = clean_html_to_text(raw)
    assert cleaned == "Reliance & Adani \"Infra\" deal: 'Special' dividend > < €100 & ₹500 crore"


def test_clean_html_indic_scripts():
    hindi_text = "<p>भारतीय रिज़र्व बैंक (RBI) ने रेपो दर <b>6.5%</b> पर अपरिवर्तित रखी।</p>"
    cleaned = clean_html_to_text(hindi_text)
    assert cleaned == "भारतीय रिज़र्व बैंक (RBI) ने रेपो दर 6.5% पर अपरिवर्तित रखी।"


def test_clean_html_truncation():
    text = "<p>Infosys acquires London AI firm for strategic expansion into European enterprise cloud solutions.</p>"
    cleaned = clean_html_to_text(text, max_chars=40)
    assert len(cleaned) <= 40
    assert cleaned.endswith("...")
    assert not cleaned.endswith(" ...")

    # Short bound
    assert clean_html_to_text("Abcdefgh", max_chars=3) == "Abc"


def test_clean_html_malformed_html():
    malformed = "<div class='snippet'><b>Unclosed bold tag <p>broken paragraph <img src='test.jpg'></div>"
    cleaned = clean_html_to_text(malformed)
    assert cleaned == "Unclosed bold tag broken paragraph"
