"""
Unit tests for event classification engine.
"""
from borsel_handler.classification.classifier import classify_event
from borsel_handler.classification.taxonomy import (
    CATEGORY_EARNINGS, CATEGORY_ORDER_WIN, CATEGORY_CAPEX_EXPANSION,
    CATEGORY_DIVIDEND, CATEGORY_ACQUISITION_MERGER, CATEGORY_REGULATORY_SEBI,
    CATEGORY_RBI_UPDATE, CATEGORY_GENERAL, CATEGORY_IPO_LISTING,
    CATEGORY_GOVERNMENT_POLICY, CATEGORY_CORPORATE_ACTION, CATEGORY_MACRO_ECONOMIC
)


def test_classify_earnings():
    title = "Infosys Q4 Audited Financial Results: Net Profit Rises 12% to Rs 6,128 Cr"
    snippet = "Company declared financial results for the quarter ended March 31."
    cat, conf, tags = classify_event(title, snippet)
    assert cat == CATEGORY_EARNINGS
    assert conf >= 50.0
    assert any("financial results" in t or "q4 results" in t for t in tags)


def test_classify_order_win():
    title = "L&T Hydrocarbon Secures Major Order Win Worth Rs 4,500 Crore"
    snippet = "The company received letter of award from an international client."
    cat, conf, tags = classify_event(title, snippet)
    assert cat == CATEGORY_ORDER_WIN
    assert conf >= 40.0
    assert any("order win" in t or "letter of award" in t for t in tags)


def test_classify_order_win_negative_disqualification():
    title = "Cancellation of order for XYZ Infrastructure project"
    snippet = "Client issued formal termination of order due to project delays."
    cat, conf, tags = classify_event(title, snippet)
    assert cat != CATEGORY_ORDER_WIN


def test_classify_dividend():
    title = "TCS Board declares interim dividend of Rs 28 per share"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_DIVIDEND
    assert conf >= 50.0


def test_classify_acquisition():
    title = "Reliance Retail completes acquisition of 100% stake in Metro Cash & Carry"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_ACQUISITION_MERGER
    assert conf >= 40.0


def test_classify_sebi_regulatory():
    title = "SEBI circular on enhanced disclosure requirements for FPIs"
    snippet = "Markets regulator issued comprehensive circular regarding ultimate beneficiaries."
    cat, conf, tags = classify_event(title, snippet)
    assert cat == CATEGORY_REGULATORY_SEBI


def test_classify_rbi_update():
    title = "RBI monetary policy committee keeps repo rate unchanged at 6.5%"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_RBI_UPDATE


def test_classify_ipo_listing():
    title = "Swiggy Files Draft Red Herring Prospectus with SEBI for $1.2B Initial Public Offering"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_IPO_LISTING
    assert conf >= 50.0


def test_classify_government_policy():
    title = "Union Cabinet Approves Rs 24,000 Crore PLI Scheme for Advanced Chemistry Cells"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_GOVERNMENT_POLICY
    assert conf >= 50.0


def test_classify_corporate_action():
    title = "Titan Board Approves 1:10 Stock Split and Bonus Issue of Equity Shares"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_CORPORATE_ACTION
    assert conf >= 50.0


def test_classify_macro_economic():
    title = "India March CPI Inflation Cools to 4.85% While IIP Growth Rebounds"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_MACRO_ECONOMIC


def test_classify_unrelated_general_news():
    title = "Sensex gains 300 points in early morning trade amid positive global cues"
    cat, conf, tags = classify_event(title, "")
    assert cat == CATEGORY_GENERAL
