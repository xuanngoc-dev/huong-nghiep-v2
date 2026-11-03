from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DatsWebsiteFields(BaseModel):
    """Các cột nghiệp vụ của một website. id và de_an_id trong JSON không dùng ở đây."""

    model_config = ConfigDict(extra="ignore")

    loai_website: str | None = Field(default=None, max_length=30)
    ten_trang: str = Field(..., max_length=255)
    url: str | None = Field(default=None, max_length=1000)
    ghi_chu: str | None = Field(default=None, max_length=20000)

    @field_validator("loai_website", "url", "ghi_chu")
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @field_validator("ten_trang")
    @classmethod
    def require_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vui lòng nhập tên trang")
        return cleaned


class DatsWebsiteWrite(DatsWebsiteFields):
    de_an_id: int = Field(..., ge=1)


class DatsWebsitePublic(BaseModel):
    id: int
    de_an_id: int
    ten_de_an: str | None = None
    truong_id: int
    ma_truong: str
    ten_truong: str
    nam_tuyen_sinh: int
    loai_website: str | None = None
    ten_trang: str | None = None
    url: str | None = None
    ghi_chu: str | None = None


class DatsWebsitePage(BaseModel):
    items: list[DatsWebsitePublic]
    total: int
    page: int
    page_size: int


class DatsWebsiteImportRequest(BaseModel):
    de_an_id: int = Field(..., ge=1)
    du_lieu: list[DatsWebsiteFields] = Field(..., min_length=1, max_length=2000)


class DatsWebsiteImportResult(BaseModel):
    created: int


class DatsWebsiteDeleteMany(BaseModel):
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


class DatsWebsiteDeleteManyResult(BaseModel):
    deleted: int
