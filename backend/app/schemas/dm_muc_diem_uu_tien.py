from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class DmMucDiemUuTienWrite(BaseModel):
    loai: Literal["KHU_VUC", "DOI_TUONG"]
    ma: str = Field(..., min_length=1, max_length=20, description="ma_khu_vuc hoặc ma_doi_tuong")
    nam_ap_dung_tu: int = Field(..., ge=2000, le=2100)
    nam_ap_dung_den: int | None = Field(default=None, ge=2000, le=2100, description="Để trống = đến nay")
    diem_cong: float = Field(..., ge=0, le=10)
    can_cu: str | None = Field(default=None, max_length=255)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ma")
    @classmethod
    def chuan_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã không được để trống")
        return cleaned

    @field_validator("can_cu", "ghi_chu")
    @classmethod
    def rong_thanh_none(cls, value: str | None) -> str | None:
        return (value or "").strip() or None

    @model_validator(mode="after")
    def kiem_khoang_nam(self):
        if self.nam_ap_dung_den is not None and self.nam_ap_dung_den < self.nam_ap_dung_tu:
            raise ValueError("Năm áp dụng đến phải lớn hơn hoặc bằng năm áp dụng từ")
        return self


class DmMucDiemUuTienPublic(BaseModel):
    id: int
    loai: str
    ma: str
    ten: str | None = None
    nam_ap_dung_tu: int
    nam_ap_dung_den: int | None = None
    diem_cong: float
    can_cu: str | None = None
    ghi_chu: str | None = None
    cap_nhat_luc: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("diem_cong", mode="before")
    @classmethod
    def decimal_to_float(cls, value: Decimal | float) -> float:
        return float(value)


class DmMucDiemUuTienPage(BaseModel):
    items: list[DmMucDiemUuTienPublic]
    total: int
    page: int
    page_size: int


class DmMucDiemUuTienDeleteMany(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)


class DmMucDiemUuTienDeleteManyResult(BaseModel):
    deleted: int
