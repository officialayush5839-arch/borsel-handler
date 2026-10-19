"""
Resilience and scheduler execution tests.
"""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from borsel_handler.collectors.base import BaseCollector
from borsel_handler.core.models import NormalizedNewsRecord
from borsel_handler.scheduler.runner import CollectionRunner
from borsel_handler.storage.models import CollectionLog


class MockFailingCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Failing Mock Exchange"

    @property
    def source_type(self) -> str:
        return "mock_failing"

    async def fetch(self, cutoff=None):
        raise ConnectionResetError("Remote server closed connection unexpectedly")


class MockSuccessfulCollector(BaseCollector):
    @property
    def source_name(self) -> str:
        return "Successful Mock Source"

    @property
    def source_type(self) -> str:
        return "mock_success"

    async def fetch(self, cutoff=None):
        return [
            NormalizedNewsRecord(
                title="Mock Successful Announcement",
                snippet="Operational report",
                original_url="https://economictimes.indiatimes.com/mock-article",
                canonical_url="https://economictimes.indiatimes.com/mock-article",
                published_at=datetime.now(timezone.utc),
                source_name=self.source_name,
                source_type=self.source_type,
                source_record_id="mock_succ_01",
            )
        ]


@pytest.mark.asyncio
async def test_scheduler_failure_logged_and_does_not_abort_others(in_memory_db):
    runner = CollectionRunner(
        collectors=[MockFailingCollector(), MockSuccessfulCollector()]
    )

    # Run failing collector
    res1 = await runner.run_collector(runner.collectors[0], in_memory_db)
    assert res1.status == "failed"
    assert "Remote server closed connection" in res1.error_message

    # Run succeeding collector
    res2 = await runner.run_collector(runner.collectors[1], in_memory_db)
    assert res2.status == "success"
    assert res2.items_found == 1
    assert res2.items_inserted == 1

    # Verify both runs are recorded in collection_logs table
    logs = in_memory_db.query(CollectionLog).order_by(CollectionLog.id.asc()).all()
    assert len(logs) == 2
    assert logs[0].status == "failed"
    assert logs[0].error_message is not None
    assert logs[1].status == "success"
    assert logs[1].items_inserted == 1
