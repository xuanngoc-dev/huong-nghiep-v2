import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.json_utf8 import Utf8JSONResponse
from app.core.logging import register_request_logging, setup_logging
from app.core.swagger_ui import docs_html
from app.db.session import engine, probe_db_connection

setup_logging()
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


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    default_response_class=Utf8JSONResponse,
    docs_url=None,
    servers=[{"url": settings.api_public_url, "description": "API công khai"}] if settings.api_public_url else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)
register_request_logging(app)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/", include_in_schema=False)
def trang_api():
    """Mở domain backend thì vào Swagger để xem và thử các API."""
    return RedirectResponse(url="/docs")


@app.get("/docs", include_in_schema=False)
def swagger_ui():
    """Swagger. Gọi đăng nhập hoặc đăng ký sẽ lưu token cho các API phía sau."""
    return docs_html(openapi_url=app.openapi_url, title=f"{settings.app_name} — Swagger")
