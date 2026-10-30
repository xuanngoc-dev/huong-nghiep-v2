from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsTruSo(Base):
    """Trụ sở, cơ sở và phân hiệu của trường."""

    __tablename__ = "dats_tru_so"
    __table_args__ = (
        Index("idx_dats_tru_so_de_an_id", "de_an_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Trụ sở, cơ sở và phân hiệu của trường",
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
            name="fk_dats_tru_so_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    vai_tro: Mapped[str | None] = mapped_column(
        String(30),
        comment="Vai trò địa điểm: chính/phụ.",
    )
    ten_co_so: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên trụ sở/cơ sở/phân hiệu.",
    )
    loai_co_so: Mapped[str | None] = mapped_column(
        String(30),
        comment="Loại địa điểm.",
    )
    dia_chi: Mapped[str | None] = mapped_column(
        String(500),
        comment="Địa chỉ đầy đủ.",
    )
    so_dien_thoai: Mapped[str | None] = mapped_column(
        String(30),
        comment="Số liên hệ tại địa điểm.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin bổ sung.",
    )
