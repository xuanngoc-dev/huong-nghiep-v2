from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HtCauHinhGoiCuoc(Base):
    """Gói cước bán cho người dùng: giá và số lượt nhận được theo từng loại chức năng."""

    __tablename__ = "ht_cau_hinh_goi_cuoc"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_goi_cuoc: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ten_goi_cuoc: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # tra_cuu: tra cứu, khao_sat: khảo sát, hoi_dap: hỏi đáp
    loai_ap_dung: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Giá tính theo VNĐ.
    gia_goc: Mapped[Decimal] = mapped_column(Numeric(15, 0), nullable=False, default=0, server_default="0")
    gia_khuyen_mai: Mapped[Decimal | None] = mapped_column(Numeric(15, 0))
    so_luot_nhan_duoc_goc: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    so_luot_nhan_duoc_khuyen_mai: Mapped[int | None] = mapped_column(Integer)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
