from datetime import date

from sqlalchemy import Date, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmVanBan(Base):
    """Văn bản quy phạm hoặc văn bản tham chiếu cho các danh mục (bổ sung thiết kế)."""

    __tablename__ = "dm_van_ban"
    __table_args__ = (
        Index("idx_dm_van_ban_so_ky_hieu", "so_ky_hieu"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Văn bản quy phạm hoặc văn bản tham chiếu cho các danh mục (bổ sung thiết kế)",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính kỹ thuật của văn bản.",
    )
    so_ky_hieu: Mapped[str | None] = mapped_column(
        String(100),
        comment="Số, ký hiệu văn bản được công bố.",
    )
    ten_van_ban: Mapped[str | None] = mapped_column(
        String(500),
        comment="Tên đầy đủ hoặc trích yếu văn bản.",
    )
    loai_van_ban: Mapped[str | None] = mapped_column(
        String(50),
        comment="Loại văn bản: thông tư, quyết định, quy chế,...",
    )
    co_quan_ban_hanh: Mapped[str | None] = mapped_column(
        String(255),
        comment="Cơ quan ban hành văn bản.",
    )
    ngay_ban_hanh: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày ban hành văn bản nếu được công bố.",
    )
    ngay_hieu_luc: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày có hiệu lực nếu được công bố.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn văn bản gốc để xác minh.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú hoặc phạm vi áp dụng.",
    )
