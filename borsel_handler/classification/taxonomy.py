"""
Financial Market Event Taxonomy
Adapted and normalized from Market Announcements idea_rules.py.
Fulfills Section 11 of Mega Prompt 2:
- Earnings and quarterly results
- IPOs and listings
- Mergers and acquisitions
- Dividends
- Corporate actions (splits, bonus, rights, buybacks)
- NSE/BSE exchange announcements
- RBI updates and monetary policy
- SEBI regulations, orders, and circulars
- Government economic policies (PIB, Ministry of Finance)
- General financial news & Macroeconomics
"""

TAXONOMY_GROUPS = [
    "Financial Results & Performance",
    "Restructuring & Strategic Deals",
    "Capital Structure & Corporate Actions",
    "IPOs & Capital Markets",
    "Operational Updates & Contracts",
    "Regulatory & Compliance",
    "Monetary & Economic Policy",
    "Corporate Governance",
    "General Financial Intelligence",
]

# Standardized Borsel Handler Category Enums / Keys
CATEGORY_EARNINGS = "earnings"
CATEGORY_DIVIDEND = "dividend"
CATEGORY_CORPORATE_ACTION = "corporate_action"
CATEGORY_ACQUISITION_MERGER = "acquisition_merger"
CATEGORY_IPO_LISTING = "ipo_listing"
CATEGORY_CAPEX_EXPANSION = "capex_expansion"
CATEGORY_ORDER_WIN = "order_win"
CATEGORY_REGULATORY_SEBI = "regulatory_sebi"
CATEGORY_RBI_UPDATE = "rbi_update"
CATEGORY_GOVERNMENT_POLICY = "government_policy"
CATEGORY_EXCHANGE_ANNOUNCEMENT = "exchange_announcement"
CATEGORY_BOARD_MANAGEMENT = "board_management"
CATEGORY_CREDIT_RATING = "credit_rating"
CATEGORY_MACRO_ECONOMIC = "macro_economic"
CATEGORY_GENERAL = "general_financial_news"

EVENT_RULES = {
    CATEGORY_ORDER_WIN: {
        "keywords": [
            ("letter of award", 2.0), ("receipt of order", 2.0), ("receives order", 2.0),
            ("bags order", 2.0), ("secures order", 1.5), ("order win", 1.5),
            ("awarded contract", 1.5), ("purchase order", 1.0), ("work order", 1.0),
            ("new order", 1.0), ("loa from", 1.5), ("contract from", 1.0),
            ("major order", 1.5), ("secured order", 1.5), ("bags mega order", 2.0),
            ("order worth", 1.5), ("contract worth", 1.5),
        ],
        "negative": ["cancellation of order", "order cancelled", "loss of order", "termination of order"],
        "category_hints": ["award of order", "receipt of order"],
    },
    CATEGORY_CAPEX_EXPANSION: {
        "keywords": [
            ("capital expenditure", 2.0), ("capacity expansion", 2.0), ("expansion of capacity", 1.5),
            ("greenfield", 1.5), ("brownfield", 1.5), ("new plant", 1.0),
            ("setting up a plant", 1.5), ("capex plan", 1.5), ("expand production", 1.0),
            ("enhance capacity", 1.0), ("commissioning of", 1.5),
        ],
        "negative": [],
        "category_hints": ["capital expenditure", "expansion", "commissioning"],
    },
    CATEGORY_ACQUISITION_MERGER: {
        "keywords": [
            ("acquisition of", 2.5), ("acquires", 2.0), ("to acquire", 2.0),
            ("completed acquisition", 2.0), ("share purchase agreement", 1.5),
            ("merger", 2.0), ("amalgamation", 2.0), ("de-merger", 2.0),
            ("scheme of arrangement", 1.5), ("takeover", 1.5), ("business transfer", 1.5),
        ],
        "negative": ["withdrawal of scheme", "merger rejected"],
        "category_hints": ["acquisition", "merger", "amalgamation"],
    },
    CATEGORY_IPO_LISTING: {
        "keywords": [
            ("initial public offering", 2.5), ("ipo", 2.5), ("drhp", 2.5),
            ("draft red herring prospectus", 2.5), ("ipo listing", 2.5), ("listing on bse", 2.0),
            ("listing on nse", 2.0), ("anchor investors", 2.0), ("price band", 2.0),
            ("issue opens", 1.5), ("issue subscribed", 1.5), ("listing date", 2.0),
            ("sme ipo", 2.0), ("public issue", 1.5),
        ],
        "negative": [],
        "category_hints": ["ipo", "listing", "public offering"],
    },
    CATEGORY_EARNINGS: {
        "keywords": [
            ("financial results", 2.5), ("quarterly results", 2.5), ("unaudited financial results", 2.5),
            ("audited financial results", 2.5), ("q1 results", 2.0), ("q2 results", 2.0),
            ("q3 results", 2.0), ("q4 results", 2.0), ("profit rises", 1.5),
            ("net profit jumps", 1.5), ("ebitda", 1.0), ("revenue up", 1.0),
            ("revenue rises", 1.5), ("pat increases", 1.5),
        ],
        "negative": [],
        "category_hints": ["financial results", "financials", "earnings"],
    },
    CATEGORY_DIVIDEND: {
        "keywords": [
            ("interim dividend", 2.5), ("final dividend", 2.5), ("special dividend", 2.5),
            ("recommended dividend", 2.0), ("declared dividend", 2.0), ("dividend of rs", 2.0),
            ("dividend payment", 2.0),
        ],
        "negative": [],
        "category_hints": ["dividend"],
    },
    CATEGORY_CORPORATE_ACTION: {
        "keywords": [
            ("bonus issue", 2.5), ("bonus shares", 2.5), ("stock split", 2.5),
            ("sub-division of shares", 2.5), ("record date", 2.0), ("rights issue", 2.0),
            ("buyback", 2.5), ("share buyback", 2.5), ("preferential allotment", 2.0),
            ("qip", 2.0), ("warrants allotment", 1.5),
        ],
        "negative": [],
        "category_hints": ["corporate action", "bonus", "split", "buyback"],
    },
    CATEGORY_REGULATORY_SEBI: {
        "keywords": [
            ("sebi circular", 2.5), ("sebi order", 2.5), ("sebi regulation", 2.5),
            ("show cause notice", 2.0), ("adjudication order", 2.0), ("settlement order", 2.0),
            ("regulatory approval", 2.0), ("nclt approval", 2.0), ("cci approval", 2.0),
            ("lodr regulations", 2.0), ("insider trading", 1.5),
        ],
        "negative": [],
        "category_hints": ["regulatory", "sebi", "legal"],
    },
    CATEGORY_RBI_UPDATE: {
        "keywords": [
            ("rbi policy", 2.5), ("reserve bank of india", 2.0), ("repo rate", 2.5),
            ("monetary policy committee", 2.5), ("rbi circular", 2.5), ("rbi guideline", 2.0),
            ("crr", 1.5), ("reverse repo", 1.5), ("prudential framework", 1.5),
        ],
        "negative": [],
        "category_hints": ["rbi", "monetary policy"],
    },
    CATEGORY_GOVERNMENT_POLICY: {
        "keywords": [
            ("union cabinet", 2.5), ("ministry of finance", 2.5), ("gst council", 2.5),
            ("press information bureau", 2.0), ("pli scheme", 2.5), ("budget outlay", 2.0),
            ("export import policy", 2.0), ("customs duty", 1.5), ("disinvestment", 2.0),
            ("economic policy", 2.0), ("fiscal policy", 2.0),
        ],
        "negative": [],
        "category_hints": ["pib", "government", "cabinet", "ministry of finance"],
    },
    CATEGORY_EXCHANGE_ANNOUNCEMENT: {
        "keywords": [
            ("corporate announcement", 2.0), ("disclosure under reg", 2.0), ("exchange notice", 1.5),
            ("asm framework", 2.0), ("gsm framework", 2.0), ("circuit breaker", 1.5),
            ("index rebalancing", 2.0), ("trading halt", 1.5),
        ],
        "negative": [],
        "category_hints": ["announcement", "disclosure", "filing"],
    },
    CATEGORY_BOARD_MANAGEMENT: {
        "keywords": [
            ("resignation of", 2.0), ("appointment of", 2.0), ("managing director", 1.5),
            ("chief executive officer", 1.5), ("ceo appointment", 2.0), ("cfo resignation", 2.0),
            ("key managerial personnel", 1.5), ("change in director", 1.5), ("board meeting outcome", 1.5),
        ],
        "negative": [],
        "category_hints": ["board", "director", "kmp", "appointment"],
    },
    CATEGORY_CREDIT_RATING: {
        "keywords": [
            ("credit rating", 2.5), ("crisil", 2.0), ("icra", 2.0), ("care ratings", 2.0),
            ("rating upgrade", 2.5), ("rating downgrade", 2.5), ("rating reaffirmed", 2.0),
        ],
        "negative": [],
        "category_hints": ["credit rating", "rating"],
    },
    CATEGORY_MACRO_ECONOMIC: {
        "keywords": [
            ("cpi inflation", 2.5), ("wpi inflation", 2.5), ("gdp growth", 2.5),
            ("iip data", 2.0), ("trade deficit", 2.0), ("forex reserves", 2.0),
        ],
        "negative": [],
        "category_hints": ["macro", "economy", "inflation", "gdp"],
    },
}
