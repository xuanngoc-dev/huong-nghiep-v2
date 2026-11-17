from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TieuDeCauTraLoi(BaseModel):
    """Một câu trả lời dùng chung của loại câu hỏi: tiêu đề và số điểm (có thể để trống)."""

    tieu_de: str = Field(..., max_length=255)
    diem: int | None = Field(default=None, ge=-1000, le=1000)

    @model_validator(mode="before")
    @classmethod
    def tu_chuoi(cls, data):
        """Dữ liệu cũ lưu mỗi tiêu đề là một chuỗi: đổi thành {tieu_de} chưa có điểm."""
        return {"tieu_de": data} if isinstance(data, str) else data

    @field_validator("tieu_de")
    @classmethod
    def strip_tieu_de(cls, value: str) -> str:
        return value.strip()


class DmLoaiCauHoiWrite(BaseModel):
    ten_loai_cau_hoi: str = Field(..., min_length=1, max_length=150)
    ghi_chu: str | None = Field(default=None, max_length=2000)
    thu_tu_uu_tien: int = Field(..., ge=1, le=9999)
    trang_thai: int = Field(default=1, ge=0, le=1)
    loai_tra_loi: Literal["diem_so", "tinh_huong"] = "diem_so"
    danh_sach_tieu_de_cau_tra_loi: list[TieuDeCauTraLoi] | None = Field(default=None, max_length=50)

    @field_validator("danh_sach_tieu_de_cau_tra_loi")
    @classmethod
    def bo_dong_trong(cls, value: list[TieuDeCauTraLoi] | None) -> list[TieuDeCauTraLoi] | None:
        """Bỏ dòng không có tiêu đề; không còn dòng nào thì lưu null."""
        if value is None:
            return None
        return [item for item in value if item.tieu_de] or None

    @field_validator("ten_loai_cau_hoi")
    @classmethod
    def strip_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên loại câu hỏi không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmLoaiCauHoiPublic(BaseModel):
    id: int
    ten_loai_cau_hoi: str
    ghi_chu: str | None = None
    thu_tu_uu_tien: int
    trang_thai: int
    loai_tra_loi: str = "diem_so"
    danh_sach_tieu_de_cau_tra_loi: list[TieuDeCauTraLoi] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmLoaiCauHoiPage(BaseModel):
    items: list[DmLoaiCauHoiPublic]
    total: int
    page: int
    page_size: int


class DmLoaiCauHoiBulkResult(BaseModel):
    created: int


class DmLoaiCauHoiDeleteMany(BaseModel):
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


class DmLoaiCauHoiDeleteManyResult(BaseModel):
    deleted: int


class DmLoaiCauHoiAnhHuongXoa(BaseModel):
    """Số bản ghi sẽ bị xóa theo khi xóa các loại câu hỏi kèm dữ liệu liên quan."""

    so_loai: int
    so_cau_hoi: int
    so_dap_an: int
    so_phien: int
