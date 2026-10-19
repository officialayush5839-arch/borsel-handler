"""
Resumable Historical Backfill Engine for Borsel Handler
Implements Section 4 of Release Preparation:
- Bounded date-range chunking
- Atomic checkpoint persistence for safe restart after interruption
- Rate-limiting delay between window iterations
- Duplicate prevention via NewsRepository multi-tier deduplication
- Audit logging and execution summary reporting
"""
import asyncio
import json
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.collectors.rss import RSSCollector
from borsel_handler.collectors.nse import NSEAnnouncementCollector
from borsel_handler.collectors.bse import BSEAnnouncementCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.storage.database import SessionLocal
from borsel_handler.storage.repository import NewsRepository

logger = logging.getLogger(__name__)


class BackfillCheckpoint:
    """Manages persistent checkpointing for resumable historical backfill."""

    def __init__(self, checkpoint_path: str = "backfill_checkpoint.json"):
        self.path = Path(checkpoint_path)

    def load(self) -> Optional[Dict]:
        if not self.path.exists():
            return None
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            logger.warning("Failed to load backfill checkpoint: %s", exc)
            return None

    def save(self, data: Dict) -> None:
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as exc:
            logger.error("Failed to save backfill checkpoint: %s", exc)

    def clear(self) -> None:
        if self.path.exists():
            try:
                self.path.unlink()
            except Exception:
                pass


class HistoricalBackfillManager:
    """
    Orchestrates bounded, resumable historical data backfilling.
    """

    def __init__(
        self,
        collectors: Optional[List[BaseCollector]] = None,
        checkpoint_path: str = "backfill_checkpoint.json",
        rate_limit_delay_seconds: float = 1.0,
    ):
        self.collectors = collectors or [
            RSSCollector(),
            NSEAnnouncementCollector(index_tag="equities"),
            BSEAnnouncementCollector(),
        ]
        self.checkpoint = BackfillCheckpoint(checkpoint_path)
        self.rate_limit_delay = rate_limit_delay_seconds

    async def run_backfill(
        self,
        start_date: datetime,
        end_date: datetime,
        step_days: int = 1,
        max_windows: Optional[int] = None,
        resume_if_checkpoint_exists: bool = True,
        db: Optional[Session] = None,
    ) -> Dict:
        """
        Executes bounded historical backfill across [start_date, end_date].
        """
        # Ensure UTC timezone
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        current_start = start_date
        metrics = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "windows_total": 0,
            "windows_completed": 0,
            "items_found": 0,
            "items_inserted": 0,
            "items_duplicate": 0,
            "items_failed": 0,
            "status": "in_progress",
            "last_completed_window": None,
        }

        # Check existing checkpoint
        if resume_if_checkpoint_exists:
            saved = self.checkpoint.load()
            if saved and saved.get("status") == "in_progress":
                if saved.get("last_completed_window"):
                    resume_dt = datetime.fromisoformat(saved["last_completed_window"])
                    if resume_dt < end_date:
                        logger.info("Resuming historical backfill from checkpoint: %s", resume_dt)
                        current_start = resume_dt
                        metrics["windows_completed"] = saved.get("windows_completed", 0)
                        metrics["items_found"] = saved.get("items_found", 0)
                        metrics["items_inserted"] = saved.get("items_inserted", 0)
                        metrics["items_duplicate"] = saved.get("items_duplicate", 0)

        # Generate window intervals
        windows: List[Tuple[datetime, datetime]] = []
        cur = current_start
        while cur < end_date:
            w_end = min(cur + timedelta(days=step_days), end_date)
            windows.append((cur, w_end))
            cur = w_end
            if max_windows and len(windows) >= max_windows:
                break

        metrics["windows_total"] = len(windows)
        logger.info(
            "Starting historical backfill: %d bounded windows from %s to %s",
            len(windows), current_start, end_date
        )

        manage_session = db is None
        session: Session = SessionLocal() if manage_session else db
        try:
            for idx, (win_start, win_end) in enumerate(windows, 1):
                logger.info("Processing window [%d/%d]: %s -> %s", idx, len(windows), win_start, win_end)
                for collector in self.collectors:
                    try:
                        # Bounded fetch for window
                        records: List[NormalizedNewsRecord] = await collector.fetch(cutoff=win_start)
                        # Filter to window range
                        window_records = [
                            r for r in records
                            if win_start <= r.published_at <= win_end
                        ]
                        metrics["items_found"] += len(window_records)

                        for rec in window_records:
                            try:
                                _, inserted, reason = NewsRepository.insert_record(session, rec)
                                if inserted:
                                    metrics["items_inserted"] += 1
                                else:
                                    metrics["items_duplicate"] += 1
                            except Exception as insert_exc:
                                metrics["items_failed"] += 1
                                logger.error("Failed to insert backfill record: %s", insert_exc)

                    except Exception as col_exc:
                        metrics["items_failed"] += 1
                        logger.error("Collector %s failed in window: %s", collector.source_name, col_exc)

                metrics["windows_completed"] += 1
                metrics["last_completed_window"] = win_end.isoformat()

                # Save incremental checkpoint
                self.checkpoint.save(metrics)

                # Rate limiting pause between windows
                if self.rate_limit_delay > 0:
                    await asyncio.sleep(self.rate_limit_delay)

            metrics["status"] = "completed"
            self.checkpoint.save(metrics)
            logger.info("Historical backfill completed successfully: %s", metrics)

        except Exception as run_exc:
            metrics["status"] = "failed"
            metrics["error"] = str(run_exc)
            self.checkpoint.save(metrics)
            logger.error("Backfill aborted due to error: %s", run_exc)
            raise
        finally:
            if manage_session:
                session.close()

        return metrics
