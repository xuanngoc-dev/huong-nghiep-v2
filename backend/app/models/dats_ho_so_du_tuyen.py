from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsHoSoDuTuyen(Base):
    """Giấy tờ và minh chứng thí sinh cần nộp."""

    __tablename__ = "dats_ho_so_du_tuyen"
    __table_args__ = (
        Index("idx_dats_ho_so_du_tuyen_de_an_id", "de_an_id"),
        Index("idx_dats_ho_so_du_tuyen_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_ho_so_du_tuyen_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        CheckConstraint("bat_buoc IS NULL OR bat_buoc IN (0,1)", name="chk_dats_ho_so_du_tuyen_bat_buoc"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Giấy tờ và minh chứng thí sinh cần nộp",
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
            name="fk_dats_ho_so_du_tuyen_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án áp dụng.",
    )
    de_an_chuong_trinh_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_ho_so_du_tuyen_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình; có thể NULL.",
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_ho_so_du_tuyen_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức; có thể NULL.",
    )
    ten_giay_to: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên giấy tờ/minh chứng.",
    )
    doi_tuong_phai_nop: Mapped[str | None] = mapped_column(
        Text,
        comment="Đối tượng cần nộp giấy tờ.",
    )
    bat_buoc: Mapped[bool | None] = mapped_column(
        Boolean,
        comment="Có bắt buộc nộp không.",
    )
    hinh_thuc_nop: Mapped[str | None] = mapped_column(
        String(30),
        comment="Cách nộp hồ sơ.",
    )
    thoi_han_nop: Mapped[str | None] = mapped_column(
        String(255),
        comment="Hạn nộp hồ sơ.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Yêu cầu/lưu ý.",
    )
