from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmToHopMonHocWrite(BaseModel):
    ma_to_hop: str = Field(..., min_length=1, max_length=20)
    ten_to_hop: str = Field(..., min_length=1, max_length=150)
    ds_mon_hoc: list[str] = Field(..., min_length=1, max_length=20)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_to_hop")
    @classmethod
    def strip_ten_to_hop(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tổ hợp không được để trống")
        return cleaned

    @field_validator("ma_to_hop")
    @classmethod
    def normalize_ma_to_hop(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã tổ hợp không được để trống")
        return cleaned

    @field_validator("ds_mon_hoc")
    @classmethod
    def normalize_ds_mon_hoc(cls, value: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()
        for code in value:
            item = str(code).strip().upper()
            if not item:
                raise ValueError("Mã môn học không được để trống")
            if len(item) > 20:
                raise ValueError("Mã môn học tối đa 20 ký tự")
            if item in seen:
                continue
            seen.add(item)
            cleaned.append(item)
        if not cleaned:
            raise ValueError("Vui lòng chọn ít nhất một môn học")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmToHopMonHocPublic(BaseModel):
    id: int
    ma_to_hop: str
    ten_to_hop: str
    ds_mon_hoc: list[str]
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmToHopMonHocPage(BaseModel):
    items: list[DmToHopMonHocPublic]
    total: int
    page: int
    page_size: int


class DmToHopMonHocBulkResult(BaseModel):
    created: int


class DmToHopMonHocDeleteMany(BaseModel):
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


class DmToHopMonHocDeleteManyResult(BaseModel):
    deleted: int
