from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmNganhHocTheoTruong(Base):
    """Ngành đào tạo của từng trường theo năm học."""

    __tablename__ = "dm_nganh_hoc_theo_truong"
    __table_args__ = (
        # Một mã xét tuyển có thể gồm nhiều ngành/chương trình nên không đặt ràng buộc duy nhất.
        Index("idx_dm_nganh_hoc_theo_truong_ma_xet_tuyen", "ma_truong", "nam_hoc", "ma_xet_tuyen"),
        Index("idx_dm_nganh_hoc_theo_truong_nam_hoc", "nam_hoc"),
        Index("idx_dm_nganh_hoc_theo_truong_ma_nganh", "ma_nganh"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_truong: Mapped[str] = mapped_column(
        String(20),
        ForeignKey(
            "dm_truong.ma_truong",
            name="fk_dm_nganh_hoc_theo_truong_ma_truong",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Mã trường, tham chiếu dm_truong.ma_truong",
    )
    nam_hoc: Mapped[int] = mapped_column(Integer, nullable=False, comment="Năm học/năm tuyển sinh")
    ma_nganh: Mapped[str | None] = mapped_column(String(20), comment="Mã ngành")
    ma_xet_tuyen: Mapped[str | None] = mapped_column(String(50), comment="Mã xét tuyển của trường")
    ten_nganh: Mapped[str | None] = mapped_column(String(255), comment="Tên ngành")
    ten_chuong_trinh: Mapped[str | None] = mapped_column(String(255), comment="Tên chương trình đào tạo")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
