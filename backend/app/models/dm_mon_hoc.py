from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmMonHoc(Base):
    """Danh mục môn học."""

    __tablename__ = "dm_mon_hoc"
    __table_args__ = (
        UniqueConstraint("ma_mon", name="uk_dm_mon_hoc_ma_mon"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_mon_hoc: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ma_mon_hoc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_viet_tat: Mapped[str | None] = mapped_column(String(50))
    # tự nhiên, xã hội, ngoại ngữ, ...
    nhom_mon: Mapped[str | None] = mapped_column(String(50))
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    mo_ta: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Bổ sung theo docs/tuyen_sinh_mysql_dm.sql.
    # NULL vì bảng đã có dữ liệu; thiết kế gốc khai báo NOT NULL.
    ma_mon: Mapped[str | None] = mapped_column(
        String(20),
        comment="Mã định danh môn học.",
    )

    # NULL vì bảng đã có dữ liệu; thiết kế gốc khai báo NOT NULL.
    ten_mon: Mapped[str | None] = mapped_column(
        String(100),
        comment="Tên môn học.",
    )

    ten_tieng_anh: Mapped[str | None] = mapped_column(
        String(100),
        comment="Tên tiếng Anh, nếu có.",
    )

    ten_goi_khac: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Tên viết tắt hoặc tên gọi khác.",
    )

    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú bổ sung.",
    )

    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )

    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật gần nhất.",
    )
