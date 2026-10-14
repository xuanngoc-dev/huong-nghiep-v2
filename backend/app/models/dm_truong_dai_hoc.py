from datetime import datetime

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.mysql import BIGINT, LONGTEXT, TIMESTAMP, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmTruongDaiHoc(Base):
    """Danh mục trường đại học."""

    __tablename__ = "dm_truong_dai_hoc"
    __table_args__ = (
        UniqueConstraint("ma_truong", name="uq_dm_truong_dai_hoc_ma_truong"),
        Index("idx_ma_truong", "ma_truong"),
        Index("idx_ten_truong", "ten_truong"),
        Index("idx_khu_vuc", "khu_vuc"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ma_truong: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Mã trường (Bộ GD&ĐT)",
    )
    ten_truong: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Tên đầy đủ tiếng Việt"
    )
    ten_viet_tat: Mapped[str | None] = mapped_column(
        String(50), comment="Tên viết tắt (HUST, NEU...)"
    )
    ten_tieng_anh: Mapped[str | None] = mapped_column(String(255), comment="Tên tiếng Anh")
    khu_vuc: Mapped[str | None] = mapped_column(String(50), comment="Tỉnh/Thành phố hoặc miền")
    dia_chi: Mapped[str | None] = mapped_column(Text, comment="Địa chỉ cơ sở chính")
    loai_hinh_dao_tao: Mapped[str | None] = mapped_column(
        String(50), comment="Công lập, Tư thục, Quốc tế..."
    )
    nhom_nganh: Mapped[str | None] = mapped_column(String(100), comment="Khối ngành chính")
    website: Mapped[str | None] = mapped_column(String(255), comment="Link website")
    email: Mapped[str | None] = mapped_column(String(100), comment="Email liên hệ")
    so_dien_thoai: Mapped[str | None] = mapped_column(String(50), comment="Hotline")
    logo: Mapped[str | None] = mapped_column(String(255), comment="URL Logo trường")
    anh_bia: Mapped[str | None] = mapped_column(String(255), comment="URL ảnh bìa/campus")
    gioi_thieu: Mapped[str | None] = mapped_column(LONGTEXT, comment="Mô tả chi tiết/Lịch sử")
    hoc_phi_trung_binh: Mapped[str | None] = mapped_column(
        String(100), comment="Mức học phí tham khảo"
    )
    nam_thanh_lap: Mapped[int | None] = mapped_column(Integer, comment="Năm thành lập")
    # 1: Hoạt động, 0: Khóa
    trang_thai: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        default=1,
        server_default="1",
        comment="1: Hoạt động, 0: Khóa",
    )
    ngay_tao: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )
    ngay_cap_nhat: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
