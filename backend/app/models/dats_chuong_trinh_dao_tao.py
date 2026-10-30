from decimal import Decimal

from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsChuongTrinhDaoTao(Base):
    """Danh sách chương trình và chỉ tiêu tổng theo chương trình."""

    __tablename__ = "dats_chuong_trinh_dao_tao"
    __table_args__ = (
        Index("idx_dats_chuong_trinh_dao_tao_de_an_id_ma_xet_tuyen", "de_an_id", "ma_xet_tuyen"),
        Index("idx_dats_chuong_trinh_dao_tao_nganh_dao_tao_id", "nganh_dao_tao_id"),
        Index("idx_dats_chuong_trinh_dao_tao_co_so_id", "co_so_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Danh sách chương trình và chỉ tiêu tổng theo chương trình",
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
            name="fk_dats_chuong_trinh_dao_tao_de_an_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        nullable=False,
        comment="Đề án áp dụng.",
    )
    nganh_dao_tao_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_nganh_dao_tao.id",
            name="fk_dats_chuong_trinh_dao_tao_nganh_dao_tao_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Ngành chuẩn; FK dm_nganh_dao_tao.id.",
    )
    ma_xet_tuyen: Mapped[str | None] = mapped_column(
        String(20),
        comment="Mã xét tuyển do trường công bố.",
    )
    ten_chuong_trinh: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Tên chương trình/ngành trong đề án.",
    )
    trinh_do_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Trình độ đào tạo.",
    )
    hinh_thuc_dao_tao: Mapped[str | None] = mapped_column(
        String(30),
        comment="Hình thức đào tạo.",
    )
    co_so_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_tru_so.id",
            name="fk_dats_chuong_trinh_dao_tao_co_so_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Cơ sở/phân hiệu phụ trách; có thể NULL.",
    )
    thoi_gian_dao_tao_nam: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1),
        comment="Thời lượng đào tạo theo năm.",
    )
    ngon_ngu_dao_tao: Mapped[str | None] = mapped_column(
        String(100),
        comment="Ngôn ngữ giảng dạy.",
    )
    chi_tieu_tuyen_sinh: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Tổng chỉ tiêu chương trình.",
    )
    kieu_phan_bo_chi_tieu: Mapped[str | None] = mapped_column(
        String(30),
        comment="Phân bổ theo phương thức hay dùng chung.",
    )
    ghi_chu: Mapped[str | None] = mapped_column(
        Text,
        comment="Thông tin bổ sung.",
    )
