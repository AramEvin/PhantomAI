"""PhantomAI FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from app.core.config import settings
from app.database import init_db
from app.api.routes.investigate import router as investigate_router
from app.api.routes.history import router as history_router
from app.api.routes.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 PhantomAI starting...")
    await init_db()
    logger.info("✓ Database initialized")
    yield
    logger.info("PhantomAI shutting down")

app = FastAPI(
    title="PhantomAI",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(investigate_router, prefix="/api/v1")
app.include_router(history_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
