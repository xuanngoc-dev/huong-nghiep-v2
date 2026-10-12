import re
from datetime import date

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

MUC_TAI_CHINH = {"Thấp", "Trung bình", "Khá", "Tốt"}
HANH_KIEM = {"Tốt", "Khá", "Trung bình", "Yếu"}
_PHONE = re.compile(r"^[0-9+\-\s]{8,20}$")
_SUBJECT_CODE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{0,19}$")
_GRADES = {"10", "11", "12"}


def _blank(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _choice(value: str | None, allowed: set[str], message: str) -> str | None:
    cleaned = _blank(value)
    if cleaned is None:
        return None
    if cleaned not in allowed:
        raise ValueError(message)
    return cleaned


def _score_map(value: dict | None) -> dict[str, float] | None:
    if not value:
        return None
    if len(value) > 200:
        raise ValueError("Danh sách điểm môn học quá dài")
    cleaned: dict[str, float] = {}
    for raw_key, raw_score in value.items():
        code = str(raw_key).strip().upper()
        if not _SUBJECT_CODE.fullmatch(code):
            raise ValueError(f"Mã môn học không hợp lệ: {raw_key}")
        if raw_score is None or raw_score == "":
            continue
        score = float(raw_score)
        if score < 0 or score > 10:
            raise ValueError(f"Điểm môn {code} phải từ 0 đến 10")
        cleaned[code] = round(score, 2)
    return cleaned or None


def _grade_scores(raw: dict) -> dict[str, float] | None:
    if "hoc_luc" in raw or "hanh_kiem" in raw:
        hoc_luc_raw = raw.get("hoc_luc")
        if hoc_luc_raw is None:
            return None
        if not isinstance(hoc_luc_raw, dict):
            raise ValueError("Học lực của mỗi lớp phải là danh sách điểm theo môn")
        return _score_map(hoc_luc_raw)
    return _score_map(raw)


def _hoc_ba(value: dict | None) -> dict[str, dict[str, float]] | None:
    if not value:
        return None
    cleaned: dict[str, dict[str, float]] = {}
    for raw_grade, raw_block in value.items():
        grade = str(raw_grade).strip()
        if grade not in _GRADES:
            raise ValueError("Điểm học bạ chỉ gồm lớp 10, 11 và 12")
        if raw_block is None:
            continue
        if not isinstance(raw_block, dict):
            raise ValueError("Điểm học bạ của mỗi lớp phải là danh sách điểm theo môn")
        scores = _grade_scores(raw_block)
        if scores:
            cleaned[grade] = scores
    return cleaned or None


def _grade_average(value: dict | None) -> dict[str, float] | None:
    if not value:
        return None
    cleaned: dict[str, float] = {}
    for raw_grade, raw_score in value.items():
        grade = str(raw_grade).strip()
        if grade not in _GRADES:
            raise ValueError("Học lực trung bình chỉ gồm lớp 10, 11 và 12")
        if raw_score is None or raw_score == "":
            continue
        score = float(raw_score)
        if score < 0 or score > 10:
            raise ValueError(f"Học lực trung bình lớp {grade} phải từ 0 đến 10")
        cleaned[grade] = round(score, 2)
    return cleaned or None


def _grade_conduct(value: dict | None) -> dict[str, str] | None:
    if not value:
        return None
    cleaned: dict[str, str] = {}
    for raw_grade, raw_label in value.items():
        grade = str(raw_grade).strip()
        if grade not in _GRADES:
            raise ValueError("Hạnh kiểm chỉ gồm lớp 10, 11 và 12")
        if raw_label is None or raw_label == "":
            continue
        label = str(raw_label).strip()
        if label not in HANH_KIEM:
            raise ValueError(f"Hạnh kiểm lớp {grade} không hợp lệ")
        cleaned[grade] = label
    return cleaned or None


class DiemThiThptQuocGia(BaseModel):
    du_kien: dict[str, float | None] | None = None

    @field_validator("du_kien")
    @classmethod
    def check_scores(cls, value: dict | None) -> dict[str, float] | None:
        return _score_map(value)


class SucKhoeTheChat(BaseModel):
    chieu_cao: float | None = Field(default=None, ge=30, le=250)
    can_nang: float | None = Field(default=None, ge=5, le=300)
    tien_su_benh: str | None = Field(default=None, max_length=1000)

    @field_validator("tien_su_benh")
    @classmethod
    def strip_tien_su(cls, value: str | None) -> str | None:
        return _blank(value)


class TrinhDoHocVan(BaseModel):
    diem_trung_binh_hoc_ba: dict | None = None
    hoc_luc_trung_binh: dict | None = None
    hanh_kiem: dict | None = None
    diem_thi_thpt_quoc_gia: DiemThiThptQuocGia | None = None
    suc_khoe_the_chat: SucKhoeTheChat | None = None

    @field_validator("diem_trung_binh_hoc_ba")
    @classmethod
    def check_hoc_ba(cls, value: dict | None) -> dict | None:
        return _hoc_ba(value)

    @field_validator("hoc_luc_trung_binh")
    @classmethod
    def check_hoc_luc_trung_binh(cls, value: dict | None) -> dict | None:
        return _grade_average(value)

    @field_validator("hanh_kiem")
    @classmethod
    def check_hanh_kiem(cls, value: dict | None) -> dict | None:
        return _grade_conduct(value)

    @model_validator(mode="after")
    def drop_empty_blocks(self):
        if self.diem_thi_thpt_quoc_gia and not self.diem_thi_thpt_quoc_gia.model_dump(exclude_none=True):
            self.diem_thi_thpt_quoc_gia = None
        if self.suc_khoe_the_chat and not self.suc_khoe_the_chat.model_dump(exclude_none=True):
            self.suc_khoe_the_chat = None
        return self


class KhaNangTaiChinh(BaseModel):
    muc: str | None = Field(default=None, max_length=50)
    ghi_chu: str | None = Field(default=None, max_length=500)

    @field_validator("muc")
    @classmethod
    def check_muc(cls, value: str | None) -> str | None:
        return _choice(value, MUC_TAI_CHINH, "Mức khả năng tài chính không hợp lệ")

    @field_validator("ghi_chu")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return _blank(value)


class HoSoWrite(BaseModel):
    ho_ten: str = Field(..., min_length=2, max_length=150)
    so_dien_thoai: str | None = Field(default=None, max_length=20)
    gioi_tinh: int | None = Field(default=None, ge=1, le=3)
    ngay_sinh: date | None = None
    dan_toc: str | None = Field(default=None, max_length=150)
    ton_giao: str | None = Field(default=None, max_length=150)
    tinh_thanh_id: int | None = Field(default=None, ge=1)
    trinh_do_hoc_van: TrinhDoHocVan | None = None
    suc_khoe_the_chat: SucKhoeTheChat | None = None
    kha_nang_tai_chinh: KhaNangTaiChinh | None = None

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
        cleaned = _blank(value)
        if cleaned is None:
            return None
        if not _PHONE.fullmatch(cleaned):
            raise ValueError("Số điện thoại không hợp lệ")
        return cleaned

    @field_validator("dan_toc", "ton_giao")
    @classmethod
    def strip_catalog_text(cls, value: str | None) -> str | None:
        return _blank(value)

    @field_validator("ngay_sinh")
    @classmethod
    def check_ngay_sinh(cls, value: date | None) -> date | None:
        if value is None:
            return None
        today = date.today()
        if value > today:
            raise ValueError("Ngày sinh không được ở tương lai")
        if value.year < 1900:
            raise ValueError("Ngày sinh không hợp lệ")
        return value


class HoSoPublic(HoSoWrite):
    email: EmailStr
