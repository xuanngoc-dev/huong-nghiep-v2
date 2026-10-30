from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


class DatsChuongTrinhDaoTaoFields(BaseModel):
    """Các cột nghiệp vụ của một chương trình. id và de_an_id trong JSON không dùng ở đây."""

    model_config = ConfigDict(extra="ignore")

    nganh_dao_tao_id: int | None = Field(default=None, ge=1)
    ma_xet_tuyen: str | None = Field(default=None, max_length=20)
    ten_chuong_trinh: str = Field(..., max_length=255)
    trinh_do_dao_tao: str | None = Field(default=None, max_length=30)
    hinh_thuc_dao_tao: str | None = Field(default=None, max_length=30)
    co_so_id: int | None = Field(default=None, ge=1)
    thoi_gian_dao_tao_nam: Decimal | None = None
    ngon_ngu_dao_tao: str | None = Field(default=None, max_length=100)
    chi_tieu_tuyen_sinh: int | None = Field(default=None, ge=0, le=4_294_967_295)
    kieu_phan_bo_chi_tieu: str | None = Field(default=None, max_length=30)
    ghi_chu: str | None = Field(default=None, max_length=20000)

    @field_validator(
        "nganh_dao_tao_id",
        "co_so_id",
        "chi_tieu_tuyen_sinh",
        "thoi_gian_dao_tao_nam",
        mode="before",
    )
    @classmethod
    def empty_number_to_none(cls, value):
        if value is None or value == "":
            return None
        return value

    @field_validator(
        "ma_xet_tuyen",
        "trinh_do_dao_tao",
        "hinh_thuc_dao_tao",
        "ngon_ngu_dao_tao",
        "kieu_phan_bo_chi_tieu",
        "ghi_chu",
    )
    @classmethod
    def empty_text_to_none(cls, value: str | None) -> str | None:
        return _clean_text(value)

    @field_validator("ten_chuong_trinh")
    @classmethod
    def require_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Vui lòng nhập tên chương trình")
        return cleaned

    @field_validator("thoi_gian_dao_tao_nam")
    @classmethod
    def check_duration(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return None
        try:
            number = Decimal(value)
        except (InvalidOperation, ValueError):
            raise ValueError("Thời gian đào tạo không hợp lệ") from None
        if number < 0 or number > Decimal("999.9"):
            raise ValueError("Thời gian đào tạo phải từ 0 đến 999.9")
        if number != number.quantize(Decimal("0.1")):
            raise ValueError("Thời gian đào tạo chỉ lấy một chữ số thập phân")
        return number


class DatsChuongTrinhDaoTaoWrite(DatsChuongTrinhDaoTaoFields):
    de_an_id: int = Field(..., ge=1)


class DatsChuongTrinhDaoTaoPublic(BaseModel):
    id: int
    de_an_id: int
    ten_de_an: str | None = None
    truong_id: int
    ma_truong: str
    ten_truong: str
    nam_tuyen_sinh: int
    nganh_dao_tao_id: int | None = None
    ma_nganh: str | None = None
    ten_nganh: str | None = None
    ma_xet_tuyen: str | None = None
    ten_chuong_trinh: str
    trinh_do_dao_tao: str | None = None
    hinh_thuc_dao_tao: str | None = None
    co_so_id: int | None = None
    ten_co_so: str | None = None
    thoi_gian_dao_tao_nam: float | None = None
    ngon_ngu_dao_tao: str | None = None
    chi_tieu_tuyen_sinh: int | None = None
    kieu_phan_bo_chi_tieu: str | None = None
    ghi_chu: str | None = None


class DatsChuongTrinhDaoTaoPage(BaseModel):
    items: list[DatsChuongTrinhDaoTaoPublic]
    total: int
    page: int
    page_size: int


class DatsChuongTrinhDaoTaoImportRequest(BaseModel):
    de_an_id: int = Field(..., ge=1)
    du_lieu: list[DatsChuongTrinhDaoTaoFields] = Field(..., min_length=1, max_length=2000)


class DatsChuongTrinhDaoTaoImportResult(BaseModel):
    created: int


class DatsChuongTrinhDaoTaoDeleteMany(BaseModel):
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


class DatsChuongTrinhDaoTaoDeleteManyResult(BaseModel):
    deleted: int
