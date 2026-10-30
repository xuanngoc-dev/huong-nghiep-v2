from sqlalchemy import JSON, String, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmThanhTichHocTap(Base):
    """Danh mục thành tích học tập."""

    __tablename__ = "dm_thanh_tich_hoc_tap"
    __table_args__ = (
        UniqueConstraint("ma_loai_thanh_tich", name="uk_dm_thanh_tich_hoc_tap_ma_loai_thanh_tich"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Danh mục thành tích học tập",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính, tự tăng.",
    )
    ma_loai_thanh_tich: Mapped[str | None] = mapped_column(
        String(30),
        comment="Mã loại thành tích.",
    )
    ten_loai_thanh_tich: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tên loại thành tích.",
    )
    loai_cuoc_thi: Mapped[str | None] = mapped_column(
        String(50),
        comment="Nhóm cuộc thi hoặc hoạt động.",
    )
    cap_cuoc_thi: Mapped[str | None] = mapped_column(
        String(50),
        comment="Cấp tổ chức hoặc phạm vi cuộc thi.",
    )
    cac_muc_giai: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách giải thưởng có thể đạt trong loại thành tích này. Mỗi giải gồm mã, tên và thứ tự.",
    )
    mo_ta: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả loại thành tích.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái sử dụng trong danh mục.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú bổ sung.",
    )
