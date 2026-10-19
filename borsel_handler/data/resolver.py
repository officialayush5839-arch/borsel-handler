"""
Company and Sector Entity Resolution Service
Provides deterministic, word-boundary entity resolution for Indian equities.
Fulfills Section 10 of Mega Prompt 2:
- Multi-company association per article
- Structured sector hierarchy
- Exact word-boundary matching to prevent subword false-positives
- Confidence scoring and extraction method attribution
- Safe unresolved fallback
"""
import re
from dataclasses import dataclass
from typing import List, Optional, Set
from borsel_handler.data.stocks import NIFTY_50

# Disallow common ambiguous short tokens from triggering symbol matches without context
AMBIGUOUS_SYMBOLS = {"IT", "ON", "BE", "AT", "OR", "IN", "LT", "TITAN", "TRENT"}

# Curated high-precision aliases for companies with ambiguous tickers or colloquial brand names
SPECIAL_ALIASES = {
    "LT": r"\b(L&T|Larsen & Toubro|Larsen)\b",
    "TITAN": r"\b(Titan Company|Titan Watches|Titan Jewellery|TITAN)\b",
    "TRENT": r"\b(Trent Ltd|Westside|Zudio|TRENT)\b",
    "COALINDIA": r"\b(Coal India|CIL|COALINDIA)\b",
    "M&M": r"\b(M&M|Mahindra & Mahindra|Mahindra)\b",
    "RELIANCE": r"\b(Reliance Industries|RIL)\b",
    "SBIN": r"\b(State Bank of India|State Bank|SBI|SBIN)\b",
}

# Structured sector hierarchy
SECTORS = {
    "IT": "Information Technology",
    "Banking": "Banking & Financial Services",
    "Finance": "Banking & Financial Services",
    "Insurance": "Banking & Financial Services",
    "Automobile": "Automotive & Manufacturing",
    "Pharma": "Healthcare & Pharmaceuticals",
    "Healthcare": "Healthcare & Pharmaceuticals",
    "Energy": "Energy, Oil & Gas",
    "Power": "Utilities & Power",
    "Metals": "Metals & Mining",
    "Infrastructure": "Infrastructure & Capital Goods",
    "Consumer": "Consumer Goods & Retail",
    "FMCG": "Fast Moving Consumer Goods",
    "Telecom": "Telecommunications",
    "Cement": "Materials & Construction",
}


@dataclass
class ResolvedCompany:
    symbol: str
    name: str
    sector: str
    confidence: float
    match_method: str  # "exact_symbol", "full_name", "alias"


class CompanyResolver:
    """
    Institutional entity resolution engine for Indian listed equities.
    """
    _REGISTRY: List[dict] = list(NIFTY_50)

    @classmethod
    def load_from_db(cls, db) -> int:
        """Loads active companies from database into resolution registry."""
        from borsel_handler.storage.models import Company
        companies = db.query(Company).filter(Company.is_active == True).all()
        seen = {s["symbol"] for s in cls._REGISTRY}
        added = 0
        for c in companies:
            if c.symbol not in seen:
                cls._REGISTRY.append({
                    "symbol": c.symbol,
                    "name": c.name,
                    "sector": c.sector or "General",
                })
                seen.add(c.symbol)
                added += 1
        return len(cls._REGISTRY)

    @classmethod
    def resolve(cls, text: str, custom_companies: Optional[List[dict]] = None) -> List[ResolvedCompany]:
        """
        Scans text for occurrences of known corporate entities and tickers.
        Returns a deduplicated list of ResolvedCompany instances.
        """
        if not text:
            return []

        results: List[ResolvedCompany] = []
        seen_symbols: Set[str] = set()
        t_clean = f" {text} "

        company_universe = custom_companies if custom_companies is not None else cls._REGISTRY
        for stock in company_universe:
            sym = stock["symbol"]
            name = stock["name"]
            raw_sector = stock.get("sector", "General")
            normalized_sector = SECTORS.get(raw_sector, raw_sector)

            # 1. Exact Symbol Match (enforce word boundaries and casing for short tickers)
            if sym not in AMBIGUOUS_SYMBOLS:
                pattern_sym = r"\b" + re.escape(sym) + r"\b"
                # For short symbols (<= 4 chars), enforce uppercase in text to prevent matching common words
                flags = 0 if len(sym) <= 4 else re.IGNORECASE
                if re.search(pattern_sym, t_clean, flags):
                    if sym not in seen_symbols:
                        seen_symbols.add(sym)
                        results.append(
                            ResolvedCompany(
                                symbol=sym,
                                name=name,
                                sector=normalized_sector,
                                confidence=0.98,
                                match_method="exact_symbol",
                            )
                        )
                        continue

            # 2. Company Name Match (excluding generic legal suffixes only)
            if sym in ("TRENT", "TITAN"):
                clean_name = name
            else:
                clean_name = re.sub(
                    r"\b(Ltd|Limited|Corporation|Corp|Enterprise|Industries)\b",
                    "",
                    name,
                    flags=re.IGNORECASE,
                ).strip()

            if len(clean_name) >= 3:
                pattern_name = r"\b" + re.escape(clean_name) + r"\b"
                if re.search(pattern_name, t_clean, re.IGNORECASE):
                    if sym not in seen_symbols:
                        seen_symbols.add(sym)
                        results.append(
                            ResolvedCompany(
                                symbol=sym,
                                name=name,
                                sector=normalized_sector,
                                confidence=0.92,
                                match_method="full_name",
                            )
                        )
                        continue

            # 3. Special curated aliases (e.g. L&T, SBI, Titan Company, Westside, Coal India)
            if sym in SPECIAL_ALIASES:
                alias_pattern = SPECIAL_ALIASES[sym]
                if re.search(alias_pattern, t_clean):
                    if sym not in seen_symbols:
                        seen_symbols.add(sym)
                        results.append(
                            ResolvedCompany(
                                symbol=sym,
                                name=name,
                                sector=normalized_sector,
                                confidence=0.95,
                                match_method="alias",
                            )
                        )

        return results

    @classmethod
    def resolve_primary(cls, text: str) -> Optional[ResolvedCompany]:
        """
        Returns the highest-confidence primary corporate entity or None.
        """
        matches = cls.resolve(text)
        if not matches:
            return None
        # Sort by confidence descending
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[0]
