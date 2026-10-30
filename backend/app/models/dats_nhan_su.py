from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsNhanSu(Base):
    """Đội ngũ giảng viên và cán bộ quản lý được đề án công bố."""

    __tablename__ = "dats_nhan_su"
    __table_args__ = (
        Index("idx_dats_nhan_su_de_an_id", "de_an_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Đội ngũ giảng viên và cán bộ quản lý được đề án công bố",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính.",
    )
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_tuyen_sinh.id",
            name="fk_dats_nhan_su_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    nhom_nhan_su: Mapped[str | None] = mapped_column(
        String(30),
        comment="Nhóm giảng viên/cán bộ quản lý.",
    )
    ten_nhan_su: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên cá nhân nếu công bố; có thể NULL.",
    )
    chuc_danh: Mapped[str | None] = mapped_column(
        String(100),
        comment="Chức danh/vị trí.",
    )
    hoc_vi: Mapped[str | None] = mapped_column(
        String(50),
        comment="Học vị.",
    )
    hoc_ham: Mapped[str | None] = mapped_column(
        String(50),
        comment="Học hàm.",
    )
    linh_vuc_chuyen_mon: Mapped[str | None] = mapped_column(
        String(255),
        comment="Lĩnh vực chuyên môn.",
    )
    so_luong: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Số lượng nếu thống kê tổng hợp.",
    )
    nam_thong_ke: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm thống kê.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú số liệu.",
    )
