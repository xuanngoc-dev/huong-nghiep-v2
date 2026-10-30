from decimal import Decimal

from sqlalchemy import (
    JSON,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsPhuongThuc(Base):
    """Phương thức, điều kiện và chỉ tiêu theo phương thức."""

    __tablename__ = "dats_phuong_thuc"
    __table_args__ = (
        Index("idx_dats_phuong_thuc_de_an_chuong_trinh_id_phuong_thuc_id", "de_an_chuong_trinh_id", "phuong_thuc_id"),
        Index("idx_dats_phuong_thuc_phuong_thuc_id", "phuong_thuc_id"),
        Index("idx_dats_phuong_thuc_to_hop_id", "to_hop_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Phương thức, điều kiện và chỉ tiêu theo phương thức",
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
            name="fk_dats_phuong_thuc_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Chương trình áp dụng.",
    )
    phuong_thuc_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "dm_phuong_thuc_tuyen_sinh.id",
            name="fk_dats_phuong_thuc_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Danh mục phương thức; FK dm_phuong_thuc_tuyen_sinh.id.",
    )
    ma_phuong_thuc_cua_truong: Mapped[str | None] = mapped_column(
        String(20),
        comment="Mã riêng của trường.",
    )
    ten_phuong_thuc_cua_truong: Mapped[str | None] = mapped_column(
        String(255),
        comment="Tên phương thức theo đề án.",
    )
    chi_tieu_phuong_thuc: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Chỉ tiêu riêng; NULL nếu không chia chỉ tiêu.",
    )
    dieu_kien_can: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Điều kiện bắt buộc.",
    )
    dieu_kien_du: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Tiêu chí để đủ điều kiện trúng tuyển.",
    )
    diem_san: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        comment="Ngưỡng nhận hồ sơ nếu công bố.",
    )
    diem_chuan: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        comment="Ngưỡng trúng tuyển hồ sơ.",
    )
    thang_diem: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        comment="Thang điểm xét tuyển.",
    )
    cong_thuc_tinh_diem: Mapped[str | None] = mapped_column(
        Text,
        comment="Công thức điểm xét tuyển.",
    )
    to_hop_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_to_hop_mon_hoc.id",
            name="fk_dats_phuong_thuc_to_hop_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Tổ hợp áp dụng; NULL nếu không dùng tổ hợp.; một tổ hợp theo Excel; nhiều tổ hợp dùng dats_phuong_thuc_to_hop.",
    )
    thu_tu_uu_tien: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự hiển thị.",
    )
    ghi_chu_chi_tieu: Mapped[str | None] = mapped_column(
        Text,
        comment="Cách phân bổ chỉ tiêu.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Lưu ý phương thức.",
    )
