from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsDoiTuongDuTuyen(Base):
    """Nhóm thí sinh được phép dự tuyển."""

    __tablename__ = "dats_doi_tuong_du_tuyen"
    __table_args__ = (
        Index("idx_dats_doi_tuong_du_tuyen_de_an_id", "de_an_id"),
        Index("idx_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Nhóm thí sinh được phép dự tuyển",
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
            name="fk_dats_doi_tuong_du_tuyen_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án liên quan.",
    )
    ma_doi_tuong: Mapped[str | None] = mapped_column(
        String(30),
        comment="Mã nhóm đối tượng.",
    )
    ten_doi_tuong: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tên đối tượng dự tuyển.",
    )
    mo_ta: Mapped[str | None] = mapped_column(
        Text,
        comment="Phạm vi đối tượng.",
    )
    nam_tot_nghiep_tu: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm tốt nghiệp tối thiểu nếu giới hạn.",
    )
    nam_tot_nghiep_den: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm tốt nghiệp tối đa; NULL nếu không giới hạn.",
    )
    pham_vi_ap_dung: Mapped[str | None] = mapped_column(
        String(30),
        comment="Toàn đề án hoặc một chương trình.",
    )
    de_an_chuong_trinh_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_chuong_trinh_dao_tao.id",
            name="fk_dats_doi_tuong_du_tuyen_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình áp dụng; có thể NULL.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái bản ghi.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú/ngoại lệ.",
    )
