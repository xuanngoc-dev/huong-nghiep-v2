from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NguoiDung(Base):
    """Bảng người dùng hệ thống."""

    __tablename__ = "nguoi_dung"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ho_ten: Mapped[str] = mapped_column(String(150), nullable=False)
    so_dien_thoai: Mapped[str | None] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    mat_khau: Mapped[str] = mapped_column(String(255), nullable=False)
    # 0: người dùng, 1: admin
    vai_tro: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    # 0: khóa, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
