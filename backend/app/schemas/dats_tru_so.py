from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DatsTruSoFields(BaseModel):
    """Các cột nghiệp vụ của một trụ sở. id và de_an_id trong JSON không dùng ở đây."""

    model_config = ConfigDict(extra="ignore")

    vai_tro: str | None = Field(default=None, max_length=30)
    ten_co_so: str = Field(..., max_length=255)
    loai_co_so: str | None = Field(default=None, max_length=30)
    dia_chi: str | None = Field(default=None, max_length=500)
    so_dien_thoai: str | None = Field(default=None, max_length=30)
    ghi_chu: str | None = Field(default=None, max_length=20000)

    @field_validator("vai_tro", "loai_co_so", "dia_chi", "so_dien_thoai", "ghi_chu")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @field_validator("ten_co_so")
    @classmethod
    def require_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vui lòng nhập tên cơ sở")
        return cleaned


class DatsTruSoWrite(DatsTruSoFields):
    de_an_id: int = Field(..., ge=1)


class DatsTruSoPublic(BaseModel):
    id: int
    de_an_id: int
    ten_de_an: str | None = None
    truong_id: int
    ma_truong: str
    ten_truong: str
    nam_tuyen_sinh: int
    vai_tro: str | None = None
    ten_co_so: str | None = None
    loai_co_so: str | None = None
    dia_chi: str | None = None
    so_dien_thoai: str | None = None
    ghi_chu: str | None = None


class DatsTruSoPage(BaseModel):
    items: list[DatsTruSoPublic]
    total: int
    page: int
    page_size: int


class DatsTruSoImportRequest(BaseModel):
    de_an_id: int = Field(..., ge=1)
    du_lieu: list[DatsTruSoFields] = Field(..., min_length=1, max_length=2000)


class DatsTruSoImportResult(BaseModel):
    created: int


class DatsTruSoDeleteMany(BaseModel):
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


class DatsTruSoDeleteManyResult(BaseModel):
    deleted: int
