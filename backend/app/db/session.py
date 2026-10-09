from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency FastAPI: lấy session DB cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> None:
    """Kiểm tra kết nối MySQL; lỗi thì raise."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def probe_db_connection() -> dict:
    """Trả về trạng thái kết nối MySQL (không raise)."""
    info = {
        "database": settings.db_name,
        "host": settings.db_host,
        "port": settings.db_port,
        "user": settings.db_user,
    }
    try:
        check_db_connection()
        return {"status": "ok", **info}
    except Exception as exc:
        return {"status": "error", **info, "detail": str(exc)}
