from sqlalchemy import (
    JSON,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsTieuChiXetTuyen(Base):
    """Tiêu chí chính, tiêu chí phụ và thứ tự xét."""

    __tablename__ = "dats_tieu_chi_xet_tuyen"
    __table_args__ = (
        Index("idx_dats_tieu_chi_xet_tuyen_de_an_id", "de_an_id"),
        Index("idx_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Tiêu chí chính, tiêu chí phụ và thứ tự xét",
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
            name="fk_dats_tieu_chi_xet_tuyen_de_an_id",
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
            name="fk_dats_tieu_chi_xet_tuyen_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình; NULL nếu chung.",
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_tieu_chi_xet_tuyen_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức; NULL nếu chung.",
    )
    ma_tieu_chi: Mapped[str | None] = mapped_column(
        String(50),
        comment="Mã tiêu chí.",
    )
    ten_tieu_chi: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên tiêu chí.",
    )
    loai_tieu_chi: Mapped[str | None] = mapped_column(
        String(30),
        comment="Chính/phụ/loại trừ.",
    )
    thu_tu_ap_dung: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự xét tiêu chí.",
    )
    toan_tu_so_sanh: Mapped[str | None] = mapped_column(
        String(10),
        comment="Toán tử nếu có ngưỡng số.",
    )
    gia_tri_tieu_chi: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Ngưỡng/giá trị tiêu chí.",
    )
    noi_dung_tieu_chi: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả đầy đủ tiêu chí.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="URL nguồn.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú.",
    )
