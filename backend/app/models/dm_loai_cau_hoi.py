from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmLoaiCauHoi(Base):
    """Danh mục loại câu hỏi."""

    __tablename__ = "dm_loai_cau_hoi"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_loai_cau_hoi: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    thu_tu_uu_tien: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
