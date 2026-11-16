from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsHocPhi(Base):
    """Học phí dự kiến theo chương trình của đề án (VNĐ/năm)."""

    __tablename__ = "dats_hoc_phi"
    __table_args__ = (
        Index("idx_dats_hoc_phi_chuong_trinh", "de_an_chuong_trinh_id"),
        Index("idx_dats_hoc_phi_de_an_id", "de_an_id"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"},
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_dats_hoc_phi_de_an_id"), nullable=False
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("dats_chuong_trinh_dao_tao.id", name="fk_dats_hoc_phi_chuong_trinh_id"),
        nullable=False,
    )
    nam_hoc: Mapped[str | None] = mapped_column(String(20))
    hoc_phi_tu: Mapped[Decimal] = mapped_column(Numeric(15, 0), nullable=False)
    hoc_phi_den: Mapped[Decimal | None] = mapped_column(Numeric(15, 0))
    ghi_chu: Mapped[str | None] = mapped_column(Text)
