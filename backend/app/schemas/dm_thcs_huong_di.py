from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

MucDoApLucHocTap = Literal["thap", "trung_binh", "cao"]
MucDoTuGiac = Literal["trung_binh", "cao", "rat_cao"]
LoaiUuNhuocDiem = Literal["uu_diem", "nhuoc_diem"]
DoiTuongNhanLuuY = Literal["hoc_sinh", "phu_huynh", "ca_hai"]


def _bat_buoc(value: str, nhan: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{nhan} không được để trống")
    return cleaned


def _rong_thanh_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class _DanhSachId(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)

    @field_validator("ids")
    @classmethod
    def unique_ids(cls, value: list[int]) -> list[int]:
        if any(item_id < 1 for item_id in value):
            raise ValueError("ID không hợp lệ")
        return list(dict.fromkeys(value))


class KetQuaThemNhieu(BaseModel):
    created: int


class KetQuaXoaNhieu(BaseModel):
    deleted: int


class KetQuaDoiTrangThaiNhieu(BaseModel):
    updated: int


class DmThcsDeleteMany(_DanhSachId):
    pass


class _HuongDiPublic(BaseModel):
    """Mã/tên hướng đi cha ghép vào bản ghi con."""

    thcs_huong_di_id: int
    ma_huong: str | None = None
    ten_huong: str | None = None


# ---------- Hướng đi ----------


class DmThcsHuongDiWrite(BaseModel):
    ma_huong: str = Field(..., min_length=1, max_length=50)
    ten_huong: str = Field(..., min_length=1, max_length=255)
    mo_ta_tong_quan: str = Field(..., min_length=1, max_length=5000)
    doi_tuong_phu_hop: str | None = Field(default=None, max_length=5000)
    chi_phi_du_kien_text: str | None = Field(default=None, max_length=255)
    # DECIMAL(10,2) — đơn vị do người nhập quy ước (thường là nghìn hoặc triệu VNĐ/tháng).
    chi_phi_thang_min: Decimal | None = Field(default=None, ge=0, le=99999999.99, decimal_places=2)
    chi_phi_thang_max: Decimal | None = Field(default=None, ge=0, le=99999999.99, decimal_places=2)
    muc_do_ap_luc_hoc_tap: MucDoApLucHocTap = "trung_binh"
    muc_do_tu_giac_can_thiet: MucDoTuGiac = "cao"
    tinh_linh_hoat_sau_lop_12: str | None = Field(default=None, max_length=5000)
    ma_holland: str | None = Field(default=None, max_length=20)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ma_huong")
    @classmethod
    def normalize_ma_huong(cls, value: str) -> str:
        return _bat_buoc(value, "Mã hướng đi").upper()

    @field_validator("ten_huong")
    @classmethod
    def strip_ten_huong(cls, value: str) -> str:
        return _bat_buoc(value, "Tên hướng đi")

    @field_validator("mo_ta_tong_quan")
    @classmethod
    def strip_mo_ta(cls, value: str) -> str:
        return _bat_buoc(value, "Mô tả tổng quan")

    @field_validator("ma_holland")
    @classmethod
    def normalize_ma_holland(cls, value: str | None) -> str | None:
        cleaned = _rong_thanh_none(value)
        return cleaned.upper() if cleaned else None

    @field_validator("doi_tuong_phu_hop", "chi_phi_du_kien_text", "tinh_linh_hoat_sau_lop_12")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang(self) -> "DmThcsHuongDiWrite":
        cp_min, cp_max = self.chi_phi_thang_min, self.chi_phi_thang_max
        if cp_min is not None and cp_max is not None and cp_min > cp_max:
            raise ValueError("Chi phí tối thiểu không được lớn hơn tối đa")
        return self


class DmThcsHuongDiPublic(BaseModel):
    id: int
    ma_huong: str
    ten_huong: str
    mo_ta_tong_quan: str
    doi_tuong_phu_hop: str | None = None
    chi_phi_du_kien_text: str | None = None
    chi_phi_thang_min: Decimal | None = None
    chi_phi_thang_max: Decimal | None = None
    muc_do_ap_luc_hoc_tap: str | None = None
    muc_do_tu_giac_can_thiet: str | None = None
    tinh_linh_hoat_sau_lop_12: str | None = None
    ma_holland: str | None = None
    thu_tu_hien_thi: int
    trang_thai: int
    ngay_tao: datetime | None = None
    ngay_cap_nhat: datetime | None = None

    model_config = {"from_attributes": True}


class DmThcsHuongDiPage(BaseModel):
    items: list[DmThcsHuongDiPublic]
    total: int
    page: int
    page_size: int


class DmThcsHuongDiTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class DmThcsHuongDiTrangThaiMany(_DanhSachId):
    """Đổi trạng thái nhiều hướng đi theo danh sách id."""

    trang_thai: int = Field(..., ge=0, le=1)


# ---------- Ưu / nhược điểm ----------


class DmThcsUuNhuocDiemWrite(BaseModel):
    thcs_huong_di_id: int = Field(..., ge=1)
    loai: LoaiUuNhuocDiem
    tieu_de: str = Field(..., min_length=1, max_length=255)
    noi_dung_chi_tiet: str = Field(..., min_length=1, max_length=5000)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("tieu_de")
    @classmethod
    def strip_tieu_de(cls, value: str) -> str:
        return _bat_buoc(value, "Tiêu đề")

    @field_validator("noi_dung_chi_tiet")
    @classmethod
    def strip_noi_dung(cls, value: str) -> str:
        return _bat_buoc(value, "Nội dung chi tiết")


class DmThcsUuNhuocDiemPublic(_HuongDiPublic):
    id: int
    loai: str
    tieu_de: str
    noi_dung_chi_tiet: str
    thu_tu_hien_thi: int


class DmThcsUuNhuocDiemPage(BaseModel):
    items: list[DmThcsUuNhuocDiemPublic]
    total: int
    page: int
    page_size: int


# ---------- Tiêu chí ----------


class DmThcsTieuChiWrite(BaseModel):
    ma_tieu_chi: str = Field(..., min_length=1, max_length=50)
    ten_tieu_chi: str = Field(..., min_length=1, max_length=255)
    mo_ta_tieu_chi: str | None = Field(default=None, max_length=255)
    nhom_tieu_chi: str | None = Field(default=None, max_length=100)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("ma_tieu_chi")
    @classmethod
    def normalize_ma_tieu_chi(cls, value: str) -> str:
        return _bat_buoc(value, "Mã tiêu chí").upper()

    @field_validator("ten_tieu_chi")
    @classmethod
    def strip_ten_tieu_chi(cls, value: str) -> str:
        return _bat_buoc(value, "Tên tiêu chí")

    @field_validator("mo_ta_tieu_chi", "nhom_tieu_chi")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThcsTieuChiPublic(BaseModel):
    id: int
    ma_tieu_chi: str
    ten_tieu_chi: str
    mo_ta_tieu_chi: str | None = None
    nhom_tieu_chi: str | None = None
    thu_tu_hien_thi: int

    model_config = {"from_attributes": True}


class DmThcsTieuChiPage(BaseModel):
    items: list[DmThcsTieuChiPublic]
    total: int
    page: int
    page_size: int


# ---------- Hướng đi - tiêu chí ----------


class DmThcsHuongDiTieuChiKhoa(BaseModel):
    thcs_huong_di_id: int = Field(..., ge=1)
    thcs_tieu_chi_id: int = Field(..., ge=1)


class DmThcsHuongDiTieuChiUpdate(BaseModel):
    diem_phu_hop: int = Field(default=3, ge=1, le=5)
    nhan_dinh_tu_van: str | None = Field(default=None, max_length=255)

    @field_validator("nhan_dinh_tu_van")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThcsHuongDiTieuChiWrite(DmThcsHuongDiTieuChiKhoa, DmThcsHuongDiTieuChiUpdate):
    pass


class DmThcsHuongDiTieuChiPublic(_HuongDiPublic):
    thcs_tieu_chi_id: int
    ma_tieu_chi: str | None = None
    ten_tieu_chi: str | None = None
    nhom_tieu_chi: str | None = None
    diem_phu_hop: int
    nhan_dinh_tu_van: str | None = None


class DmThcsHuongDiTieuChiPage(BaseModel):
    items: list[DmThcsHuongDiTieuChiPublic]
    total: int
    page: int
    page_size: int


class DmThcsHuongDiTieuChiDeleteMany(BaseModel):
    items: list[DmThcsHuongDiTieuChiKhoa] = Field(..., min_length=1, max_length=500)


# ---------- Lời khuyên, lưu ý ----------


class DmThcsLoiKhuyenLuuYWrite(BaseModel):
    thcs_huong_di_id: int = Field(..., ge=1)
    doi_tuong_nhan: DoiTuongNhanLuuY = "ca_hai"
    noi_dung_luu_y: str = Field(..., min_length=1, max_length=5000)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("noi_dung_luu_y")
    @classmethod
    def strip_noi_dung(cls, value: str) -> str:
        return _bat_buoc(value, "Nội dung lưu ý")


class DmThcsLoiKhuyenLuuYPublic(_HuongDiPublic):
    id: int
    doi_tuong_nhan: str | None = None
    noi_dung_luu_y: str
    thu_tu_hien_thi: int


class DmThcsLoiKhuyenLuuYPage(BaseModel):
    items: list[DmThcsLoiKhuyenLuuYPublic]
    total: int
    page: int
    page_size: int
