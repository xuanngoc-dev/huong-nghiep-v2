import json
import logging
import time
from copy import deepcopy
from datetime import date, timedelta
from logging.config import dictConfig
from pathlib import Path

from fastapi import FastAPI, Request
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.nguoi_dung import NguoiDung

logger = logging.getLogger("app.api")

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
_configured = False
_MAX_BODY_CHARS = 20_000
_SENSITIVE_KEYS = {
    "mat_khau",
    "password",
    "access_token",
    "refresh_token",
    "token",
    "secret",
    "authorization",
}


class DailyFileHandler(logging.Handler):
    """Ghi log vào một file mỗi ngày và xóa file cũ hơn số ngày cấu hình."""

    def __init__(self, directory: Path, retention_days: int) -> None:
        super().__init__()
        self.directory = directory
        self.retention_days = retention_days
        self._current_date: date | None = None
        self._stream = None
        self.directory.mkdir(parents=True, exist_ok=True)
        self._purge_old_files()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._roll_if_needed()
            if self._stream is None:
                return
            self._stream.write(self.format(record) + "\n")
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        self.acquire()
        try:
            if self._stream is not None:
                self._stream.close()
                self._stream = None
            super().close()
        finally:
            self.release()

    def _roll_if_needed(self) -> None:
        today = date.today()
        if self._current_date == today and self._stream is not None:
            return
        if self._stream is not None:
            self._stream.close()
        self._current_date = today
        path = self.directory / f"{today.isoformat()}.log"
        self._stream = path.open("a", encoding="utf-8")
        self._purge_old_files()

    def _purge_old_files(self) -> None:
        cutoff = date.today() - timedelta(days=self.retention_days - 1)
        for path in self.directory.glob("*.log"):
            try:
                file_date = date.fromisoformat(path.stem)
            except ValueError:
                continue
            if file_date < cutoff:
                path.unlink(missing_ok=True)


def setup_logging() -> None:
    """Cấu hình log ra console (uvicorn) và file theo ngày."""
    global _configured
    if _configured:
        return

    config = deepcopy(LOGGING_CONFIG)
    config["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
    config["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
    config["loggers"]["app"] = {
        "handlers": ["default"],
        "level": "INFO",
        "propagate": False,
    }
    # Dòng access mặc định của uvicorn trùng với log request bên dưới.
    config["loggers"]["uvicorn.access"]["level"] = "WARNING"
    dictConfig(config)

    file_handler = DailyFileHandler(LOG_DIR, settings.log_retention_days)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger("app").addHandler(file_handler)
    logging.getLogger("uvicorn").addHandler(file_handler)
    _configured = True


def _redact(value):
    """Che mật khẩu và token trước khi ghi log."""
    if isinstance(value, dict):
        return {
            key: "***" if str(key).lower() in _SENSITIVE_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


def _format_body(raw: bytes, content_type: str | None) -> tuple[str, object | None]:
    """Đổi body thành chữ để ghi log. Trả thêm dữ liệu JSON nếu đọc được."""
    if not raw:
        return "-", None
    media = (content_type or "").lower()
    if media and "json" not in media and "text" not in media and "form" not in media:
        return f"[{content_type} {len(raw)} bytes]", None

    text = raw.decode("utf-8", errors="replace")
    parsed = None
    try:
        parsed = json.loads(text)
        text = json.dumps(_redact(parsed), ensure_ascii=False, separators=(",", ":"))
    except json.JSONDecodeError:
        parsed = None
    if len(text) > _MAX_BODY_CHARS:
        text = text[:_MAX_BODY_CHARS] + "...[đã cắt]"
    return text, parsed


def _caller_label(request: Request, body: object | None) -> str:
    """Tên người gọi: tài khoản từ Bearer token, hoặc khách."""
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        user_id = decode_access_token(token)
        if user_id is None:
            return "token không hợp lệ"
        db = SessionLocal()
        try:
            user = db.get(NguoiDung, int(user_id))
        except Exception:
            logger.exception("Không tra được người gọi API")
            return f"user #{user_id}"
        finally:
            db.close()
        if user is None:
            return f"user #{user_id} không tồn tại"
        return f"{user.ho_ten} <{user.email}> (#{user.id})"

    if isinstance(body, dict) and body.get("email"):
        return f"khách ({body.get('email')})"
    return "khách"


async def _capture_response(response: Response) -> tuple[bytes, Response]:
    """Đọc body phản hồi rồi tạo lại response để client vẫn nhận đủ dữ liệu."""
    chunks: list[bytes] = []
    async for chunk in response.body_iterator:
        chunks.append(chunk)
    body = b"".join(chunks)
    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"content-length", "content-type"}
    }
    rebuilt = Response(
        content=body,
        status_code=response.status_code,
        headers=headers,
        media_type=response.media_type,
        background=response.background,
    )
    return body, rebuilt


def register_request_logging(app: FastAPI) -> None:
    """Ghi người gọi, request và phản hồi của mỗi API."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        started = time.perf_counter()
        path = request.url.path
        if request.url.query:
            path = f"{path}?{request.url.query}"
        client = request.client.host if request.client else "-"
        raw_request = await request.body()
        request_text, request_data = _format_body(raw_request, request.headers.get("content-type"))
        caller = _caller_label(request, request_data)

        try:
            response = await call_next(request)
            raw_response, response = await _capture_response(response)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "%s %s %s thất bại sau %.0fms | %s\n  request: %s",
                client,
                request.method,
                path,
                elapsed_ms,
                caller,
                request_text,
            )
            raise

        elapsed_ms = (time.perf_counter() - started) * 1000
        response_text, _ = _format_body(raw_response, response.media_type)
        if response.status_code >= 500:
            level = logging.ERROR
        elif response.status_code >= 400:
            level = logging.WARNING
        else:
            level = logging.INFO
        logger.log(
            level,
            "%s %s %s %s %.0fms | %s\n  request: %s\n  response: %s",
            client,
            request.method,
            path,
            response.status_code,
            elapsed_ms,
            caller,
            request_text,
            response_text,
        )
        return response
