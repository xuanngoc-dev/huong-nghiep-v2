from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

YeuCauGioiTinh = Literal["nam", "nu", "ca_hai"]
LoaiChiPhiXkld = Literal["phi_dich_vu_xuat_canh", "dao_tao_tieng_tay_nghe", "kham_suc_khoe_ho_so", "ky_quy_chong_tron"]
LoaiKenhXkld = Literal["co_quan_nha_nuoc", "doanh_nghiep_cap_phep", "trung_tam_lao_dong_ngoai_nuoc", "ho_tro_he_thong"]


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


class DmThptXkldDeleteMany(_DanhSachId):
    pass


class _LienKet(BaseModel):
    """Khóa liên kết chung của các bảng con: nhóm nghề bắt buộc, thị trường NULL = áp dụng chung cho nhóm nghề."""

    thpt_xkld_nhom_nghe_id: int = Field(..., ge=1)
    thpt_xkld_thi_truong_id: int | None = Field(default=None, ge=1)


class _LienKetPublic(BaseModel):
    thpt_xkld_nhom_nghe_id: int
    ma_nhom: str | None = None
    ten_nhom: str | None = None
    thpt_xkld_thi_truong_id: int | None = None
    ma_quoc_gia: str | None = None
    ten_quoc_gia: str | None = None


# ---------- Nhóm nghề ----------


class DmThptXkldNhomNgheWrite(BaseModel):
    ma_nhom: str = Field(..., min_length=1, max_length=50)
    ten_nhom: str = Field(..., min_length=1, max_length=255)
    mo_ta_cong_viec: str = Field(..., min_length=1, max_length=5000)
    dieu_kien_suc_khoe_the_luc: str | None = Field(default=None, max_length=5000)
    yeu_cau_ngoai_ngu: str | None = Field(default=None, max_length=255)
    thoi_gian_chuan_bi_text: str | None = Field(default=None, max_length=100)
    thoi_gian_chuan_bi_thang_min: int | None = Field(default=0, ge=0, le=120)
    thoi_gian_chuan_bi_thang_max: int | None = Field(default=0, ge=0, le=120)
    muc_thu_nhap_text: str | None = Field(default=None, max_length=255)
    # Triệu VNĐ/tháng — cột DECIMAL(5,2).
    thu_nhap_thang_min: Decimal | None = Field(default=None, ge=0, le=999.99, decimal_places=2)
    thu_nhap_thang_max: Decimal | None = Field(default=None, ge=0, le=999.99, decimal_places=2)
    trien_vong_sau_ve_nuoc: str | None = Field(default=None, max_length=5000)
    kha_nang_gia_han_visa: str | None = Field(default=None, max_length=255)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ma_nhom")
    @classmethod
    def normalize_ma_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Mã nhóm nghề").upper()

    @field_validator("ten_nhom")
    @classmethod
    def strip_ten_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Tên nhóm nghề")

    @field_validator("mo_ta_cong_viec")
    @classmethod
    def strip_mo_ta(cls, value: str) -> str:
        return _bat_buoc(value, "Mô tả công việc")

    @field_validator(
        "dieu_kien_suc_khoe_the_luc", "yeu_cau_ngoai_ngu", "thoi_gian_chuan_bi_text", "muc_thu_nhap_text",
        "trien_vong_sau_ve_nuoc", "kha_nang_gia_han_visa",
    )
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang(self) -> "DmThptXkldNhomNgheWrite":
        tg_min, tg_max = self.thoi_gian_chuan_bi_thang_min, self.thoi_gian_chuan_bi_thang_max
        if tg_min is not None and tg_max is not None and tg_min > tg_max:
            raise ValueError("Thời gian chuẩn bị tối thiểu không được lớn hơn tối đa")
        tn_min, tn_max = self.thu_nhap_thang_min, self.thu_nhap_thang_max
        if tn_min is not None and tn_max is not None and tn_min > tn_max:
            raise ValueError("Thu nhập tối thiểu không được lớn hơn tối đa")
        return self


class DmThptXkldNhomNghePublic(BaseModel):
    id: int
    ma_nhom: str
    ten_nhom: str
    mo_ta_cong_viec: str
    dieu_kien_suc_khoe_the_luc: str | None = None
    yeu_cau_ngoai_ngu: str | None = None
    thoi_gian_chuan_bi_text: str | None = None
    thoi_gian_chuan_bi_thang_min: int | None = None
    thoi_gian_chuan_bi_thang_max: int | None = None
    muc_thu_nhap_text: str | None = None
    thu_nhap_thang_min: Decimal | None = None
    thu_nhap_thang_max: Decimal | None = None
    trien_vong_sau_ve_nuoc: str | None = None
    kha_nang_gia_han_visa: str | None = None
    trang_thai: int
    ngay_tao: datetime | None = None
    ngay_cap_nhat: datetime | None = None

    model_config = {"from_attributes": True}


class DmThptXkldNhomNghePage(BaseModel):
    items: list[DmThptXkldNhomNghePublic]
    total: int
    page: int
    page_size: int


class DmThptXkldNhomNgheTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class DmThptXkldNhomNgheTrangThaiMany(_DanhSachId):
    """Đổi trạng thái nhiều nhóm nghề theo danh sách id."""

    trang_thai: int = Field(..., ge=0, le=1)


# ---------- Thị trường ----------


class DmThptXkldThiTruongWrite(BaseModel):
    thpt_xkld_nhom_nghe_id: int = Field(..., ge=1)
    ma_quoc_gia: str = Field(..., min_length=1, max_length=20)
    ten_quoc_gia: str = Field(..., min_length=1, max_length=100)
    loai_visa: str | None = Field(default=None, max_length=100)
    dac_diem_thi_truong: str | None = Field(default=None, max_length=5000)
    thu_nhap_rieng_text: str | None = Field(default=None, max_length=255)
    thoi_han_hop_dong_nam: int | None = Field(default=3, ge=0, le=50)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("ma_quoc_gia")
    @classmethod
    def normalize_ma_quoc_gia(cls, value: str) -> str:
        return _bat_buoc(value, "Mã quốc gia").upper()

    @field_validator("ten_quoc_gia")
    @classmethod
    def strip_ten_quoc_gia(cls, value: str) -> str:
        return _bat_buoc(value, "Tên quốc gia")

    @field_validator("loai_visa", "dac_diem_thi_truong", "thu_nhap_rieng_text")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptXkldThiTruongPublic(BaseModel):
    id: int
    thpt_xkld_nhom_nghe_id: int
    ma_nhom: str | None = None
    ten_nhom: str | None = None
    ma_quoc_gia: str
    ten_quoc_gia: str
    loai_visa: str | None = None
    dac_diem_thi_truong: str | None = None
    thu_nhap_rieng_text: str | None = None
    thoi_han_hop_dong_nam: int | None = None
    thu_tu_hien_thi: int


class DmThptXkldThiTruongPage(BaseModel):
    items: list[DmThptXkldThiTruongPublic]
    total: int
    page: int
    page_size: int


# ---------- Nghề cụ thể ----------


class DmThptXkldNgheCuTheWrite(_LienKet):
    ten_cong_viec: str = Field(..., min_length=1, max_length=255)
    mo_ta_ngan: str | None = Field(default=None, max_length=5000)
    yeu_cau_gioi_tinh: YeuCauGioiTinh = "ca_hai"

    @field_validator("ten_cong_viec")
    @classmethod
    def strip_ten_cong_viec(cls, value: str) -> str:
        return _bat_buoc(value, "Tên công việc")

    @field_validator("mo_ta_ngan")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptXkldNgheCuThePublic(_LienKetPublic):
    id: int
    ten_cong_viec: str
    mo_ta_ngan: str | None = None
    yeu_cau_gioi_tinh: str | None = None


class DmThptXkldNgheCuThePage(BaseModel):
    items: list[DmThptXkldNgheCuThePublic]
    total: int
    page: int
    page_size: int

# ---------- Chi phí ----------


class DmThptXkldChiPhiWrite(_LienKet):
    loai_chi_phi: LoaiChiPhiXkld
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
    def kiem_tra_khoang(self) -> "DmThptXkldChiPhiWrite":
        if self.chi_phi_min is not None and self.chi_phi_max is not None and self.chi_phi_min > self.chi_phi_max:
            raise ValueError("Chi phí tối thiểu không được lớn hơn tối đa")
        return self


class DmThptXkldChiPhiPublic(_LienKetPublic):
    id: int
    loai_chi_phi: str
    ten_khoan_chi: str
    chi_phi_min: Decimal | None = None
    chi_phi_max: Decimal | None = None
    don_vi_tien: str
    chi_phi_quy_doi_vnd_text: str | None = None
    ghi_chu: str | None = None


class DmThptXkldChiPhiPage(BaseModel):
    items: list[DmThptXkldChiPhiPublic]
    total: int
    page: int
    page_size: int


# ---------- Thủ tục ----------


class DmThptXkldThuTucWrite(_LienKet):
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


class DmThptXkldThuTucPublic(_LienKetPublic):
    id: int
    buoc_so: int
    ten_buoc: str
    mo_ta_thu_tuc: str
    giay_to_can_co: str | None = None
    thoi_gian_du_kien: str | None = None


class DmThptXkldThuTucPage(BaseModel):
    items: list[DmThptXkldThuTucPublic]
    total: int
    page: int
    page_size: int


# ---------- Kênh kết nối ----------


class DmThptXkldKenhKetNoiWrite(_LienKet):
    loai_kenh: LoaiKenhXkld
    ten_kenh: str = Field(..., min_length=1, max_length=255)
    thong_tin_lien_he: str | None = Field(default=None, max_length=255)
    mo_ta_ho_tro: str | None = Field(default=None, max_length=5000)
    luu_y_tranh_rui_ro: str | None = Field(default=None, max_length=255)
    thu_tu_hien_thi: int = Field(default=0, ge=0, le=100000)

    @field_validator("ten_kenh")
    @classmethod
    def strip_ten_kenh(cls, value: str) -> str:
        return _bat_buoc(value, "Tên kênh")

    @field_validator("thong_tin_lien_he", "mo_ta_ho_tro", "luu_y_tranh_rui_ro")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmThptXkldKenhKetNoiPublic(_LienKetPublic):
    id: int
    loai_kenh: str
    ten_kenh: str
    thong_tin_lien_he: str | None = None
    mo_ta_ho_tro: str | None = None
    luu_y_tranh_rui_ro: str | None = None
    thu_tu_hien_thi: int


class DmThptXkldKenhKetNoiPage(BaseModel):
    items: list[DmThptXkldKenhKetNoiPublic]
    total: int
    page: int
    page_size: int
