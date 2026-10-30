import re
from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

_LIST_FIELDS = (
    "ten_goi_khac",
    "bac_dao_tao",
    "linh_vuc_dao_tao_chinh",
    "linh_vuc_dao_tao_khac",
)

_TEXT_FIELDS = (
    "ten_tieng_anh",
    "ten_viet_tat",
    "slug",
    "loai_co_so",
    "loai_hinh",
    "co_quan_chu_quan",
    "gioi_thieu_ngan",
    "gioi_thieu_chi_tiet",
    "the_manh",
    "ma_tinh_thanh",
    "ten_tinh_thanh",
    "ma_phuong_xa",
    "ten_phuong_xa",
    "dia_chi_tru_so",
    "vung_mien",
    "so_dien_thoai",
    "website",
    "website_tuyen_sinh",
    "hotline_tuyen_sinh",
    "logo_url",
    "anh_dai_dien_url",
    "hoc_phi_trung_binh",
    "trang_thai_hoat_dong",
    "nguon_du_lieu_url",
    "ghi_chu",
)


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_list(value: list | None) -> list[str] | None:
    if not value:
        return None
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError("Mỗi mục trong danh sách phải là chuỗi")
        text = item.strip()
        if not text:
            continue
        if len(text) > 255:
            raise ValueError("Mỗi mục trong danh sách tối đa 255 ký tự")
        if text in seen:
            continue
        seen.add(text)
        cleaned.append(text)
    if len(cleaned) > 50:
        raise ValueError("Mỗi danh sách tối đa 50 mục")
    return cleaned or None


class DmTruongWrite(BaseModel):
    ma_truong: str = Field(..., min_length=1, max_length=20)
    ten_truong: str = Field(..., min_length=1, max_length=255)
    ten_tieng_anh: str | None = Field(default=None, max_length=255)
    ten_viet_tat: str | None = Field(default=None, max_length=50)
    ten_goi_khac: list[str] | None = None
    slug: str | None = Field(default=None, max_length=255)
    loai_co_so: str | None = Field(default=None, max_length=50)
    loai_hinh: str | None = Field(default=None, max_length=50)
    co_quan_chu_quan: str | None = Field(default=None, max_length=255)
    truong_cha_id: int | None = Field(default=None, ge=1)
    ngay_thanh_lap: date | None = None
    nam_thanh_lap: int | None = Field(default=None, ge=1000, le=2100)
    gioi_thieu_ngan: str | None = Field(default=None, max_length=1000)
    gioi_thieu_chi_tiet: str | None = Field(default=None, max_length=20000)
    the_manh: str | None = Field(default=None, max_length=20000)
    bac_dao_tao: list[str] | None = None
    linh_vuc_dao_tao_chinh: list[str] | None = None
    linh_vuc_dao_tao_khac: list[str] | None = None
    ma_tinh_thanh: str | None = Field(default=None, max_length=10)
    ten_tinh_thanh: str | None = Field(default=None, max_length=100)
    ma_phuong_xa: str | None = Field(default=None, max_length=10)
    ten_phuong_xa: str | None = Field(default=None, max_length=100)
    dia_chi_tru_so: str | None = Field(default=None, max_length=500)
    vung_mien: str | None = Field(default=None, max_length=20)
    vi_do: float | None = Field(default=None, ge=-90, le=90)
    kinh_do: float | None = Field(default=None, ge=-180, le=180)
    so_dien_thoai: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=255)
    website: str | None = Field(default=None, max_length=500)
    website_tuyen_sinh: str | None = Field(default=None, max_length=500)
    hotline_tuyen_sinh: str | None = Field(default=None, max_length=30)
    email_tuyen_sinh: str | None = Field(default=None, max_length=255)
    logo_url: str | None = Field(default=None, max_length=1000)
    anh_dai_dien_url: str | None = Field(default=None, max_length=1000)
    dien_tich_m2: float | None = Field(default=None, ge=0)
    hoc_phi_trung_binh: str | None = Field(default=None, max_length=100)
    trang_thai_hoat_dong: str | None = Field(default=None, max_length=30)
    nguon_du_lieu_url: str | None = Field(default=None, max_length=1000)
    ngay_xac_minh: datetime | None = None
    ghi_chu: str | None = Field(default=None, max_length=20000)

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

    @field_validator("email", "email_tuyen_sinh", mode="before")
    @classmethod
    def empty_email(cls, value: str | None) -> str | None:
        cleaned = _blank_to_none(value)
        if cleaned and not _EMAIL.match(cleaned):
            raise ValueError("Email không hợp lệ")
        return cleaned

    @field_validator(*_TEXT_FIELDS)
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)

    @field_validator(*_LIST_FIELDS)
    @classmethod
    def normalize_lists(cls, value: list[str] | None) -> list[str] | None:
        return _clean_list(value)

    @field_validator("vi_do", "kinh_do", "dien_tich_m2", mode="before")
    @classmethod
    def empty_number(cls, value: float | None) -> float | None:
        if value is None or value == "":
            return None
        return value


class DmTruongPublic(BaseModel):
    id: int
    ma_truong: str
    ten_truong: str
    ten_tieng_anh: str | None = None
    ten_viet_tat: str | None = None
    ten_goi_khac: list[str] | None = None
    slug: str | None = None
    loai_co_so: str | None = None
    loai_hinh: str | None = None
    co_quan_chu_quan: str | None = None
    truong_cha_id: int | None = None
    ngay_thanh_lap: date | None = None
    nam_thanh_lap: int | None = None
    gioi_thieu_ngan: str | None = None
    gioi_thieu_chi_tiet: str | None = None
    the_manh: str | None = None
    bac_dao_tao: list[str] | None = None
    linh_vuc_dao_tao_chinh: list[str] | None = None
    linh_vuc_dao_tao_khac: list[str] | None = None
    ma_tinh_thanh: str | None = None
    ten_tinh_thanh: str | None = None
    ma_phuong_xa: str | None = None
    ten_phuong_xa: str | None = None
    dia_chi_tru_so: str | None = None
    vung_mien: str | None = None
    vi_do: float | None = None
    kinh_do: float | None = None
    so_dien_thoai: str | None = None
    email: str | None = None
    website: str | None = None
    website_tuyen_sinh: str | None = None
    hotline_tuyen_sinh: str | None = None
    email_tuyen_sinh: str | None = None
    logo_url: str | None = None
    anh_dai_dien_url: str | None = None
    dien_tich_m2: float | None = None
    hoc_phi_trung_binh: str | None = None
    trang_thai_hoat_dong: str | None = None
    nguon_du_lieu_url: str | None = None
    ngay_xac_minh: datetime | None = None
    ghi_chu: str | None = None
    tao_luc: datetime | None = None
    cap_nhat_luc: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("vi_do", "kinh_do", "dien_tich_m2", mode="before")
    @classmethod
    def decimal_to_float(cls, value: float | None) -> float | None:
        if value is None:
            return None
        return float(value)

    @field_validator(*_LIST_FIELDS, mode="before")
    @classmethod
    def coerce_lists(cls, value: list | None) -> list[str] | None:
        if value is None:
            return None
        if not isinstance(value, list):
            return None
        return [str(item) for item in value if str(item).strip()]


class DmTruongPage(BaseModel):
    items: list[DmTruongPublic]
    total: int
    page: int
    page_size: int


class DmTruongBulkResult(BaseModel):
    created: int


class DmTruongDeleteMany(BaseModel):
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


class DmTruongDeleteManyResult(BaseModel):
    deleted: int
