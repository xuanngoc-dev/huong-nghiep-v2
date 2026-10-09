from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class DmKhuVucUuTienWrite(BaseModel):
    ten_khu_vuc: str = Field(..., min_length=1, max_length=150)
    ma_khu_vuc: str = Field(..., min_length=1, max_length=20)
    diem_cong: float = Field(default=0, ge=0, le=99.99)
    ghi_chu: str | None = Field(default=None, max_length=2000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_khu_vuc")
    @classmethod
    def strip_ten_khu_vuc(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên khu vực không được để trống")
        return cleaned

    @field_validator("ma_khu_vuc")
    @classmethod
    def normalize_ma_khu_vuc(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã khu vực không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmKhuVucUuTienPublic(BaseModel):
    id: int
    ten_khu_vuc: str
    ma_khu_vuc: str
    diem_cong: float
    ghi_chu: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("diem_cong", mode="before")
    @classmethod
    def decimal_to_float(cls, value: Decimal | float | None) -> float:
        if value is None:
            return 0
        return float(value)


class DmKhuVucUuTienPage(BaseModel):
    items: list[DmKhuVucUuTienPublic]
    total: int
    page: int
    page_size: int


class DmKhuVucUuTienBulkResult(BaseModel):
    created: int


class DmKhuVucUuTienDeleteMany(BaseModel):
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


class DmKhuVucUuTienDeleteManyResult(BaseModel):
    deleted: int
