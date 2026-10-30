from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsTyLeViecLam(Base):
    """Tỷ lệ việc làm của người học sau tốt nghiệp."""

    __tablename__ = "dats_ty_le_viec_lam"
    __table_args__ = (
        Index("idx_dats_ty_le_viec_lam_de_an_id", "de_an_id"),
        Index("idx_dats_ty_le_viec_lam_nganh_dao_tao_id", "nganh_dao_tao_id"),
        CheckConstraint("ty_le_co_viec_lam IS NULL OR (ty_le_co_viec_lam BETWEEN 0 AND 100)", name="chk_dats_ty_le_viec_lam_ty_le_co_viec_lam"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Tỷ lệ việc làm của người học sau tốt nghiệp",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính.",
    )
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_tuyen_sinh.id",
            name="fk_dats_ty_le_viec_lam_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án công bố số liệu.",
    )
    nganh_dao_tao_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_nganh_dao_tao.id",
            name="fk_dats_ty_le_viec_lam_nganh_dao_tao_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Ngành thống kê; NULL nếu tổng hợp.",
    )
    trinh_do_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Trình độ khóa tốt nghiệp.",
    )
    nam_tot_nghiep: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm tốt nghiệp.",
    )
    thoi_diem_khao_sat_thang: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Số tháng sau tốt nghiệp khi khảo sát.",
    )
    so_nguoi_tot_nghiep: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Tổng số người tốt nghiệp trong mẫu/khóa.",
    )
    so_nguoi_co_viec_lam: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Số người có việc làm theo khảo sát.",
    )
    ty_le_co_viec_lam: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment="Tỷ lệ có việc làm theo %.",
    )
    phuong_phap_khao_sat: Mapped[str | None] = mapped_column(
        Text,
        comment="Cách thu thập kết quả.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="URL nguồn công bố.",
    )
