import json
from typing import Annotated
from urllib.parse import quote_plus

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


class Settings(BaseSettings):
    app_name: str = "Định hướng nghề"
    api_v1_prefix: str = "/api/v1"
    # Domain frontend được phép gọi API từ trình duyệt. Postman/Bruno không cần nằm trong danh sách này.
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: list(_LOCAL_FRONTEND_ORIGINS))
    # Origin công khai của API, không gồm /api/v1. Để trống thì /docs dùng đúng host đang mở.
    api_public_url: str = ""
    port: int = 3060
    log_retention_days: int = Field(default=14, ge=1)

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "huongnghiep"

    # JWT
    secret_key: str = "doi-secret-key-trong-moi-truong-that"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 ngày
    jwt_algorithm: str = "HS256"

    # Hỏi đáp tài liệu. Nếu để trống, tự động tìm data_dh_json ở thư mục gốc hoặc backend/tai_lieu.
    tai_lieu_dir: str = ""
    tai_lieu_max_bytes: int = 15 * 1024 * 1024
    # Ảnh và video thư viện. Nếu để trống, lưu tại backend/thu_vien.
    thu_vien_dir: str = ""
    thu_vien_max_bytes: int = 100 * 1024 * 1024
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    openai_api_key: str = ""
    openai_model: str = "gpt-6-luna"
    chat_timeout_seconds: int = Field(default=75, ge=10, le=300)
    chat_context_max_chars: int = Field(default=60_000, ge=4_000, le=200_000)
    chat_detail_context_max_chars: int = Field(default=100_000, ge=4_000, le=300_000)
    chat_planning_timeout_seconds: int = Field(default=20, ge=3, le=60)
    chat_score_margin: float = Field(default=1.0, ge=0, le=100)

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None or value == "":
            return list(_LOCAL_FRONTEND_ORIGINS)
        if isinstance(value, str):
            text = value.strip()
            parsed = json.loads(text) if text.startswith("[") else text.split(",")
        elif isinstance(value, (list, tuple)):
            parsed = value
        else:
            return value
        origins: list[str] = []
        for item in parsed:
            origin = str(item).strip().rstrip("/")
            if origin and origin not in origins:
                origins.append(origin)
        return origins or list(_LOCAL_FRONTEND_ORIGINS)

    @field_validator("api_public_url")
    @classmethod
    def strip_public_url(cls, value: str) -> str:
        return value.strip().rstrip("/")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )


settings = Settings()
