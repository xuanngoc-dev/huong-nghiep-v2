from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class NguoiDungCreate(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    mat_khau: str = Field(..., min_length=6, max_length=128)
    vai_tro: int = Field(default=0, ge=0, le=1)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ho_ten")
    @classmethod
    def strip_ho_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Họ tên phải có ít nhất 2 ký tự")
        return cleaned

    @field_validator("so_dien_thoai")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class NguoiDungUpdate(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    mat_khau: str | None = Field(default=None, min_length=6, max_length=128)
    vai_tro: int = Field(..., ge=0, le=1)
    trang_thai: int = Field(..., ge=0, le=1)

    @field_validator("ho_ten")
    @classmethod
    def strip_ho_ten(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 2:
            raise ValueError("Họ tên phải có ít nhất 2 ký tự")
        return cleaned

    @field_validator("so_dien_thoai")
    @classmethod
    def normalize_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("mat_khau")
    @classmethod
    def empty_password_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class NguoiDungAdminPublic(BaseModel):
    id: int
    ho_ten: str
    email: EmailStr
    so_dien_thoai: str | None = None
    vai_tro: int
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class NguoiDungPage(BaseModel):
    items: list[NguoiDungAdminPublic]
    total: int
    page: int
    page_size: int


class NguoiDungDeleteMany(BaseModel):
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


class NguoiDungDeleteManyResult(BaseModel):
    deleted: int
