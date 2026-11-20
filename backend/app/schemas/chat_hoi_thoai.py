from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ChatPhienItem(BaseModel):
    id: int
    ma_dinh_danh: str
    tieu_de: str | None = None
    trang_thai: str
    user_id: int | None = None
    ho_ten: str | None = None
    email: str | None = None
    ma_khach_vang_lai: str | None = None
    model_ai: str | None = None
    so_tin_nhan: int = 0
    tin_nhan_cuoi_luc: datetime | None = None
    # Đoạn đầu của tin nhắn gần nhất (câu hỏi hoặc câu trả lời) để xem nhanh trong danh sách.
    tin_nhan_cuoi: str | None = None
    created_at: datetime | None = None


class ChatPhienPage(BaseModel):
    items: list[ChatPhienItem]
    total: int
    page: int
    page_size: int


class ChatTinNhanItem(BaseModel):
    id: int
    loai_nguoi_gui: str
    nguoi_gui_id: int | None = None
    noi_dung_tin_nhan: str | None = None
    noi_dung_phan_hoi: str | None = None
    nguon_tham_khao: Any | None = None
    model_ai: str | None = None
    so_token_vao: int | None = None
    so_token_ra: int | None = None
    thoi_gian_phan_hoi_ms: int | None = None
    trang_thai: str
    loi_chi_tiet: str | None = None
    danh_gia: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class ChatPhienChiTiet(BaseModel):
    phien: ChatPhienItem
    tin_nhan: list[ChatTinNhanItem]


class ChatPhienTrangThai(BaseModel):
    # dang_hoat_dong: đang hỏi đáp; da_dong: đã kết thúc, không hỏi tiếp được.
    trang_thai: Literal["dang_hoat_dong", "da_dong"]


class ChatPhienDoiTieuDe(BaseModel):
    tieu_de: str = Field(max_length=255)

    @field_validator("tieu_de")
    @classmethod
    def bo_khoang_trang(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Vui lòng nhập tiêu đề cuộc hội thoại.")
        return value
