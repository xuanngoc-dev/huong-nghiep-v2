from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


class _NganhFields(BaseModel):
    # Dữ liệu import có thể thiếu một số thông tin, nên các trường ngành đều được để trống.
    ma_nganh: str | None = Field(default=None, max_length=20)
    ma_xet_tuyen: str | None = Field(default=None, max_length=50)
    ten_nganh: str | None = Field(default=None, max_length=255)
    ten_chuong_trinh: str | None = Field(default=None, max_length=255)
    ghi_chu: str | None = Field(default=None, max_length=2000)

    @field_validator("ma_nganh", "ma_xet_tuyen", mode="before")
    @classmethod
    def normalize_ma(cls, value: object) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip().upper()
        return cleaned or None

    @field_validator("ten_nganh", "ten_chuong_trinh", mode="before")
    @classmethod
    def normalize_ten(cls, value: object) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(str(value).split())
        return cleaned or None

    @field_validator("ghi_chu", mode="before")
    @classmethod
    def empty_to_none(cls, value: object) -> str | None:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    def is_empty(self) -> bool:
        """Không có thông tin ngành nào (mã xét tuyển, mã ngành, tên ngành, tên chương trình)."""
        return not (self.ma_xet_tuyen or self.ma_nganh or self.ten_nganh or self.ten_chuong_trinh)


def _normalize_ma_truong(value: str) -> str:
    cleaned = value.strip().upper()
    if not cleaned:
        raise ValueError("Mã trường không được để trống")
    return cleaned


class DmNganhHocTheoTruongWrite(_NganhFields):
    ma_truong: str = Field(..., min_length=1, max_length=20)
    nam_hoc: int = Field(..., ge=2000, le=2100)

    @field_validator("ma_truong")
    @classmethod
    def normalize_ma_truong(cls, value: str) -> str:
        return _normalize_ma_truong(value)

    @model_validator(mode="after")
    def check_co_thong_tin(self) -> "DmNganhHocTheoTruongWrite":
        if self.is_empty():
            raise ValueError("Cần nhập ít nhất một trong: mã xét tuyển, mã ngành, tên ngành, tên chương trình")
        return self


class DmNganhTheoTruongImportChuongTrinh(_NganhFields):
    pass


class DmNganhTheoTruongImport(BaseModel):
    """Một trường trong file JSON import: mã trường, năm tuyển sinh và các chương trình đào tạo."""

    ma_truong: str = Field(..., min_length=1, max_length=20)
    nam_tuyen_sinh: int = Field(..., ge=2000, le=2100)
    chuong_trinh_dao_tao: list[DmNganhTheoTruongImportChuongTrinh] = Field(default_factory=list, max_length=1000)

    @field_validator("ma_truong")
    @classmethod
    def normalize_ma_truong(cls, value: str) -> str:
        return _normalize_ma_truong(value)


class DmNganhTheoTruongImportResult(BaseModel):
    # Số trường đã xử lý (dùng cho thanh tiến độ theo lô).
    created: int
    them_moi: int
    cap_nhat: int
    # Chương trình không có thông tin ngành nào.
    bo_qua: int = 0


class DmNganhTheoTruongKiemTra(BaseModel):
    ma_truong: list[str] = Field(..., min_length=1, max_length=5000)


class DmNganhTheoTruongKiemTraResult(BaseModel):
    thieu: list[str]


class DmNganhHocTheoTruongPublic(BaseModel):
    id: int
    ma_truong: str
    ten_truong: str | None = None
    nam_hoc: int
    ma_nganh: str | None = None
    ma_xet_tuyen: str | None = None
    ten_nganh: str | None = None
    ten_chuong_trinh: str | None = None
    ghi_chu: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class DmNganhHocTheoTruongPage(BaseModel):
    items: list[DmNganhHocTheoTruongPublic]
    total: int
    page: int
    page_size: int


class DmNganhHocTheoTruongDeleteMany(BaseModel):
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


class DmNganhHocTheoTruongDeleteManyResult(BaseModel):
    deleted: int
