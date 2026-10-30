from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsDiemCong(Base):
    """Điểm thưởng, điểm xét thưởng và điểm khuyến khích."""

    __tablename__ = "dats_diem_cong"
    __table_args__ = (
        Index("idx_dats_diem_cong_de_an_id", "de_an_id"),
        Index("idx_dats_diem_cong_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_diem_cong_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        CheckConstraint("co_cong_don IS NULL OR co_cong_don IN (0,1)", name="chk_dats_diem_cong_co_cong_don"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Điểm thưởng, điểm xét thưởng và điểm khuyến khích",
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
            name="fk_dats_diem_cong_de_an_id",
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
            name="fk_dats_diem_cong_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình; NULL nếu chung.",
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_diem_cong_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức; NULL nếu chung.",
    )
    loai_diem_cong: Mapped[str | None] = mapped_column(
        String(30),
        comment="Điểm thưởng/xét thưởng/khuyến khích.",
    )
    ma_doi_tuong_cong: Mapped[str | None] = mapped_column(
        String(50),
        comment="Mã thành tích/chứng chỉ được cộng.",
    )
    doi_tuong_duoc_cong: Mapped[str | None] = mapped_column(
        Text,
        comment="Mô tả đối tượng.",
    )
    dieu_kien_ap_dung: Mapped[str | None] = mapped_column(
        Text,
        comment="Điều kiện chi tiết.",
    )
    diem_cong: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 3),
        comment="Mức điểm được cộng.",
    )
    thang_diem: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 2),
        comment="Thang điểm áp dụng.",
    )
    muc_diem_cong_toi_da: Mapped[Decimal | None] = mapped_column(
        Numeric(6, 3),
        comment="Mức cộng tối đa.",
    )
    co_cong_don: Mapped[bool | None] = mapped_column(
        Boolean,
        comment="Có cộng dồn quyền lợi không.",
    )
    quy_tac_ket_hop: Mapped[str | None] = mapped_column(
        Text,
        comment="Xử lý nhiều diện cùng lúc.",
    )
    nam_tuyen_sinh: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm áp dụng.",
    )
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(
        String(1000),
        comment="URL nguồn.",
    )
    trang_thai: Mapped[str | None] = mapped_column(
        String(20),
        comment="Trạng thái quy tắc.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú.",
    )
