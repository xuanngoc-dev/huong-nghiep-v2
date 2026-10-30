from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsQuyDoiDiemTrungTuyen(Base):
    """Quy đổi điểm trúng tuyển giữa phương thức/tổ hợp."""

    __tablename__ = "dats_quy_doi_diem_trung_tuyen"
    __table_args__ = (
        Index("idx_dats_quy_doi_diem_trung_tuyen_de_an_id_nam_tuyen_sinh", "de_an_id", "nam_tuyen_sinh"),
        Index("idx_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id", "phuong_thuc_nguon_id"),
        Index("idx_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id", "phuong_thuc_dich_id"),
        Index("idx_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id", "to_hop_nguon_id"),
        Index("idx_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id", "to_hop_dich_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Quy đổi điểm trúng tuyển giữa phương thức/tổ hợp",
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
            name="fk_dats_quy_doi_diem_trung_tuyen_de_an_id",
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
            name="fk_dats_quy_doi_diem_trung_tuyen_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình áp dụng.",
    )
    nam_tuyen_sinh: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm tuyển sinh.",
    )
    phuong_thuc_nguon_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_phuong_thuc_tuyen_sinh.id",
            name="fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_nguon_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức nguồn.",
    )
    to_hop_nguon_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_to_hop_mon_hoc.id",
            name="fk_dats_quy_doi_diem_trung_tuyen_to_hop_nguon_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Tổ hợp nguồn; NULL nếu không dùng.",
    )
    phuong_thuc_dich_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_phuong_thuc_tuyen_sinh.id",
            name="fk_dats_quy_doi_diem_trung_tuyen_phuong_thuc_dich_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức đích.",
    )
    to_hop_dich_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_to_hop_mon_hoc.id",
            name="fk_dats_quy_doi_diem_trung_tuyen_to_hop_dich_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Tổ hợp đích; NULL nếu không dùng.",
    )
    diem_moc_nguon: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 3),
        comment="Mốc điểm trúng tuyển nguồn.",
    )
    diem_moc_dich: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 3),
        comment="Mốc điểm tương đương đích.",
    )
    do_lech_diem: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 3),
        comment="Điểm đích trừ điểm nguồn.",
    )
    thang_diem_nguon: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        comment="Thang điểm nguồn tối đa.",
    )
    thang_diem_dich: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        comment="Thang điểm đích tối đa.",
    )
    cong_thuc_noi_suy: Mapped[str | None] = mapped_column(
        Text,
        comment="Công thức nội suy giữa các mốc.",
    )
    dieu_kien_ap_dung: Mapped[str | None] = mapped_column(
        Text,
        comment="Điều kiện/phạm vi áp dụng.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="URL bảng quy đổi gốc.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái quy tắc.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú.",
    )
