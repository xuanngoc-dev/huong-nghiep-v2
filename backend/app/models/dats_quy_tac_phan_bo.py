from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DatsQuyTacPhanBo(Base):
    """Quy tắc phân bổ thí sinh vào ngành/chương trình."""

    __tablename__ = "dats_quy_tac_phan_bo"
    __table_args__ = (
        Index("idx_dats_quy_tac_phan_bo_de_an_id", "de_an_id"),
        Index("idx_dats_quy_tac_phan_bo_de_an_chuong_trinh_id", "de_an_chuong_trinh_id"),
        Index("idx_dats_quy_tac_phan_bo_de_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Quy tắc phân bổ thí sinh vào ngành/chương trình",
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
            name="fk_dats_quy_tac_phan_bo_de_an_id",
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
            name="fk_dats_quy_tac_phan_bo_de_an_chuong_trinh_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Chương trình; NULL nếu chung.",
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dats_phuong_thuc.id",
            name="fk_dats_quy_tac_phan_bo_de_an_phuong_thuc_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="Phương thức; NULL nếu chung.",
    )
    kieu_phan_bo: Mapped[str | None] = mapped_column(
        String(30),
        comment="Cách phân bổ thí sinh.",
    )
    thu_tu_uu_tien: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự ưu tiên.",
    )
    quy_tac_xu_ly_dong_diem: Mapped[str | None] = mapped_column(
        Text,
        comment="Xử lý bằng điểm tại ranh giới chỉ tiêu.",
    )
    quy_tac_chuyen_chi_tieu: Mapped[str | None] = mapped_column(
        Text,
        comment="Cách xử lý chỉ tiêu dư/điều chỉnh.",
    )
    noi_dung_quy_tac: Mapped[str | None] = mapped_column(
        Text,
        comment="Nội dung quy tắc phân bổ.",
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
