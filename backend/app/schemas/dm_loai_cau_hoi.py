from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmLoaiCauHoiWrite(BaseModel):
    ten_loai_cau_hoi: str = Field(..., min_length=1, max_length=150)
    ghi_chu: str | None = Field(default=None, max_length=2000)
    thu_tu_uu_tien: int = Field(..., ge=1, le=9999)
    trang_thai: int = Field(default=1, ge=0, le=1)

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
