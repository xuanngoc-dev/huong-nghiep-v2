from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmMonHoc(Base):
    """Danh mục môn học."""

    __tablename__ = "dm_mon_hoc"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ma_mon_hoc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_viet_tat: Mapped[str | None] = mapped_column(String(50))
    # tự nhiên, xã hội, ngoại ngữ, ...
    nhom_mon: Mapped[str | None] = mapped_column(String(50))
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    mo_ta: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
