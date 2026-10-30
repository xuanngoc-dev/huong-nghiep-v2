from decimal import Decimal

from sqlalchemy import (
    JSON,
    ForeignKey,
    Index,
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
        Index(
            "idx_dats_phuong_thuc_de_an_chuong_trinh_id_ma_bo",
            "de_an_chuong_trinh_id",
            "ma_phuong_thuc_cua_bo",
        ),
        Index("idx_dats_phuong_thuc_ma_phuong_thuc_cua_bo", "ma_phuong_thuc_cua_bo"),
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
    ma_phuong_thuc_cua_bo: Mapped[str] = mapped_column(
        String(20),
        ForeignKey(
            "dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc",
            name="fk_dats_phuong_thuc_ma_phuong_thuc_cua_bo",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Mã phương thức của Bộ; FK dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc.",
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
    to_hop_mon_hoc: Mapped[list | None] = mapped_column(
        JSON,
        comment='Danh sách mã tổ hợp môn áp dụng, ví dụ ["A01"]. NULL nếu phương thức áp dụng cho mọi tổ hợp.',
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
