from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

KieuTraLoi = Literal["diem_so", "tinh_huong"]


class HtCauHinhEnduserWrite(BaseModel):
    ten_cau_hinh: str = Field(..., min_length=1, max_length=255)
    noi_dung_cau_hinh: Any = None
    kieu_tra_loi: KieuTraLoi = "diem_so"
    mo_ta: str | None = Field(default=None, max_length=2000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_cau_hinh")
    @classmethod
    def strip_ten_cau_hinh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên cấu hình không được để trống")
        return cleaned

    @field_validator("mo_ta")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class HtCauHinhEnduserPublic(BaseModel):
    id: int
    ten_cau_hinh: str
    noi_dung_cau_hinh: Any = None
    kieu_tra_loi: str
    mo_ta: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class HtCauHinhEnduserApDung(BaseModel):
    """Cấu hình đang áp dụng cho người dùng cuối, không kèm mô tả nội bộ."""

    id: int
    ten_cau_hinh: str
    kieu_tra_loi: str
    noi_dung_cau_hinh: Any = None

    model_config = {"from_attributes": True}


class HtCauHinhEnduserPage(BaseModel):
    items: list[HtCauHinhEnduserPublic]
    total: int
    page: int
    page_size: int


class HtCauHinhEnduserTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class HtCauHinhEnduserDeleteMany(BaseModel):
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


class HtCauHinhEnduserDeleteManyResult(BaseModel):
    deleted: int
