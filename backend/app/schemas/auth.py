from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.constants.doi_tuong_huong_den import chuan_hoa_doi_tuong


class RegisterRequest(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    mat_khau: str = Field(..., min_length=6, max_length=128)
    # Mã đối tượng hướng đến (app/constants/doi_tuong_huong_den.py): trợ lý chat dùng cố định đối tượng này cho
    # tài khoản. Tỉnh thành đang ở lưu vào nguoi_dung_thong_tin.
    doi_tuong: str | None = Field(default=None, max_length=50)
    tinh_thanh_id: int | None = Field(default=None, ge=1)

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

    @field_validator("doi_tuong")
    @classmethod
    def check_doi_tuong(cls, value: str | None) -> str | None:
        return chuan_hoa_doi_tuong(value)


class LoginRequest(BaseModel):
    email: EmailStr
    mat_khau: str = Field(..., min_length=1, max_length=128)


class NguoiDungPublic(BaseModel):
    id: int
    ho_ten: str
    email: EmailStr
    so_dien_thoai: str | None = None
    doi_tuong: str | None = None
    vai_tro: int
    trang_thai: int
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: NguoiDungPublic


class DoiMatKhauRequest(BaseModel):
    mat_khau_cu: str = Field(..., min_length=1, max_length=128)
    mat_khau_moi: str = Field(..., min_length=6, max_length=128)


class DoiMatKhauKetQua(BaseModel):
    thanh_cong: bool = True
