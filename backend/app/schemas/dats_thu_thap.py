from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, StringConstraints, field_validator, model_validator

TrangThaiThuThap = Literal["thu_thap", "cho_duyet", "yeu_cau_bo_sung", "da_duyet_va_nhap"]
LuaChonNguon = Literal["chua_chon", "su_dung", "loai"]
TinhTrangNguon = Literal["chua_tim_nguon", "chua_co_nguon_phu_hop", "cho_chon_nguon", "san_sang_tao_nhap"]
MaTruong = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=20)]
DuongDan = Annotated[str, StringConstraints(min_length=2, max_length=1000, pattern=r"^/")]
VanBan = Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)]


class PhienThuThapCreate(BaseModel):
    ma_truong: MaTruong
    nam_tuyen_sinh: int = Field(ge=1990, le=2100)


class ThemNguon(BaseModel):
    url: Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=2000)]


class ChonNguon(BaseModel):
    lua_chon: LuaChonNguon
    ly_do: VanBan = ""


class ChonTatCaNguon(BaseModel):
    lua_chon: Literal["su_dung"]


class PhienBanRequest(BaseModel):
    phien_ban: int = Field(ge=1)


class DungTaoBanNhap(BaseModel):
    luot_tao_ban_nhap: int = Field(ge=1, strict=True)


class DanChungMoi(BaseModel):
    nguon_id: int = Field(ge=1)
    vi_tri: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=400)]
    trich_dan: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    gia_tri: JsonValue


class SuaMucBanNhap(BaseModel):
    duong_dan: DuongDan
    gia_tri: JsonValue = None
    dan_chung_ids: list[str] = Field(default_factory=list, max_length=50)
    dan_chung_moi: list[DanChungMoi] = Field(default_factory=list, max_length=20)
    ghi_chu: VanBan = ""
    da_kiem_tra: bool = False


class CanCuDoiChieu(BaseModel):
    nguon_id: int = Field(ge=1)
    ly_do: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class XacNhanDoiChieu(BaseModel):
    chuong_trinh: CanCuDoiChieu | None = None
    chi_tieu: CanCuDoiChieu | None = None


class SuaBanNhap(PhienBanRequest):
    thay_doi: list[SuaMucBanNhap] = Field(default_factory=list, max_length=500)
    xac_nhan_doi_chieu: XacNhanDoiChieu | None = None

    @model_validator(mode="after")
    def co_thay_doi(self):
        if not self.thay_doi and not (self.xac_nhan_doi_chieu and self.xac_nhan_doi_chieu.model_fields_set):
            raise ValueError("Cần chỉnh sửa bản nháp hoặc xác nhận đối chiếu.")
        return self


class BoSungBanNhap(PhienBanRequest):
    duong_dan: list[DuongDan] = Field(min_length=1, max_length=100)
    ly_do: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class NguonThuThap(BaseModel):
    id: int
    url: str
    tieu_de: str
    co_quan: str | None = None
    loai: str = "khac"
    nam_ap_dung: int | None = None
    ngay_cong_bo: str | None = None
    truy_cap_luc: str | None = None
    ngay_hieu_luc: str | None = None
    thay_the_url: str | None = None
    url_trang_cong_bo: str | None = None
    pham_vi_dieu_chinh: str | None = None
    phu_hop: bool = False
    chinh_thuc: bool = False
    chi_diem_lich_su: bool = False
    ly_do: str | None = None
    ly_do_loai: str | None = None
    lua_chon: LuaChonNguon = "chua_chon"


class DanChungThuThap(DanChungMoi):
    id: str
    url_tai_lieu: str | None = None


class MucBanNhap(BaseModel):
    duong_dan: str
    gia_tri_ai: JsonValue
    dan_chung: list[DanChungThuThap]
    dan_chung_ids: list[str]
    ghi_chu: str
    da_kiem_tra: bool
    mau_thuan: bool


class TomTatPhienBan(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phien_ban: int
    tao_luc: datetime
    ten_nguoi_tao: str


class DoiChieuBanNhapPublic(BaseModel):
    nguon: list[dict] = Field(default_factory=list)
    xac_nhan: XacNhanDoiChieu = Field(default_factory=XacNhanDoiChieu)
    can_xac_nhan: dict[str, str] = Field(default_factory=dict)


class BanNhapThuThapPublic(TomTatPhienBan):
    du_lieu: dict
    muc: list[MucBanNhap]
    nguon: list[NguonThuThap]
    ghi_chu: list[str]
    loi: list[str]
    doi_chieu: DoiChieuBanNhapPublic


class NhatKyThuThapPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hanh_dong: str
    phien_ban: int | None
    nguoi_dung: str
    tao_luc: datetime
    chi_tiet: dict


class YeuCauBoSungPublic(BaseModel):
    duong_dan: list[str]
    ly_do: str


class TruongThuThapPublic(BaseModel):
    ma_truong: str
    ten_truong: str
    co_so: str | None
    website: str | None
    website_tuyen_sinh: str | None


class LoiTaoBanNhapPublic(BaseModel):
    message: str
    loi: list[str] = Field(default_factory=list)
    nguon_ids: list[int] = Field(default_factory=list)
    xay_ra_luc: datetime


class TienDoTaoBanNhap(BaseModel):
    buoc: str
    da_xu_ly: int | None = None
    tong: int | None = None


class PhienThuThapPublic(BaseModel):
    id: int
    ma_truong: str
    ten_truong: str
    co_so: str | None
    nam_tuyen_sinh: int
    trang_thai: TrangThaiThuThap
    tinh_trang_nguon: TinhTrangNguon
    dang_tao_ban_nhap: bool = False
    luot_tao_ban_nhap: int | None = None
    bat_dau_tao_ban_nhap_luc: datetime | None = None
    tien_do_tao_ban_nhap: TienDoTaoBanNhap | None = None
    loi_tao_ban_nhap: LoiTaoBanNhapPublic | None = None
    tao_boi: int | None
    ten_nguoi_tao: str | None
    tao_luc: datetime
    cap_nhat_luc: datetime
    phien_ban: int | None
    de_an_id: int | None
    duyet_boi: int | None
    ten_nguoi_duyet: str | None
    duyet_luc: datetime | None


class PhienThuThapDetail(PhienThuThapPublic):
    nguon: list[NguonThuThap]
    canh_bao_nguon: list[str]
    ban_nhap: BanNhapThuThapPublic | None
    lich_su: list[NhatKyThuThapPublic]
    yeu_cau_bo_sung: YeuCauBoSungPublic | None
    cac_phien_ban: list[TomTatPhienBan]


class PhienThuThapPage(BaseModel):
    items: list[PhienThuThapPublic]
    total: int
    page: int
    page_size: int


class PhienThuThapDeleteResult(BaseModel):
    deleted: int


class PhienDuyetHangLoat(PhienBanRequest):
    id: int = Field(ge=1)


class DuyetHangLoatRequest(BaseModel):
    phien: list[PhienDuyetHangLoat] = Field(min_length=1, max_length=200)

    @field_validator("phien")
    @classmethod
    def ma_phien_duy_nhat(cls, phien: list[PhienDuyetHangLoat]) -> list[PhienDuyetHangLoat]:
        if len({item.id for item in phien}) != len(phien):
            raise ValueError("Mỗi phiên chỉ được xuất hiện một lần trong danh sách duyệt.")
        return phien


class PhienDaDuyetHangLoat(PhienDuyetHangLoat):
    de_an_id: int


class PhienDuyetThatBai(PhienDuyetHangLoat):
    status: int
    detail: str | dict


class DuyetHangLoatResult(BaseModel):
    da_duyet: list[PhienDaDuyetHangLoat] = Field(default_factory=list)
    that_bai: list[PhienDuyetThatBai] = Field(default_factory=list)
