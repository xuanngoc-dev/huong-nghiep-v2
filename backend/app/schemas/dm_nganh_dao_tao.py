from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants.don_vi_tien import DON_VI_TIEN
from app.constants.ky_luong import KY_LUONG, KY_LUONG_MAC_DINH, KY_LUONG_NHAN


def _so_luong(value: float) -> float:
    try:
        amount = Decimal(str(value))
    except Exception as exc:
        raise ValueError("Mức lương phải là số") from exc
    if amount < 0 or amount > Decimal("99.9") or amount != amount.quantize(Decimal("0.1")):
        raise ValueError("Mức lương chỉ gồm tối đa 2 chữ số và 1 chữ số thập phân")
    return float(amount.quantize(Decimal("0.1")))


def _ma_ky_luong(value: str) -> str:
    raw = value.strip().lower()
    if raw in KY_LUONG:
        return raw
    for code, label in KY_LUONG_NHAN.items():
        if raw == label:
            return code
    raise ValueError("Đơn vị thời gian lương không hợp lệ")


class MucLuongThamKhao(BaseModel):
    """Một mốc lương: kinh nghiệm, khoảng từ–đến, đơn vị tiền và kỳ lương."""

    name: str = Field(..., min_length=1, max_length=255)
    min: float = Field(..., ge=0, le=99.9)
    max: float = Field(..., ge=0, le=99.9)
    unit: str = Field(..., min_length=1, max_length=10)
    period: str = Field(default=KY_LUONG_MAC_DINH, max_length=20)

    @field_validator("name", "unit")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Không được để trống")
        return cleaned

    @field_validator("min", "max")
    @classmethod
    def mot_chu_so_thap_phan(cls, value: float) -> float:
        return _so_luong(value)

    @field_validator("unit")
    @classmethod
    def don_vi_hop_le(cls, value: str) -> str:
        code = value.strip().upper()
        if code not in DON_VI_TIEN:
            raise ValueError("Đơn vị tính không hợp lệ")
        return code

    @field_validator("period")
    @classmethod
    def ky_luong_hop_le(cls, value: str) -> str:
        if not value or not value.strip():
            return KY_LUONG_MAC_DINH
        return _ma_ky_luong(value)

    @model_validator(mode="after")
    def tu_khong_lon_hon_den(self):
        if self.min > self.max:
            raise ValueError("Mức từ không được lớn hơn mức đến")
        return self


class MucLuongThamKhaoPublic(BaseModel):
    """Đọc được cả dòng mới {name, min, max, unit, period} và dòng cũ {name, value}."""

    name: str = ""
    min: float | None = None
    max: float | None = None
    unit: str | None = None
    period: str | None = None
    value: str | None = None


class MucTenGiaTri(BaseModel):
    """Một dòng tên–giá trị, có thể kèm ghi chú."""

    name: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1, max_length=2000)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("name", "value")
    @classmethod
    def strip_required(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


def _normalize_ma_holand(value: list[str] | None) -> list[str] | None:
    if not value:
        return None
    cleaned: list[str] = []
    seen: set[str] = set()
    for code in value:
        item = str(code).strip().upper()
        if not item:
            raise ValueError("Mã Holland không được để trống")
        if len(item) > 20:
            raise ValueError("Mã Holland tối đa 20 ký tự")
        if item in seen:
            continue
        seen.add(item)
        cleaned.append(item)
    if len(cleaned) > 10:
        raise ValueError("Chỉ chọn tối đa 10 mã Holland")
    return cleaned or None


class DmNganhDaoTaoWrite(BaseModel):
    ma_nhom_nganh: str = Field(..., min_length=1, max_length=20)
    ma_nganh: str = Field(..., min_length=1, max_length=20)
    ten_nganh: str = Field(..., min_length=1, max_length=255)
    ten_tieng_anh: str = Field(..., min_length=1, max_length=255)
    trinh_do: str = Field(..., min_length=1, max_length=100)
    ma_holand: list[str] | None = None
    mo_ta: str | None = Field(default=None, max_length=5000)
    hinh_anh_mo_ta: str | None = Field(default=None, max_length=500)
    muc_luong_tham_khao: list[MucLuongThamKhao] | None = None
    mo_ta_cong_viec: list[MucTenGiaTri] | None = None
    lo_trinh_phat_trien: list[MucTenGiaTri] | None = None
    nhan_dan: str | None = Field(default=None, max_length=100)
    thoi_gian_dao_tao: str | None = Field(default=None, max_length=100)
    chi_tiet: str | None = Field(default=None, max_length=10000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_nganh")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên ngành không được để trống")
        return cleaned

    @field_validator("ten_tieng_anh")
    @classmethod
    def strip_ten_tieng_anh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên tiếng Anh không được để trống")
        return cleaned

    @field_validator("ma_nhom_nganh")
    @classmethod
    def normalize_ma_nhom_nganh(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã nhóm ngành không được để trống")
        return cleaned

    @field_validator("ma_nganh")
    @classmethod
    def normalize_ma(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã ngành không được để trống")
        return cleaned

    @field_validator("trinh_do")
    @classmethod
    def strip_trinh_do(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Trình độ không được để trống")
        return cleaned

    @field_validator("ma_holand")
    @classmethod
    def normalize_ma_holand(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_ma_holand(value)

    @field_validator("muc_luong_tham_khao")
    @classmethod
    def normalize_luong(cls, value: list[MucLuongThamKhao] | None) -> list[MucLuongThamKhao] | None:
        if not value:
            return None
        if len(value) > 50:
            raise ValueError("Chỉ nhập tối đa 50 dòng")
        return value

    @field_validator("mo_ta_cong_viec", "lo_trinh_phat_trien")
    @classmethod
    def normalize_cap(cls, value: list[MucTenGiaTri] | None) -> list[MucTenGiaTri] | None:
        if not value:
            return None
        if len(value) > 50:
            raise ValueError("Chỉ nhập tối đa 50 dòng")
        return value

    @field_validator(
        "mo_ta",
        "hinh_anh_mo_ta",
        "nhan_dan",
        "thoi_gian_dao_tao",
        "chi_tiet",
    )
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmNganhDaoTaoPublic(BaseModel):
    id: int
    ma_nhom_nganh: str
    ten_nhom_nganh: str
    ma_nganh: str
    ten_nganh: str
    ten_tieng_anh: str
    trinh_do: str
    ma_holand: list[str] | None = None
    mo_ta: str | None = None
    hinh_anh_mo_ta: str | None = None
    muc_luong_tham_khao: list[MucLuongThamKhaoPublic] | None = None
    mo_ta_cong_viec: list[MucTenGiaTri] | None = None
    lo_trinh_phat_trien: list[MucTenGiaTri] | None = None
    nhan_dan: str | None = None
    thoi_gian_dao_tao: str | None = None
    chi_tiet: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DmNganhDaoTaoPage(BaseModel):
    items: list[DmNganhDaoTaoPublic]
    total: int
    page: int
    page_size: int


class DmNganhDaoTaoBulkResult(BaseModel):
    created: int


class DmNganhDaoTaoDeleteMany(BaseModel):
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


class DmNganhDaoTaoDeleteManyResult(BaseModel):
    deleted: int
