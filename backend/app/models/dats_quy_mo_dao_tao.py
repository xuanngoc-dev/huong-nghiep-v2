from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsQuyMoDaoTao(Base):
    """Quy mô người học theo năm, trình độ và hình thức đào tạo."""

    __tablename__ = "dats_quy_mo_dao_tao"
    __table_args__ = (
        Index("idx_dats_quy_mo_dao_tao_de_an_id", "de_an_id"),
        Index("idx_dats_quy_mo_dao_tao_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Quy mô người học theo năm, trình độ và hình thức đào tạo",
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
            name="fk_dats_quy_mo_dao_tao_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    de_an_chuong_trinh_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_quy_mo_dao_tao_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình cụ thể; NULL nếu toàn trường.",
    )
    trinh_do_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Trình độ đào tạo.",
    )
    hinh_thuc_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Hình thức đào tạo.",
    )
    nam_thong_ke: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm thống kê.",
    )
    so_luong_nguoi_hoc: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Quy mô người học.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Phạm vi/cách thống kê.",
    )
