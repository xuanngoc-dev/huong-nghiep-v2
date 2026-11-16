from sqlalchemy import Boolean, ForeignKey, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class XtPhuongAn(Base):
    """Phương án xét tuyển: một cách cụ thể để vào một chương trình = chương trình x công thức x tổ hợp."""

    __tablename__ = "xt_phuong_an"
    __table_args__ = (
        UniqueConstraint("de_an_chuong_trinh_id", "cong_thuc_id", "to_hop_id", name="uk_xt_phuong_an"),
        Index("idx_xt_phuong_an_de_an_id", "de_an_id"),
        Index("idx_xt_phuong_an_cong_thuc_id", "cong_thuc_id"),
        Index("idx_xt_phuong_an_to_hop_id", "to_hop_id"),
        Index("idx_xt_phuong_an_phuong_thuc_id", "de_an_phuong_thuc_id"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"},
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", name="fk_xt_phuong_an_de_an_id"), nullable=False
    )
    de_an_chuong_trinh_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("dats_chuong_trinh_dao_tao.id", name="fk_xt_phuong_an_chuong_trinh_id"),
        nullable=False,
    )
    de_an_phuong_thuc_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_phuong_thuc.id", name="fk_xt_phuong_an_phuong_thuc_id")
    )
    cong_thuc_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("xt_cong_thuc.id", name="fk_xt_phuong_an_cong_thuc_id"), nullable=False
    )
    # Bắt buộc với công thức TO_HOP_MON.
    to_hop_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("dm_to_hop_mon_hoc.id", name="fk_xt_phuong_an_to_hop_id")
    )
    trang_thai: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
