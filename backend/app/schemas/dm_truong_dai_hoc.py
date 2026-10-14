from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DmTruongDaiHocWrite(BaseModel):
    ma_truong: str = Field(..., min_length=1, max_length=20)
    ten_truong: str = Field(..., min_length=1, max_length=255)
    ten_viet_tat: str | None = Field(default=None, max_length=50)
    ten_tieng_anh: str | None = Field(default=None, max_length=255)
    khu_vuc: str | None = Field(default=None, max_length=50)
    dia_chi: str | None = Field(default=None, max_length=5000)
    loai_hinh_dao_tao: str | None = Field(default=None, max_length=50)
    nhom_nganh: str | None = Field(default=None, max_length=100)
    website: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=100)
    so_dien_thoai: str | None = Field(default=None, max_length=50)
    logo: str | None = Field(default=None, max_length=255)
    anh_bia: str | None = Field(default=None, max_length=255)
    gioi_thieu: str | None = Field(default=None, max_length=20000)
    hoc_phi_trung_binh: str | None = Field(default=None, max_length=100)
    nam_thanh_lap: int | None = Field(default=None, ge=1000, le=2100)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_truong")
    @classmethod
    def strip_ten_truong(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên trường không được để trống")
        return cleaned

    @field_validator("ma_truong")
    @classmethod
    def normalize_ma_truong(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã trường không được để trống")
        return cleaned

    @field_validator("email", mode="before")
    @classmethod
    def empty_email(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @field_validator(
        "ten_viet_tat",
        "ten_tieng_anh",
        "khu_vuc",
        "dia_chi",
        "loai_hinh_dao_tao",
        "nhom_nganh",
        "website",
        "so_dien_thoai",
        "logo",
        "anh_bia",
        "gioi_thieu",
        "hoc_phi_trung_binh",
    )
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)


class DmTruongDaiHocPublic(BaseModel):
    id: int
    ma_truong: str
    ten_truong: str
    ten_viet_tat: str | None = None
    ten_tieng_anh: str | None = None
    khu_vuc: str | None = None
    dia_chi: str | None = None
    loai_hinh_dao_tao: str | None = None
    nhom_nganh: str | None = None
    website: str | None = None
    email: str | None = None
    so_dien_thoai: str | None = None
    logo: str | None = None
    anh_bia: str | None = None
    gioi_thieu: str | None = None
    hoc_phi_trung_binh: str | None = None
    nam_thanh_lap: int | None = None
    trang_thai: int
    ngay_tao: datetime | None = None
    ngay_cap_nhat: datetime | None = None

    model_config = {"from_attributes": True}


class DmTruongDaiHocPage(BaseModel):
    items: list[DmTruongDaiHocPublic]
    total: int
    page: int
    page_size: int


class DmTruongDaiHocBulkResult(BaseModel):
    created: int


class DmTruongDaiHocDeleteMany(BaseModel):
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


class DmTruongDaiHocDeleteManyResult(BaseModel):
    deleted: int
