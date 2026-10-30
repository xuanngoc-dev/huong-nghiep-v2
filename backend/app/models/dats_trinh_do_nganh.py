from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsTrinhDoNganh(Base):
    """Trình độ và hình thức đào tạo gắn với chương trình."""

    __tablename__ = "dats_trinh_do_nganh"
    __table_args__ = (
        Index("idx_dats_trinh_do_nganh_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Trình độ và hình thức đào tạo gắn với chương trình",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính.",
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_trinh_do_nganh_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Chương trình thuộc đề án.",
    )
    trinh_do_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Trình độ.",
    )
    hinh_thuc_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Hình thức.",
    )
    thoi_gian_dao_tao_nam: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1),
        comment="Thời lượng chương trình.",
    )
    ma_nganh_chuan: Mapped[str | None] = mapped_column(
        String(20),
        comment="Mã ngành chuẩn tại thời điểm đề án.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin bổ sung.",
    )
