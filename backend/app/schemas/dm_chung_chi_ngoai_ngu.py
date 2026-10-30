from datetime import datetime
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, field_validator, model_validator

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
    "ma_ngon_ngu",
    "ten_ngon_ngu",
    "don_vi_cap",
    "thang_diem",
    "don_vi_diem",
    "ghi_chu_hinh_thuc_thi",
    "ghi_chu",
)
_LIST_FIELDS = ("ky_nang_duoc_danh_gia", "hinh_thuc_thi")
_SCORE_LIMIT = Decimal("9999.99")


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


def _optional_score(value: Decimal | float | int | str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        number = value if isinstance(value, Decimal) else Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        raise ValueError("Thang điểm phải là số") from None
    if number < 0 or number > _SCORE_LIMIT:
        raise ValueError("Thang điểm phải từ 0 đến 9999.99")
    return number.quantize(Decimal("0.01"))


class DmChungChiNgoaiNguWrite(BaseModel):
    ma_chung_chi: str = Field(..., min_length=1, max_length=50)
    ten_chung_chi: str = Field(..., min_length=1, max_length=255)
    ten_chi_tiet: str | None = Field(default=None, max_length=500)
    linh_vuc: str | None = Field(default=None, max_length=150)
    mon: str | None = Field(default=None, max_length=150)
    ma_ngon_ngu: str | None = Field(default=None, max_length=10)
    ten_ngon_ngu: str | None = Field(default=None, max_length=100)
    don_vi_cap: str | None = Field(default=None, max_length=255)
    loai_chung_chi: str | None = Field(default=None, max_length=50)
    thang_diem: str | None = Field(default=None, max_length=100)
    thang_diem_min: Decimal | None = None
    thang_diem_max: Decimal | None = None
    don_vi_diem: str | None = Field(default=None, max_length=30)
    ky_nang_duoc_danh_gia: list[str] | None = None
    hinh_thuc_thi: list[str] | None = None
    ghi_chu_hinh_thuc_thi: str | None = None
    thoi_han_hieu_luc_thang: int | None = Field(default=None, ge=0, le=65535)
    trang_thai: str = Field(default="Hoạt động", max_length=20)
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

    @field_validator("loai_chung_chi", mode="before")
    @classmethod
    def normalize_loai(cls, value: str | None) -> str | None:
        cleaned = _blank_to_none(None if value is None else str(value))
        if cleaned is None:
            return None
        canonical = _LOAI_CANONICAL.get(cleaned.lower())
        return canonical or cleaned

    @field_validator("trang_thai", mode="before")
    @classmethod
    def normalize_trang_thai(cls, value: str | int | None) -> str:
        if value is None or value == "":
            return "Hoạt động"
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
            return "Hoạt động"
        lowered = text.lower()
        if lowered in _ACTIVE:
            return "Hoạt động"
        if lowered in _INACTIVE:
            return "Ngừng sử dụng"
        if len(text) > 20:
            raise ValueError("Trạng thái tối đa 20 ký tự")
        return text

    @field_validator(*_TEXT_FIELDS, mode="before")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _blank_to_none(str(value))

    @field_validator(*_LIST_FIELDS)
    @classmethod
    def clean_lists(cls, value: list[str] | None) -> list[str] | None:
        return _clean_list(value)

    @field_validator("thang_diem_min", "thang_diem_max", mode="before")
    @classmethod
    def clean_score(cls, value: Decimal | float | int | str | None) -> Decimal | None:
        return _optional_score(value)

    @field_validator("thoi_han_hieu_luc_thang", mode="before")
    @classmethod
    def empty_months(cls, value: int | str | None) -> int | None:
        if value is None or value == "":
            return None
        return value

    @model_validator(mode="after")
    def check_score_range(self) -> "DmChungChiNgoaiNguWrite":
        if (
            self.thang_diem_min is not None
            and self.thang_diem_max is not None
            and self.thang_diem_max < self.thang_diem_min
        ):
            raise ValueError("Điểm cao nhất phải lớn hơn hoặc bằng điểm thấp nhất")
        return self


class DmChungChiNgoaiNguPublic(BaseModel):
    id: int
    ma_chung_chi: str | None = None
    ten_chung_chi: str
    ten_chi_tiet: str | None = None
    linh_vuc: str | None = None
    mon: str | None = None
    ma_ngon_ngu: str | None = None
    ten_ngon_ngu: str | None = None
    don_vi_cap: str | None = None
    loai_chung_chi: str | None = None
    thang_diem: str | None = None
    thang_diem_min: float | None = None
    thang_diem_max: float | None = None
    don_vi_diem: str | None = None
    ky_nang_duoc_danh_gia: list | None = None
    hinh_thuc_thi: list | None = None
    ghi_chu_hinh_thuc_thi: str | None = None
    thoi_han_hieu_luc_thang: int | None = None
    trang_thai: str | None = None
    ghi_chu: str | None = None
    tao_luc: datetime | None = None
    cap_nhat_luc: datetime | None = None

    model_config = {"from_attributes": True}

    @field_validator("thang_diem_min", "thang_diem_max", mode="before")
    @classmethod
    def decimal_to_float(cls, value: Decimal | float | None) -> float | None:
        if value is None:
            return None
        return float(value)


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
