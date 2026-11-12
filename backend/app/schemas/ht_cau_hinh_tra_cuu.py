from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

# Giới hạn trên cho số lượt mỗi ngày, tránh nhập nhầm số quá lớn.
_LUOT_TOI_DA = 10000


class HtCauHinhTraCuuWrite(BaseModel):
    so_luot_tra_cuu_khach_ngay: int = Field(..., ge=0, le=_LUOT_TOI_DA)
    so_luot_tra_cuu_thanh_vien_ngay: int = Field(..., ge=0, le=_LUOT_TOI_DA)
    so_luot_tu_van_ai_ngay: int = Field(..., ge=0, le=_LUOT_TOI_DA)
    so_luot_phan_tich_truong_ngay: int = Field(..., ge=0, le=_LUOT_TOI_DA)
    bat_tinh_nang_holland: bool = True
    bat_thanh_toan: bool = False
    gia_bao_cao_chuyen_sau: Decimal = Field(default=Decimal(0), ge=0, le=Decimal("999999999999999"))
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("gia_bao_cao_chuyen_sau")
    @classmethod
    def lam_tron_gia(cls, value: Decimal) -> Decimal:
        # Giá tính theo VNĐ, không có phần lẻ.
        if value != value.to_integral_value():
            raise ValueError("Giá báo cáo phải là số nguyên (VNĐ)")
        return value


class HtCauHinhTraCuuPublic(BaseModel):
    id: int
    so_luot_tra_cuu_khach_ngay: int
    so_luot_tra_cuu_thanh_vien_ngay: int
    so_luot_tu_van_ai_ngay: int
    so_luot_phan_tich_truong_ngay: int
    bat_tinh_nang_holland: bool
    bat_thanh_toan: bool
    gia_bao_cao_chuyen_sau: int
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class HtCauHinhTraCuuPage(BaseModel):
    items: list[HtCauHinhTraCuuPublic]
    total: int
    page: int
    page_size: int


class HtCauHinhTraCuuTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class HtCauHinhTraCuuDeleteMany(BaseModel):
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


class HtCauHinhTraCuuDeleteManyResult(BaseModel):
    deleted: int
