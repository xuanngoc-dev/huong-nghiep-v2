import json
from typing import Annotated, Literal
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Mặc định cho phép mọi domain gọi API từ trình duyệt. Muốn giới hạn thì đặt CORS_ORIGINS là danh sách domain.
_MOI_DOMAIN = ["*"]


class Settings(BaseSettings):
    app_name: str = "Định hướng nghề"
    api_v1_prefix: str = "/api/v1"
    # Domain được phép gọi API từ trình duyệt; "*" (mặc định, kể cả khi để trống) là mọi domain.
    # Postman/Bruno không bị CORS nên không cần nằm trong danh sách này.
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=lambda: list(_MOI_DOMAIN))
    # Origin công khai của API, không gồm /api/v1. Để trống thì /docs dùng đúng host đang mở.
    api_public_url: str = ""
    port: int = 3060
    log_retention_days: int = Field(default=14, ge=1)
    # Múi giờ của hệ thống (tên IANA): giờ lưu vào CSDL, NOW() của MySQL, ngày hiện tại, log... Env: TIMEZONE.
    timezone: str = "Asia/Ho_Chi_Minh"

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
    # Nguồn dữ liệu tuyển sinh cho chat: "database" dựng từ các đề án đã công bố (dats_tuyen_sinh và bảng liên quan,
    # mặc định), "thu_muc" đọc file JSON/TXT trong TAI_LIEU_DIR. Env: CHAT_NGUON_DU_LIEU.
    chat_nguon_du_lieu: Literal["thu_muc", "database"] = "database"
    # Chế độ database: số giây giữ dữ liệu đã dựng trước khi đọc lại CSDL. Env: CHAT_DB_CACHE_SECONDS.
    chat_db_cache_seconds: int = Field(default=300, ge=0, le=86_400)
    # Ảnh và video thư viện. Nếu để trống, lưu tại backend/thu_vien.
    thu_vien_dir: str = ""
    thu_vien_max_bytes: int = 100 * 1024 * 1024
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-6.2-sol"
    chat_timeout_seconds: int = Field(default=75, ge=10, le=300)
    chat_context_max_chars: int = Field(default=60_000, ge=4_000, le=200_000)
    chat_detail_context_max_chars: int = Field(default=100_000, ge=4_000, le=300_000)
    chat_planning_timeout_seconds: int = Field(default=20, ge=3, le=60)
    chat_score_margin: float = Field(default=1.0, ge=0, le=100)
    # Chat luôn trừ token khả dụng / cộng token đã dùng của thành viên sau mỗi lượt trả lời. True (mặc định):
    # thành viên hết token thì không hỏi được (402, mời nạp gói token); khách vãng lai không bị chặn.
    # False: chỉ trừ, không chặn. Env: CHAT_YEU_CAU_TOKEN.
    chat_yeu_cau_token: bool = True
    # Tìm trường phù hợp: False chỉ dùng dm_nganh_hoc_theo_truong; True giữ thêm điều kiện
    # trường có ngành trong đề án/phương thức tuyển sinh cùng năm. Env: TIM_TRUONG_KET_HOP_PHUONG_THUC.
    tim_truong_ket_hop_phuong_thuc: bool = False
    # Khóa xác thực webhook giao dịch ngân hàng (SePay gửi header "Authorization: Apikey <khóa>").
    # Để trống thì KHÔNG xác thực (chỉ dùng cho hệ thống test). Env: WEBHOOK_NGAN_HANG_API_KEY.
    webhook_ngan_hang_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None or value == "":
            return list(_MOI_DOMAIN)
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
        return origins or list(_MOI_DOMAIN)

    @field_validator("timezone")
    @classmethod
    def kiem_tra_mui_gio(cls, value: str) -> str:
        value = value.strip() or "Asia/Ho_Chi_Minh"
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"TIMEZONE không hợp lệ: {value} (dùng tên IANA, vd. Asia/Ho_Chi_Minh)") from exc
        return value

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
