from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TnPhienKhaoSat(Base):
    """Một phiên làm bài khảo sát, kèm kết quả và thông tin thanh toán."""

    __tablename__ = "tn_phien_khao_sat"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ssid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    nguoi_khao_sat_id: Mapped[int | None] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="SET NULL"),
        index=True,
    )
    ma_giao_dich: Mapped[str | None] = mapped_column(String(64), unique=True)
    # Định hướng người dùng chọn khi làm bài, mã theo app/constants/doi_tuong_ap_dung.py (1: thi ĐH & CĐ, 2: đi làm...).
    dinh_huong: Mapped[int | None] = mapped_column(SmallInteger, index=True)
    chi_tiet_ket_qua: Mapped[Any | None] = mapped_column(JSON)
    thong_tin_thanh_toan: Mapped[Any | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
