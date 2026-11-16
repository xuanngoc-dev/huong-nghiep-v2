from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class XtBangQuyDoi(Base):
    """Bảng quy đổi chứng chỉ / bài thi sang điểm xét, do đề án ban hành."""

    __tablename__ = "xt_bang_quy_doi"
    __table_args__ = (UniqueConstraint("de_an_id", "ma_bang", name="uk_xt_bang_quy_doi"), _BANG)

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_xt_bang_quy_doi_de_an_id"), nullable=False
    )
    ma_bang: Mapped[str] = mapped_column(String(50), nullable=False)
    ten_bang: Mapped[str] = mapped_column(String(255), nullable=False)
    thang_diem_dich: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    ghi_chu: Mapped[str | None] = mapped_column(Text)


class XtBangQuyDoiChiTiet(Base):
    """Một mức của bảng quy đổi (bậc thang hoặc nội suy tuyến tính)."""

    __tablename__ = "xt_bang_quy_doi_chi_tiet"
    __table_args__ = (
        Index("idx_xt_bang_quy_doi_chi_tiet_bang", "bang_quy_doi_id", "chung_chi_id"),
        Index("idx_xt_bang_quy_doi_chi_tiet_bai_thi", "bang_quy_doi_id", "bai_thi_id"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    bang_quy_doi_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("xt_bang_quy_doi.id", name="fk_xt_bqd_ct_bang_quy_doi_id", ondelete="CASCADE"),
        nullable=False,
    )
    chung_chi_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dm_bang_cap_chung_chi.id", name="fk_xt_bqd_ct_chung_chi_id")
    )
    bai_thi_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dm_bai_thi_danh_gia.id", name="fk_xt_bqd_ct_bai_thi_id")
    )
    mon_hoc_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dm_mon_hoc.id", name="fk_xt_bqd_ct_mon_hoc_id"))
    cap_do: Mapped[str | None] = mapped_column(String(30))
    diem_tu: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    diem_den: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    diem_quy_doi: Mapped[Decimal] = mapped_column(Numeric(7, 3), nullable=False)
    # Điểm quy đổi = diem_quy_doi + he_so_noi_suy * (điểm - diem_tu); 0 = bảng bậc thang.
    he_so_noi_suy: Mapped[Decimal] = mapped_column(Numeric(12, 8), nullable=False, default=0, server_default="0")
    # False: mức có trong bảng nhưng dưới ngưỡng bảo đảm chất lượng, không dùng để xét.
    dat_nguong: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
