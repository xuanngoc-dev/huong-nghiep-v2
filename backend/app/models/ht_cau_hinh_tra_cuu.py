from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, SmallInteger, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtCauHinhTraCuu(Base):
    """Cấu hình hạn mức tra cứu, tư vấn AI và thanh toán của hệ thống."""

    __tablename__ = "ht_cau_hinh_tra_cuu"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Hạn mức trong một ngày: khách vãng lai tính theo thiết bị, thành viên tính theo tài khoản.
    so_luot_tra_cuu_khach_ngay: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    so_luot_tra_cuu_thanh_vien_ngay: Mapped[int] = mapped_column(
        Integer, nullable=False, default=5, server_default="5"
    )
    so_luot_tu_van_ai_ngay: Mapped[int] = mapped_column(Integer, nullable=False, default=10, server_default="10")
    so_luot_phan_tich_truong_ngay: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default="3"
    )
    bat_tinh_nang_holland: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="1"
    )
    bat_thanh_toan: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    # Giá báo cáo chuyên sâu, đơn vị VNĐ.
    gia_bao_cao_chuyen_sau: Mapped[Decimal] = mapped_column(
        Numeric(15, 0), nullable=False, default=0, server_default="0"
    )
    # 0: ngừng sử dụng, 1: đang áp dụng
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
