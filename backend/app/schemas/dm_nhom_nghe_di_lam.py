import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

LoaiHinhDauVao = Literal["di_lam_ngay", "hoc_nghe_ngan_han", "tu_hoc_ky_nang"]
NhomMucTieu = Literal["kiem_tien_ngay", "nghe_vung_chac", "thu_nhap_dot_pha"]
ChuKyLuong = Literal["gio", "ngay", "thang", "nam"]
MucDoApLuc = Literal["thap", "trung_binh", "cao"]

# Cột chữ chi tiết của nghề cụ thể: chuỗi rỗng lưu thành null.
COT_CHU_NGHE = (
    "mo_ta_cong_viec", "trach_nhiem_chinh", "vi_tri_tuyen_dung_mau", "hinh_thuc_dao_tao", "trinh_do_toi_thieu",
    "chuyen_nganh_phu_hop", "ky_nang_chuyen_mon", "ky_nang_mem", "chung_chi_giay_phep", "ghi_chu_luong",
    "moi_truong_lam_viec", "dac_thu_thoi_gian", "yeu_cau_suc_khoe", "trien_vong_nghe_nghiep", "tu_khoa_tim_kiem",
)
# Lương mỗi giai đoạn lộ trình: số nguyên VND (lưu trong cột JSON nên không dùng Decimal).
LUONG_BUOC_TOI_DA = 10**13
# Cặp lương (tối thiểu, tối đa, nhãn) của nghề cụ thể.
CAP_LUONG_NGHE = (
    ("luong_khoi_diem_min", "luong_khoi_diem_max", "Lương khởi điểm"),
    ("luong_trung_binh_min", "luong_trung_binh_max", "Lương trung bình"),
    ("luong_cao_min", "luong_cao_max", "Lương mức cao"),
)


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
    hinh_anh_mo_ta: str | None = Field(default=None, max_length=500)
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
        "xu_huong_tuong_lai", "ket_luan", "hinh_anh_mo_ta",
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
    hinh_anh_mo_ta: str | None = None
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


def tach_lo_trinh(value: str) -> list[dict[str, Any]]:
    """Lộ trình dạng chữ cũ "Thợ phụ → Thợ hàn 3G → Tổ trưởng." → các giai đoạn (chỉ có tên)."""
    buoc = [phan.strip().rstrip(".").strip() for phan in re.split(r"→|->|=>", value)]
    return [{"giai_doan": ten} for ten in buoc if ten]


def _lo_trinh_dau_vao(value: Any) -> Any:
    """Nhận cả chuỗi kiểu cũ (file JSON import cũ, dữ liệu chưa chuyển) và danh sách; rỗng → None."""
    if isinstance(value, str):
        value = tach_lo_trinh(value)
    return value or None


class BuocLoTrinhNghe(BaseModel):
    """Một giai đoạn trong lộ trình phát triển của nghề cụ thể."""

    giai_doan: str = Field(..., min_length=1, max_length=255)
    mo_ta_cong_viec: str | None = Field(default=None, max_length=2000)
    # Mức lương trung bình của giai đoạn, VND theo chu_ky_luong của nghề.
    luong_trung_binh_min: int | None = Field(default=None, ge=0, le=LUONG_BUOC_TOI_DA)
    luong_trung_binh_max: int | None = Field(default=None, ge=0, le=LUONG_BUOC_TOI_DA)
    ghi_chu: str | None = Field(default=None, max_length=1000)

    @field_validator("giai_doan")
    @classmethod
    def strip_giai_doan(cls, value: str) -> str:
        return _bat_buoc(value, "Tên giai đoạn lộ trình")

    @field_validator("mo_ta_cong_viec", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def kiem_tra_khoang_luong(self) -> "BuocLoTrinhNghe":
        tu, den = self.luong_trung_binh_min, self.luong_trung_binh_max
        if tu is not None and den is not None and tu > den:
            raise ValueError(f"Lộ trình \"{self.giai_doan}\": lương trung bình từ không được lớn hơn đến")
        return self


class DmNgheCuTheDiLamWrite(BaseModel):
    nhom_nghe_di_lam_id: int = Field(..., ge=1)
    ten_nghe: str = Field(..., min_length=1, max_length=255)
    mo_ta_ngan: str | None = Field(default=None, max_length=5000)
    yeu_cau_them: str | None = Field(default=None, max_length=500)
    # Bằng cấp / chứng chỉ bắt buộc; bỏ trống nếu không yêu cầu.
    yeu_cau_bang_cap: str | None = Field(default=None, max_length=255)
    # 1: bắt buộc đào tạo chính quy; bỏ trống (null) nếu không. Gửi 0 cũng được lưu thành null.
    bat_buoc_dao_tao_chinh_quy: int | None = Field(default=None, ge=0, le=1)
    hinh_anh_mo_ta: str | None = Field(default=None, max_length=500)
    mo_ta_cong_viec: str | None = Field(default=None, max_length=10000)
    trach_nhiem_chinh: str | None = Field(default=None, max_length=10000)
    vi_tri_tuyen_dung_mau: str | None = Field(default=None, max_length=5000)
    hinh_thuc_dao_tao: str | None = Field(default=None, max_length=255)
    trinh_do_toi_thieu: str | None = Field(default=None, max_length=100)
    chuyen_nganh_phu_hop: str | None = Field(default=None, max_length=5000)
    ky_nang_chuyen_mon: str | None = Field(default=None, max_length=5000)
    ky_nang_mem: str | None = Field(default=None, max_length=5000)
    chung_chi_giay_phep: str | None = Field(default=None, max_length=5000)
    luong_khoi_diem_min: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    luong_khoi_diem_max: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    luong_trung_binh_min: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    luong_trung_binh_max: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    luong_cao_min: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    luong_cao_max: Decimal | None = Field(default=None, ge=0, max_digits=15, decimal_places=2)
    don_vi_tien_te: str = Field(default="VND", min_length=1, max_length=10)
    chu_ky_luong: ChuKyLuong = "thang"
    ghi_chu_luong: str | None = Field(default=None, max_length=500)
    moi_truong_lam_viec: str | None = Field(default=None, max_length=5000)
    dac_thu_thoi_gian: str | None = Field(default=None, max_length=500)
    muc_do_ap_luc: MucDoApLuc | None = None
    yeu_cau_suc_khoe: str | None = Field(default=None, max_length=500)
    trien_vong_nghe_nghiep: str | None = Field(default=None, max_length=5000)
    # Các giai đoạn theo thứ tự; nhận cả chuỗi kiểu cũ "A → B → C" (tự tách thành giai đoạn).
    lo_trinh_phat_trien: list[BuocLoTrinhNghe] | None = Field(default=None, max_length=20)
    nhom_holland: str | None = Field(default=None, max_length=20)
    tu_khoa_tim_kiem: str | None = Field(default=None, max_length=500)

    @field_validator("lo_trinh_phat_trien", mode="before")
    @classmethod
    def chuan_hoa_lo_trinh(cls, value: Any) -> Any:
        return _lo_trinh_dau_vao(value)

    @field_validator("ten_nghe")
    @classmethod
    def strip_ten_nghe(cls, value: str) -> str:
        return _bat_buoc(value, "Tên nghề")

    @field_validator("mo_ta_ngan", "yeu_cau_them", "yeu_cau_bang_cap", "hinh_anh_mo_ta", *COT_CHU_NGHE)
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @field_validator("don_vi_tien_te")
    @classmethod
    def normalize_don_vi_tien_te(cls, value: str) -> str:
        return _bat_buoc(value, "Đơn vị tiền tệ").upper()

    @field_validator("nhom_holland")
    @classmethod
    def normalize_nhom_holland(cls, value: str | None) -> str | None:
        cleaned = _rong_thanh_none(value)
        return cleaned.upper() if cleaned else None

    @model_validator(mode="after")
    def kiem_tra_khoang_luong(self) -> "DmNgheCuTheDiLamWrite":
        for cot_min, cot_max, nhan in CAP_LUONG_NGHE:
            tu, den = getattr(self, cot_min), getattr(self, cot_max)
            if tu is not None and den is not None and tu > den:
                raise ValueError(f"{nhan} tối thiểu không được lớn hơn tối đa")
        return self

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
    hinh_anh_mo_ta: str | None = None
    mo_ta_cong_viec: str | None = None
    trach_nhiem_chinh: str | None = None
    vi_tri_tuyen_dung_mau: str | None = None
    hinh_thuc_dao_tao: str | None = None
    trinh_do_toi_thieu: str | None = None
    chuyen_nganh_phu_hop: str | None = None
    ky_nang_chuyen_mon: str | None = None
    ky_nang_mem: str | None = None
    chung_chi_giay_phep: str | None = None
    luong_khoi_diem_min: Decimal | None = None
    luong_khoi_diem_max: Decimal | None = None
    luong_trung_binh_min: Decimal | None = None
    luong_trung_binh_max: Decimal | None = None
    luong_cao_min: Decimal | None = None
    luong_cao_max: Decimal | None = None
    don_vi_tien_te: str = "VND"
    chu_ky_luong: str = "thang"
    ghi_chu_luong: str | None = None
    moi_truong_lam_viec: str | None = None
    dac_thu_thoi_gian: str | None = None
    muc_do_ap_luc: str | None = None
    yeu_cau_suc_khoe: str | None = None
    trien_vong_nghe_nghiep: str | None = None
    # [{giai_doan, mo_ta_cong_viec, luong_trung_binh_min, luong_trung_binh_max, ghi_chu}]
    lo_trinh_phat_trien: list[BuocLoTrinhNghe] | None = None
    nhom_holland: str | None = None
    tu_khoa_tim_kiem: str | None = None

    @field_validator("lo_trinh_phat_trien", mode="before")
    @classmethod
    def chuan_hoa_lo_trinh(cls, value: Any) -> Any:
        return _lo_trinh_dau_vao(value)


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
