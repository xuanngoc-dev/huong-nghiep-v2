from datetime import datetime

from sqlalchemy import DateTime, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtNganHangThanhToan(Base):
    """Tài khoản ngân hàng nhận thanh toán của hệ thống."""

    __tablename__ = "ht_ngan_hang_thanh_toan"
    __table_args__ = (
        UniqueConstraint(
            "ten_ngan_hang_viet_tat",
            "so_tai_khoan",
            name="uq_ht_ngan_hang_thanh_toan_tai_khoan",
        ),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_ngan_hang: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ten_ngan_hang_tieng_anh: Mapped[str | None] = mapped_column(String(255))
    ten_ngan_hang_viet_tat: Mapped[str] = mapped_column(String(50), nullable=False)
    so_tai_khoan: Mapped[str] = mapped_column(String(50), nullable=False)
    chu_tai_khoan: Mapped[str] = mapped_column(String(255), nullable=False)
    # URL logo ngân hàng.
    logo_ngan_hang: Mapped[str | None] = mapped_column(String(500))
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
