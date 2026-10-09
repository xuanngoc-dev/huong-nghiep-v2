from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    mat_khau: str = Field(..., min_length=6, max_length=128)

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


class LoginRequest(BaseModel):
    email: EmailStr
    mat_khau: str = Field(..., min_length=1, max_length=128)


class NguoiDungPublic(BaseModel):
    id: int
    ho_ten: str
    email: EmailStr
    so_dien_thoai: str | None = None
    vai_tro: int
    trang_thai: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: NguoiDungPublic
