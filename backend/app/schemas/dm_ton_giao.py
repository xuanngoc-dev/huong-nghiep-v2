from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmTonGiaoWrite(BaseModel):
    ma_ton_giao: str = Field(..., min_length=1, max_length=20)
    ten_ton_giao: str = Field(..., min_length=1, max_length=150)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_ton_giao")
    @classmethod
    def strip_ten_ton_giao(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tôn giáo không được để trống")
        return cleaned

    @field_validator("ma_ton_giao")
    @classmethod
    def normalize_ma_ton_giao(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã tôn giáo không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmTonGiaoPublic(BaseModel):
    id: int
    ma_ton_giao: str
    ten_ton_giao: str
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmTonGiaoPage(BaseModel):
    items: list[DmTonGiaoPublic]
    total: int
    page: int
    page_size: int


class DmTonGiaoBulkResult(BaseModel):
    created: int


class DmTonGiaoDeleteMany(BaseModel):
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


class DmTonGiaoDeleteManyResult(BaseModel):
    deleted: int
