"""
FastAPI Application Entry Point for Borsel Handler
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from borsel_handler.api.routes import router
from borsel_handler.config import settings
from borsel_handler.storage.database import init_db

logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("borsel_handler")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Borsel Handler database tables...")
    init_db()
    logger.info("Borsel Handler platform startup complete.")
    yield
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
