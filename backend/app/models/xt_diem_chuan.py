from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class XtDiemChuan(Base):
    """Điểm trúng tuyển các năm theo mã trường + mã xét tuyển, làm mốc so sánh khi tìm trường phù hợp."""

    __tablename__ = "xt_diem_chuan"
    __table_args__ = (
        Index("idx_xt_diem_chuan_tra_cuu", "ma_truong", "ma_xet_tuyen", "nam_tuyen_sinh"),
        Index("idx_xt_diem_chuan_to_hop_id", "to_hop_id"),
        Index("idx_xt_diem_chuan_ma_phuong_thuc", "ma_phuong_thuc_cua_bo"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Điểm trúng tuyển các năm, làm mốc so sánh",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    ma_truong: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("dm_truong.ma_truong", name="fk_xt_diem_chuan_ma_truong", onupdate="CASCADE"),
        nullable=False,
        comment="FK dm_truong.ma_truong.",
    )
    nam_tuyen_sinh: Mapped[int] = mapped_column(SMALLINT(unsigned=True), nullable=False)
    ma_xet_tuyen: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Mã xét tuyển năm đó; dùng để nối với chương trình của đề án hiện hành.",
    )
    ten_chuong_trinh: Mapped[str | None] = mapped_column(String(255))
    ma_phuong_thuc_cua_bo: Mapped[str | None] = mapped_column(
        String(20),
        ForeignKey("dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc", name="fk_xt_diem_chuan_ma_phuong_thuc"),
        comment="NULL = điểm chuẩn chung mọi phương thức.",
    )
    to_hop_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("dm_to_hop_mon_hoc.id", name="fk_xt_diem_chuan_to_hop_id"),
        comment="NULL = chung mọi tổ hợp.",
    )
    diem_chuan: Mapped[Decimal] = mapped_column(Numeric(7, 2), nullable=False)
    thang_diem: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, default=30, server_default="30.00")
    tieu_chi_phu: Mapped[str | None] = mapped_column(String(255))
    nguon_du_lieu_url: Mapped[str | None] = mapped_column(String(1000))
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    tao_luc: Mapped[datetime | None] = mapped_column(DateTime, comment="Thời điểm tạo bản ghi.")
    cap_nhat_luc: Mapped[datetime | None] = mapped_column(DateTime, comment="Thời điểm cập nhật gần nhất.")
