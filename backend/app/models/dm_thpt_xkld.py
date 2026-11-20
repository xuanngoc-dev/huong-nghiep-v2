from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

YEU_CAU_GIOI_TINH = ("nam", "nu", "ca_hai")
LOAI_CHI_PHI_XKLD = ("phi_dich_vu_xuat_canh", "dao_tao_tieng_tay_nghe", "kham_suc_khoe_ho_so", "ky_quy_chong_tron")
LOAI_KENH_XKLD = ("co_quan_nha_nuoc", "doanh_nghiep_cap_phep", "trung_tam_lao_dong_ngoai_nuoc", "ho_tro_he_thong")


def _fk_nhom_nghe(ten_fk: str):
    return mapped_column(
        Integer,
        ForeignKey("dm_thpt_xkld_nhom_nghe.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


def _fk_thi_truong(ten_fk: str):
    # NULL: áp dụng chung cho cả nhóm nghề, không riêng thị trường nào.
    return mapped_column(
        Integer,
        ForeignKey("dm_thpt_xkld_thi_truong.id", name=ten_fk, ondelete="CASCADE"),
        nullable=True,
        index=True,
    )


class DmThptXkldNhomNghe(Base):
    """Danh mục nhóm nghề xuất khẩu lao động cho học sinh sau THPT."""

    __tablename__ = "dm_thpt_xkld_nhom_nghe"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_nhom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_nhom: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_cong_viec: Mapped[str] = mapped_column(Text, nullable=False)
    dieu_kien_suc_khoe_the_luc: Mapped[str | None] = mapped_column(Text)
    yeu_cau_ngoai_ngu: Mapped[str | None] = mapped_column(String(255))
    thoi_gian_chuan_bi_text: Mapped[str | None] = mapped_column(String(100))
    thoi_gian_chuan_bi_thang_min: Mapped[int | None] = mapped_column(Integer, default=0, server_default="0")
    thoi_gian_chuan_bi_thang_max: Mapped[int | None] = mapped_column(Integer, default=0, server_default="0")
    muc_thu_nhap_text: Mapped[str | None] = mapped_column(String(255))
    # DECIMAL(5,2) — tối đa 999.99, nên lưu theo đơn vị triệu VNĐ/tháng.
    thu_nhap_thang_min: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    thu_nhap_thang_max: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    trien_vong_sau_ve_nuoc: Mapped[str | None] = mapped_column(Text)
    kha_nang_gia_han_visa: Mapped[str | None] = mapped_column(String(255))
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(TINYINT, nullable=False, default=1, server_default="1")
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DmThptXkldThiTruong(Base):
    """Thị trường (quốc gia) tiếp nhận lao động thuộc một nhóm nghề."""

    __tablename__ = "dm_thpt_xkld_thi_truong"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_xkld_nhom_nghe_id: Mapped[int] = _fk_nhom_nghe("fk_dm_txtt_nhom_nghe_id")
    # Mã ISO 3166-1 alpha-2, ví dụ "JP", "KR".
    ma_quoc_gia: Mapped[str] = mapped_column(String(20), nullable=False)
    ten_quoc_gia: Mapped[str] = mapped_column(String(100), nullable=False)
    loai_visa: Mapped[str | None] = mapped_column(String(100))
    dac_diem_thi_truong: Mapped[str | None] = mapped_column(Text)
    thu_nhap_rieng_text: Mapped[str | None] = mapped_column(String(255))
    thoi_han_hop_dong_nam: Mapped[int | None] = mapped_column(Integer, default=3, server_default="3")
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class DmThptXkldNgheCuThe(Base):
    """Công việc cụ thể theo nhóm nghề (và thị trường nếu có)."""

    __tablename__ = "dm_thpt_xkld_nghe_cu_the"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_xkld_nhom_nghe_id: Mapped[int] = _fk_nhom_nghe("fk_dm_txnct_nhom_nghe_id")
    thpt_xkld_thi_truong_id: Mapped[int | None] = _fk_thi_truong("fk_dm_txnct_thi_truong_id")
    ten_cong_viec: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_ngan: Mapped[str | None] = mapped_column(Text)
    yeu_cau_gioi_tinh: Mapped[str | None] = mapped_column(
        Enum(*YEU_CAU_GIOI_TINH, name="yeu_cau_gioi_tinh"), default="ca_hai", server_default="ca_hai"
    )


class DmThptXkldChiPhi(Base):
    """Khoản chi phí xuất khẩu lao động theo nhóm nghề (và thị trường nếu có)."""

    __tablename__ = "dm_thpt_xkld_chi_phi"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_xkld_nhom_nghe_id: Mapped[int] = _fk_nhom_nghe("fk_dm_txcp_nhom_nghe_id")
    thpt_xkld_thi_truong_id: Mapped[int | None] = _fk_thi_truong("fk_dm_txcp_thi_truong_id")
    loai_chi_phi: Mapped[str] = mapped_column(Enum(*LOAI_CHI_PHI_XKLD, name="loai_chi_phi_xkld"), nullable=False)
    ten_khoan_chi: Mapped[str] = mapped_column(String(255), nullable=False)
    # Tính theo don_vi_tien.
    chi_phi_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    chi_phi_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    don_vi_tien: Mapped[str] = mapped_column(String(20), nullable=False, default="VND", server_default="VND")
    chi_phi_quy_doi_vnd_text: Mapped[str | None] = mapped_column(String(255))
    ghi_chu: Mapped[str | None] = mapped_column(String(255))


class DmThptXkldThuTuc(Base):
    """Các bước thủ tục xuất khẩu lao động theo nhóm nghề (và thị trường nếu có)."""

    __tablename__ = "dm_thpt_xkld_thu_tuc"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_xkld_nhom_nghe_id: Mapped[int] = _fk_nhom_nghe("fk_dm_txtht_nhom_nghe_id")
    thpt_xkld_thi_truong_id: Mapped[int | None] = _fk_thi_truong("fk_dm_txtht_thi_truong_id")
    buoc_so: Mapped[int] = mapped_column(TINYINT, nullable=False)
    ten_buoc: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_thu_tuc: Mapped[str] = mapped_column(Text, nullable=False)
    giay_to_can_co: Mapped[str | None] = mapped_column(Text)
    thoi_gian_du_kien: Mapped[str | None] = mapped_column(String(100))


class DmThptXkldKenhKetNoi(Base):
    """Kênh kết nối, hỗ trợ xuất khẩu lao động theo nhóm nghề (và thị trường nếu có)."""

    __tablename__ = "dm_thpt_xkld_kenh_ket_noi"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_xkld_nhom_nghe_id: Mapped[int] = _fk_nhom_nghe("fk_dm_txkkn_nhom_nghe_id")
    thpt_xkld_thi_truong_id: Mapped[int | None] = _fk_thi_truong("fk_dm_txkkn_thi_truong_id")
    loai_kenh: Mapped[str] = mapped_column(Enum(*LOAI_KENH_XKLD, name="loai_kenh_xkld"), nullable=False)
    ten_kenh: Mapped[str] = mapped_column(String(255), nullable=False)
    thong_tin_lien_he: Mapped[str | None] = mapped_column(String(255))
    mo_ta_ho_tro: Mapped[str | None] = mapped_column(Text)
    luu_y_tranh_rui_ro: Mapped[str | None] = mapped_column(String(255))
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
