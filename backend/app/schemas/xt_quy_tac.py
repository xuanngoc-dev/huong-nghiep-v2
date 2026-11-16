from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.hs_ho_so import HoSoXetTuyenWrite


class XtImportRequest(BaseModel):
    du_lieu: dict[str, Any]
    ten_file: str | None = Field(default=None, max_length=255)


class XtTrangThaiWrite(BaseModel):
    """0 chưa chuẩn hóa, 1 thử nghiệm, 2 đang áp dụng (kết quả tìm trường của người dùng dùng bộ tính mới)."""

    trang_thai_xet_tuyen: Literal[0, 1, 2]


class XtTrangThaiResult(BaseModel):
    de_an_id: int
    trang_thai_xet_tuyen: int


class XtImportResult(BaseModel):
    de_an_id: int
    lich_su_id: int | None = None
    so_dong: dict[str, int]
    canh_bao: list[str]
    quy_dinh_chua_mo_hinh_hoa: list[dict[str, Any]]


class XtHeSoMonPublic(BaseModel):
    ma_mon: str | None = None
    nhom_mon: str | None = None
    he_so: float


class XtThanhPhanPublic(BaseModel):
    vi_tri: int
    ten_thanh_phan: str | None = None
    loai_nguon: str
    ma_bai_thi: str | None = None
    ma_bang: str | None = None
    ma_mon: str | None = None
    he_so: float


class XtCongThucPublic(BaseModel):
    id: int
    ma_cong_thuc: str
    ten_cong_thuc: str
    ma_phuong_thuc_cua_bo: str
    kieu_tinh: str
    nguon_diem_mon: str | None = None
    thay_ngoai_ngu: str
    thang_diem: float
    he_so_nhan: float
    diem_san: float | None = None
    trang_thai: bool
    mo_ta_cong_thuc: str | None = None
    so_phuong_an: int
    he_so_mon: list[XtHeSoMonPublic]
    thanh_phan: list[XtThanhPhanPublic]


class XtPhuongAnNhomPublic(BaseModel):
    """Phương án của một chương trình theo một công thức; to_hop rỗng = công thức không theo tổ hợp."""

    ma_cong_thuc: str
    to_hop: list[str]


class XtChuongTrinhPublic(BaseModel):
    id: int
    ma_xet_tuyen: str | None = None
    ten_chuong_trinh: str
    phuong_an: list[XtPhuongAnNhomPublic]


class XtDieuKienPublic(BaseModel):
    ma_chi_so: str
    khoa: str
    toan_tu: str
    gia_tri_so: float
    mo_ta: str | None = None


class XtNhomDieuKienPublic(BaseModel):
    id: int
    ma_nhom: str
    ten_nhom: str
    mo_ta: str | None = None
    bat_buoc: bool
    ma_cong_thuc: str | None = None
    ma_xet_tuyen: str | None = None
    dieu_kien: list[XtDieuKienPublic]


class XtDiemCongPublic(BaseModel):
    id: int
    ma_cong_thuc: str | None = None
    loai_diem_cong: str
    nhom_cong: str
    ma_chi_so: str
    khoa: str
    toan_tu: str
    gia_tri_so: float
    diem_cong: float
    mo_ta: str | None = None


class XtBangQuyDoiPublic(BaseModel):
    id: int
    ma_bang: str
    ten_bang: str
    thang_diem_dich: float
    so_muc: int


class XtLichSuImportPublic(BaseModel):
    id: int
    ten_file: str | None = None
    phien_ban_chuan: str | None = None
    so_dong: dict[str, int] | None = None
    quy_dinh_chua_mo_hinh_hoa: list[dict[str, Any]] | None = None
    nguoi_import: str | None = None
    tao_luc: datetime


class XtQuyTacDeAn(BaseModel):
    """Toàn bộ quy tắc xét tuyển của một đề án (chỉ đọc). Chưa import thì các danh sách rỗng."""

    de_an_id: int
    trang_thai_xet_tuyen: int
    cong_thuc: list[XtCongThucPublic]
    chuong_trinh: list[XtChuongTrinhPublic]
    nhom_dieu_kien: list[XtNhomDieuKienPublic]
    diem_cong: list[XtDiemCongPublic]
    bang_quy_doi: list[XtBangQuyDoiPublic]
    lich_su: list[XtLichSuImportPublic]


class XtChayThuRequest(BaseModel):
    """Hồ sơ dạng hồ sơ xét tuyển (`PUT /ho-so-xet-tuyen/cua-toi`) và ngày tính (hạn chứng chỉ)."""

    ho_so: HoSoXetTuyenWrite
    hom_nay: date | None = None


class XtChayThuPhuongAn(BaseModel):
    ma_xet_tuyen: str | None = None
    ten_chuong_trinh: str
    ma_cong_thuc: str
    ma_to_hop: str | None = None
    diem_goc: float | None = None
    diem_cong: float = 0
    diem_uu_tien: float = 0
    diem_xet: float | None = None
    du_dieu_kien: bool
    ly_do: str = ""
    chenh_lech_30: float | None = None


class XtChayThuXepHang(BaseModel):
    ma_xet_tuyen: str | None = None
    ten_chuong_trinh: str
    ma_cong_thuc: str
    ma_to_hop: str | None = None
    diem_phu_hop: float | None = None
    xep_loai: str


class XtChayThuKetQua(BaseModel):
    """Cùng dạng file ket_qua/<ten>.json của bộ test hồi quy."""

    so_phuong_an: int
    so_chuong_trinh: int
    phuong_an: list[XtChayThuPhuongAn]
    xep_hang: list[XtChayThuXepHang]


class XtChayThuResult(BaseModel):
    de_an_id: int
    ma_truong: str
    nam_tuyen_sinh: int
    trang_thai_xet_tuyen: int
    hom_nay: date
    gia_dinh: list[str]
    # Hồ sơ đã chuyển sang dạng bộ tính: lưu thành ho_so/<ten>.json của bộ test hồi quy.
    ho_so_bo_tinh: dict[str, Any]
    ket_qua: XtChayThuKetQua
