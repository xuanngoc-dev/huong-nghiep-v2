from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

LoaiHinhDauVao = Literal["di_lam_ngay", "hoc_nghe_ngan_han", "tu_hoc_ky_nang"]
NhomMucTieu = Literal["kiem_tien_ngay", "nghe_vung_chac", "thu_nhap_dot_pha"]


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


class KetQuaThemNhieu(BaseModel):
    created: int


class KetQuaXoaNhieu(BaseModel):
    deleted: int


class KetQuaDoiTrangThaiNhieu(BaseModel):
    updated: int


# ---------- Nhóm nghề đi làm ----------


class DmNhomNgheDiLamWrite(BaseModel):
    ma_nhom: str = Field(..., min_length=1, max_length=50)
    ten_nhom: str = Field(..., min_length=1, max_length=255)
    mo_ta_dac_diem: str = Field(..., min_length=1, max_length=5000)
    loai_hinh_dau_vao: LoaiHinhDauVao | None = None
    thoi_gian_dao_tao_text: str | None = Field(default=None, max_length=100)
    thoi_gian_dao_tao_thang_min: int | None = Field(default=None, ge=0, le=120)
    thoi_gian_dao_tao_thang_max: int | None = Field(default=None, ge=0, le=120)
    dieu_kien_dau_vao: str | None = Field(default=None, max_length=5000)
    muc_luong_text: str | None = Field(default=None, max_length=100)
    luong_khoi_diem_min: Decimal | None = Field(default=None, ge=0, le=999.99, decimal_places=2)
    luong_khoi_diem_max: Decimal | None = Field(default=None, ge=0, le=999.99, decimal_places=2)
    luong_kinh_nghiem_max: Decimal | None = Field(default=None, ge=0, le=999.99, decimal_places=2)
    danh_gia_trien_vong: str | None = Field(default=None, max_length=255)
    lo_trinh_phat_trien: str | None = Field(default=None, max_length=5000)
    nhom_muc_tieu: NhomMucTieu | None = None
    ma_holland: str | None = Field(default=None, max_length=20)
    nganh_nay_la_gi: str | None = Field(default=None, max_length=10000)
    noi_lam_viec_o_dau: str | None = Field(default=None, max_length=10000)
    cong_viec_hang_ngay_nhu_the_nao: str | None = Field(default=None, max_length=10000)
    ap_luc_va_rui_ro: str | None = Field(default=None, max_length=10000)
    xu_huong_tuong_lai: str | None = Field(default=None, max_length=10000)
    ket_luan: str | None = Field(default=None, max_length=10000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ma_nhom")
    @classmethod
    def normalize_ma_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Mã nhóm").upper()

    @field_validator("ten_nhom")
    @classmethod
    def strip_ten_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Tên nhóm")

    @field_validator("mo_ta_dac_diem")
    @classmethod
    def strip_mo_ta(cls, value: str) -> str:
        return _bat_buoc(value, "Mô tả đặc điểm")

    @field_validator("ma_holland")
    @classmethod
    def normalize_ma_holland(cls, value: str | None) -> str | None:
        cleaned = _rong_thanh_none(value)
        return cleaned.upper() if cleaned else None

    @field_validator(
        "thoi_gian_dao_tao_text", "dieu_kien_dau_vao", "muc_luong_text", "danh_gia_trien_vong", "lo_trinh_phat_trien",
        "nganh_nay_la_gi", "noi_lam_viec_o_dau", "cong_viec_hang_ngay_nhu_the_nao", "ap_luc_va_rui_ro",
        "xu_huong_tuong_lai", "ket_luan",
    )
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang(self) -> "DmNhomNgheDiLamWrite":
        tg_min, tg_max = self.thoi_gian_dao_tao_thang_min, self.thoi_gian_dao_tao_thang_max
        if tg_min is not None and tg_max is not None and tg_min > tg_max:
            raise ValueError("Thời gian đào tạo tối thiểu không được lớn hơn tối đa")
        luong_min, luong_max = self.luong_khoi_diem_min, self.luong_khoi_diem_max
        if luong_min is not None and luong_max is not None and luong_min > luong_max:
            raise ValueError("Lương khởi điểm tối thiểu không được lớn hơn tối đa")
        return self


class DmNhomNgheDiLamPublic(BaseModel):
    id: int
    ma_nhom: str
    ten_nhom: str
    mo_ta_dac_diem: str
    loai_hinh_dau_vao: str | None = None
    thoi_gian_dao_tao_text: str | None = None
    thoi_gian_dao_tao_thang_min: int | None = None
    thoi_gian_dao_tao_thang_max: int | None = None
    dieu_kien_dau_vao: str | None = None
    muc_luong_text: str | None = None
    luong_khoi_diem_min: Decimal | None = None
    luong_khoi_diem_max: Decimal | None = None
    luong_kinh_nghiem_max: Decimal | None = None
    danh_gia_trien_vong: str | None = None
    lo_trinh_phat_trien: str | None = None
    nhom_muc_tieu: str | None = None
    ma_holland: str | None = None
    nganh_nay_la_gi: str | None = None
    noi_lam_viec_o_dau: str | None = None
    cong_viec_hang_ngay_nhu_the_nao: str | None = None
    ap_luc_va_rui_ro: str | None = None
    xu_huong_tuong_lai: str | None = None
    ket_luan: str | None = None
    trang_thai: int
    ngay_tao: datetime | None = None
    ngay_cap_nhat: datetime | None = None

    model_config = {"from_attributes": True}


class DmNhomNgheDiLamPage(BaseModel):
    items: list[DmNhomNgheDiLamPublic]
    total: int
    page: int
    page_size: int


class DmNhomNgheDiLamDeleteMany(_DanhSachId):
    pass


class DmNhomNgheDiLamTrangThai(BaseModel):
    trang_thai: int = Field(..., ge=0, le=1)


class DmNhomNgheDiLamTrangThaiMany(_DanhSachId):
    """Đổi trạng thái nhiều nhóm theo danh sách id (cùng cách kiểm tra ids như xóa nhiều)."""

    trang_thai: int = Field(..., ge=0, le=1)


# ---------- Nghề cụ thể ----------


class DmNgheCuTheDiLamWrite(BaseModel):
    nhom_nghe_di_lam_id: int = Field(..., ge=1)
    ten_nghe: str = Field(..., min_length=1, max_length=255)
    mo_ta_ngan: str | None = Field(default=None, max_length=5000)
    yeu_cau_them: str | None = Field(default=None, max_length=500)
    # Bằng cấp / chứng chỉ bắt buộc; bỏ trống nếu không yêu cầu.
    yeu_cau_bang_cap: str | None = Field(default=None, max_length=255)
    # 1: bắt buộc đào tạo chính quy; bỏ trống (null) nếu không. Gửi 0 cũng được lưu thành null.
    bat_buoc_dao_tao_chinh_quy: int | None = Field(default=None, ge=0, le=1)

    @field_validator("ten_nghe")
    @classmethod
    def strip_ten_nghe(cls, value: str) -> str:
        return _bat_buoc(value, "Tên nghề")

    @field_validator("mo_ta_ngan", "yeu_cau_them", "yeu_cau_bang_cap")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @field_validator("bat_buoc_dao_tao_chinh_quy")
    @classmethod
    def khong_bat_buoc_thanh_none(cls, value: int | None) -> int | None:
        return value or None


class DmNgheCuTheDiLamPublic(BaseModel):
    id: int
    nhom_nghe_di_lam_id: int
    ma_nhom: str | None = None
    ten_nhom: str | None = None
    ten_nghe: str
    mo_ta_ngan: str | None = None
    yeu_cau_them: str | None = None
    yeu_cau_bang_cap: str | None = None
    bat_buoc_dao_tao_chinh_quy: int | None = None


class DmNgheCuTheDiLamPage(BaseModel):
    items: list[DmNgheCuTheDiLamPublic]
    total: int
    page: int
    page_size: int


class DmNgheCuTheDiLamDeleteMany(_DanhSachId):
    pass


# ---------- Tiêu chí gợi ý ----------


class DmTieuChiGoiYWrite(BaseModel):
    ma_tieu_chi: str = Field(..., min_length=1, max_length=50)
    ten_tieu_chi: str = Field(..., min_length=1, max_length=255)
    nhom_tieu_chi: str | None = Field(default=None, max_length=100)

    @field_validator("ma_tieu_chi")
    @classmethod
    def normalize_ma_tieu_chi(cls, value: str) -> str:
        return _bat_buoc(value, "Mã tiêu chí").upper()

    @field_validator("ten_tieu_chi")
    @classmethod
    def strip_ten_tieu_chi(cls, value: str) -> str:
        return _bat_buoc(value, "Tên tiêu chí")

    @field_validator("nhom_tieu_chi")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmTieuChiGoiYPublic(BaseModel):
    id: int
    ma_tieu_chi: str
    ten_tieu_chi: str
    nhom_tieu_chi: str | None = None

    model_config = {"from_attributes": True}


class DmTieuChiGoiYPage(BaseModel):
    items: list[DmTieuChiGoiYPublic]
    total: int
    page: int
    page_size: int


class DmTieuChiGoiYDeleteMany(_DanhSachId):
    pass


# ---------- Nhóm nghề - tiêu chí ----------


class DmNhomNgheTieuChiKhoa(BaseModel):
    nhom_nghe_di_lam_id: int = Field(..., ge=1)
    tieu_chi_goi_y_id: int = Field(..., ge=1)


class DmNhomNgheTieuChiUpdate(BaseModel):
    diem_phu_hop: int | None = Field(default=None, ge=1, le=5)
    ghi_chu: str | None = Field(default=None, max_length=500)

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)


class DmNhomNgheTieuChiWrite(DmNhomNgheTieuChiKhoa, DmNhomNgheTieuChiUpdate):
    pass


class DmNhomNgheTieuChiPublic(BaseModel):
    nhom_nghe_di_lam_id: int
    ma_nhom: str | None = None
    ten_nhom: str | None = None
    tieu_chi_goi_y_id: int
    ma_tieu_chi: str | None = None
    ten_tieu_chi: str | None = None
    nhom_tieu_chi: str | None = None
    diem_phu_hop: int | None = None
    ghi_chu: str | None = None


class DmNhomNgheTieuChiPage(BaseModel):
    items: list[DmNhomNgheTieuChiPublic]
    total: int
    page: int
    page_size: int


class DmNhomNgheTieuChiDeleteMany(BaseModel):
    items: list[DmNhomNgheTieuChiKhoa] = Field(..., min_length=1, max_length=500)
