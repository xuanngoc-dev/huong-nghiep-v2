from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmMonHocWrite(BaseModel):
    ma_mon_hoc: str = Field(..., min_length=1, max_length=20)
    ten_mon_hoc: str = Field(..., min_length=1, max_length=150)
    ten_viet_tat: str | None = Field(default=None, max_length=50)
    nhom_mon: str | None = Field(default=None, max_length=50)
    trang_thai: int = Field(default=1, ge=0, le=1)
    mo_ta: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_mon_hoc")
    @classmethod
    def strip_ten_mon_hoc(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên môn học không được để trống")
        return cleaned

    @field_validator("ma_mon_hoc")
    @classmethod
    def normalize_ma_mon_hoc(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã môn học không được để trống")
        return cleaned

    @field_validator("ten_viet_tat", "nhom_mon", "mo_ta")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmMonHocPublic(BaseModel):
    id: int
    ma_mon_hoc: str
    ten_mon_hoc: str
    ten_viet_tat: str | None = None
    nhom_mon: str | None = None
    trang_thai: int
    mo_ta: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmMonHocPage(BaseModel):
    items: list[DmMonHocPublic]
    total: int
    page: int
    page_size: int


class DmMonHocBulkResult(BaseModel):
    created: int


class DmMonHocDeleteMany(BaseModel):
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


class DmMonHocDeleteManyResult(BaseModel):
    deleted: int
