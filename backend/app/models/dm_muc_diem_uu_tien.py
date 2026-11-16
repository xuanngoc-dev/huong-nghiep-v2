from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String, Text, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmMucDiemUuTien(Base):
    """Mức điểm cộng khu vực / đối tượng ưu tiên theo khoảng năm; không có dòng khớp năm thì dùng diem_cong của danh mục."""

    __tablename__ = "dm_muc_diem_uu_tien"
    __table_args__ = (
        UniqueConstraint("loai", "ma", "nam_ap_dung_tu", name="uk_dm_muc_diem_uu_tien"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Mức điểm cộng khu vực / đối tượng ưu tiên theo năm tuyển sinh",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    loai: Mapped[str] = mapped_column(Enum("KHU_VUC", "DOI_TUONG", name="loai_uu_tien"), nullable=False)
    ma: Mapped[str] = mapped_column(String(20), nullable=False, comment="ma_khu_vuc hoặc ma_doi_tuong.")
    nam_ap_dung_tu: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)
    nam_ap_dung_den: Mapped[int | None] = mapped_column(SMALLINT(unsigned=True), comment="NULL = đến nay.")
    diem_cong: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, comment="Điểm cộng thang 30.")
    can_cu: Mapped[str | None] = mapped_column(String(255), comment="Văn bản quy định.")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    tao_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    cap_nhat_luc: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
