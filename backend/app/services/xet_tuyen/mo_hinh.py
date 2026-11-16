"""Dữ liệu vào / ra của bộ tính xét tuyển (bước 3.1). Thuần dữ liệu, không phụ thuộc CSDL.

Quy tắc (`QuyTacXetTuyen`) được nạp từ các bảng xt_* (bước 3.5) hoặc từ dữ liệu mẫu trong test; hồ sơ
(`HoSoXetTuyen`) dựng từ hồ sơ học sinh (bước 3.3). Mã (môn, tổ hợp, bài thi, chứng chỉ, khu vực...) là mã danh mục.
"""

from dataclasses import dataclass, field


@dataclass
class CongThucTinh:
    id: int
    ma: str
    de_an_id: int
    ma_phuong_thuc: str
    kieu: str  # TO_HOP_MON / THANH_PHAN / CHI_DIEU_KIEN / THU_CONG
    thang: float
    nguon: str | None = None  # THI_THPT / HOC_BA
    he_so_nhan: float = 1.0
    bang_ngoai_ngu_id: int | None = None
    thay_ngoai_ngu: str = "KHONG"
    ap_dung_diem_cong: bool = True
    ap_dung_uu_tien: bool = True
    tran_diem_cong: float = 0.1
    so_le: int = 2
    diem_san: float | None = None
    nguong_tb_mon: float | None = None
    nguong_thpt_to_hop: float | None = None
    trang_thai: bool = True


@dataclass
class ChuongTrinhTinh:
    id: int
    de_an_id: int
    nam: int
    ma_truong: str
    ma_xet_tuyen: str | None
    ma_tinh: str | None = None
    vung: str | None = None
    hoc_phi_tu: float | None = None


@dataclass
class HeSoMonTinh:
    cong_thuc_id: int
    he_so: float
    ma_mon: str | None = None
    nhom_mon: str | None = None


@dataclass
class ThanhPhanTinh:
    id: int
    cong_thuc_id: int
    vi_tri: int
    loai: str  # BAI_THI / CHUNG_CHI
    ten: str | None = None
    ma_bai_thi: str | None = None
    bang_id: int | None = None
    ma_mon: str | None = None
    he_so: float = 1.0
    nam_tu: int | None = None
    nam_den: int | None = None
    phan_tu_chon: str | None = None


@dataclass
class MucQuyDoiTinh:
    bang_id: int
    quy_doi: float
    ma_chung_chi: str | None = None
    ma_bai_thi: str | None = None
    ma_mon: str | None = None
    cap_do: str | None = None
    tu: float | None = None
    den: float | None = None
    he_so_noi_suy: float = 0.0
    dat_nguong: bool = True


@dataclass
class PhuongAnTinh:
    id: int
    chuong_trinh_id: int
    cong_thuc_id: int
    ma_to_hop: str | None = None


@dataclass
class NhomDieuKienTinh:
    id: int
    de_an_id: int
    ten: str
    cong_thuc_id: int | None = None
    chuong_trinh_id: int | None = None


@dataclass
class DieuKienTinh:
    nhom_id: int
    chi_so: str
    toan_tu: str
    gia_tri: float
    khoa: str = ""


@dataclass
class DiemCongTinh:
    de_an_id: int
    nhom: str
    chi_so: str
    toan_tu: str
    gia_tri: float
    diem: float
    khoa: str = ""
    cong_thuc_id: int | None = None


@dataclass
class MucPhuHopTinh:
    loai: str  # KHA_NANG_TRUNG_TUYEN / TONG_HOP
    nhan: str
    tu: float | None = None
    den: float | None = None
    diem: float | None = None


@dataclass
class DiemChuanTinh:
    ma_truong: str
    ma_xet_tuyen: str
    nam: int
    diem: float | None
    thang: float | None
    ma_phuong_thuc: str | None = None
    ma_to_hop: str | None = None


@dataclass
class MonTinh:
    ten: str
    nhom: str | None = None


@dataclass
class QuyTacXetTuyen:
    """Toàn bộ quy tắc của các đề án cần tính, cùng danh mục và tham số chấm điểm."""

    cong_thuc: list[CongThucTinh] = field(default_factory=list)
    chuong_trinh: list[ChuongTrinhTinh] = field(default_factory=list)
    he_so_mon: list[HeSoMonTinh] = field(default_factory=list)
    thanh_phan: list[ThanhPhanTinh] = field(default_factory=list)
    quy_doi: list[MucQuyDoiTinh] = field(default_factory=list)
    phuong_an: list[PhuongAnTinh] = field(default_factory=list)
    nhom_dieu_kien: list[NhomDieuKienTinh] = field(default_factory=list)
    dieu_kien: list[DieuKienTinh] = field(default_factory=list)
    diem_cong: list[DiemCongTinh] = field(default_factory=list)
    # Mã tổ hợp → danh sách vị trí, mỗi vị trí là các mã môn thay thế nhau.
    to_hop: dict[str, list[list[str]]] = field(default_factory=dict)
    mon: dict[str, MonTinh] = field(default_factory=dict)
    # Mã khu vực / đối tượng ưu tiên → điểm cộng (thang 30).
    khu_vuc: dict[str, float] = field(default_factory=dict)
    doi_tuong: dict[str, float] = field(default_factory=dict)
    trong_so: dict[str, float] = field(default_factory=dict)
    muc_phu_hop: list[MucPhuHopTinh] = field(default_factory=list)


@dataclass
class KetQuaNamHocTinh:
    tbc: float | None = None
    hoc_luc: int | None = None
    ren_luyen: int | None = None


@dataclass
class BaiThiTinh:
    ma: str
    diem: float | None
    nam: int | None = None
    phan_tu_chon: str | None = None


@dataclass
class ChungChiTinh:
    ma: str
    diem: float | None = None
    cap_do: str | None = None
    het_han: str | None = None  # YYYY-MM-DD; None = không hết hạn


@dataclass
class ThanhTichTinh:
    ma: str
    muc_giai: int


@dataclass
class HoSoXetTuyen:
    nam_tot_nghiep: int | None = None
    da_tot_nghiep: bool = False
    he_chuyen: bool = False
    mon_chuyen: str | None = None
    khu_vuc: str | None = None
    doi_tuong: str | None = None
    ngan_sach: float | None = None
    mong_muon_tinh: list[str] = field(default_factory=list)
    mong_muon_vung: list[str] = field(default_factory=list)
    nam_hoc: dict[int, KetQuaNamHocTinh] = field(default_factory=dict)
    diem_thpt: dict[str, float] = field(default_factory=dict)
    # Mã môn → {lớp: điểm trung bình cả năm}.
    hoc_ba: dict[str, dict[int, float]] = field(default_factory=dict)
    bai_thi: list[BaiThiTinh] = field(default_factory=list)
    chung_chi: list[ChungChiTinh] = field(default_factory=list)
    thanh_tich: list[ThanhTichTinh] = field(default_factory=list)


@dataclass
class KetQuaPhuongAn:
    phuong_an_id: int
    chuong_trinh_id: int
    cong_thuc_id: int
    ma_to_hop: str | None
    kieu: str
    thang: float
    diem_goc: float | None = None
    tb_mon: float | None = None
    tong_thpt: float | None = None
    diem_cong: float = 0.0
    diem_uu_tien: float = 0.0
    diem_xet: float | None = None
    dat_nguong: bool | None = None
    du_dieu_kien: bool = False
    ly_do: str = ""
    so_nhom: int = 0
    so_nhom_dat: int = 0
    diem_chuan: float | None = None
    nam_diem_chuan: int | None = None
    thang_diem_chuan: float | None = None
    chenh_lech_30: float | None = None
    chi_tiet: str = ""


@dataclass
class KetQuaTinh:
    chi_so: dict[tuple[str, str], float]
    phuong_an: list[KetQuaPhuongAn]
    muc_uu_tien: float


@dataclass
class DongXepHang:
    thu_hang: int
    chuong_trinh_id: int
    ma_truong: str
    phuong_an: KetQuaPhuongAn
    la_xet_thang: bool
    diem_kha_nang: float | None
    nhan_kha_nang: str | None
    diem_hoc_phi: float | None
    diem_vi_tri: float | None
    diem_phu_hop: float | None
    xep_loai: str


@dataclass
class KetQuaTruong:
    ma_truong: str
    so_chuong_trinh: int
    so_da_cham: int
    so_phu_hop: int
    diem_cao_nhat: float | None
    diem_truong: float | None
    hang_tot_nhat: int
