from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class DmTinhThanhWrite(BaseModel):
    ten_tinh: str = Field(..., min_length=1, max_length=150)
    ma_tinh: str = Field(..., min_length=1, max_length=20)
    khu_vuc: str | None = Field(default=None, max_length=100)
    dien_tich: float | None = Field(default=None, ge=0, le=99_999_999)
    nam_thanh_lap: int | None = Field(default=None, ge=1000, le=2100)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_tinh")
    @classmethod
    def strip_ten_tinh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tỉnh không được để trống")
        return cleaned

    @field_validator("ma_tinh")
    @classmethod
    def normalize_ma_tinh(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã tỉnh không được để trống")
        return cleaned

    @field_validator("khu_vuc", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmTinhThanhPublic(BaseModel):
    id: int
    ten_tinh: str
    ma_tinh: str
    khu_vuc: str | None = None
    dien_tich: float | None = None
    nam_thanh_lap: int | None = None
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("dien_tich", mode="before")
    @classmethod
    def decimal_to_float(cls, value: Decimal | float | None) -> float | None:
        if value is None:
            return None
        return float(value)


class DmTinhThanhPage(BaseModel):
    items: list[DmTinhThanhPublic]
    total: int
    page: int
    page_size: int


class DmTinhThanhBulkResult(BaseModel):
    created: int


class DmTinhThanhDeleteMany(BaseModel):
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


class DmTinhThanhDeleteManyResult(BaseModel):
    deleted: int
