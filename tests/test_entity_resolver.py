"""
Unit tests for CompanyResolver entity resolution.
"""
from borsel_handler.data.resolver import CompanyResolver


def test_single_symbol_resolution():
    text = "Tata Consultancy Services (TCS) reported robust growth in BFSI sector."
    resolved = CompanyResolver.resolve(text)
    assert len(resolved) == 1
    assert resolved[0].symbol == "TCS"
    assert resolved[0].name == "Tata Consultancy Services"
    assert resolved[0].sector == "Information Technology"


def test_multi_company_resolution():
    text = "IT giants TCS and Infosys sign joint research pact while HDFC Bank finances infrastructure."
    resolved = CompanyResolver.resolve(text)
    symbols = {r.symbol for r in resolved}
    assert "TCS" in symbols
    assert "INFY" in symbols
    assert "HDFCBANK" in symbols


def test_subword_false_positive_prevention():
    # 'DELT' should not match 'LT'
    text1 = "Delta Corp secures new operational license."
    resolved1 = CompanyResolver.resolve(text1)
    symbols1 = {r.symbol for r in resolved1}
    assert "LT" not in symbols1

    # Ambiguous token 'IT' or 'ON' alone should not falsely match ITC or ONGC
    text2 = "The committee went on to discuss general IT hardware policies."
    resolved2 = CompanyResolver.resolve(text2)
    symbols2 = {r.symbol for r in resolved2}
    assert "ONGC" not in symbols2


def test_alias_resolution():
    text = "L&T wins order worth Rs 2,500 crore from domestic client."
    resolved = CompanyResolver.resolve(text)
    assert len(resolved) == 1
    assert resolved[0].symbol == "LT"


def test_empty_input_fallback():
    assert CompanyResolver.resolve("") == []
    assert CompanyResolver.resolve_primary(None) is None


def test_common_word_and_negative_disambiguation():
    # Common noun 'coal' should not match Coal India Ltd
    res_coal = CompanyResolver.resolve("Global coal prices drop by 5% as thermal demand cools")
    assert "COALINDIA" not in {r.symbol for r in res_coal}

    # Common noun 'titan' should not match Titan Company Ltd
    res_titan = CompanyResolver.resolve("Tech titan Google faces antitrust scrutiny in European markets")
    assert "TITAN" not in {r.symbol for r in res_titan}

    # Military abbreviation 'Lt' should not match Larsen & Toubro
    res_lt = CompanyResolver.resolve("He was promoted to Lt Colonel in the armed forces")
    assert "LT" not in {r.symbol for r in res_lt}

    # Name 'Trent' should not match Trent Ltd
    res_trent = CompanyResolver.resolve("Trent Boult takes 4 wickets in championship match")
    assert "TRENT" not in {r.symbol for r in res_trent}

    # Verified positives for disambiguated entities
    assert "COALINDIA" in {r.symbol for r in CompanyResolver.resolve("Coal India reports 20% increase in production")}
    assert "TITAN" in {r.symbol for r in CompanyResolver.resolve("Titan Company reports 25% festive jewellery sales growth")}
    assert "TITAN" in {r.symbol for r in CompanyResolver.resolve("TITAN declares interim dividend of Rs 5 per share")}
    assert "TRENT" in {r.symbol for r in CompanyResolver.resolve("Trent Ltd and Zudio expand retail presence with 50 new stores")}
