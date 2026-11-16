from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class XtDiemChuanWrite(BaseModel):
    ma_truong: str = Field(..., min_length=1, max_length=20)
    nam_tuyen_sinh: int = Field(..., ge=1990, le=2100)
    ma_xet_tuyen: str = Field(..., min_length=1, max_length=20)
    ten_chuong_trinh: str | None = Field(default=None, max_length=255)
    ma_phuong_thuc_cua_bo: str | None = Field(default=None, max_length=20)
    to_hop_id: int | None = Field(default=None, ge=1)
    diem_chuan: Decimal = Field(..., ge=0, max_digits=7, decimal_places=2)
    thang_diem: Decimal = Field(default=Decimal("30"), gt=0, max_digits=6, decimal_places=2)
    tieu_chi_phu: str | None = Field(default=None, max_length=255)
    nguon_du_lieu_url: str | None = Field(default=None, max_length=1000)
    ghi_chu: str | None = Field(default=None, max_length=20000)

    @field_validator("ma_truong", "ma_xet_tuyen")
    @classmethod
    def require_code(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Không được để trống")
        return cleaned

    @field_validator("to_hop_id", mode="before")
    @classmethod
    def empty_number_to_none(cls, value):
        if value is None or value == "":
            return None
        return value

    @field_validator("ten_chuong_trinh", "ma_phuong_thuc_cua_bo", "tieu_chi_phu", "nguon_du_lieu_url", "ghi_chu")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @model_validator(mode="after")
    def check_scale(self):
        if self.diem_chuan > self.thang_diem:
            raise ValueError("Điểm chuẩn không được lớn hơn thang điểm")
        return self


class XtDiemChuanPublic(BaseModel):
    id: int
    ma_truong: str
    ten_truong: str | None = None
    nam_tuyen_sinh: int
    ma_xet_tuyen: str
    ten_chuong_trinh: str | None = None
    ma_phuong_thuc_cua_bo: str | None = None
    ten_phuong_thuc: str | None = None
    to_hop_id: int | None = None
    ma_to_hop: str | None = None
    diem_chuan: float
    thang_diem: float
    tieu_chi_phu: str | None = None
    nguon_du_lieu_url: str | None = None
    ghi_chu: str | None = None
    tao_luc: datetime | None = None
    cap_nhat_luc: datetime | None = None


class XtDiemChuanPage(BaseModel):
    items: list[XtDiemChuanPublic]
    total: int
    page: int
    page_size: int


class XtDiemChuanBulkResult(BaseModel):
    created: int


class XtDiemChuanDeleteMany(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)

    @field_validator("ids")
    @classmethod
    def unique_ids(cls, value: list[int]) -> list[int]:
        if any(item_id < 1 for item_id in value):
            raise ValueError("ID không hợp lệ")
        return list(dict.fromkeys(value))


class XtDiemChuanDeleteManyResult(BaseModel):
    deleted: int
