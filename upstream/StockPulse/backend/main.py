import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")

from routers.news import router as news_router

SITE_PASSWORD = os.getenv("SITE_PASSWORD", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.rss_service import _get_cached_feeds
    try:
        await _get_cached_feeds()
    except Exception:
        pass
    yield


app = FastAPI(title="Indian Stock News API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def password_gate(request: Request, call_next):
    if request.method == "OPTIONS" or request.url.path in ("/health", "/api/auth"):
        return await call_next(request)
    if SITE_PASSWORD:
        if request.headers.get("X-Password", "") != SITE_PASSWORD:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
    return await call_next(request)


app.include_router(news_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
