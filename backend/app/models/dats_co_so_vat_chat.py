from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsCoSoVatChat(Base):
    """Cơ sở vật chất phục vụ đào tạo."""

    __tablename__ = "dats_co_so_vat_chat"
    __table_args__ = (
        Index("idx_dats_co_so_vat_chat_de_an_id", "de_an_id"),
        Index("idx_dats_co_so_vat_chat_co_so_id", "co_so_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Cơ sở vật chất phục vụ đào tạo",
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
            name="fk_dats_co_so_vat_chat_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    co_so_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_tru_so.id",
            name="fk_dats_co_so_vat_chat_co_so_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Cơ sở sở hữu hạng mục; có thể NULL.",
    )
    loai_co_so_vat_chat: Mapped[str | None] = mapped_column(
        String(50),
        comment="Loại hạng mục.",
    )
    ten_hang_muc: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên cơ sở vật chất/thiết bị.",
    )
    so_luong: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        comment="Số lượng hoặc diện tích.",
    )
    don_vi_tinh: Mapped[str | None] = mapped_column(
        String(30),
        comment="Đơn vị đo.",
    )
    muc_dich_su_dung: Mapped[str | None] = mapped_column(
        Text,
        comment="Công năng đào tạo.",
    )
    nam_thong_ke: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm ghi nhận.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú bổ sung.",
    )
