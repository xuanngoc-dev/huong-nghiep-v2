from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

MA_TIEU_CHI = ("KHA_NANG_TRUNG_TUYEN", "NGANH", "HOC_PHI", "VI_TRI")


class XtBoTieuChi(Base):
    """Bộ tiêu chí chấm điểm mức độ phù hợp (có thể có nhiều phiên bản, một bộ mặc định)."""

    __tablename__ = "xt_bo_tieu_chi"
    __table_args__ = (UniqueConstraint("ma_bo", name="uk_xt_bo_tieu_chi_ma_bo"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ma_bo: Mapped[str] = mapped_column(String(50), nullable=False)
    ten_bo: Mapped[str] = mapped_column(String(255), nullable=False)
    mac_dinh: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    ghi_chu: Mapped[str | None] = mapped_column(Text)


class XtTieuChiPhuHop(Base):
    """Trọng số từng tiêu chí; tiêu chí thiếu dữ liệu bị loại khỏi mẫu số."""

    __tablename__ = "xt_tieu_chi_phu_hop"
    __table_args__ = (UniqueConstraint("bo_tieu_chi_id", "ma_tieu_chi", name="uk_xt_tieu_chi_phu_hop"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    bo_tieu_chi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_bo_tieu_chi.id", name="fk_xt_tcph_bo_tieu_chi_id", ondelete="CASCADE"),
        nullable=False,
    )
    ma_tieu_chi: Mapped[str] = mapped_column(Enum(*MA_TIEU_CHI, name="ma_tieu_chi"), nullable=False)
    trong_so: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(String(500))


class XtMucPhuHop(Base):
    """Mốc quy đổi: KHA_NANG_TRUNG_TUYEN quy chênh lệch điểm (thang 30) thành điểm 0-100; TONG_HOP xếp loại."""

    __tablename__ = "xt_muc_phu_hop"
    __table_args__ = (Index("idx_xt_muc_phu_hop", "bo_tieu_chi_id", "loai_muc"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    bo_tieu_chi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_bo_tieu_chi.id", name="fk_xt_mph_bo_tieu_chi_id", ondelete="CASCADE"),
        nullable=False,
    )
    loai_muc: Mapped[str] = mapped_column(Enum("KHA_NANG_TRUNG_TUYEN", "TONG_HOP", name="loai_muc"), nullable=False)
    # Cận dưới (>=), NULL = âm vô cùng; cận trên (<), NULL = dương vô cùng.
    gia_tri_tu: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    gia_tri_den: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    diem: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    nhan: Mapped[str] = mapped_column(String(50), nullable=False)
