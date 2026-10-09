from fastapi import APIRouter, Response, status

from app.core.config import settings
from app.db.session import probe_db_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Kiểm tra API còn hoạt động."""
    return HealthResponse(status="ok", app_name=settings.app_name)


@router.get("/health/db", response_model=DatabaseHealthResponse)
def database_health_check(response: Response) -> DatabaseHealthResponse:
    """Kiểm tra kết nối cơ sở dữ liệu. Trả 503 nếu không kết nối được."""
    result = probe_db_connection()
    if result["status"] != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return DatabaseHealthResponse(**result)
