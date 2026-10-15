from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.ho_so import KhaNangTaiChinh, SucKhoeTheChat, TrinhDoHocVan


class ModelChat(BaseModel):
    id: str
    ten: str
    nha_cung_cap: str
    phi: bool
    mo_ta: str
    san_sang: bool
    provider: str = "gemini"
    timeout_giay: int = 75


class TaiLieuItem(BaseModel):
    ten: str
    kich_thuoc: int
    cap_nhat: datetime


class TinNhan(BaseModel):
    vai_tro: Literal["user", "bot"]
    noi_dung: str = Field(min_length=1, max_length=16000)


class NguCanhChat(BaseModel):
    ma_truong: list[Annotated[str, Field(max_length=32)]] = Field(default_factory=list, max_length=50)
    nganh: list[Annotated[str, Field(max_length=500)]] = Field(default_factory=list, max_length=20)
    nam: int | None = Field(default=None, ge=1900, le=2200)
    nam_du_tuyen: int | None = Field(default=None, ge=1900, le=2200)
    diem: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    to_hop: list[Annotated[str, Field(pattern=r"^[A-Z]\d{2}$")]] = Field(default_factory=list, max_length=10)
    khu_vuc: str | None = Field(default=None, max_length=200)
    nguon_diem: str | None = Field(default=None, max_length=100)
    tom_tat: str = Field(default="", max_length=2000)


class KeHoachTraCuu(BaseModel):
    """Model-selected query parameters, not fixed admission recommendation rules."""
    ngu_canh: NguCanhChat = Field(default_factory=NguCanhChat)
    ma_truong: list[Annotated[str, Field(max_length=32)]] = Field(default_factory=list, max_length=50)
    nganh: list[Annotated[str, Field(max_length=500)]] = Field(default_factory=list, max_length=20)
    nam: list[int] = Field(default_factory=list, max_length=10)
    to_hop: list[Annotated[str, Field(pattern=r"^[A-Z]\d{2}$")]] = Field(default_factory=list, max_length=10)
    phuong_thuc: list[Annotated[str, Field(max_length=100)]] = Field(default_factory=list, max_length=10)
    thang_diem: float | None = Field(default=None, gt=0, le=100_000, allow_inf_nan=False)
    diem_tu: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    diem_den: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    diem_muc_tieu: float | None = Field(default=None, ge=0, le=100_000, allow_inf_nan=False)
    sap_xep: Literal["gan_diem", "diem_tang", "diem_giam", "giu_nguyen"] = "giu_nguyen"
    che_do: Literal["tong_quan", "chi_tiet"] = "tong_quan"
    thong_tin: list[Literal["diem", "to_hop", "chi_tieu", "hoc_phi", "dieu_kien", "phuong_thuc", "danh_sach"]] = Field(default_factory=list, max_length=7)
    can_lam_ro: str = Field(default="", max_length=1000)
    khong_can_tra_cuu: bool = False
    ly_do: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def validate_score_query(self):
        if (self.diem_tu is not None or self.diem_den is not None or self.diem_muc_tieu is not None or self.sap_xep != "giu_nguyen") and self.thang_diem is None:
            raise ValueError("So sánh điểm cần chỉ rõ thang điểm.")
        if self.diem_tu is not None and self.diem_den is not None and self.diem_tu > self.diem_den:
            raise ValueError("Khoảng điểm không hợp lệ.")
        if self.sap_xep == "gan_diem" and self.diem_muc_tieu is None:
            raise ValueError("Sắp xếp gần điểm cần chỉ rõ điểm mục tiêu.")
        return self


class HoSoChat(BaseModel):
    """Phần hồ sơ dùng để cá nhân hóa câu trả lời. Không gồm email, họ tên hay số điện thoại."""

    gioi_tinh: int | None = Field(default=None, ge=1, le=3)
    ngay_sinh: date | None = None
    dan_toc: str | None = Field(default=None, max_length=150)
    ton_giao: str | None = Field(default=None, max_length=150)
    tinh_thanh_id: int | None = Field(default=None, ge=1)
    khu_vuc_uu_tien_id: int | None = Field(default=None, ge=1)
    doi_tuong_uu_tien_id: int | None = Field(default=None, ge=1)
    trinh_do_hoc_van: TrinhDoHocVan | None = None
    suc_khoe_the_chat: SucKhoeTheChat | None = None
    kha_nang_tai_chinh: KhaNangTaiChinh | None = None


class HoiChatRequest(BaseModel):
    cau_hoi: str = Field(min_length=1, max_length=4000)
    model_id: str = Field(min_length=1, max_length=80)
    lich_su: list[TinNhan] = Field(default_factory=list, max_length=50)
    ngu_canh: NguCanhChat | None = None
    ho_so: HoSoChat | None = None

    @model_validator(mode="after")
    def check_history_budget(self):
        if not self.cau_hoi.strip():
            raise ValueError("Vui lòng nhập câu hỏi.")
        if sum(len(item.noi_dung) for item in self.lich_su) > 64000:
            raise ValueError("Lịch sử quá dài. Hãy bắt đầu hội thoại mới.")
        if self.ho_so is not None and len(self.ho_so.model_dump_json(exclude_none=True)) > 20000:
            raise ValueError("Hồ sơ gửi kèm quá dài.")
        return self


class NguonChat(BaseModel):
    id: int
    ten: str
    ma_truong: str = ""
    nam: int | None = None
    cap_nhat: datetime
    duong_dan: str
    url_goc: str | None = None


class HoiChatResponse(BaseModel):
    tra_loi: str
    model_id: str
    model_ten: str
    tai_lieu: list[str]
    nguon: list[NguonChat] = Field(default_factory=list)
    goi_y: list[str] = Field(default_factory=list)
    ghi_chu: list[str] = Field(default_factory=list)
    ngu_canh: NguCanhChat | None = None
