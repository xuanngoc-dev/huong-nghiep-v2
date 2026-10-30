from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsLienHeTuyenSinh(Base):
    """Đầu mối, số điện thoại và email tư vấn tuyển sinh."""

    __tablename__ = "dats_lien_he_tuyen_sinh"
    __table_args__ = (
        Index("idx_dats_lien_he_tuyen_sinh_de_an_id", "de_an_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Đầu mối, số điện thoại và email tư vấn tuyển sinh",
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
            name="fk_dats_lien_he_tuyen_sinh_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    ten_don_vi: Mapped[str | None] = mapped_column(
        String(255),
        comment="Đơn vị phụ trách.",
    )
    ten_nguoi_lien_he: Mapped[str | None] = mapped_column(
        String(255),
        comment="Người liên hệ nếu công bố.",
    )
    chuc_vu: Mapped[str | None] = mapped_column(
        String(150),
        comment="Chức vụ người liên hệ.",
    )
    so_dien_thoai: Mapped[str | None] = mapped_column(
        String(30),
        comment="Số điện thoại.",
    )
    email: Mapped[str | None] = mapped_column(
        String(255),
        comment="Email liên hệ.",
    )
    thoi_gian_lien_he: Mapped[str | None] = mapped_column(
        String(255),
        comment="Khung giờ hỗ trợ.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin liên hệ bổ sung.",
    )
