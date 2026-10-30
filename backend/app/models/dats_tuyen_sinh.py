from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsTuyenSinh(Base):
    """Thông tin chung của đề án theo trường và năm tuyển sinh."""

    __tablename__ = "dats_tuyen_sinh"
    __table_args__ = (
        Index("idx_dats_tuyen_sinh_truong_id_nam_tuyen_sinh", "truong_id", "nam_tuyen_sinh"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Thông tin chung của đề án theo trường và năm tuyển sinh",
        },
    )

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True,
        autoincrement=True,
        comment="Khóa chính, tự tăng.",
    )
    truong_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dm_truong.id",
            name="fk_dats_tuyen_sinh_truong_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đơn vị đào tạo; khóa ngoại đến dm_truong.id.",
    )
    nam_tuyen_sinh: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True),
        nullable=False,
        comment="Năm tuyển sinh của đề án.",
    )
    chi_tieu: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Tổng chỉ tiêu của đợt tuyển sinh",
    )
    ten_de_an: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên đề án/thông tin tuyển sinh.",
    )
    hinh_thuc_dao_tao: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Danh sách hình thức đào tạo tuyển sinh.",
    )
    gioi_thieu: Mapped[str | None] = mapped_column(
        Text,
        comment="Nội dung tổng quan đề án.",
    )
    ngay_cong_bo: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày công bố đề án.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="Đường dẫn đề án gốc.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái đề án.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú/cập nhật.",
    )
    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật gần nhất.",
    )
