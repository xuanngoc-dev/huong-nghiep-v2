from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmToHopMonHoc(Base):
    """Danh mục tổ hợp môn học. ds_mon_hoc là danh sách ma_mon_hoc của dm_mon_hoc."""

    __tablename__ = "dm_to_hop_mon_hoc"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_to_hop: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ma_to_hop: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    # Danh sách mã môn học, ví dụ ["TOAN", "LY", "HOA"]
    ds_mon_hoc: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
