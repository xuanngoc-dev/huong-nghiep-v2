from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

MUC_DO_AP_LUC_HOC_TAP = ("thap", "trung_binh", "cao")
MUC_DO_TU_GIAC = ("trung_binh", "cao", "rat_cao")
LOAI_UU_NHUOC_DIEM = ("uu_diem", "nhuoc_diem")
DOI_TUONG_NHAN_LUU_Y = ("hoc_sinh", "phu_huynh", "ca_hai")


def _fk_huong_di(ten_fk: str, **kwargs):
    return mapped_column(
        Integer,
        ForeignKey("dm_thcs_huong_di.id", name=ten_fk, ondelete="CASCADE"),
        nullable=False,
        **kwargs,
    )


class DmThcsHuongDi(Base):
    """Danh mục hướng đi cho học sinh sau THCS."""

    __tablename__ = "dm_thcs_huong_di"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_huong: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_huong: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_tong_quan: Mapped[str] = mapped_column(Text, nullable=False)
    doi_tuong_phu_hop: Mapped[str | None] = mapped_column(Text)
    chi_phi_du_kien_text: Mapped[str | None] = mapped_column(String(255))
    chi_phi_thang_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    chi_phi_thang_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    muc_do_ap_luc_hoc_tap: Mapped[str | None] = mapped_column(
        Enum(*MUC_DO_AP_LUC_HOC_TAP, name="muc_do_ap_luc_hoc_tap"),
        default="trung_binh",
        server_default="trung_binh",
    )
    muc_do_tu_giac_can_thiet: Mapped[str | None] = mapped_column(
        Enum(*MUC_DO_TU_GIAC, name="muc_do_tu_giac_can_thiet"), default="cao", server_default="cao"
    )
    tinh_linh_hoat_sau_lop_12: Mapped[str | None] = mapped_column(Text)
    ma_holland: Mapped[str | None] = mapped_column(String(20))
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(TINYINT(1), nullable=False, default=1, server_default="1")
    ngay_tao: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class DmThcsUuNhuocDiem(Base):
    """Ưu điểm / nhược điểm của một hướng đi sau THCS."""

    __tablename__ = "dm_thcs_uu_nhuoc_diem"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thcs_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tund_huong_di_id", index=True)
    loai: Mapped[str] = mapped_column(Enum(*LOAI_UU_NHUOC_DIEM, name="loai_uu_nhuoc_diem"), nullable=False)
    tieu_de: Mapped[str] = mapped_column(String(255), nullable=False)
    noi_dung_chi_tiet: Mapped[str] = mapped_column(Text, nullable=False)
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class DmThcsTieuChi(Base):
    """Tiêu chí đánh giá mức phù hợp của hướng đi sau THCS."""

    __tablename__ = "dm_thcs_tieu_chi"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_tieu_chi: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_tieu_chi: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta_tieu_chi: Mapped[str | None] = mapped_column(String(255))
    nhom_tieu_chi: Mapped[str | None] = mapped_column(String(100))
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")


class DmThcsHuongDiTieuChi(Base):
    """Mức độ phù hợp (1-5) giữa hướng đi sau THCS và tiêu chí."""

    __tablename__ = "dm_thcs_huong_di_tieu_chi"
    __table_args__ = (
        CheckConstraint("diem_phu_hop BETWEEN 1 AND 5", name="chk_dm_thcs_huong_di_tieu_chi_diem"),
        _BANG,
    )

    thcs_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_thdtc_huong_di_id", primary_key=True)
    thcs_tieu_chi_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("dm_thcs_tieu_chi.id", name="fk_dm_thdtc_tieu_chi_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    diem_phu_hop: Mapped[int] = mapped_column(TINYINT, nullable=False, default=3, server_default="3")
    nhan_dinh_tu_van: Mapped[str | None] = mapped_column(String(255))


class DmThcsLoiKhuyenLuuY(Base):
    """Lời khuyên, lưu ý cho học sinh / phụ huynh theo hướng đi sau THCS."""

    __tablename__ = "dm_thcs_loi_khuyen_luu_y"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thcs_huong_di_id: Mapped[int] = _fk_huong_di("fk_dm_tlkly_huong_di_id", index=True)
    doi_tuong_nhan: Mapped[str | None] = mapped_column(
        Enum(*DOI_TUONG_NHAN_LUU_Y, name="doi_tuong_nhan_luu_y"), default="ca_hai", server_default="ca_hai"
    )
    noi_dung_luu_y: Mapped[str] = mapped_column(Text, nullable=False)
    thu_tu_hien_thi: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
