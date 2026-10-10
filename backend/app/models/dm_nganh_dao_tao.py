from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmNganhDaoTao(Base):
    """Danh mục ngành đào tạo, thuộc một nhóm ngành."""

    __tablename__ = "dm_nganh_dao_tao"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_nhom_nganh: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("dm_nhom_nganh_dao_tao.ma_nhom_nganh", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ma_nganh: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_nganh: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ten_tieng_anh: Mapped[str] = mapped_column(String(255), nullable=False)
    trinh_do: Mapped[str] = mapped_column(String(100), nullable=False)
    # Danh sách mã nhóm Holland, ví dụ ["R", "I"]. Không bắt buộc.
    ma_holand: Mapped[list[str] | None] = mapped_column(JSON)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
