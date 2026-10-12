from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_LOAI = {"trong_nuoc", "quoc_te"}


class DmChungChiNgoaiNguWrite(BaseModel):
    ma_chung_chi: str = Field(..., min_length=1, max_length=50)
    ten_chung_chi: str = Field(..., min_length=1, max_length=255)
    ten_chi_tiet: str | None = Field(default=None, max_length=500)
    linh_vuc: str | None = Field(default=None, max_length=150)
    mon: str | None = Field(default=None, max_length=150)
    loai_chung_chi: str = Field(..., min_length=1, max_length=20)
    thang_diem: str | None = Field(default=None, max_length=100)
    don_vi_cap: str | None = Field(default=None, max_length=255)
    trang_thai: int = Field(default=1, ge=0, le=1)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_chung_chi")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên chứng chỉ không được để trống")
        return cleaned

    @field_validator("ma_chung_chi")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã chứng chỉ không được để trống")
        return cleaned

    @field_validator("loai_chung_chi")
    @classmethod
    def check_loai(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if cleaned not in _LOAI:
            raise ValueError("Loại chứng chỉ phải là trong_nuoc hoặc quoc_te")
        return cleaned

    @field_validator("ten_chi_tiet", "linh_vuc", "mon", "thang_diem", "don_vi_cap", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmChungChiNgoaiNguPublic(BaseModel):
    id: int
    ma_chung_chi: str
    ten_chung_chi: str
    ten_chi_tiet: str | None = None
    linh_vuc: str | None = None
    mon: str | None = None
    loai_chung_chi: str
    thang_diem: str | None = None
    don_vi_cap: str | None = None
    trang_thai: int
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmChungChiNgoaiNguPage(BaseModel):
    items: list[DmChungChiNgoaiNguPublic]
    total: int
    page: int
    page_size: int


class DmChungChiNgoaiNguBulkResult(BaseModel):
    created: int


class DmChungChiNgoaiNguDeleteMany(BaseModel):
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


class DmChungChiNgoaiNguDeleteManyResult(BaseModel):
    deleted: int
