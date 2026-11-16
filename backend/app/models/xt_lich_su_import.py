from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class XtLichSuImport(Base):
    """Nhật ký mỗi lần import quy tắc xét tuyển của đề án: ai, lúc nào, file nào, số dòng."""

    __tablename__ = "xt_lich_su_import"
    __table_args__ = (
        Index("idx_xt_lich_su_import_de_an", "de_an_id", "tao_luc"),
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"},
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    de_an_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("dats_tuyen_sinh.id", name="fk_xt_lsi_de_an_id", ondelete="CASCADE"),
        nullable=False,
    )
    ten_file: Mapped[str | None] = mapped_column(String(255))
    # SHA-256 nội dung file, để biết file nào đã được nạp.
    ma_bam: Mapped[str | None] = mapped_column(String(64))
    phien_ban_chuan: Mapped[str | None] = mapped_column(String(20))
    so_dong: Mapped[dict | None] = mapped_column(JSON)
    quy_dinh_chua_mo_hinh_hoa: Mapped[list | None] = mapped_column(JSON)
    nguoi_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nguoi_dung.id", name="fk_xt_lsi_nguoi_import_id", ondelete="SET NULL")
    )
    tao_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    ghi_chu: Mapped[str | None] = mapped_column(Text)
