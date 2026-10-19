# Each entry defines what news matters for a given stock.
# To add a new stock: copy an existing entry and fill in the fields.
#
# Fields:
#   display_name       : human-readable company name
#   sector             : sector label
#   direct_keywords    : list of names/aliases — matched against article text for "Company News"
#   related_companies  : dict of {company_name: why_it_matters_label} for "Supply Chain" section
#   commodity_keywords : commodity/input price terms matched for "Supply Chain" section
#   macro_keywords     : sector/macro terms matched for "Sector & Macro" section

DEPENDENCY_MAP = {

    # ── IT SECTOR ──────────────────────────────────────────────────────────────

    "TCS": {
        "display_name": "Tata Consultancy Services",
        "sector": "IT",
        "direct_keywords": ["TCS", "Tata Consultancy", "Tata Consultancy Services"],
        "related_companies": {
            "Infosys":       "Direct competitor — results affect sector-wide sentiment",
            "Wipro":         "Direct competitor — results affect sector-wide sentiment",
            "HCL Tech":      "Direct competitor — results affect sector-wide sentiment",
            "Accenture":     "Global IT peer — guides industry deal flow and margins",
        },
        "commodity_keywords": ["USD INR", "dollar rupee", "rupee depreciation", "rupee appreciation"],
        "macro_keywords": [
            "IT sector", "NASSCOM", "H1-B visa", "US economy", "US recession",
            "tech layoffs", "AI spending", "cloud computing", "digital transformation",
            "US Federal Reserve", "IT hiring", "offshore outsourcing",
        ],
    },

    "INFY": {
        "display_name": "Infosys",
        "sector": "IT",
        "direct_keywords": ["Infosys", "INFY"],
        "related_companies": {
            "TCS":       "Direct competitor — results affect sector-wide sentiment",
            "Wipro":     "Direct competitor — results affect sector-wide sentiment",
            "HCL Tech":  "Direct competitor — results affect sector-wide sentiment",
            "Accenture": "Global IT peer — guides industry deal flow and margins",
        },
        "commodity_keywords": ["USD INR", "dollar rupee", "rupee depreciation"],
        "macro_keywords": [
            "IT sector", "NASSCOM", "H1-B visa", "US economy", "US recession",
            "tech layoffs", "AI spending", "cloud computing", "digital transformation",
            "US Federal Reserve", "IT hiring",
        ],
    },

    "WIPRO": {
        "display_name": "Wipro",
        "sector": "IT",
        "direct_keywords": ["Wipro"],
        "related_companies": {
            "TCS":       "Direct competitor — results affect sector-wide sentiment",
            "Infosys":   "Direct competitor — results affect sector-wide sentiment",
            "HCL Tech":  "Direct competitor — results affect sector-wide sentiment",
            "Accenture": "Global IT peer — guides industry deal flow and margins",
        },
        "commodity_keywords": ["USD INR", "dollar rupee", "rupee depreciation"],
        "macro_keywords": [
            "IT sector", "NASSCOM", "H1-B visa", "US economy", "US recession",
            "tech layoffs", "AI spending", "cloud computing", "digital transformation",
            "IT hiring",
        ],
    },

    "HCLTECH": {
        "display_name": "HCL Technologies",
        "sector": "IT",
        "direct_keywords": ["HCL Technologies", "HCL Tech", "HCLTECH"],
        "related_companies": {
            "TCS":       "Direct competitor — results affect sector-wide sentiment",
            "Infosys":   "Direct competitor — results affect sector-wide sentiment",
            "Wipro":     "Direct competitor — results affect sector-wide sentiment",
            "Accenture": "Global IT peer — guides industry deal flow and margins",
        },
        "commodity_keywords": ["USD INR", "dollar rupee", "rupee depreciation"],
        "macro_keywords": [
            "IT sector", "NASSCOM", "H1-B visa", "US economy", "US recession",
            "tech layoffs", "AI spending", "cloud computing", "IT hiring",
        ],
    },

    "TECHM": {
        "display_name": "Tech Mahindra",
        "sector": "IT",
        "direct_keywords": ["Tech Mahindra", "TechM", "TECHM"],
        "related_companies": {
            "TCS":      "Direct competitor — results affect sector-wide sentiment",
            "Infosys":  "Direct competitor — results affect sector-wide sentiment",
            "Wipro":    "Direct competitor — results affect sector-wide sentiment",
        },
        "commodity_keywords": ["USD INR", "dollar rupee", "rupee depreciation"],
        "macro_keywords": [
            "IT sector", "NASSCOM", "H1-B visa", "US economy", "telecom IT",
            "5G services", "tech layoffs", "AI spending", "IT hiring",
        ],
    },

    # ── BANKING ────────────────────────────────────────────────────────────────

    "HDFCBANK": {
        "display_name": "HDFC Bank",
        "sector": "Banking",
        "direct_keywords": ["HDFC Bank", "HDFCBANK"],
        "related_companies": {
            "ICICI Bank":  "Peer private bank — policy/regulation news affects the sector",
            "Axis Bank":   "Peer private bank — NPA and credit growth trends shared",
            "SBI":         "State bank leader — RBI policy impact benchmark",
            "Kotak Bank":  "Peer private bank — results affect sector sentiment",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "RBI monetary policy", "MPC meeting", "repo rate",
            "CRR", "SLR", "inflation", "NPA", "bad loans", "credit growth",
            "banking sector", "NBFC", "loan growth", "deposit rates",
            "banking regulation", "Basel norms", "RBI guidelines",
        ],
    },

    "ICICIBANK": {
        "display_name": "ICICI Bank",
        "sector": "Banking",
        "direct_keywords": ["ICICI Bank", "ICICIBANK"],
        "related_companies": {
            "HDFC Bank":   "Peer private bank — policy/regulation news affects the sector",
            "Axis Bank":   "Peer private bank — NPA and credit growth trends shared",
            "SBI":         "State bank leader — RBI policy impact benchmark",
            "Kotak Bank":  "Peer private bank — results affect sector sentiment",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "RBI monetary policy", "MPC meeting", "repo rate",
            "CRR", "inflation", "NPA", "bad loans", "credit growth",
            "banking sector", "NBFC", "loan growth", "deposit rates", "banking regulation",
        ],
    },

    "AXISBANK": {
        "display_name": "Axis Bank",
        "sector": "Banking",
        "direct_keywords": ["Axis Bank", "AXISBANK"],
        "related_companies": {
            "HDFC Bank":   "Peer private bank — policy/regulation news affects the sector",
            "ICICI Bank":  "Peer private bank — NPA and credit growth trends shared",
            "SBI":         "State bank leader — RBI policy impact benchmark",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "RBI monetary policy", "MPC meeting", "repo rate",
            "CRR", "inflation", "NPA", "bad loans", "credit growth",
            "banking sector", "loan growth", "deposit rates", "banking regulation",
        ],
    },

    "KOTAKBANK": {
        "display_name": "Kotak Mahindra Bank",
        "sector": "Banking",
        "direct_keywords": ["Kotak Mahindra Bank", "Kotak Bank", "KOTAKBANK"],
        "related_companies": {
            "HDFC Bank":   "Peer private bank — policy/regulation news affects the sector",
            "ICICI Bank":  "Peer private bank — NPA and credit growth trends shared",
            "SBI":         "State bank leader — RBI policy impact benchmark",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "RBI monetary policy", "MPC meeting", "repo rate",
            "CRR", "inflation", "NPA", "bad loans", "credit growth",
            "banking sector", "loan growth", "deposit rates",
        ],
    },

    "INDUSINDBK": {
        "display_name": "IndusInd Bank",
        "sector": "Banking",
        "direct_keywords": ["IndusInd Bank", "INDUSINDBK"],
        "related_companies": {
            "HDFC Bank":  "Peer private bank — sector-wide credit and NPA trends",
            "ICICI Bank": "Peer private bank — sector-wide credit and NPA trends",
            "Axis Bank":  "Peer private bank — sector-wide credit and NPA trends",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "MPC meeting", "repo rate", "CRR", "inflation",
            "NPA", "bad loans", "credit growth", "banking sector", "microfinance",
            "vehicle loans", "commercial vehicle", "loan growth",
        ],
    },

    "SBIN": {
        "display_name": "State Bank of India",
        "sector": "Banking",
        "direct_keywords": ["State Bank of India", "SBI", "SBIN"],
        "related_companies": {
            "HDFC Bank":   "Peer bank — private sector results set sector tone",
            "ICICI Bank":  "Peer bank — private sector results set sector tone",
            "Bank of Baroda": "Public sector peer — government banking policy shared",
            "Punjab National Bank": "Public sector peer — NPA and government scheme impacts shared",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "RBI monetary policy", "MPC meeting", "repo rate",
            "CRR", "inflation", "NPA", "bad loans", "credit growth",
            "banking sector", "government bank", "PSU bank", "recapitalisation",
            "priority sector lending", "Jan Dhan", "Mudra loans",
        ],
    },

    # ── FINANCE / NBFC / INSURANCE ─────────────────────────────────────────────

    "BAJFINANCE": {
        "display_name": "Bajaj Finance",
        "sector": "Finance",
        "direct_keywords": ["Bajaj Finance", "BFL", "BAJFINANCE"],
        "related_companies": {
            "Bajaj Finserv":  "Parent company — corporate actions directly impact Bajaj Finance",
            "HDFC Bank":      "Peer lender — credit growth and NPA trends shared",
            "Shriram Finance":"Peer NBFC — RBI NBFC guidelines shared",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "NBFC", "RBI NBFC", "consumer lending", "EMI",
            "retail loans", "credit growth", "NPA", "digital lending",
            "personal loans", "two wheeler loans", "consumer durable loans",
            "MPC meeting", "inflation",
        ],
    },

    "BAJAJFINSV": {
        "display_name": "Bajaj Finserv",
        "sector": "Finance",
        "direct_keywords": ["Bajaj Finserv", "BAJAJFINSV"],
        "related_companies": {
            "Bajaj Finance":  "Subsidiary — primary earnings contributor",
            "Bajaj Allianz":  "Insurance subsidiary — premium growth affects revenue",
            "HDFC Life":      "Insurance sector peer — IRDAI regulation shared",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "RBI repo rate", "NBFC", "consumer lending", "credit growth",
            "insurance sector", "IRDAI", "health insurance", "MPC meeting",
        ],
    },

    "HDFCLIFE": {
        "display_name": "HDFC Life Insurance",
        "sector": "Insurance",
        "direct_keywords": ["HDFC Life", "HDFCLIFE"],
        "related_companies": {
            "SBI Life":          "Direct peer — IRDAI regulation and product launches affect sector",
            "ICICI Prudential":  "Direct peer — premium growth and margin trends shared",
            "LIC":               "Dominant market player — market share and product benchmarks",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "IRDAI", "insurance sector", "insurance penetration", "life insurance",
            "equity market performance", "interest rates", "annuity products",
            "tax benefits insurance", "budget insurance",
        ],
    },

    "SBILIFE": {
        "display_name": "SBI Life Insurance",
        "sector": "Insurance",
        "direct_keywords": ["SBI Life", "SBILIFE"],
        "related_companies": {
            "HDFC Life":         "Direct peer — IRDAI regulation and product trends shared",
            "ICICI Prudential":  "Direct peer — premium growth trends shared",
            "LIC":               "Dominant market player — market share benchmarks",
        },
        "commodity_keywords": [],
        "macro_keywords": [
            "IRDAI", "insurance sector", "insurance penetration", "life insurance",
            "equity market performance", "interest rates", "annuity products",
            "tax benefits insurance",
        ],
    },

    "SHRIRAMFIN": {
        "display_name": "Shriram Finance",
        "sector": "Finance",
        "direct_keywords": ["Shriram Finance", "Shriram Transport", "SHRIRAMFIN"],
        "related_companies": {
            "Bajaj Finance":  "Peer NBFC — RBI NBFC guidelines and credit trends shared",
            "Mahindra Finance":"Peer rural NBFC — vehicle loan and rural credit trends shared",
        },
        "commodity_keywords": ["commercial vehicle", "used vehicle", "truck prices"],
        "macro_keywords": [
            "NBFC", "RBI NBFC", "vehicle loans", "commercial vehicle finance",
            "used vehicle market", "truck market", "repo rate", "NPA",
            "rural economy", "infrastructure spending",
        ],
    },

    # ── AUTOMOBILE ─────────────────────────────────────────────────────────────

    "MARUTI": {
        "display_name": "Maruti Suzuki",
        "sector": "Automobile",
        "direct_keywords": ["Maruti Suzuki", "MSIL", "Maruti", "Suzuki India"],
        "related_companies": {
            "JSW Steel":        "Steel is a key input — price hikes raise manufacturing cost",
            "Tata Steel":       "Key flat steel supplier for auto body panels",
            "Hindalco":         "Aluminium supplier for engine and body components",
            "Bosch India":      "Supplies fuel injection systems and EV components",
            "Minda Industries": "Supplies switches, sensors and lighting systems",
            "Motherson Sumi":   "Major wiring harness and mirror supplier",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices", "semiconductor chips", "auto components"],
        "macro_keywords": [
            "auto sales", "passenger vehicle sales", "EV policy", "vehicle scrappage",
            "auto sector", "RBI interest rate", "auto loan", "GST automobile",
            "petrol prices", "CNG prices", "FAME subsidy",
        ],
    },

    "BAJAJ-AUTO": {
        "display_name": "Bajaj Auto",
        "sector": "Automobile",
        "direct_keywords": ["Bajaj Auto", "BAJAJ-AUTO"],
        "related_companies": {
            "Hero MotoCorp":    "Direct two-wheeler competitor — market share data affects both",
            "TVS Motor":        "Direct two-wheeler competitor — market share data affects both",
            "Bosch India":      "Supplies fuel injection and engine management systems",
            "Minda Industries": "Supplies switches, sensors and lighting systems",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices", "auto components"],
        "macro_keywords": [
            "two wheeler sales", "motorcycle sales", "EV two wheeler", "EV policy",
            "FAME subsidy", "auto sector", "rural demand", "petrol prices",
            "auto loan", "GST automobile", "vehicle scrappage",
        ],
    },

    "HEROMOTOCO": {
        "display_name": "Hero MotoCorp",
        "sector": "Automobile",
        "direct_keywords": ["Hero MotoCorp", "Hero Honda", "HEROMOTOCO"],
        "related_companies": {
            "Bajaj Auto":       "Direct two-wheeler competitor — market share data affects both",
            "TVS Motor":        "Direct two-wheeler competitor — market share data affects both",
            "Bosch India":      "Supplies engine management and ABS systems",
            "Minda Industries": "Supplies electrical components and switches",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices", "auto components"],
        "macro_keywords": [
            "two wheeler sales", "motorcycle sales", "EV two wheeler", "EV policy",
            "FAME subsidy", "auto sector", "rural demand", "petrol prices",
            "auto loan", "GST automobile",
        ],
    },

    "EICHERMOT": {
        "display_name": "Eicher Motors",
        "sector": "Automobile",
        "direct_keywords": ["Eicher Motors", "Royal Enfield", "EICHERMOT"],
        "related_companies": {
            "Bajaj Auto":       "Two-wheeler peer — premium motorcycle segment overlap",
            "Hero MotoCorp":    "Two-wheeler peer — general motorcycle demand trends shared",
            "Bosch India":      "Supplies fuel injection and emission systems",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices"],
        "macro_keywords": [
            "two wheeler sales", "motorcycle sales", "premium motorcycle", "EV policy",
            "auto sector", "VECV", "commercial vehicle", "petrol prices", "auto loan",
        ],
    },

    "TATAMOTORS": {
        "display_name": "Tata Motors",
        "sector": "Automobile",
        "direct_keywords": ["Tata Motors", "TATAMOTORS", "Jaguar Land Rover", "JLR"],
        "related_companies": {
            "JSW Steel":        "Steel is a key input for vehicle manufacturing",
            "Tata Steel":       "Group company — flat steel supplier for auto body",
            "Bosch India":      "Supplies braking, engine and EV powertrain components",
            "Motherson Sumi":   "Major wiring and interior components supplier",
            "Minda Industries": "Supplies electrical systems",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices", "semiconductor chips", "lithium prices", "EV battery"],
        "macro_keywords": [
            "auto sales", "passenger vehicle sales", "commercial vehicle sales",
            "EV policy", "FAME subsidy", "EV charging", "auto sector",
            "UK economy", "Europe auto market", "JLR sales",
            "petrol prices", "diesel prices", "auto loan",
        ],
    },

    "M&M": {
        "display_name": "Mahindra & Mahindra",
        "sector": "Automobile",
        "direct_keywords": ["Mahindra", "M&M", "Mahindra & Mahindra"],
        "related_companies": {
            "JSW Steel":        "Steel is a key input for vehicle manufacturing",
            "Tata Steel":       "Key flat steel supplier for SUV body panels",
            "Bosch India":      "Supplies fuel injection and EV components",
            "Motherson Sumi":   "Major wiring harness and component supplier",
        },
        "commodity_keywords": ["steel prices", "aluminium prices", "rubber prices", "tractor", "farm equipment"],
        "macro_keywords": [
            "auto sales", "SUV sales", "tractor sales", "farm equipment",
            "EV policy", "FAME subsidy", "auto sector", "rural demand",
            "monsoon", "agriculture", "petrol prices", "diesel prices", "auto loan",
        ],
    },

    # ── FMCG ───────────────────────────────────────────────────────────────────

    "HINDUNILVR": {
        "display_name": "Hindustan Unilever",
        "sector": "FMCG",
        "direct_keywords": ["Hindustan Unilever", "HUL", "HINDUNILVR"],
        "related_companies": {
            "ITC":           "Direct FMCG peer — consumer demand and inflation trends shared",
            "Nestle India":  "FMCG peer — urban consumption trends shared",
            "Dabur India":   "FMCG peer — rural demand and raw material trends shared",
            "Procter & Gamble": "Global parent Unilever's competitor — input cost benchmarks",
        },
        "commodity_keywords": ["palm oil prices", "crude palm oil", "wheat prices", "sugar prices", "milk prices", "packaging costs"],
        "macro_keywords": [
            "FMCG sector", "rural demand", "urban consumption", "inflation",
            "GST FMCG", "monsoon", "rural income", "consumer staples",
            "commodity prices", "input costs FMCG", "consumer spending",
        ],
    },

    "ITC": {
        "display_name": "ITC Ltd",
        "sector": "FMCG",
        "direct_keywords": ["ITC Ltd", "ITC", "ITC Limited"],
        "related_companies": {
            "Hindustan Unilever": "Direct FMCG peer — consumer demand trends shared",
            "Nestle India":       "FMCG peer — packaged food segment overlap",
            "Godfrey Phillips":   "Tobacco sector peer — cigarette regulation and taxation shared",
        },
        "commodity_keywords": ["tobacco prices", "wheat prices", "palm oil prices", "paper prices", "agri commodity"],
        "macro_keywords": [
            "cigarette tax", "tobacco regulation", "GST cigarette", "sin tax",
            "FMCG sector", "rural demand", "agri business", "hotel sector",
            "consumer spending", "budget FMCG", "inflation",
        ],
    },

    "BRITANNIA": {
        "display_name": "Britannia Industries",
        "sector": "FMCG",
        "direct_keywords": ["Britannia", "Britannia Industries"],
        "related_companies": {
            "Hindustan Unilever": "FMCG sector peer — consumer demand and cost trends shared",
            "ITC":                "FMCG sector peer — packaged food overlap",
            "Nestle India":       "Packaged food peer — urban consumption trends shared",
        },
        "commodity_keywords": ["wheat prices", "sugar prices", "milk prices", "palm oil prices", "packaging costs", "flour prices"],
        "macro_keywords": [
            "FMCG sector", "biscuits market", "bakery market", "rural demand",
            "urban consumption", "inflation", "GST FMCG",
            "consumer spending", "input costs",
        ],
    },

    "NESTLEIND": {
        "display_name": "Nestle India",
        "sector": "FMCG",
        "direct_keywords": ["Nestle India", "Nestle", "NESTLEIND"],
        "related_companies": {
            "Hindustan Unilever": "FMCG sector peer — consumer demand and cost trends shared",
            "Britannia":          "Packaged food peer — urban consumption trends shared",
            "ITC":                "FMCG peer — packaged food overlap",
        },
        "commodity_keywords": ["milk prices", "wheat prices", "sugar prices", "cocoa prices", "palm oil prices"],
        "macro_keywords": [
            "FMCG sector", "packaged food", "infant nutrition", "noodles market",
            "urban consumption", "inflation", "GST FMCG",
            "consumer spending", "input costs",
        ],
    },

    "TATACONSUM": {
        "display_name": "Tata Consumer Products",
        "sector": "FMCG",
        "direct_keywords": ["Tata Consumer", "Tata Consumer Products", "TATACONSUM", "Tata Tea", "Tata Salt"],
        "related_companies": {
            "Hindustan Unilever": "FMCG sector peer — consumer demand trends shared",
            "ITC":                "FMCG peer — packaged food segment overlap",
            "Starbucks India":    "JV partner — premium beverage market indicator",
        },
        "commodity_keywords": ["tea prices", "coffee prices", "salt prices", "spice prices", "commodity agri"],
        "macro_keywords": [
            "FMCG sector", "tea market", "beverage market", "rural demand",
            "urban consumption", "inflation", "GST FMCG",
            "consumer spending", "monsoon", "plantation sector",
        ],
    },

    # ── PHARMA ─────────────────────────────────────────────────────────────────

    "SUNPHARMA": {
        "display_name": "Sun Pharmaceutical",
        "sector": "Pharma",
        "direct_keywords": ["Sun Pharma", "Sun Pharmaceutical", "SUNPHARMA"],
        "related_companies": {
            "Cipla":         "Pharma peer — USFDA and regulatory trends shared",
            "Dr Reddy's":    "Pharma peer — US generics market trends shared",
            "Lupin":         "Pharma peer — US generics and USFDA actions shared",
            "Divi's Labs":   "API supplier — active pharmaceutical ingredient cost input",
        },
        "commodity_keywords": ["API prices", "active pharmaceutical ingredient", "chemical prices"],
        "macro_keywords": [
            "USFDA", "FDA approval", "FDA warning letter", "FDA import alert",
            "US generics market", "pharma regulation", "patent expiry",
            "drug pricing", "Medicaid", "US healthcare policy",
            "clinical trial", "pharma sector", "CDSCO",
        ],
    },

    "CIPLA": {
        "display_name": "Cipla",
        "sector": "Pharma",
        "direct_keywords": ["Cipla"],
        "related_companies": {
            "Sun Pharma":    "Pharma peer — USFDA and regulatory trends shared",
            "Dr Reddy's":    "Pharma peer — US generics market trends shared",
            "Divi's Labs":   "API supplier — active pharmaceutical ingredient cost input",
        },
        "commodity_keywords": ["API prices", "active pharmaceutical ingredient", "chemical prices"],
        "macro_keywords": [
            "USFDA", "FDA approval", "FDA warning letter", "FDA import alert",
            "US generics market", "pharma regulation", "patent expiry",
            "drug pricing", "US healthcare", "pharma sector", "CDSCO",
        ],
    },

    "DRREDDY": {
        "display_name": "Dr Reddy's Laboratories",
        "sector": "Pharma",
        "direct_keywords": ["Dr Reddy", "Dr. Reddy", "Dr Reddy's Laboratories", "DRREDDY"],
        "related_companies": {
            "Sun Pharma":    "Pharma peer — USFDA and US generics trends shared",
            "Cipla":         "Pharma peer — US generics market trends shared",
            "Divi's Labs":   "API supplier — active pharmaceutical ingredient cost input",
        },
        "commodity_keywords": ["API prices", "active pharmaceutical ingredient", "chemical prices"],
        "macro_keywords": [
            "USFDA", "FDA approval", "FDA warning letter", "FDA import alert",
            "US generics market", "pharma regulation", "patent expiry",
            "drug pricing", "US healthcare", "pharma sector", "CDSCO",
            "Russia pharma", "emerging markets pharma",
        ],
    },

    # ── ENERGY / OIL & GAS ─────────────────────────────────────────────────────

    "RELIANCE": {
        "display_name": "Reliance Industries",
        "sector": "Energy",
        "direct_keywords": ["Reliance Industries", "Reliance", "RIL", "Jio", "Reliance Retail"],
        "related_companies": {
            "ONGC":          "Upstream oil peer — crude production and pricing trends shared",
            "BPCL":          "Downstream refining peer — refining margin trends shared",
            "Bharti Airtel": "Telecom competitor to Jio — subscriber and ARPU data matters",
            "Vodafone Idea": "Telecom competitor to Jio — spectrum and subscriber data matters",
        },
        "commodity_keywords": ["crude oil", "Brent crude", "WTI crude", "natural gas", "LNG prices", "refining margins", "petrochemical prices"],
        "macro_keywords": [
            "oil prices", "OPEC", "OPEC+ production", "crude oil supply",
            "petrol prices", "diesel prices", "government fuel pricing",
            "5G spectrum", "Jio subscriber", "telecom ARPU",
            "retail sector India", "FDI retail", "Reliance Jio",
        ],
    },

    "ONGC": {
        "display_name": "Oil & Natural Gas Corp",
        "sector": "Energy",
        "direct_keywords": ["ONGC", "Oil and Natural Gas", "Oil & Natural Gas"],
        "related_companies": {
            "BPCL":      "Downstream customer — crude offtake and pricing linked",
            "Reliance":  "Private sector peer — upstream oil & gas trends shared",
            "IOC":       "Downstream customer and peer — government pricing policy shared",
        },
        "commodity_keywords": ["crude oil", "Brent crude", "WTI crude", "natural gas", "LNG", "oil field"],
        "macro_keywords": [
            "oil prices", "OPEC", "OPEC+ production", "crude oil production",
            "government fuel pricing", "petrol prices", "diesel prices",
            "upstream oil", "oil exploration", "natural gas price",
            "APM gas price", "windfall tax",
        ],
    },

    "BPCL": {
        "display_name": "Bharat Petroleum",
        "sector": "Energy",
        "direct_keywords": ["BPCL", "Bharat Petroleum", "Bharat Petroleum Corp"],
        "related_companies": {
            "ONGC":      "Upstream crude supplier — crude price directly impacts refining margins",
            "IOC":       "Public sector peer — government fuel pricing policy shared",
            "Reliance":  "Private refining peer — refining margin benchmark",
        },
        "commodity_keywords": ["crude oil", "Brent crude", "WTI crude", "refining margins", "petrol", "diesel", "LPG prices"],
        "macro_keywords": [
            "oil prices", "petrol prices", "diesel prices", "LPG subsidy",
            "government fuel pricing", "OPEC", "refining sector",
            "fuel subsidy", "marketing margins", "downstream oil",
        ],
    },

    # ── METALS & MINING ────────────────────────────────────────────────────────

    "JINDALSTEL": {
        "display_name": "Jindal Steel & Power",
        "sector": "Metals",
        "direct_keywords": ["Jindal Steel", "JSPL", "Jindal Steel & Power", "JINDALSTEL"],
        "related_companies": {
            "JSW Steel":     "Direct steel competitor — HRC/structural steel price trends shared",
            "Tata Steel":    "Steel sector peer — margin and demand outlook shared",
            "NMDC":          "Iron ore supplier — ore price movements directly impact input cost",
            "Coal India":    "Coking coal supplier — coal price affects steel manufacturing cost",
            "SAIL":          "Public sector steel peer — government policy and pricing impacts shared",
        },
        "commodity_keywords": ["steel prices", "iron ore prices", "coking coal", "HRC prices", "DRI prices", "sponge iron", "structural steel"],
        "macro_keywords": [
            "steel sector", "China steel", "steel imports", "anti-dumping duty steel",
            "infrastructure spending", "government capex", "construction demand",
            "real estate demand", "PLI steel", "power sector expansion",
        ],
    },

    "JSWSTEEL": {
        "display_name": "JSW Steel",
        "sector": "Metals",
        "direct_keywords": ["JSW Steel", "JSWSTEEL"],
        "related_companies": {
            "Tata Steel":    "Direct competitor — steel price and margin trends shared",
            "SAIL":          "Public sector steel peer — government policy impacts shared",
            "NMDC":          "Iron ore supplier — ore price movements directly impact cost",
            "Coal India":    "Coking coal input supplier — coal price affects steel cost",
        },
        "commodity_keywords": ["steel prices", "HRC prices", "iron ore prices", "coking coal", "scrap metal", "hot rolled coil"],
        "macro_keywords": [
            "steel sector", "China steel", "steel imports", "anti-dumping duty",
            "infrastructure spending", "construction demand", "real estate demand",
            "auto sector steel", "government capex", "PLI steel",
        ],
    },

    "TATASTEEL": {
        "display_name": "Tata Steel",
        "sector": "Metals",
        "direct_keywords": ["Tata Steel", "TATASTEEL"],
        "related_companies": {
            "JSW Steel":     "Direct competitor — steel price and margin trends shared",
            "SAIL":          "Public sector steel peer — government policy impacts shared",
            "NMDC":          "Iron ore supplier — ore price movements directly impact cost",
            "Coal India":    "Coking coal input supplier — coal price affects steel cost",
        },
        "commodity_keywords": ["steel prices", "HRC prices", "iron ore prices", "coking coal", "scrap metal", "UK steel"],
        "macro_keywords": [
            "steel sector", "China steel", "steel imports", "anti-dumping duty",
            "infrastructure spending", "construction demand", "government capex",
            "UK economy", "Europe steel", "auto sector steel",
        ],
    },

    "HINDALCO": {
        "display_name": "Hindalco Industries",
        "sector": "Metals",
        "direct_keywords": ["Hindalco", "Hindalco Industries", "Novelis"],
        "related_companies": {
            "Nalco":         "Aluminium sector peer — aluminium price and policy trends shared",
            "Vedanta":       "Aluminium and metals peer — commodity price trends shared",
            "Coal India":    "Power coal supplier — energy cost input for smelting",
        },
        "commodity_keywords": ["aluminium prices", "copper prices", "bauxite prices", "alumina prices", "LME aluminium"],
        "macro_keywords": [
            "aluminium sector", "LME prices", "China aluminium", "aluminium imports",
            "anti-dumping duty aluminium", "auto sector aluminium",
            "packaging aluminium", "US tariffs aluminium",
            "Novelis earnings", "EV aluminium demand",
        ],
    },

    "COALINDIA": {
        "display_name": "Coal India",
        "sector": "Metals",
        "direct_keywords": ["Coal India", "CIL", "COALINDIA"],
        "related_companies": {
            "NTPC":          "Largest coal customer — power generation demand drives coal offtake",
            "Tata Power":    "Coal customer — coal supply agreements and pricing",
            "JSW Steel":     "Coking coal customer — coal supply agreements",
        },
        "commodity_keywords": ["coal prices", "thermal coal", "coking coal", "coal production", "coal imports"],
        "macro_keywords": [
            "coal sector", "power demand", "electricity generation",
            "coal mine", "coal auction", "coal import duty",
            "renewable energy impact on coal", "government energy policy",
            "coal linkage", "e-auction coal",
        ],
    },

    # ── CEMENT ─────────────────────────────────────────────────────────────────

    "ULTRACEMCO": {
        "display_name": "UltraTech Cement",
        "sector": "Cement",
        "direct_keywords": ["UltraTech", "UltraTech Cement", "ULTRACEMCO"],
        "related_companies": {
            "Shree Cement":  "Direct cement competitor — pricing and volume trends shared",
            "ACC":           "Direct cement competitor — pricing and volume trends shared",
            "Ambuja Cement": "Direct cement competitor — pricing and volume trends shared",
            "Coal India":    "Coal supplier — fuel cost is largest input after limestone",
        },
        "commodity_keywords": ["cement prices", "coal prices", "pet coke prices", "limestone prices", "freight costs"],
        "macro_keywords": [
            "cement sector", "infrastructure spending", "housing demand",
            "real estate market", "government capex", "road construction",
            "NHAI projects", "smart cities", "affordable housing",
            "budget infrastructure", "construction sector",
        ],
    },

    "GRASIM": {
        "display_name": "Grasim Industries",
        "sector": "Cement",
        "direct_keywords": ["Grasim", "Grasim Industries"],
        "related_companies": {
            "UltraTech Cement": "Subsidiary — UltraTech results directly flow to Grasim P&L",
            "Shree Cement":     "Cement sector peer — pricing trends shared",
            "Aditya Birla":     "Group company — conglomerate decisions affect Grasim",
        },
        "commodity_keywords": ["cement prices", "coal prices", "pet coke prices", "VSF prices", "caustic soda"],
        "macro_keywords": [
            "cement sector", "infrastructure spending", "housing demand",
            "government capex", "VSF market", "viscose staple fibre",
            "textiles sector", "paint sector", "Birla",
        ],
    },

    # ── TELECOM ────────────────────────────────────────────────────────────────

    "BHARTIARTL": {
        "display_name": "Bharti Airtel",
        "sector": "Telecom",
        "direct_keywords": ["Bharti Airtel", "Airtel", "BHARTIARTL"],
        "related_companies": {
            "Reliance Jio":   "Largest telecom competitor — ARPU and subscriber trends matter",
            "Vodafone Idea":  "Telecom peer — spectrum, regulation, and tariff trends shared",
            "Indus Towers":   "Tower infrastructure subsidiary — tower economics matter",
        },
        "commodity_keywords": ["spectrum prices", "telecom equipment"],
        "macro_keywords": [
            "5G rollout", "5G spectrum", "TRAI", "telecom regulation",
            "ARPU", "mobile subscribers", "broadband", "telecom tariff",
            "telecom sector", "AGR dues", "spectrum auction",
            "Africa telecom", "enterprise telecom",
        ],
    },

    # ── POWER ──────────────────────────────────────────────────────────────────

    "NTPC": {
        "display_name": "NTPC",
        "sector": "Power",
        "direct_keywords": ["NTPC", "National Thermal Power"],
        "related_companies": {
            "Power Grid":    "Sister PSU — government power sector policy impacts both",
            "Coal India":    "Largest coal supplier — fuel cost directly impacts NTPC margins",
            "Adani Power":   "Private power peer — merchant power tariffs and capacity trends",
        },
        "commodity_keywords": ["coal prices", "thermal coal", "natural gas prices", "solar panel prices"],
        "macro_keywords": [
            "power sector", "electricity demand", "renewable energy",
            "solar energy", "wind energy", "power tariff",
            "government energy policy", "coal supply", "power deficit",
            "electricity generation", "green hydrogen", "DISCOM",
        ],
    },

    "POWERGRID": {
        "display_name": "Power Grid Corp",
        "sector": "Power",
        "direct_keywords": ["Power Grid", "Power Grid Corp", "POWERGRID"],
        "related_companies": {
            "NTPC":          "Sister PSU — power generation feeds transmission network",
            "Adani Transmission": "Private transmission peer — tariff and regulatory trends shared",
        },
        "commodity_keywords": ["copper prices", "transformer prices", "steel prices"],
        "macro_keywords": [
            "power sector", "electricity transmission", "power tariff",
            "government energy policy", "renewable energy integration",
            "CERC", "smart grid", "power infrastructure",
            "electricity demand", "DISCOM",
        ],
    },

    # ── INFRASTRUCTURE / CONGLOMERATES ─────────────────────────────────────────

    "LT": {
        "display_name": "Larsen & Toubro",
        "sector": "Infrastructure",
        "direct_keywords": ["Larsen & Toubro", "L&T", "LT", "Larsen and Toubro"],
        "related_companies": {
            "Adani Enterprises": "Infrastructure peer — government project pipeline shared",
            "Tata Projects":     "Direct competitor for EPC projects",
            "ABB India":         "Electrical equipment supplier to L&T projects",
        },
        "commodity_keywords": ["steel prices", "cement prices", "copper prices", "project costs"],
        "macro_keywords": [
            "government capex", "infrastructure spending", "defence contracts",
            "NHAI", "smart cities", "metro rail", "defence orders",
            "budget infrastructure", "PLI scheme", "semiconductor fab",
            "nuclear power", "hydrocarbon EPC", "IT services",
        ],
    },

    "ADANIENT": {
        "display_name": "Adani Enterprises",
        "sector": "Infrastructure",
        "direct_keywords": ["Adani Enterprises", "Adani Group", "ADANIENT", "Gautam Adani"],
        "related_companies": {
            "Adani Ports":   "Group company — port business health indicator",
            "Adani Power":   "Group company — power generation status",
            "Adani Green":   "Group company — renewable energy pipeline",
            "NDTV":          "Group company — media segment",
        },
        "commodity_keywords": ["coal prices", "solar panel prices", "green hydrogen"],
        "macro_keywords": [
            "Adani group", "government infrastructure", "airport privatisation",
            "road projects", "renewable energy", "solar energy",
            "Hindenburg report", "SEBI Adani", "FPO", "data centre",
        ],
    },

    "ADANIPORTS": {
        "display_name": "Adani Ports & SEZ",
        "sector": "Infrastructure",
        "direct_keywords": ["Adani Ports", "APSEZ", "ADANIPORTS"],
        "related_companies": {
            "Adani Enterprises": "Parent group — group-level news affects all Adani entities",
            "Container Corp":    "Rail logistics peer — port-hinterland freight trends shared",
            "DP World":          "Global port operator — international container volumes benchmark",
        },
        "commodity_keywords": ["container freight rates", "shipping rates", "port traffic"],
        "macro_keywords": [
            "port sector", "container volumes", "shipping", "trade data",
            "import export India", "India trade deficit",
            "port privatisation", "logistics sector", "SEZ policy",
        ],
    },

    # ── HEALTHCARE ─────────────────────────────────────────────────────────────

    "APOLLOHOSP": {
        "display_name": "Apollo Hospitals",
        "sector": "Healthcare",
        "direct_keywords": ["Apollo Hospitals", "Apollo Health", "APOLLOHOSP"],
        "related_companies": {
            "Fortis Healthcare":  "Direct hospital chain competitor — sector trends shared",
            "Max Healthcare":     "Direct hospital chain competitor — sector trends shared",
            "Narayana Hrudayalaya": "Healthcare peer — pricing and capacity trends shared",
        },
        "commodity_keywords": ["medical equipment prices", "pharma consumables"],
        "macro_keywords": [
            "healthcare sector", "health insurance", "Ayushman Bharat",
            "NHPS", "hospital beds", "medical tourism",
            "healthcare FDI", "digital health", "telemedicine",
            "health infrastructure spending",
        ],
    },

    # ── CONSUMER / RETAIL / FOOD ───────────────────────────────────────────────

    "ASIANPAINT": {
        "display_name": "Asian Paints",
        "sector": "Consumer",
        "direct_keywords": ["Asian Paints", "ASIANPAINT"],
        "related_companies": {
            "Berger Paints":    "Direct paint competitor — volume and pricing trends shared",
            "Kansai Nerolac":   "Direct paint competitor — volume and pricing trends shared",
            "Akzo Nobel India": "Direct paint competitor — premium segment overlap",
        },
        "commodity_keywords": ["crude oil prices", "titanium dioxide prices", "vinyl acetate monomer", "paint raw material"],
        "macro_keywords": [
            "paint sector", "housing demand", "real estate",
            "construction activity", "home improvement", "renovation",
            "crude derivatives", "input costs paints", "decorative paint",
        ],
    },

    "TITAN": {
        "display_name": "Titan Company",
        "sector": "Consumer",
        "direct_keywords": ["Titan", "Titan Company", "Tanishq", "Fastrack"],
        "related_companies": {
            "Kalyan Jewellers":  "Jewellery retail competitor — gold demand trends shared",
            "Senco Gold":        "Jewellery peer — gold buying sentiment shared",
        },
        "commodity_keywords": ["gold prices", "silver prices", "diamond prices", "gold import duty"],
        "macro_keywords": [
            "gold prices", "gold import", "jewellery sector",
            "GST jewellery", "wedding season", "festive demand",
            "luxury retail", "consumer spending", "premium consumer",
            "watches market", "eyewear market",
        ],
    },

    "TRENT": {
        "display_name": "Trent Ltd",
        "sector": "Consumer",
        "direct_keywords": ["Trent", "Trent Ltd", "Westside", "Zudio"],
        "related_companies": {
            "Reliance Retail": "Retail competitor — fashion and value retail trends shared",
            "V-Mart":          "Value fashion retail peer — tier-2/3 city demand trends shared",
            "Avenue Supermarts": "Retail peer — consumer spending and footfall trends",
        },
        "commodity_keywords": ["cotton prices", "fabric prices", "retail rent"],
        "macro_keywords": [
            "retail sector", "fashion retail", "value retail",
            "consumer spending", "GST retail", "urban consumption",
            "festive sales", "Zara India", "fast fashion",
            "e-commerce retail competition",
        ],
    },

    "ZOMATO": {
        "display_name": "Zomato",
        "sector": "Consumer",
        "direct_keywords": ["Zomato", "Blinkit"],
        "related_companies": {
            "Swiggy":             "Direct competitor — market share and growth trends shared",
            "Zepto":              "Quick commerce competitor — Blinkit overlap",
            "BigBasket":          "Grocery delivery competitor — quick commerce overlap",
        },
        "commodity_keywords": ["fuel prices", "delivery costs"],
        "macro_keywords": [
            "food delivery", "quick commerce", "hyperlocal delivery",
            "restaurant industry", "online food ordering",
            "e-commerce sector", "startup funding", "consumer internet",
            "GST food delivery", "ONDC", "FDI e-commerce",
        ],
    },
}
