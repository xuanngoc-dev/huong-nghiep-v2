from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmToHopMonHocChiTiet(Base):
    """Bảng nối nhiều-nhiều giữa tổ hợp và môn học (bổ sung thiết kế)."""

    __tablename__ = "dm_to_hop_mon_hoc_chi_tiet"
    __table_args__ = (
        Index("idx_dm_to_hop_mon_hoc_chi_tiet_to_hop_id", "to_hop_id"),
        Index("idx_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id", "mon_hoc_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Bảng nối nhiều-nhiều giữa tổ hợp và môn học (bổ sung thiết kế)",
        },
    )

    to_hop_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "dm_to_hop_mon_hoc.id",
            name="fk_dm_to_hop_mon_hoc_chi_tiet_to_hop_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        comment="Khóa ngoại đến tổ hợp môn học.",
    )
    mon_hoc_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "dm_mon_hoc.id",
            name="fk_dm_to_hop_mon_hoc_chi_tiet_mon_hoc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        comment="Khóa ngoại đến môn học trong tổ hợp.",
    )
    thu_tu_mon: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự của môn trong tổ hợp, nếu có.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Lưu ý riêng về môn học trong tổ hợp.",
    )
