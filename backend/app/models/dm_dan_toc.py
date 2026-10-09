from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmDanToc(Base):
    """Danh mục dân tộc."""

    __tablename__ = "dm_dan_toc"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_dan_toc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_dan_toc: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ten_goi_khac: Mapped[str | None] = mapped_column(String(255))
    dan_so: Mapped[int | None] = mapped_column(Integer)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
