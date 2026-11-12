import re
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class LuotTimTruong(BaseModel):
    la_thanh_vien: bool
    # Hạn mức trong ngày theo cấu hình đang áp dụng.
    so_luot_ngay: int
    so_luot_khach_ngay: int
    so_luot_thanh_vien_ngay: int
    # Thành viên đếm theo tài khoản; khách đếm theo ma_thiet_bi (không gửi mã thì không đếm được).
    da_dung: int | None = None
    con_lai: int | None = None
    # True: danh sách trường kết hợp thêm đề án/phương thức tuyển sinh (có chỉ tiêu).
    ket_hop_phuong_thuc: bool = False


class TieuChiTimTruong(BaseModel):
    tu_khoa: str | None = Field(default=None, max_length=255)
    khu_vuc: str | None = Field(default=None, max_length=20)
    loai_co_so: str | None = Field(default=None, max_length=50)
    tinh: str | None = Field(default=None, max_length=100)
    sap_xep: Literal["ten_asc", "ten_desc", "chi_tieu_desc", "chuong_trinh_desc", "gan_toi"] = "ten_asc"
    uu_tien_tinh: str | None = Field(default=None, max_length=100)
    uu_tien_khu_vuc: str | None = Field(default=None, max_length=20)

    @field_validator("tu_khoa", "khu_vuc", "loai_co_so", "tinh", "uu_tien_tinh", "uu_tien_khu_vuc")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
_SO_DIEN_THOAI = re.compile(r"^(\+84|0)\d{9,10}$")
MA_THIET_BI_PATTERN = r"^[A-Za-z0-9_-]{8,64}$"


class ThongTinKhach(BaseModel):
    """Thông tin liên hệ khách vãng lai tự nhập, đều không bắt buộc."""

    ho_ten: str | None = Field(default=None, max_length=150)
    email: str | None = Field(default=None, max_length=255)
    so_dien_thoai: str | None = Field(default=None, max_length=20)

    @field_validator("ho_ten")
    @classmethod
    def clean_ho_ten(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None

    @field_validator("email")
    @classmethod
    def check_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        cleaned = value.strip().lower()
        if not _EMAIL.fullmatch(cleaned):
            raise ValueError("Email chưa đúng định dạng")
        return cleaned

    @field_validator("so_dien_thoai")
    @classmethod
    def check_so_dien_thoai(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        cleaned = re.sub(r"[\s.-]", "", value)
        if not _SO_DIEN_THOAI.fullmatch(cleaned):
            raise ValueError("Số điện thoại chưa đúng định dạng")
        return cleaned


class TimTruongPhuHopRequest(BaseModel):
    # Client sinh một mã cho mỗi lần bấm tìm; gửi lại cùng mã thì không bị trừ thêm lượt.
    ma_yeu_cau: str = Field(..., min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    ma_nganh: str = Field(..., min_length=1, max_length=20)
    nam_tuyen_sinh: int = Field(..., ge=1990, le=2100)
    du_lieu_nang_luc: dict[str, Any] = Field(default_factory=dict)
    du_lieu_tai_chinh: dict[str, Any] = Field(default_factory=dict)
    tieu_chi_tim_kiem: TieuChiTimTruong = Field(default_factory=TieuChiTimTruong)
    # Khách vãng lai: mã thiết bị (bắt buộc với khách) và thông tin liên hệ tự nhập.
    ma_thiet_bi: str | None = Field(default=None, pattern=MA_THIET_BI_PATTERN)
    thong_tin_khach: ThongTinKhach | None = None

    @field_validator("ma_nganh")
    @classmethod
    def strip_ma_nganh(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Mã ngành không được để trống")
        return cleaned


class TimTruongPhuHopResult(BaseModel):
    lich_su_id: int
    ma_yeu_cau: str
    trang_thai_xu_ly: str
    so_truong_tim_thay: int
    so_truong_phu_hop_so_bo: int
    luot: LuotTimTruong


class LichSuTimTruongQuanTri(BaseModel):
    id: int
    ma_yeu_cau: str
    tai_khoan_id: int | None = None
    la_khach: bool = False
    ma_thiet_bi: str | None = None
    thong_tin_khach: dict[str, Any] | None = None
    ho_ten: str | None = None
    email: str | None = None
    so_dien_thoai: str | None = None
    ma_nganh: str
    ten_nganh: str | None = None
    nam_tuyen_sinh: int
    tieu_chi_tim_kiem: dict[str, Any] | None = None
    so_truong_tim_thay: int
    so_truong_phu_hop_so_bo: int
    loai_luot: str
    da_tinh_luot: bool
    da_mo_khoa_chuyen_sau: bool
    trang_thai_xu_ly: str
    thong_bao_loi: str | None = None
    ngay_tao: datetime
    ngay_hoan_thanh: datetime | None = None


class LichSuTimTruongQuanTriChiTiet(LichSuTimTruongQuanTri):
    du_lieu_nang_luc: dict[str, Any] | None = None
    du_lieu_tai_chinh: dict[str, Any] | None = None
    du_lieu_ket_qua: dict[str, Any] | None = None
    phien_ban_thuat_toan: str | None = None
    gia_bao_cao_tai_thoi_diem: int | None = None
    giao_dich_thanh_toan_id: int | None = None
    ngay_mo_khoa: datetime | None = None


class LichSuTimTruongQuanTriPage(BaseModel):
    items: list[LichSuTimTruongQuanTri]
    total: int
    page: int
    page_size: int
