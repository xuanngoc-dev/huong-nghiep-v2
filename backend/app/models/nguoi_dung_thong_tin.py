from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NguoiDungThongTin(Base):
    """Hồ sơ mở rộng của một người dùng."""

    __tablename__ = "nguoi_dung_thong_tin"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nguoi_dung_id: Mapped[int] = mapped_column(
        ForeignKey("nguoi_dung.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    # 1: nam, 2: nữ, 3: khác
    gioi_tinh: Mapped[int | None] = mapped_column(SmallInteger)
    ngay_sinh: Mapped[date | None] = mapped_column(Date)
    dan_toc: Mapped[str | None] = mapped_column(String(150))
    ton_giao: Mapped[str | None] = mapped_column(String(150))
    trinh_do_hoc_van: Mapped[Any | None] = mapped_column(JSON)
    suc_khoe_the_chat: Mapped[Any | None] = mapped_column(JSON)
    kha_nang_tai_chinh: Mapped[Any | None] = mapped_column(JSON)
    tinh_thanh_id: Mapped[int | None] = mapped_column(
        ForeignKey("dm_tinh_thanh.id", ondelete="SET NULL"),
        index=True,
    )
    edu_coin: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    xu_he_thong: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    mat_khau_thanh_toan: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
