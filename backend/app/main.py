import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

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



# Khai báo trước CORS nên nằm bên trong CORS: lỗi không bắt được đổi thành JSON 500 vẫn có header CORS.
# Không có lớp này, lỗi 500 đi thẳng ra ngoài CORS và trình duyệt báo "bị chặn CORS" thay vì lỗi thật.
@app.middleware("http")
async def loi_khong_bat_van_co_cors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:
        logger.exception("Lỗi không xử lý: %s %s", request.method, request.url.path)
        return JSONResponse({"detail": "Lỗi hệ thống. Vui lòng thử lại sau."}, status_code=500)


# CORS_ORIGINS="*" (mặc định): mọi domain đều gọi được; trả đúng origin của request nên vẫn dùng được credentials.
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
