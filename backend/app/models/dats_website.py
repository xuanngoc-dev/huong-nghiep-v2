from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsWebsite(Base):
    """Các trang thông tin điện tử liên quan đến đề án."""

    __tablename__ = "dats_website"
    __table_args__ = (
        Index("idx_dats_website_de_an_id", "de_an_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Các trang thông tin điện tử liên quan đến đề án",
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
            name="fk_dats_website_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    loai_website: Mapped[str | None] = mapped_column(
        String(30),
        comment="Phân loại website.",
    )
    ten_trang: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên trang thông tin.",
    )
    url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Địa chỉ trang.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả/lưu ý.",
    )
