"""
Company Directory Synchronization Engine
Ingests official NSE equity master CSV (EQUITY_L.csv) to maintain an authoritative,
expanded reference directory of Indian listed equities (~2,600+ companies).
Fulfills Section 5 (Task C) of Partial Completion Mega Prompt.
"""
import csv
import io
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session

from borsel_handler.storage.models import Company

logger = logging.getLogger(__name__)

NSE_EQUITY_L_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 BorselHandler/1.0"
    ),
    "Accept": "text/csv,text/plain,*/*",
}


class CompanyDirectorySync:
    """
    Idempotent, transactional synchronization service for Indian listed equities.
    """

    @classmethod
    def parse_csv_content(cls, csv_text: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Parses official NSE EQUITY_L.csv content.
        Handles BOM, whitespace, arbitrary column order, and validates required fields.
        Returns:
            (valid_records: List[Dict], rejected_count: int)
        """
        valid_records: List[Dict[str, Any]] = []
        rejected_count = 0

        if not csv_text or not csv_text.strip():
            return [], 0

        # Strip BOM if present
        cleaned_text = csv_text.lstrip("\ufeff")
        f = io.StringIO(cleaned_text)
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return [], 0

        # Normalize fieldnames map (strip whitespace, uppercase)
        clean_field_map = {fn.strip().upper(): fn for fn in reader.fieldnames if fn}

        sym_col = clean_field_map.get("SYMBOL")
        name_col = clean_field_map.get("NAME OF COMPANY")
        isin_col = clean_field_map.get("ISIN NUMBER") or clean_field_map.get("ISIN")
        series_col = clean_field_map.get("SERIES")
        listing_date_col = clean_field_map.get("DATE OF LISTING")

        if not sym_col or not name_col:
            logger.warning("EQUITY_L.csv missing critical SYMBOL or NAME OF COMPANY column")
            return [], 0

        seen_symbols = set()
        for row in reader:
            sym = (row.get(sym_col) or "").strip().upper()
            name = (row.get(name_col) or "").strip()
            isin = (row.get(isin_col) or "").strip().upper() if isin_col else None
            series = (row.get(series_col) or "").strip() if series_col else "EQ"
            listing_dt = (row.get(listing_date_col) or "").strip() if listing_date_col else None

            # Validation: Symbol and Name are strictly required
            if not sym or not name or len(sym) > 32 or sym in seen_symbols:
                rejected_count += 1
                continue

            # Basic ISIN format validation (should be 12 chars starting with INE or similar)
            if isin and len(isin) != 12:
                isin = None

            seen_symbols.add(sym)
            valid_records.append({
                "symbol": sym,
                "name": name,
                "isin": isin,
                "series": series,
                "listing_date": listing_dt,
            })

        return valid_records, rejected_count

    @classmethod
    def sync_to_database(
        cls, db: Session, records: List[Dict[str, Any]], source_label: str = "NSE_EQUITY_L"
    ) -> Dict[str, Any]:
        """
        Applies company records transactionally to the database.
        Upserts companies without duplicating symbols.
        Preserves existing data if an error occurs.
        """
        if not records:
            return {
                "status": "skipped",
                "reason": "no_valid_records",
                "imported_count": 0,
                "updated_count": 0,
                "rejected_count": 0,
            }

        imported_count = 0
        updated_count = 0

        try:
            # Query existing companies
            existing_companies = {c.symbol: c for c in db.query(Company).all()}

            for rec in records:
                sym = rec["symbol"]
                name = rec["name"]
                isin = rec.get("isin")

                if sym in existing_companies:
                    # Update existing record
                    comp = existing_companies[sym]
                    changed = False
                    if comp.name != name:
                        comp.name = name
                        changed = True
                    if isin and comp.isin != isin:
                        comp.isin = isin
                        changed = True
                    if not comp.is_active:
                        comp.is_active = True
                        changed = True
                    if changed:
                        updated_count += 1
                else:
                    # Insert new company
                    new_comp = Company(
                        symbol=sym,
                        name=name,
                        isin=isin,
                        is_active=True,
                    )
                    db.add(new_comp)
                    existing_companies[sym] = new_comp
                    imported_count += 1

            db.commit()

            total_active = db.query(Company).filter(Company.is_active == True).count()
            summary = {
                "status": "success",
                "source": source_label,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_parsed": len(records),
                "imported_count": imported_count,
                "updated_count": updated_count,
                "total_active_companies": total_active,
            }
            logger.info("CompanyDirectorySync completed: %s", summary)
            return summary

        except Exception as exc:
            db.rollback()
            logger.error("Error during company directory sync transaction: %s", exc)
            return {
                "status": "failed",
                "error": str(exc),
                "imported_count": 0,
                "updated_count": 0,
            }

    @classmethod
    async def sync_live(
        cls, db: Session, url: str = NSE_EQUITY_L_URL, timeout: float = 20.0
    ) -> Dict[str, Any]:
        """
        Downloads official NSE equity master CSV and synchronizes the reference directory.
        If download fails, preserves the existing directory and reports error safely.
        """
        try:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                resp = await client.get(url, headers=NSE_HEADERS)
                if resp.status_code != 200 or len(resp.content) < 1000:
                    logger.warning("Failed to download EQUITY_L.csv: HTTP %d", resp.status_code)
                    return {
                        "status": "download_failed",
                        "status_code": resp.status_code,
                        "imported_count": 0,
                        "updated_count": 0,
                    }

                csv_text = resp.text
                records, rejected = cls.parse_csv_content(csv_text)
                res = cls.sync_to_database(db, records, source_label="NSE_EQUITY_L_LIVE")
                res["rejected_count"] = rejected
                return res

        except Exception as exc:
            logger.error("Network or parsing failure during live company sync: %s", exc)
            return {
                "status": "network_error",
                "error": str(exc),
                "imported_count": 0,
                "updated_count": 0,
            }
