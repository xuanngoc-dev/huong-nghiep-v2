from datetime import datetime

from pydantic import BaseModel, Field, field_validator


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class NapTienTao(BaseModel):
    """Thành viên bấm Đăng ký một gói cước."""

    goi_cuoc_id: int = Field(..., ge=1)
    ngan_hang_thanh_toan_id: int | None = Field(default=None, ge=1)


class NapTienCapNhat(BaseModel):
    """Thành viên đổi ngân hàng chuyển khoản hoặc báo đã chuyển khoản cho giao dịch đang chờ."""

    ngan_hang_thanh_toan_id: int | None = Field(default=None, ge=1)
    da_chuyen_khoan: bool = False


class NapTienXacNhan(BaseModel):
    """Admin xác nhận đã nhận tiền."""

    so_tien_thuc_nhan: int | None = Field(default=None, ge=0, le=999_999_999_999_999)
    ma_tham_chieu_ngan_hang: str | None = Field(default=None, max_length=100)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ma_tham_chieu_ngan_hang", "ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _blank(value)


class NapTienTuChoi(BaseModel):
    """Admin từ chối giao dịch (không nhận được tiền)."""

    ghi_chu: str = Field(..., min_length=1, max_length=2000)

    @field_validator("ghi_chu")
    @classmethod
    def strip_ghi_chu(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vui lòng nhập lý do từ chối")
        return cleaned


class NapTienPublic(BaseModel):
    """Giao dịch nạp tiền hiển thị cho chính người nạp."""

    id: int
    ma_giao_dich: str
    goi_cuoc_dang_ky_id: int | None = None
    ma_goi_cuoc: str
    ten_goi_cuoc: str
    loai_ap_dung: str
    so_luot_nhan_duoc: int
    so_tien_nap: int
    so_tien_thuc_nhan: int | None = None
    ngan_hang_thanh_toan_id: int | None = None
    ten_ngan_hang_viet_tat: str | None = None
    so_tai_khoan_nhan: str | None = None
    chu_tai_khoan_nhan: str | None = None
    noi_dung_chuyen_khoan: str | None = None
    trang_thai: int
    thoi_gian_thanh_toan: datetime | None = None
    thoi_gian_xac_nhan: datetime | None = None
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class NapTienQuanTri(NapTienPublic):
    """Giao dịch nạp tiền cho admin, kèm người nạp và thông tin đối soát."""

    nguoi_dung_id: int | None = None
    ho_ten: str | None = None
    email: str | None = None
    ma_tham_chieu_ngan_hang: str | None = None
    nguoi_xac_nhan_id: int | None = None


class NapTienPage(BaseModel):
    items: list[NapTienPublic]
    total: int
    page: int
    page_size: int


class NapTienQuanTriPage(BaseModel):
    items: list[NapTienQuanTri]
    total: int
    page: int
    page_size: int
