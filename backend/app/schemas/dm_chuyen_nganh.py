from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _normalize_ma_holand(value: list[str] | None) -> list[str] | None:
    if not value:
        return None
    cleaned: list[str] = []
    seen: set[str] = set()
    for code in value:
        item = str(code).strip().upper()
        if not item:
            raise ValueError("Mã Holland không được để trống")
        if len(item) > 20:
            raise ValueError("Mã Holland tối đa 20 ký tự")
        if item in seen:
            continue
        seen.add(item)
        cleaned.append(item)
    if len(cleaned) > 10:
        raise ValueError("Chỉ chọn tối đa 10 mã Holland")
    return cleaned or None


class DmChuyenNganhWrite(BaseModel):
    ma_nganh: str = Field(..., min_length=1, max_length=20)
    ten_chuyen_nganh: str = Field(..., min_length=1, max_length=255)
    ma_chuyen_nganh: str = Field(..., min_length=1, max_length=20)
    ten_tieng_anh: str = Field(..., min_length=1, max_length=255)
    mo_ta: str | None = Field(default=None, max_length=5000)
    ma_holand: list[str] | None = None
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_chuyen_nganh")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên chuyên ngành không được để trống")
        return cleaned

    @field_validator("ten_tieng_anh")
    @classmethod
    def strip_ten_tieng_anh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tiếng Anh không được để trống")
        return cleaned

    @field_validator("ma_nganh")
    @classmethod
    def normalize_ma_nganh(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã ngành không được để trống")
        return cleaned

    @field_validator("ma_chuyen_nganh")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã chuyên ngành không được để trống")
        return cleaned

    @field_validator("ma_holand")
    @classmethod
    def normalize_ma_holand(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_ma_holand(value)

    @field_validator("mo_ta")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmChuyenNganhPublic(BaseModel):
    id: int
    ma_nganh: str
    ten_nganh: str
    ten_chuyen_nganh: str
    ma_chuyen_nganh: str
    ten_tieng_anh: str
    mo_ta: str | None = None
    ma_holand: list[str] | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DmChuyenNganhPage(BaseModel):
    items: list[DmChuyenNganhPublic]
    total: int
    page: int
    page_size: int


class DmChuyenNganhBulkResult(BaseModel):
    created: int


class DmChuyenNganhDeleteMany(BaseModel):
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


class DmChuyenNganhDeleteManyResult(BaseModel):
    deleted: int
