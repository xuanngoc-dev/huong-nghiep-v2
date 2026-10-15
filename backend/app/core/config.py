from urllib.parse import quote_plus

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Định hướng nghề"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
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
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    openai_api_key: str = ""
    openai_model: str = "gpt-6-luna"
    chat_timeout_seconds: int = Field(default=75, ge=10, le=300)
    chat_context_max_chars: int = Field(default=60_000, ge=4_000, le=200_000)
    chat_detail_context_max_chars: int = Field(default=100_000, ge=4_000, le=300_000)
    chat_planning_timeout_seconds: int = Field(default=20, ge=3, le=60)

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

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
