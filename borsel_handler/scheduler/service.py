"""
Standalone Ingestion Scheduler Service.
Automates recurring financial data collection for localhost & production workers.
"""
import asyncio
import logging
from datetime import datetime, timezone

from borsel_handler.config import settings
from borsel_handler.scheduler.runner import CollectionRunner
from borsel_handler.storage.database import init_db

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] [Automation] %(message)s",
)
logger = logging.getLogger("borsel_scheduler")


async def run_automation_loop():
    logger.info("=" * 70)
    logger.info("BORSEL HANDLER — AUTOMATED INGESTION SCHEDULER")
    logger.info("Interval: Every %d minutes | Cutoff: %d hours", settings.COLLECTION_INTERVAL_MINUTES, settings.DEFAULT_LOOKBACK_HOURS)
    logger.info("=" * 70)

    # Ensure tables are initialized
    init_db()

    runner = CollectionRunner()
    while True:
        try:
            logger.info("Executing scheduled collection run at %s...", datetime.now(timezone.utc).isoformat())
            summaries = await runner.run_all(cutoff_hours=settings.DEFAULT_LOOKBACK_HOURS)
            total_found = sum(s.items_found for s in summaries)
            total_ins = sum(s.items_inserted for s in summaries)
            total_dups = sum(s.items_duplicate for s in summaries)
            logger.info(
                "Run completed: Discovered %d items, Inserted %d new, Prevented %d duplicates.",
                total_found, total_ins, total_dups
            )
        except Exception as exc:
            logger.error("Error during scheduled run: %s", exc)

        sleep_seconds = max(60, settings.COLLECTION_INTERVAL_MINUTES * 60)
        logger.info("Next collection cycle in %d minutes (%d seconds)...", settings.COLLECTION_INTERVAL_MINUTES, sleep_seconds)
        await asyncio.sleep(sleep_seconds)


if __name__ == "__main__":
    try:
        asyncio.run(run_automation_loop())
    except KeyboardInterrupt:
        logger.info("Scheduler interrupted by user. Exiting.")
