from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmLinhVucDaoTao(Base):
    """Danh mục lĩnh vực đào tạo."""

    __tablename__ = "dm_linh_vuc_dao_tao"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_linh_vuc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_linh_vuc: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ten_tieng_anh: Mapped[str] = mapped_column(String(255), nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
