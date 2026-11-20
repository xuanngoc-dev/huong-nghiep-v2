from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

LoaiHinhDuHoc = Literal["du_hoc_nghe", "du_hoc_hoc_thuat", "chuyen_tiep"]
LoaiChiPhi = Literal["truoc_khi_bay", "tai_nuoc_so_tai", "chung_minh_tai_chinh", "khoan_bu_dap"]
LoaiKenh = Literal["chinh_thong", "trung_tam_tu_van", "cong_dong", "ho_tro_he_thong"]


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


class DmThptDuhocDeleteMany(_DanhSachId):
    pass


class _LienKet(BaseModel):
    """Khóa liên kết chung của các bảng con: hướng đi bắt buộc, quốc gia NULL = áp dụng chung cho hướng đi."""

    thpt_duhoc_huong_di_id: int = Field(..., ge=1)
    thpt_duhoc_quoc_gia_id: int | None = Field(default=None, ge=1)


class _LienKetPublic(BaseModel):
    thpt_duhoc_huong_di_id: int
    ma_huong: str | None = None
    ten_huong: str | None = None
    thpt_duhoc_quoc_gia_id: int | None = None
    ma_quoc_gia: str | None = None
    ten_quoc_gia: str | None = None


# ---------- Hướng đi ----------


class DmThptDuhocHuongDiWrite(BaseModel):
    ma_huong: str = Field(..., min_length=1, max_length=50)
    ten_huong: str = Field(..., min_length=1, max_length=255)
    loai_hinh: LoaiHinhDuHoc
    mo_ta_dac_diem: str = Field(..., min_length=1, max_length=5000)
    yeu_cau_ngoai_ngu: str | None = Field(default=None, max_length=255)
    thoi_gian_chuan_bi_text: str | None = Field(default=None, max_length=100)
    thoi_gian_chuan_bi_thang_min: int | None = Field(default=0, ge=0, le=120)
    thoi_gian_chuan_bi_thang_max: int | None = Field(default=0, ge=0, le=120)
    chi_phi_du_kien_text: str | None = Field(default=None, max_length=255)
    co_hoi_lam_them: str | None = Field(default=None, max_length=5000)
    lo_trinh_visa_dinh_cu: str | None = Field(default=None, max_length=5000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ma_huong")
    @classmethod
    def normalize_ma_huong(cls, value: str) -> str:
        return _bat_buoc(value, "Mã hướng đi").upper()

    @field_validator("ten_huong")
    @classmethod
    def strip_ten_huong(cls, value: str) -> str:
        return _bat_buoc(value, "Tên hướng đi")

    @field_validator("mo_ta_dac_diem")
    @classmethod
    def strip_mo_ta(cls, value: str) -> str:
        return _bat_buoc(value, "Mô tả đặc điểm")

    @field_validator(
        "yeu_cau_ngoai_ngu", "thoi_gian_chuan_bi_text", "chi_phi_du_kien_text", "co_hoi_lam_them",
        "lo_trinh_visa_dinh_cu",
    )
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang(self) -> "DmThptDuhocHuongDiWrite":
        tg_min, tg_max = self.thoi_gian_chuan_bi_thang_min, self.thoi_gian_chuan_bi_thang_max
        if tg_min is not None and tg_max is not None and tg_min > tg_max:
            raise ValueError("Thời gian chuẩn bị tối thiểu không được lớn hơn tối đa")
        return self


class DmThptDuhocHuongDiPublic(BaseModel):
    id: int
    ma_huong: str
    ten_huong: str
    loai_hinh: str
    mo_ta_dac_diem: str
    yeu_cau_ngoai_ngu: str | None = None
    thoi_gian_chuan_bi_text: str | None = None
    thoi_gian_chuan_bi_thang_min: int | None = None
    thoi_gian_chuan_bi_thang_max: int | None = None
    chi_phi_du_kien_text: str | None = None
    co_hoi_lam_them: str | None = None
    lo_trinh_visa_dinh_cu: str | None = None
    trang_thai: int
    ngay_tao: datetime | None = None
    ngay_cap_nhat: datetime | None = None

    model_config = {"from_attributes": True}


class DmThptDuhocHuongDiPage(BaseModel):
    items: list[DmThptDuhocHuongDiPublic]
    total: int
    page: int
    page_size: int


class DmThptDuhocHuongDiTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class DmThptDuhocHuongDiTrangThaiMany(_DanhSachId):
    """Đổi trạng thái nhiều hướng đi theo danh sách id."""

    trang_thai: int = Field(..., ge=0, le=1)


# ---------- Quốc gia ----------


class DmThptDuhocQuocGiaWrite(BaseModel):
    thpt_duhoc_huong_di_id: int = Field(..., ge=1)
    ma_quoc_gia: str = Field(..., min_length=1, max_length=20)
    ten_quoc_gia: str = Field(..., min_length=1, max_length=100)
    dac_diem_noi_bat: str | None = Field(default=None, max_length=5000)
    yeu_cau_ngoai_ngu_rieng: str | None = Field(default=None, max_length=255)
    co_hoi_viec_lam_visa: str | None = Field(default=None, max_length=5000)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("ma_quoc_gia")
    @classmethod
    def normalize_ma_quoc_gia(cls, value: str) -> str:
        return _bat_buoc(value, "Mã quốc gia").upper()

    @field_validator("ten_quoc_gia")
    @classmethod
    def strip_ten_quoc_gia(cls, value: str) -> str:
        return _bat_buoc(value, "Tên quốc gia")

    @field_validator("dac_diem_noi_bat", "yeu_cau_ngoai_ngu_rieng", "co_hoi_viec_lam_visa")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptDuhocQuocGiaPublic(BaseModel):
    id: int
    thpt_duhoc_huong_di_id: int
    ma_huong: str | None = None
    ten_huong: str | None = None
    ma_quoc_gia: str
    ten_quoc_gia: str
    dac_diem_noi_bat: str | None = None
    yeu_cau_ngoai_ngu_rieng: str | None = None
    co_hoi_viec_lam_visa: str | None = None
    thu_tu_hien_thi: int


class DmThptDuhocQuocGiaPage(BaseModel):
    items: list[DmThptDuhocQuocGiaPublic]
    total: int
    page: int
    page_size: int


# ---------- Ngành ----------


class DmThptDuhocNganhWrite(_LienKet):
    ten_nganh: str = Field(..., min_length=1, max_length=255)
    nhu_cau_nhan_luc: str | None = Field(default=None, max_length=255)
    muc_luong_tham_khao: str | None = Field(default=None, max_length=255)
    ghi_chu: str | None = Field(default=None, max_length=5000)

    @field_validator("ten_nganh")
    @classmethod
    def strip_ten_nganh(cls, value: str) -> str:
        return _bat_buoc(value, "Tên ngành")

    @field_validator("nhu_cau_nhan_luc", "muc_luong_tham_khao", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptDuhocNganhPublic(_LienKetPublic):
    id: int
    ten_nganh: str
    nhu_cau_nhan_luc: str | None = None
    muc_luong_tham_khao: str | None = None
    ghi_chu: str | None = None


class DmThptDuhocNganhPage(BaseModel):
    items: list[DmThptDuhocNganhPublic]
    total: int
    page: int
    page_size: int


# ---------- Chi phí ----------


class DmThptDuhocChiPhiWrite(_LienKet):
    loai_chi_phi: LoaiChiPhi
    ten_khoan_chi: str = Field(..., min_length=1, max_length=255)
    chi_phi_min: Decimal | None = Field(default=None, ge=0, le=9999999999.99, decimal_places=2)
    chi_phi_max: Decimal | None = Field(default=None, ge=0, le=9999999999.99, decimal_places=2)
    don_vi_tien: str = Field(default="VND", min_length=1, max_length=20)
    chi_phi_quy_doi_vnd_text: str | None = Field(default=None, max_length=255)
    ghi_chu: str | None = Field(default=None, max_length=255)

    @field_validator("ten_khoan_chi")
    @classmethod
    def strip_ten_khoan_chi(cls, value: str) -> str:
        return _bat_buoc(value, "Tên khoản chi")

    @field_validator("don_vi_tien")
    @classmethod
    def normalize_don_vi_tien(cls, value: str) -> str:
        return _bat_buoc(value, "Đơn vị tiền").upper()

    @field_validator("chi_phi_quy_doi_vnd_text", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang(self) -> "DmThptDuhocChiPhiWrite":
        if self.chi_phi_min is not None and self.chi_phi_max is not None and self.chi_phi_min > self.chi_phi_max:
            raise ValueError("Chi phí tối thiểu không được lớn hơn tối đa")
        return self


class DmThptDuhocChiPhiPublic(_LienKetPublic):
    id: int
    loai_chi_phi: str
    ten_khoan_chi: str
    chi_phi_min: Decimal | None = None
    chi_phi_max: Decimal | None = None
    don_vi_tien: str
    chi_phi_quy_doi_vnd_text: str | None = None
    ghi_chu: str | None = None


class DmThptDuhocChiPhiPage(BaseModel):
    items: list[DmThptDuhocChiPhiPublic]
    total: int
    page: int
    page_size: int


# ---------- Thủ tục ----------


class DmThptDuhocThuTucWrite(_LienKet):
    buoc_so: int = Field(..., ge=1, le=100)
    ten_buoc: str = Field(..., min_length=1, max_length=255)
    mo_ta_thu_tuc: str = Field(..., min_length=1, max_length=5000)
    giay_to_can_co: str | None = Field(default=None, max_length=5000)
    thoi_gian_du_kien: str | None = Field(default=None, max_length=100)

    @field_validator("ten_buoc")
    @classmethod
    def strip_ten_buoc(cls, value: str) -> str:
        return _bat_buoc(value, "Tên bước")

    @field_validator("mo_ta_thu_tuc")
    @classmethod
    def strip_mo_ta(cls, value: str) -> str:
        return _bat_buoc(value, "Mô tả thủ tục")

    @field_validator("giay_to_can_co", "thoi_gian_du_kien")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptDuhocThuTucPublic(_LienKetPublic):
    id: int
    buoc_so: int
    ten_buoc: str
    mo_ta_thu_tuc: str
    giay_to_can_co: str | None = None
    thoi_gian_du_kien: str | None = None


class DmThptDuhocThuTucPage(BaseModel):
    items: list[DmThptDuhocThuTucPublic]
    total: int
    page: int
    page_size: int


# ---------- Kênh kết nối ----------


class DmThptDuhocKenhKetNoiWrite(_LienKet):
    loai_kenh: LoaiKenh
    ten_kenh: str = Field(..., min_length=1, max_length=255)
    thong_tin_lien_he: str | None = Field(default=None, max_length=255)
    mo_ta_ho_tro: str | None = Field(default=None, max_length=5000)
    luu_y_khi_ket_noi: str | None = Field(default=None, max_length=255)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("ten_kenh")
    @classmethod
    def strip_ten_kenh(cls, value: str) -> str:
        return _bat_buoc(value, "Tên kênh")

    @field_validator("thong_tin_lien_he", "mo_ta_ho_tro", "luu_y_khi_ket_noi")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptDuhocKenhKetNoiPublic(_LienKetPublic):
    id: int
    loai_kenh: str
    ten_kenh: str
    thong_tin_lien_he: str | None = None
    mo_ta_ho_tro: str | None = None
    luu_y_khi_ket_noi: str | None = None
    thu_tu_hien_thi: int


class DmThptDuhocKenhKetNoiPage(BaseModel):
    items: list[DmThptDuhocKenhKetNoiPublic]
    total: int
    page: int
    page_size: int
