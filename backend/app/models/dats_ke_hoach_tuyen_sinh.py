from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsKeHoachTuyenSinh(Base):
    """Kế hoạch và phạm vi tuyển sinh của chương trình."""

    __tablename__ = "dats_ke_hoach_tuyen_sinh"
    __table_args__ = (
        Index("idx_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Kế hoạch và phạm vi tuyển sinh của chương trình",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính.",
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_ke_hoach_tuyen_sinh_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Chương trình tuyển sinh.",
    )
    don_vi_chi_tieu: Mapped[str | None] = mapped_column(
        String(30),
        comment="Đơn vị tính chỉ tiêu.",
    )
    pham_vi_tuyen_sinh: Mapped[str | None] = mapped_column(
        String(255),
        comment="Phạm vi tuyển sinh.",
    )
    dot_tuyen_sinh: Mapped[str | None] = mapped_column(
        String(100),
        comment="Đợt tuyển sinh.",
    )
    thoi_gian_nhan_ho_so: Mapped[str | None] = mapped_column(
        String(255),
        comment="Thời gian nhận hồ sơ.",
    )
    dieu_kien_chung: Mapped[str | None] = mapped_column(
        Text,
        comment="Điều kiện chung trong kế hoạch.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú kế hoạch.",
    )
