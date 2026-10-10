from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TnCauHoiTracNghiem(Base):
    """Câu hỏi trắc nghiệm, gắn một mã Holland và một loại câu hỏi."""

    __tablename__ = "tn_cau_hoi_trac_nghiem"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_holand: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("dm_nhom_tinh_cach_holland.ma_nhom", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    loai_cau_hoi_id: Mapped[int] = mapped_column(
        ForeignKey("dm_loai_cau_hoi.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    noi_dung_cau_hoi: Mapped[str] = mapped_column(Text, nullable=False)
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
