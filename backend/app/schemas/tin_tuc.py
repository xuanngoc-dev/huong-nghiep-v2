import re
import unicodedata
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

SLUG_TOI_DA = 255


def tao_slug(value: str) -> str:
    """Tiêu đề tiếng Việt → slug không dấu: "Hướng nghiệp 2026!" → "huong-nghiep-2026"."""
    text = unicodedata.normalize("NFD", value.replace("đ", "d").replace("Đ", "D"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")[:SLUG_TOI_DA].rstrip("-")


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


def _chuan_hoa_slug(value: str | None) -> str | None:
    """Slug nhập tay cũng được chuẩn hóa (bỏ dấu, chữ thường, gạch nối); rỗng → None để tự sinh từ tên/tiêu đề."""
    if value is None or not value.strip():
        return None
    return tao_slug(value) or None


class _DanhSachId(BaseModel):
    ids: list[int] = Field(..., min_length=1, max_length=500)

    @field_validator("ids")
    @classmethod
    def unique_ids(cls, value: list[int]) -> list[int]:
        return list(dict.fromkeys(value))


class KetQuaXoaNhieu(BaseModel):
    deleted: int


# ---------- Nhóm tin ----------


class TinTucNhomTinWrite(BaseModel):
    ma_nhom: str = Field(..., min_length=1, max_length=50)
    ten_nhom: str = Field(..., min_length=1, max_length=255)
    # Bỏ trống: tự sinh từ tên nhóm.
    slug: str | None = Field(default=None, max_length=SLUG_TOI_DA)
    mo_ta: str | None = Field(default=None, max_length=5000)
    thu_tu: int = Field(default=0, ge=0, le=100000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ma_nhom")
    @classmethod
    def normalize_ma_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Mã nhóm").upper()

    @field_validator("ten_nhom")
    @classmethod
    def strip_ten_nhom(cls, value: str) -> str:
        return _bat_buoc(value, "Tên nhóm")

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        return _chuan_hoa_slug(value)

    @field_validator("mo_ta")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def slug_mac_dinh(self) -> "TinTucNhomTinWrite":
        if not self.slug:
            self.slug = tao_slug(self.ten_nhom) or self.ma_nhom.lower()
        return self


class TinTucNhomTinPublic(BaseModel):
    id: int
    ma_nhom: str
    ten_nhom: str
    slug: str
    mo_ta: str | None = None
    thu_tu: int
    trang_thai: int
    # Số bài viết thuộc nhóm (mọi trạng thái).
    so_bai_viet: int = 0
    created_at: datetime
    updated_at: datetime


class TinTucNhomTinPage(BaseModel):
    items: list[TinTucNhomTinPublic]
    total: int
    page: int
    page_size: int


class TinTucNhomTinDeleteMany(_DanhSachId):
    pass


# ---------- Bài viết ----------


class TinTucBaiVietWrite(BaseModel):
    nhom_tin_tuc_id: int = Field(..., ge=1)
    tieu_de: str = Field(..., min_length=1, max_length=500)
    # Bỏ trống: tự sinh từ tiêu đề.
    slug: str | None = Field(default=None, max_length=SLUG_TOI_DA)
    tom_tat: str | None = Field(default=None, max_length=5000)
    # Nội dung HTML.
    noi_dung: str | None = Field(default=None, max_length=1_000_000)
    anh_dai_dien: str | None = Field(default=None, max_length=500)
    tac_gia: str | None = Field(default=None, max_length=255)
    # 0: nháp / ẩn, 1: xuất bản
    trang_thai: int = Field(default=1, ge=0, le=1)
    is_noi_bat: int = Field(default=0, ge=0, le=1)

    @field_validator("tieu_de")
    @classmethod
    def strip_tieu_de(cls, value: str) -> str:
        return _bat_buoc(value, "Tiêu đề")

    @field_validator("slug")
    @classmethod
    def normalize_slug(cls, value: str | None) -> str | None:
        return _chuan_hoa_slug(value)

    @field_validator("tom_tat", "noi_dung", "anh_dai_dien", "tac_gia")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        return _rong_thanh_none(value)

    @model_validator(mode="after")
    def slug_mac_dinh(self) -> "TinTucBaiVietWrite":
        if not self.slug:
            self.slug = tao_slug(self.tieu_de)
        if not self.slug:
            raise ValueError("Không tạo được slug từ tiêu đề, vui lòng nhập slug")
        return self


class TinTucBaiVietHienThi(BaseModel):
    """Đổi nhanh trạng thái xuất bản / nổi bật từ bảng danh sách; trường bỏ trống giữ nguyên."""

    trang_thai: int | None = Field(default=None, ge=0, le=1)
    is_noi_bat: int | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def co_it_nhat_mot_truong(self) -> "TinTucBaiVietHienThi":
        if self.trang_thai is None and self.is_noi_bat is None:
            raise ValueError("Cần gửi trang_thai hoặc is_noi_bat")
        return self


class TinTucBaiVietTomTat(BaseModel):
    """Một dòng trong danh sách bài viết (không kèm nội dung để nhẹ dữ liệu)."""

    id: int
    nhom_tin_tuc_id: int
    ten_nhom: str | None = None
    tieu_de: str
    slug: str
    tom_tat: str | None = None
    anh_dai_dien: str | None = None
    tac_gia: str | None = None
    trang_thai: int
    is_noi_bat: int
    luot_xem: int
    created_at: datetime
    updated_at: datetime


class TinTucBaiVietPublic(TinTucBaiVietTomTat):
    noi_dung: str | None = None


class TinTucBaiVietPage(BaseModel):
    items: list[TinTucBaiVietTomTat]
    total: int
    page: int
    page_size: int


class TinTucBaiVietDeleteMany(_DanhSachId):
    pass
