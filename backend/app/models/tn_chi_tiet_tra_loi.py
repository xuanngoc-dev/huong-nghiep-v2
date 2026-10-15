from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TnChiTietTraLoi(Base):
    """Một câu trả lời trong phiên khảo sát."""

    __tablename__ = "tn_chi_tiet_tra_loi"
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
        "mysql_engine": "InnoDB",
    }

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ssid: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("tn_phien_khao_sat.ssid", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    loai_cau_hoi_id: Mapped[int] = mapped_column(
        ForeignKey("dm_loai_cau_hoi.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    cau_hoi_id: Mapped[int] = mapped_column(
        ForeignKey("tn_cau_hoi_trac_nghiem.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    # Để trống khi mới gán câu hỏi cho phiên, điền khi người khảo sát trả lời.
    cau_tra_loi_id: Mapped[int | None] = mapped_column(
        ForeignKey("tn_cau_tra_loi.id", ondelete="RESTRICT"),
        index=True,
    )
    diem_dat_duoc: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
