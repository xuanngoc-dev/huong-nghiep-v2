from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmChiSoXetTuyen(Base):
    """Danh mục chỉ số (dữ kiện) của học sinh dùng để kiểm tra điều kiện xét tuyển và điểm cộng."""

    __tablename__ = "dm_chi_so_xet_tuyen"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}

    ma_chi_so: Mapped[str] = mapped_column(String(50), primary_key=True)
    ten_chi_so: Mapped[str] = mapped_column(String(255), nullable=False)
    # MON_HOC, BAI_THI, CHUNG_CHI, THANH_TICH, LOP; NULL nếu chỉ số không cần khóa.
    kieu_khoa: Mapped[str | None] = mapped_column(String(30))
    y_nghia_gia_tri: Mapped[str | None] = mapped_column(String(500))
    ghi_chu: Mapped[str | None] = mapped_column(Text)
