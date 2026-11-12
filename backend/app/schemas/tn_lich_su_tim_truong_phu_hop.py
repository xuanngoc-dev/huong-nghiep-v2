from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class LuotTimTruong(BaseModel):
    la_thanh_vien: bool
    # Hạn mức trong ngày theo cấu hình đang áp dụng.
    so_luot_ngay: int
    so_luot_khach_ngay: int
    so_luot_thanh_vien_ngay: int
    # Chỉ đếm được cho thành viên; khách vãng lai do trình duyệt tự đếm.
    da_dung: int | None = None
    con_lai: int | None = None


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


class TimTruongPhuHopRequest(BaseModel):
    # Client sinh một mã cho mỗi lần bấm tìm; gửi lại cùng mã thì không bị trừ thêm lượt.
    ma_yeu_cau: str = Field(..., min_length=8, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    ma_nganh: str = Field(..., min_length=1, max_length=20)
    nam_tuyen_sinh: int = Field(..., ge=1990, le=2100)
    du_lieu_nang_luc: dict[str, Any] = Field(default_factory=dict)
    du_lieu_tai_chinh: dict[str, Any] = Field(default_factory=dict)
    tieu_chi_tim_kiem: TieuChiTimTruong = Field(default_factory=TieuChiTimTruong)

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
