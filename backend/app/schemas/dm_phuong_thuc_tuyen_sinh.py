from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class DmPhuongThucTuyenSinhWrite(BaseModel):
    ten_phuong_thuc: str = Field(..., min_length=1, max_length=255)
    ma_phuong_thuc: str = Field(..., min_length=1, max_length=20)
    giai_thich: str | None = Field(default=None, max_length=5000)
    truong_hop_cu_the: str | None = Field(default=None, max_length=5000)
    luu_y: str | None = Field(default=None, max_length=5000)
    trang_thai: int = Field(default=1, ge=0, le=1)

    @field_validator("ten_phuong_thuc")
    @classmethod
    def strip_ten_phuong_thuc(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Tên phương thức không được để trống")
        return cleaned

    @field_validator("ma_phuong_thuc")
    @classmethod
    def normalize_ma_phuong_thuc(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã phương thức không được để trống")
        return cleaned

    @field_validator("giai_thich", "truong_hop_cu_the", "luu_y")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class DmPhuongThucTuyenSinhPublic(BaseModel):
    id: int
    ten_phuong_thuc: str
    ma_phuong_thuc: str
    giai_thich: str | None = None
    truong_hop_cu_the: str | None = None
    luu_y: str | None = None
    trang_thai: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmPhuongThucTuyenSinhPage(BaseModel):
    items: list[DmPhuongThucTuyenSinhPublic]
    total: int
    page: int
    page_size: int


class DmPhuongThucTuyenSinhBulkResult(BaseModel):
    created: int


class DmPhuongThucTuyenSinhDeleteMany(BaseModel):
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


class DmPhuongThucTuyenSinhDeleteManyResult(BaseModel):
    deleted: int
