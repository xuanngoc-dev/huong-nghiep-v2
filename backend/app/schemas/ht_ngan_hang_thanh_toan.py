import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_SO_TAI_KHOAN = re.compile(r"^[0-9A-Za-z]{4,50}$")


class HtNganHangThanhToanWrite(BaseModel):
    ten_ngan_hang: str = Field(..., min_length=1, max_length=255)
    ten_ngan_hang_tieng_anh: str | None = Field(default=None, max_length=255)
    ten_ngan_hang_viet_tat: str = Field(..., min_length=1, max_length=50)
    so_tai_khoan: str = Field(..., min_length=1, max_length=50)
    chu_tai_khoan: str = Field(..., min_length=1, max_length=255)
    logo_ngan_hang: str | None = Field(default=None, max_length=500)
    ghi_chu: str | None = Field(default=None, max_length=2000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_ngan_hang")
    @classmethod
    def strip_ten_ngan_hang(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên ngân hàng không được để trống")
        return cleaned

    @field_validator("ten_ngan_hang_viet_tat")
    @classmethod
    def normalize_viet_tat(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Tên viết tắt không được để trống")
        return cleaned

    @field_validator("so_tai_khoan")
    @classmethod
    def normalize_so_tai_khoan(cls, value: str) -> str:
        # Bỏ khoảng trắng và dấu gạch người dùng hay gõ để dễ đọc.
        cleaned = re.sub(r"[\s.-]", "", value)
        if not _SO_TAI_KHOAN.fullmatch(cleaned):
            raise ValueError("Số tài khoản chỉ gồm chữ và số, từ 4 đến 50 ký tự")
        return cleaned

    @field_validator("chu_tai_khoan")
    @classmethod
    def normalize_chu_tai_khoan(cls, value: str) -> str:
        # Tên chủ tài khoản in hoa như trên thẻ/ứng dụng ngân hàng.
        cleaned = " ".join(value.split()).upper()
        if not cleaned:
            raise ValueError("Chủ tài khoản không được để trống")
        return cleaned

    @field_validator("logo_ngan_hang")
    @classmethod
    def check_logo(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        if not re.match(r"^(https?://|/)", cleaned, re.IGNORECASE):
            raise ValueError("Logo phải là URL bắt đầu bằng http(s):// hoặc /")
        return cleaned

    @field_validator("ten_ngan_hang_tieng_anh", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class HtNganHangThanhToanPublic(BaseModel):
    id: int
    ten_ngan_hang: str
    ten_ngan_hang_tieng_anh: str | None = None
    ten_ngan_hang_viet_tat: str
    so_tai_khoan: str
    chu_tai_khoan: str
    logo_ngan_hang: str | None = None
    ghi_chu: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class HtNganHangThanhToanPage(BaseModel):
    items: list[HtNganHangThanhToanPublic]
    total: int
    page: int
    page_size: int


class HtNganHangThanhToanTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class HtNganHangLuaChon(BaseModel):
    ten_ngan_hang_viet_tat: str
    ten_ngan_hang: str


class HtNganHangThanhToanDeleteMany(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)

    @field_validator("ids")
    @classmethod
    def unique_ids(cls, value: list[int]) -> list[int]:
        unique: list[int] = []
        seen: set[int] = set()
        for item_id in value:
            if item_id < 1:
                raise ValueError("ID không hợp lệ")
            if item_id in seen:
                continue
            seen.add(item_id)
            unique.append(item_id)
        return unique


class HtNganHangThanhToanDeleteManyResult(BaseModel):
    deleted: int
