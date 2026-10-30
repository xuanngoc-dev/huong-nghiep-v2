from datetime import datetime
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, field_validator

_LOAI_CANONICAL = {
    "trong_nuoc": "trong_nuoc",
    "trong nuoc": "trong_nuoc",
    "trong nước": "trong_nuoc",
    "quoc_te": "quoc_te",
    "quoc te": "quoc_te",
    "quốc tế": "quoc_te",
}
_ACTIVE = {"1", "hoat_dong", "hoạt động", "hoat dong"}
_INACTIVE = {"0", "ngung", "ngừng sử dụng", "ngung su dung"}
_TEXT_FIELDS = (
    "ten_chi_tiet",
    "linh_vuc",
    "mon",
    "ten_viet_tat",
    "don_vi_to_chuc",
    "loai_danh_gia",
    "mo_ta",
    "doi_tuong_du_thi",
    "thang_diem",
    "don_vi_diem",
    "cach_cong_bo_ket_qua",
    "website_chinh_thuc",
    "nguon_du_lieu_url",
    "ghi_chu",
)
_SCORE_LIMIT = Decimal("999999.99")


def normalize_trang_thai(value: str | int | None) -> str | None:
    """Chuẩn hóa 0/1 và các cách gọi trạng thái về Hoạt động hoặc Ngừng sử dụng."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return "Hoạt động" if value else "Ngừng sử dụng"
    if isinstance(value, int):
        if value == 1:
            return "Hoạt động"
        if value == 0:
            return "Ngừng sử dụng"
        raise ValueError("Trạng thái không hợp lệ")
    text = str(value).strip()
    if not text:
        return None
    lowered = text.lower()
    if lowered in _ACTIVE:
        return "Hoạt động"
    if lowered in _INACTIVE:
        return "Ngừng sử dụng"
    if len(text) > 20:
        raise ValueError("Trạng thái tối đa 20 ký tự")
    return text


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _optional_score(value: Decimal | float | int | str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Điểm phải là số") from None
    if number < 0 or number > _SCORE_LIMIT:
        raise ValueError("Điểm phải từ 0 đến 999999.99")
    return number.quantize(Decimal("0.01"))


class DmBaiThiDanhGiaNangLucWrite(BaseModel):
    ma_bai_thi: str = Field(..., min_length=1, max_length=50)
    ten_bai_thi: str = Field(..., min_length=1, max_length=255)
    ten_chi_tiet: str | None = Field(default=None, max_length=500)
    linh_vuc: str | None = Field(default=None, max_length=150)
    mon: str | None = Field(default=None, max_length=150)
    ten_viet_tat: str | None = Field(default=None, max_length=50)
    don_vi_to_chuc: str | None = Field(default=None, max_length=255)
    loai_danh_gia: str | None = Field(default=None, max_length=50)
    loai_chung_chi: str | None = Field(default=None, max_length=50)
    mo_ta: str | None = None
    doi_tuong_du_thi: str | None = None
    hinh_thuc_thi: list | dict | None = None
    thang_diem: str | None = Field(default=None, max_length=100)
    diem_toi_thieu: Decimal | None = None
    don_vi_diem: str | None = Field(default=None, max_length=30)
    cau_truc_bai_thi: list | dict | None = None
    thoi_luong_phut: int | None = Field(default=None, ge=0, le=65535)
    cach_cong_bo_ket_qua: str | None = None
    nam_ap_dung_tu: int | None = Field(default=None, ge=0, le=65535)
    nam_ap_dung_den: int | None = Field(default=None, ge=0, le=65535)
    website_chinh_thuc: str | None = Field(default=None, max_length=1000)
    nguon_du_lieu_url: str | None = Field(default=None, max_length=1000)
    trang_thai: str | None = Field(default="Hoạt động", max_length=20)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ten_bai_thi")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên bài thi không được để trống")
        return cleaned

    @field_validator("ma_bai_thi")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã bài thi không được để trống")
        return cleaned

    @field_validator("loai_chung_chi", mode="before")
    @classmethod
    def normalize_loai(cls, value: str | None) -> str | None:
        cleaned = _blank_to_none(None if value is None else str(value))
        if cleaned is None:
            return None
        return _LOAI_CANONICAL.get(cleaned.lower()) or cleaned

    @field_validator("trang_thai", mode="before")
    @classmethod
    def normalize_status(cls, value: str | int | None) -> str:
        return normalize_trang_thai(value) or "Hoạt động"

    @field_validator(*_TEXT_FIELDS, mode="before")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _blank_to_none(str(value))

    @field_validator("diem_toi_thieu", mode="before")
    @classmethod
    def clean_score(cls, value: Decimal | float | int | str | None) -> Decimal | None:
        return _optional_score(value)

    @field_validator("thoi_luong_phut", "nam_ap_dung_tu", "nam_ap_dung_den", mode="before")
    @classmethod
    def empty_int(cls, value: int | str | None) -> int | None:
        if value is None or value == "":
            return None
        return value


class DmBaiThiDanhGiaNangLucPublic(BaseModel):
    id: int
    ma_bai_thi: str | None = None
    ten_bai_thi: str
    ten_chi_tiet: str | None = None
    linh_vuc: str | None = None
    mon: str | None = None
    ten_viet_tat: str | None = None
    don_vi_to_chuc: str | None = None
    loai_danh_gia: str | None = None
    loai_chung_chi: str | None = None
    mo_ta: str | None = None
    doi_tuong_du_thi: str | None = None
    hinh_thuc_thi: list | dict | None = None
    thang_diem: str | None = None
    diem_toi_thieu: float | None = None
    don_vi_diem: str | None = None
    cau_truc_bai_thi: list | dict | None = None
    thoi_luong_phut: int | None = None
    cach_cong_bo_ket_qua: str | None = None
    nam_ap_dung_tu: int | None = None
    nam_ap_dung_den: int | None = None
    website_chinh_thuc: str | None = None
    nguon_du_lieu_url: str | None = None
    trang_thai: str | None = None
    ghi_chu: str | None = None
    tao_luc: datetime | None = None
    cap_nhat_luc: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("diem_toi_thieu", mode="before")
    @classmethod
    def decimal_to_float(cls, value: Decimal | float | None) -> float | None:
        if value is None:
            return None
        return float(value)


class DmBaiThiDanhGiaNangLucPage(BaseModel):
    items: list[DmBaiThiDanhGiaNangLucPublic]
    total: int
    page: int
    page_size: int


class DmBaiThiDanhGiaNangLucBulkResult(BaseModel):
    created: int


class DmBaiThiDanhGiaNangLucDeleteMany(BaseModel):
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


class DmBaiThiDanhGiaNangLucDeleteManyResult(BaseModel):
    deleted: int
