from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DatsTuyenSinhWrite(BaseModel):
    truong_id: int = Field(..., ge=1)
    nam_tuyen_sinh: int = Field(..., ge=1990, le=2100)
    chi_tieu: int | None = Field(default=None, ge=0, le=4_294_967_295)
    ten_de_an: str | None = Field(default=None, max_length=255)
    hinh_thuc_dao_tao: list[str] | None = None
    gioi_thieu: str | None = Field(default=None, max_length=20000)
    ngay_cong_bo: date | None = None
    nguon_du_lieu_url: str | None = Field(default=None, max_length=1000)
    trang_thai: str | None = Field(default=None, max_length=20)
    ghi_chu: str | None = Field(default=None, max_length=20000)

    @field_validator("ten_de_an", "gioi_thieu", "nguon_du_lieu_url", "ghi_chu")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @field_validator("trang_thai", mode="before")
    @classmethod
    def normalize_trang_thai(cls, value: str | int | None) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    @field_validator("ngay_cong_bo", mode="before")
    @classmethod
    def empty_date_to_none(cls, value: date | str | None) -> date | str | None:
        if value is None or value == "":
            return None
        return value

    @field_validator("hinh_thuc_dao_tao", mode="before")
    @classmethod
    def normalize_hinh_thuc(cls, value: list | str | None) -> list[str] | None:
        if value is None or value == "":
            return None
        if isinstance(value, str):
            value = [part.strip() for part in value.split(",")]
        if not isinstance(value, list):
            raise ValueError("Hình thức đào tạo phải là danh sách")
        cleaned: list[str] = []
        seen: set[str] = set()
        for item in value:
            text = str(item).strip()
            if not text:
                continue
            if len(text) > 100:
                raise ValueError("Mỗi hình thức đào tạo tối đa 100 ký tự")
            if text in seen:
                continue
            seen.add(text)
            cleaned.append(text)
        if len(cleaned) > 20:
            raise ValueError("Chỉ chọn tối đa 20 hình thức đào tạo")
        return cleaned or None


class DatsTuyenSinhPublic(BaseModel):
    id: int
    truong_id: int
    ma_truong: str
    ten_truong: str
    nam_tuyen_sinh: int
    chi_tieu: int | None = None
    ten_de_an: str | None = None
    hinh_thuc_dao_tao: list | None = None
    gioi_thieu: str | None = None
    ngay_cong_bo: date | None = None
    nguon_du_lieu_url: str | None = None
    trang_thai: str | None = None
    ghi_chu: str | None = None
    tao_luc: datetime | None = None
    cap_nhat_luc: datetime | None = None


class DatsTuyenSinhPage(BaseModel):
    items: list[DatsTuyenSinhPublic]
    total: int
    page: int
    page_size: int


class DatsTuyenSinhBulkResult(BaseModel):
    created: int


class DatsImportRequest(BaseModel):
    truong_id: int = Field(..., ge=1)
    nam_tuyen_sinh: int = Field(..., ge=1990, le=2100)
    du_lieu: dict


class DatsImportResult(BaseModel):
    de_an_id: int
    counts: dict[str, int]


class DatsTuyenSinhDeleteMany(BaseModel):
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


class DatsTuyenSinhDeleteManyResult(BaseModel):
    deleted: int
