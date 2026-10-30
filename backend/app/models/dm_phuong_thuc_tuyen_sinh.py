from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.mysql import SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmPhuongThucTuyenSinh(Base):
    """Danh mục phương thức tuyển sinh."""

    __tablename__ = "dm_phuong_thuc_tuyen_sinh"
    __table_args__ = (
        Index("idx_dm_phuong_thuc_tuyen_sinh_nam_ap_dung_tu", "nam_ap_dung_tu"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_phuong_thuc: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ma_phuong_thuc: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    giai_thich: Mapped[str | None] = mapped_column(Text)
    truong_hop_cu_the: Mapped[str | None] = mapped_column(Text)
    luu_y: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Bổ sung theo docs/tuyen_sinh_mysql_dm.sql.
    loai_phuong_thuc: Mapped[str | None] = mapped_column(
        String(50),
        comment="Nhóm phương thức để phân loại.",
    )

    pham_vi_ap_dung: Mapped[str | None] = mapped_column(
        String(30),
        comment="Phạm vi định nghĩa: danh mục chung hay phương thức riêng của trường.",
    )

    nam_ap_dung_tu: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm bắt đầu áp dụng bản ghi.",
    )

    nam_ap_dung_den: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm kết thúc áp dụng; để NULL nếu chưa xác định.",
    )

    thu_tu_hien_thi: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự hiển thị trong giao diện.",
    )

    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn văn bản hoặc trang nguồn của thông tin.",
    )

    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú quản trị hoặc nội dung cần kiểm tra.",
    )

    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )

    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật gần nhất.",
    )
