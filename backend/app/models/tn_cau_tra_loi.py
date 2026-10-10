from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TnCauTraLoi(Base):
    """Đáp án của một câu hỏi trắc nghiệm."""

    __tablename__ = "tn_cau_tra_loi"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cau_hoi_id: Mapped[int] = mapped_column(
        ForeignKey("tn_cau_hoi_trac_nghiem.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    noi_dung_cau_tra_loi: Mapped[str] = mapped_column(Text, nullable=False)
    diem: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
