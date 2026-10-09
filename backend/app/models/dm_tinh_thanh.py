from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmTinhThanh(Base):
    """Danh mục tỉnh thành."""

    __tablename__ = "dm_tinh_thanh"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_tinh: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ma_tinh: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    khu_vuc: Mapped[str | None] = mapped_column(String(100))
    dien_tich: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    nam_thanh_lap: Mapped[int | None] = mapped_column(SmallInteger)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
