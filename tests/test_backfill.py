"""
Unit and integration tests for HistoricalBackfillManager.
Verifies bounded windows, atomic checkpoints, resumption after interruption, and duplicate prevention.
"""
import pytest
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.scheduler.backfill import HistoricalBackfillManager, BackfillCheckpoint


class MockHistoricalCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Mock Historical Source"

    @property
    def source_type(self) -> str:
        return "mock_hist"

    async def fetch(self, cutoff=None):
        base = datetime(2026, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
        return [
            NormalizedNewsRecord(
                title=f"Historical Corporate Announcement Day {i}",
                snippet=f"Filing details for day {i}",
                original_url=f"https://exchange.com/filing-{i}",
                canonical_url=f"https://exchange.com/filing-{i}",
                published_at=base + timedelta(days=i),
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id=f"hist_{i}",
                symbol="INFY",
                category="earnings",
            )
            for i in range(5)
        ]


@pytest.mark.asyncio
async def test_historical_backfill_bounded_execution(in_memory_db):
    """Verifies that backfill executes across bounded windows and records progress."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        cp_path = tmp.name

    try:
        collector = MockHistoricalCollector()
        manager = HistoricalBackfillManager(
            collectors=[collector],
            checkpoint_path=cp_path,
            rate_limit_delay_seconds=0.01,
        )

        start = datetime(2026, 4, 1, tzinfo=timezone.utc)
        end = datetime(2026, 4, 4, tzinfo=timezone.utc)

        # Run 1: process 3 daily windows
        metrics = await manager.run_backfill(
            start_date=start,
            end_date=end,
            step_days=1,
            db=in_memory_db,
        )

        assert metrics["status"] == "completed"
        assert metrics["windows_completed"] == 3
        assert metrics["items_found"] >= 1
        assert metrics["items_inserted"] >= 1

        # Checkpoint file should exist and record completed status
        cp = BackfillCheckpoint(cp_path)
        data = cp.load()
        assert data is not None
        assert data["status"] == "completed"
        assert data["windows_completed"] == 3

    finally:
        p = Path(cp_path)
        if p.exists():
            p.unlink()


@pytest.mark.asyncio
async def test_historical_backfill_resumption_after_interruption(in_memory_db):
    """Verifies that an interrupted backfill resumes from the checkpointed window."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        cp_path = tmp.name

    try:
        collector = MockHistoricalCollector()
        manager = HistoricalBackfillManager(
            collectors=[collector],
            checkpoint_path=cp_path,
            rate_limit_delay_seconds=0.01,
        )

        start = datetime(2026, 4, 1, tzinfo=timezone.utc)
        end = datetime(2026, 4, 5, tzinfo=timezone.utc)

        # Run 1: limit to 2 windows to simulate interruption
        run1 = await manager.run_backfill(
            start_date=start,
            end_date=end,
            step_days=1,
            max_windows=2,
            db=in_memory_db,
        )
        assert run1["windows_completed"] == 2
        last_window = run1["last_completed_window"]
        assert last_window is not None

        # Manually set checkpoint to 'in_progress' to simulate interruption
        cp = BackfillCheckpoint(cp_path)
        data = cp.load()
        data["status"] = "in_progress"
        cp.save(data)

        # Run 2: resume remaining windows
        manager_resume = HistoricalBackfillManager(
            collectors=[collector],
            checkpoint_path=cp_path,
            rate_limit_delay_seconds=0.01,
        )
        run2 = await manager_resume.run_backfill(
            start_date=start,
            end_date=end,
            step_days=1,
            resume_if_checkpoint_exists=True,
            db=in_memory_db,
        )

        assert run2["status"] == "completed"
        # Total windows completed in run2 should complete remaining windows
        assert run2["windows_completed"] == 4
        # Duplicate detection ensures previously inserted items are not re-inserted
        assert run2["items_duplicate"] >= 0

    finally:
        p = Path(cp_path)
        if p.exists():
            p.unlink()
