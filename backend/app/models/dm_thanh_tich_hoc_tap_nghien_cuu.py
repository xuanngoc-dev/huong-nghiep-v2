from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmThanhTichHocTapNghienCuu(Base):
    """Danh mục thành tích học tập, nghiên cứu."""

    __tablename__ = "dm_thanh_tich_hoc_tap_nghien_cuu"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_thanh_tich: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ten_thanh_tich: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ten_chi_tiet: Mapped[str | None] = mapped_column(String(500))
    linh_vuc: Mapped[str | None] = mapped_column(String(150))
    mon: Mapped[str | None] = mapped_column(String(150))
    thang_diem: Mapped[str | None] = mapped_column(String(100))
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
