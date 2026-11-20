from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

LOAI_HINH_DU_HOC = ("du_hoc_nghe", "du_hoc_hoc_thuat", "chuyen_tiep")
LOAI_CHI_PHI = ("truoc_khi_bay", "tai_nuoc_so_tai", "chung_minh_tai_chinh", "khoan_bu_dap")
LOAI_KENH = ("chinh_thong", "trung_tam_tu_van", "cong_dong", "ho_tro_he_thong")


def _fk_huong_di(ten_fk: str):
    return mapped_column(
        Integer,
        ForeignKey("dm_thpt_duhoc_huong_di.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


def _fk_quoc_gia(ten_fk: str):
    # NULL: áp dụng chung cho cả hướng đi, không riêng quốc gia nào.
    return mapped_column(
        Integer,
        ForeignKey("dm_thpt_duhoc_quoc_gia.id", name=ten_fk, ondelete="CASCADE"),
        nullable=True,
        index=True,
    )


class DmThptDuhocHuongDi(Base):
    """Danh mục hướng đi du học cho học sinh sau THPT (du học nghề, học thuật, chuyển tiếp)."""

    __tablename__ = "dm_thpt_duhoc_huong_di"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_huong: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_huong: Mapped[str] = mapped_column(String(255), nullable=False)
    loai_hinh: Mapped[str] = mapped_column(Enum(*LOAI_HINH_DU_HOC, name="loai_hinh_du_hoc"), nullable=False)
    mo_ta_dac_diem: Mapped[str] = mapped_column(Text, nullable=False)
    yeu_cau_ngoai_ngu: Mapped[str | None] = mapped_column(String(255))
    thoi_gian_chuan_bi_text: Mapped[str | None] = mapped_column(String(100))
    thoi_gian_chuan_bi_thang_min: Mapped[int | None] = mapped_column(Integer, default=0, server_default="0")
    thoi_gian_chuan_bi_thang_max: Mapped[int | None] = mapped_column(Integer, default=0, server_default="0")
    chi_phi_du_kien_text: Mapped[str | None] = mapped_column(String(255))
    co_hoi_lam_them: Mapped[str | None] = mapped_column(Text)
    lo_trinh_visa_dinh_cu: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(TINYINT, nullable=False, default=1, server_default="1")
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DmThptDuhocQuocGia(Base):
    """Quốc gia thuộc một hướng đi du học."""

    __tablename__ = "dm_thpt_duhoc_quoc_gia"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_duhoc_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tdqg_huong_di_id")
    # Mã ISO 3166-1 alpha-2, ví dụ "DE", "JP".
    ma_quoc_gia: Mapped[str] = mapped_column(String(20), nullable=False)
    ten_quoc_gia: Mapped[str] = mapped_column(String(100), nullable=False)
    dac_diem_noi_bat: Mapped[str | None] = mapped_column(Text)
    yeu_cau_ngoai_ngu_rieng: Mapped[str | None] = mapped_column(String(255))
    co_hoi_viec_lam_visa: Mapped[str | None] = mapped_column(Text)
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class DmThptDuhocNganh(Base):
    """Ngành học gợi ý theo hướng đi (và quốc gia nếu có)."""

    __tablename__ = "dm_thpt_duhoc_nganh"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_duhoc_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tdn_huong_di_id")
    thpt_duhoc_quoc_gia_id: Mapped[int | None] = _fk_quoc_gia("fk_dm_tdn_quoc_gia_id")
    ten_nganh: Mapped[str] = mapped_column(String(255), nullable=False)
    nhu_cau_nhan_luc: Mapped[str | None] = mapped_column(String(255))
    muc_luong_tham_khao: Mapped[str | None] = mapped_column(String(255))
    ghi_chu: Mapped[str | None] = mapped_column(Text)


class DmThptDuhocChiPhi(Base):
    """Khoản chi phí du học theo hướng đi (và quốc gia nếu có)."""

    __tablename__ = "dm_thpt_duhoc_chi_phi"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_duhoc_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tdcp_huong_di_id")
    thpt_duhoc_quoc_gia_id: Mapped[int | None] = _fk_quoc_gia("fk_dm_tdcp_quoc_gia_id")
    loai_chi_phi: Mapped[str] = mapped_column(Enum(*LOAI_CHI_PHI, name="loai_chi_phi"), nullable=False)
    ten_khoan_chi: Mapped[str] = mapped_column(String(255), nullable=False)
    # Tính theo don_vi_tien.
    chi_phi_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    chi_phi_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    don_vi_tien: Mapped[str] = mapped_column(String(20), nullable=False, default="VND", server_default="VND")
    chi_phi_quy_doi_vnd_text: Mapped[str | None] = mapped_column(String(255))
    ghi_chu: Mapped[str | None] = mapped_column(String(255))


class DmThptDuhocThuTuc(Base):
    """Các bước thủ tục du học theo hướng đi (và quốc gia nếu có)."""

    __tablename__ = "dm_thpt_duhoc_thu_tuc"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_duhoc_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tdtt_huong_di_id")
    thpt_duhoc_quoc_gia_id: Mapped[int | None] = _fk_quoc_gia("fk_dm_tdtt_quoc_gia_id")
    buoc_so: Mapped[int] = mapped_column(TINYINT, nullable=False)
    ten_buoc: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_thu_tuc: Mapped[str] = mapped_column(Text, nullable=False)
    giay_to_can_co: Mapped[str | None] = mapped_column(Text)
    thoi_gian_du_kien: Mapped[str | None] = mapped_column(String(100))


class DmThptDuhocKenhKetNoi(Base):
    """Kênh kết nối, hỗ trợ du học theo hướng đi (và quốc gia nếu có)."""

    __tablename__ = "dm_thpt_duhoc_kenh_ket_noi"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thpt_duhoc_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tdkkn_huong_di_id")
    thpt_duhoc_quoc_gia_id: Mapped[int | None] = _fk_quoc_gia("fk_dm_tdkkn_quoc_gia_id")
    loai_kenh: Mapped[str] = mapped_column(Enum(*LOAI_KENH, name="loai_kenh"), nullable=False)
    ten_kenh: Mapped[str] = mapped_column(String(255), nullable=False)
    thong_tin_lien_he: Mapped[str | None] = mapped_column(String(255))
    mo_ta_ho_tro: Mapped[str | None] = mapped_column(Text)
    luu_y_khi_ket_noi: Mapped[str | None] = mapped_column(String(255))
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
