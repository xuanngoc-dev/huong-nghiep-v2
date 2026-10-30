from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsDieuKienDuTuyen(Base):
    """Điều kiện cần đáp ứng để dự tuyển."""

    __tablename__ = "dats_dieu_kien_du_tuyen"
    __table_args__ = (
        Index("idx_dats_dieu_kien_du_tuyen_de_an_id", "de_an_id"),
        Index("idx_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        Index("idx_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id", "doi_tuong_du_tuyen_id"),
        CheckConstraint("bat_buoc IS NULL OR bat_buoc IN (0,1)", name="chk_dats_dieu_kien_du_tuyen_bat_buoc"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Điều kiện cần đáp ứng để dự tuyển",
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
            name="fk_dats_dieu_kien_du_tuyen_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án áp dụng.",
    )
    doi_tuong_du_tuyen_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_doi_tuong_du_tuyen.id",
            name="fk_dats_dieu_kien_du_tuyen_doi_tuong_du_tuyen_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Đối tượng chịu điều kiện; có thể NULL.",
    )
    de_an_chuong_trinh_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_dieu_kien_du_tuyen_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình áp dụng; có thể NULL.",
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_dieu_kien_du_tuyen_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức áp dụng; có thể NULL.",
    )
    ma_dieu_kien: Mapped[str | None] = mapped_column(
        String(50),
        comment="Mã tiêu chí.",
    )
    ten_dieu_kien: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên điều kiện.",
    )
    loai_dieu_kien: Mapped[str | None] = mapped_column(
        String(30),
        comment="Nhóm điều kiện.",
    )
    noi_dung_dieu_kien: Mapped[str | None] = mapped_column(
        Text,
        comment="Nội dung đầy đủ.",
    )
    toan_tu_so_sanh: Mapped[str | None] = mapped_column(
        String(10),
        comment="Toán tử điều kiện số.",
    )
    gia_tri_dieu_kien: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Giá trị có cấu trúc.",
    )
    bat_buoc: Mapped[bool | None] = mapped_column(
        Boolean,
        comment="Điều kiện bắt buộc hay không.",
    )
    minh_chung_can_nop: Mapped[str | None] = mapped_column(
        Text,
        comment="Giấy tờ chứng minh.",
    )
    thu_tu_kiem_tra: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự kiểm tra.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="URL nguồn quy định.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú.",
    )
