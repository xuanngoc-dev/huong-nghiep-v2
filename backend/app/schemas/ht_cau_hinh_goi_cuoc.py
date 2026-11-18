from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

LoaiApDung = Literal["edu_coin", "tra_cuu", "khao_sat", "hoi_dap", "token"]

_GIA_TOI_DA = 999_999_999_999_999


class HtCauHinhGoiCuocWrite(BaseModel):
    ma_goi_cuoc: str = Field(..., min_length=1, max_length=50)
    ten_goi_cuoc: str = Field(..., min_length=1, max_length=255)
    loai_ap_dung: LoaiApDung
    gia_goc: int = Field(default=0, ge=0, le=_GIA_TOI_DA)
    gia_khuyen_mai: int | None = Field(default=None, ge=0, le=_GIA_TOI_DA)
    so_luot_nhan_duoc_goc: int = Field(default=0, ge=0, le=1_000_000_000)
    so_luot_nhan_duoc_khuyen_mai: int | None = Field(default=None, ge=0, le=1_000_000_000)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ma_goi_cuoc")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã gói cước không được để trống")
        return cleaned

    @field_validator("ten_goi_cuoc")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên gói cước không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def check_gia_khuyen_mai(self) -> "HtCauHinhGoiCuocWrite":
        if self.gia_khuyen_mai is not None and self.gia_khuyen_mai > self.gia_goc:
            raise ValueError("Giá khuyến mãi không được lớn hơn giá gốc")
        return self


class HtCauHinhGoiCuocPublic(BaseModel):
    id: int
    ma_goi_cuoc: str
    ten_goi_cuoc: str
    loai_ap_dung: str
    gia_goc: int
    gia_khuyen_mai: int | None = None
    so_luot_nhan_duoc_goc: int
    so_luot_nhan_duoc_khuyen_mai: int | None = None
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class HtCauHinhGoiCuocDangBan(BaseModel):
    """Gói đang bán hiển thị cho thành viên ở trang nạp tiền, không kèm ghi chú nội bộ."""

    id: int
    ma_goi_cuoc: str
    ten_goi_cuoc: str
    loai_ap_dung: str
    gia_goc: int
    gia_khuyen_mai: int | None = None
    so_luot_nhan_duoc_goc: int
    so_luot_nhan_duoc_khuyen_mai: int | None = None

    model_config = {"from_attributes": True}


class HtCauHinhGoiCuocPage(BaseModel):
    items: list[HtCauHinhGoiCuocPublic]
    total: int
    page: int
    page_size: int


class HtCauHinhGoiCuocTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class HtCauHinhGoiCuocDeleteMany(BaseModel):
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


class HtCauHinhGoiCuocDeleteManyResult(BaseModel):
    deleted: int
