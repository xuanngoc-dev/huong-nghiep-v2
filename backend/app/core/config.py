from urllib.parse import quote_plus

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Định hướng nghề"
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:5173"]
    port: int = 3060

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "huongnghiep"

    # JWT
    secret_key: str = "doi-secret-key-trong-moi-truong-that"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 ngày
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
