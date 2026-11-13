from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtCauHinhEnduser(Base):
    """Cấu hình hiển thị phía người dùng cuối."""

    __tablename__ = "ht_cau_hinh_enduser"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_cau_hinh: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    noi_dung_cau_hinh: Mapped[dict | list | None] = mapped_column(JSON)
    # diem_so: trả lời bằng điểm số, tinh_huong: trả lời theo tình huống
    kieu_tra_loi: Mapped[str] = mapped_column(
        String(20), nullable=False, default="diem_so", server_default="diem_so"
    )
    mo_ta: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
