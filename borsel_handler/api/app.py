"""
FastAPI Application Entry Point for Borsel Handler
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
from borsel_handler.api.routes import router
from borsel_handler.config import settings
from borsel_handler.storage.database import init_db

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("borsel_handler")


async def _background_scheduler_loop():
    """
    Background automation worker for localhost and continuous collection.
    Runs an initial ingestion cycle shortly after startup, followed by
    periodic recurring runs based on settings.COLLECTION_INTERVAL_MINUTES.
    """
    from borsel_handler.scheduler.runner import CollectionRunner

    await asyncio.sleep(settings.AUTO_INGEST_INITIAL_DELAY_SECONDS)
    runner = CollectionRunner()

    while True:
        try:
            logger.info(
                "Automation: Triggering scheduled collection cycle (lookback: %d hours)...",
                settings.DEFAULT_LOOKBACK_HOURS,
            )
            summaries = await runner.run_all(cutoff_hours=settings.DEFAULT_LOOKBACK_HOURS)
            total_ins = sum(s.items_inserted for s in summaries)
            total_dups = sum(s.items_duplicate for s in summaries)
            logger.info(
                "Automation: Cycle completed. Inserted: %d, Duplicates Prevented: %d",
                total_ins,
                total_dups,
            )
        except asyncio.CancelledError:
            logger.info("Automation: Background scheduler loop cancelled.")
            break
        except Exception as exc:
            logger.error("Automation: Scheduled collection cycle error: %s", exc)

        interval_seconds = max(60, settings.COLLECTION_INTERVAL_MINUTES * 60)
        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            break


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Borsel Handler database tables...")
    init_db()
    logger.info("Borsel Handler platform startup complete.")

    scheduler_task = None
    if settings.ENABLE_AUTO_INGEST:
        logger.info(
            "Localhost automation enabled: Starting background scheduler worker (Interval: %d min, Initial Delay: %ds)...",
            settings.COLLECTION_INTERVAL_MINUTES,
            settings.AUTO_INGEST_INITIAL_DELAY_SECONDS,
        )
        scheduler_task = asyncio.create_task(_background_scheduler_loop())

    yield

    if scheduler_task:
        logger.info("Shutting down background scheduler worker...")
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass

    logger.info("Borsel Handler shutdown.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Indian Stock Market Intelligence Platform — Data Collection Module",
    lifespan=lifespan,
)

allow_creds = False if "*" in settings.ALLOWED_ORIGINS else True

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=allow_creds,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router)
