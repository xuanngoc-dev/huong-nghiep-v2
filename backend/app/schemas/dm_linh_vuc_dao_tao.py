from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmLinhVucDaoTaoWrite(BaseModel):
    ma_linh_vuc: str = Field(..., min_length=1, max_length=20)
    ten_linh_vuc: str = Field(..., min_length=1, max_length=255)
    ten_tieng_anh: str = Field(..., min_length=1, max_length=255)
    mo_ta: str | None = Field(default=None, max_length=5000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_linh_vuc")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên lĩnh vực không được để trống")
        return cleaned

    @field_validator("ten_tieng_anh")
    @classmethod
    def strip_ten_tieng_anh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tiếng Anh không được để trống")
        return cleaned

    @field_validator("ma_linh_vuc")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã lĩnh vực không được để trống")
        return cleaned

    @field_validator("mo_ta")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmLinhVucDaoTaoPublic(BaseModel):
    id: int
    ma_linh_vuc: str
    ten_linh_vuc: str
    ten_tieng_anh: str
    mo_ta: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmLinhVucDaoTaoPage(BaseModel):
    items: list[DmLinhVucDaoTaoPublic]
    total: int
    page: int
    page_size: int


class DmLinhVucDaoTaoBulkResult(BaseModel):
    created: int


class DmLinhVucDaoTaoDeleteMany(BaseModel):
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


class DmLinhVucDaoTaoDeleteManyResult(BaseModel):
    deleted: int
