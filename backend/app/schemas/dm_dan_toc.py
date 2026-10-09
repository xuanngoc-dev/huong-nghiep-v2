from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmDanTocWrite(BaseModel):
    ma_dan_toc: str = Field(..., min_length=1, max_length=20)
    ten_dan_toc: str = Field(..., min_length=1, max_length=150)
    ten_goi_khac: str | None = Field(default=None, max_length=255)
    dan_so: int | None = Field(default=None, ge=0, le=200_000_000)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_dan_toc")
    @classmethod
    def strip_ten_dan_toc(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên dân tộc không được để trống")
        return cleaned

    @field_validator("ma_dan_toc")
    @classmethod
    def normalize_ma_dan_toc(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã dân tộc không được để trống")
        return cleaned

    @field_validator("ten_goi_khac", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmDanTocPublic(BaseModel):
    id: int
    ma_dan_toc: str
    ten_dan_toc: str
    ten_goi_khac: str | None = None
    dan_so: int | None = None
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmDanTocPage(BaseModel):
    items: list[DmDanTocPublic]
    total: int
    page: int
    page_size: int


class DmDanTocBulkResult(BaseModel):
    created: int


class DmDanTocDeleteMany(BaseModel):
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


class DmDanTocDeleteManyResult(BaseModel):
    deleted: int
