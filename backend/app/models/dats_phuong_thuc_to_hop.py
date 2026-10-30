from sqlalchemy import ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsPhuongThucToHop(Base):
    """Liên kết N-N giữa phương thức của đề án và tổ hợp môn (bổ sung thiết kế)."""

    __tablename__ = "dats_phuong_thuc_to_hop"
    __table_args__ = (
        Index("idx_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        Index("idx_dats_phuong_thuc_to_hop_to_hop_id", "to_hop_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Liên kết N-N giữa phương thức của đề án và tổ hợp môn (bổ sung thiết kế)",
        },
    )

    de_an_phuong_thuc_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_phuong_thuc_to_hop_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        comment="Khóa ngoại đến phương thức xét tuyển cụ thể trong đề án.",
    )
    to_hop_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "dm_to_hop_mon_hoc.id",
            name="fk_dats_phuong_thuc_to_hop_to_hop_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        primary_key=True,
        comment="Khóa ngoại đến tổ hợp môn xét tuyển.",
    )
    thu_tu_hien_thi: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự hiển thị tổ hợp của phương thức.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Lưu ý phạm vi hoặc điều kiện riêng của tổ hợp.",
    )
