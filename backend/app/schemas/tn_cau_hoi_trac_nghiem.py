from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class TnCauTraLoiWrite(BaseModel):
    id: int | None = Field(default=None, ge=1)
    noi_dung_cau_tra_loi: str = Field(..., min_length=1, max_length=2000)
    diem: int = Field(..., ge=-9999, le=9999)

    @field_validator("noi_dung_cau_tra_loi")
    @classmethod
    def strip_noi_dung(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung câu trả lời không được để trống")
        return cleaned


class TnCauTraLoiPublic(BaseModel):
    id: int
    cau_hoi_id: int
    noi_dung_cau_tra_loi: str
    diem: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class TnCauHoiTracNghiemWrite(BaseModel):
    ma_holand: str = Field(..., min_length=1, max_length=20)
    loai_cau_hoi_id: int = Field(..., ge=1)
    noi_dung_cau_hoi: str = Field(..., min_length=1, max_length=5000)
    ghi_chu: str | None = Field(default=None, max_length=2000)
    trang_thai: int = Field(default=1, ge=0, le=1)
    cau_tra_loi: list[TnCauTraLoiWrite] = Field(default_factory=list, max_length=20)

    @field_validator("ma_holand")
    @classmethod
    def normalize_ma_holand(cls, value: str) -> str:
        cleaned = value.strip().upper()
        if not cleaned:
            raise ValueError("Mã Holland không được để trống")
        return cleaned

    @field_validator("noi_dung_cau_hoi")
    @classmethod
    def strip_noi_dung(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Nội dung câu hỏi không được để trống")
        return cleaned

    @field_validator("ghi_chu")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @field_validator("cau_tra_loi")
    @classmethod
    def unique_answer_ids(cls, value: list[TnCauTraLoiWrite]) -> list[TnCauTraLoiWrite]:
        seen: set[int] = set()
        for answer in value:
            if answer.id is None:
                continue
            if answer.id in seen:
                raise ValueError("Đáp án bị trùng trong câu hỏi")
            seen.add(answer.id)
        return value


class TnCauHoiTracNghiemPublic(BaseModel):
    id: int
    ma_holand: str
    loai_cau_hoi_id: int
    ten_loai_cau_hoi: str
    noi_dung_cau_hoi: str
    ghi_chu: str | None = None
    trang_thai: int
    cau_tra_loi: list[TnCauTraLoiPublic] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class TnCauHoiTracNghiemPage(BaseModel):
    items: list[TnCauHoiTracNghiemPublic]
    total: int
    page: int
    page_size: int


class TnCauHoiTracNghiemBulkResult(BaseModel):
    created: int


class TnCauHoiTracNghiemDeleteMany(BaseModel):
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


class TnCauHoiTracNghiemDeleteManyResult(BaseModel):
    deleted: int
