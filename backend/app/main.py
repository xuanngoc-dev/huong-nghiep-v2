import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import engine, probe_db_connection

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    result = probe_db_connection()
    if result["status"] == "ok":
        logger.info(
            "MySQL connected: %s@%s:%s/%s",
            result["user"],
            result["host"],
            result["port"],
            result["database"],
        )
    else:
        logger.warning("MySQL connection failed: %s", result.get("detail"))
    yield
    engine.dispose()


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
