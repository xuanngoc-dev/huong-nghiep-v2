from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, SmallInteger, String
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_MYSQL = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


class DatsPhienThuThap(Base):
    __tablename__ = "dats_phien_thu_thap"
    __table_args__ = (
        Index("idx_dats_thu_thap_trang_thai", "trang_thai", "cap_nhat_luc"),
        Index("idx_dats_thu_thap_truong_nam", "ma_truong", "nam_tuyen_sinh"),
        _MYSQL,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ma_truong: Mapped[str] = mapped_column(
        String(20), ForeignKey("dm_truong.ma_truong", onupdate="CASCADE", ondelete="RESTRICT")
    )
    nam_tuyen_sinh: Mapped[int] = mapped_column(SmallInteger)
    trang_thai: Mapped[str] = mapped_column(String(24))
    tao_boi: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id", ondelete="SET NULL"))
    tao_luc: Mapped[datetime] = mapped_column(DateTime)
    cap_nhat_luc: Mapped[datetime] = mapped_column(DateTime)
    bat_dau_tao_ban_nhap_luc: Mapped[datetime | None] = mapped_column(DateTime)
    tien_do_tao_ban_nhap: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    sua_lan: Mapped[int] = mapped_column(Integer, default=0)
    phien_ban: Mapped[int | None] = mapped_column(Integer)
    nguon: Mapped[list] = mapped_column(JSON, default=list)
    canh_bao_nguon: Mapped[list] = mapped_column(JSON, default=list)
    yeu_cau_bo_sung: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    de_an_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True), ForeignKey("dats_tuyen_sinh.id", ondelete="SET NULL")
    )
    duyet_boi: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id", ondelete="SET NULL"))
    duyet_luc: Mapped[datetime | None] = mapped_column(DateTime)


class DatsBanNhapThuThap(Base):
    __tablename__ = "dats_ban_nhap_thu_thap"
    __table_args__ = _MYSQL

    phien_id: Mapped[int] = mapped_column(ForeignKey("dats_phien_thu_thap.id", ondelete="CASCADE"), primary_key=True)
    phien_ban: Mapped[int] = mapped_column(Integer, primary_key=True)
    tao_luc: Mapped[datetime] = mapped_column(DateTime)
    ten_nguoi_tao: Mapped[str] = mapped_column(String(150))
    du_lieu: Mapped[dict] = mapped_column(JSON)
    muc: Mapped[list] = mapped_column(JSON)
    ghi_chu: Mapped[list] = mapped_column(JSON)
    nguon: Mapped[list] = mapped_column(JSON)
    doi_chieu: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))


class DatsNhatKyThuThap(Base):
    __tablename__ = "dats_nhat_ky_thu_thap"
    __table_args__ = (Index("idx_dats_nhat_ky_thu_thap_phien", "phien_id", "id"), _MYSQL)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phien_id: Mapped[int] = mapped_column(ForeignKey("dats_phien_thu_thap.id", ondelete="CASCADE"))
    phien_ban: Mapped[int | None] = mapped_column(Integer)
    hanh_dong: Mapped[str] = mapped_column(String(30))
    nguoi_dung_id: Mapped[int | None] = mapped_column(ForeignKey("nguoi_dung.id", ondelete="SET NULL"))
    nguoi_dung: Mapped[str] = mapped_column(String(150))
    tao_luc: Mapped[datetime] = mapped_column(DateTime)
    chi_tiet: Mapped[dict] = mapped_column(JSON)
