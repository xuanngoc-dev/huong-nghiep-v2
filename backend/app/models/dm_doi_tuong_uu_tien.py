from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmDoiTuongUuTien(Base):
    """Danh mục đối tượng ưu tiên."""

    __tablename__ = "dm_doi_tuong_uu_tien"
    __table_args__ = (
        Index("idx_dm_doi_tuong_uu_tien_ma_doi_tuong_nam_ap_dung", "ma_doi_tuong", "nam_ap_dung"),
        Index("idx_dm_doi_tuong_uu_tien_van_ban_id", "van_ban_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ten_doi_tuong: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    ma_doi_tuong: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    diem_cong: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False, default=0, server_default="0")
    ghi_chu: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Bổ sung theo docs/tuyen_sinh_mysql_dm.sql.
    mo_ta_dieu_kien: Mapped[str | None] = mapped_column(
        Text,
        comment="Điều kiện để được hưởng ưu tiên.",
    )

    nhom_uu_tien: Mapped[str | None] = mapped_column(
        String(10),
        comment="Nhóm ưu tiên.",
    )

    diem_uu_tien_co_ban: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        comment="Mức điểm ưu tiên cơ bản theo thang điểm 30.",
    )

    # NULL vì bảng đã có dữ liệu; thiết kế gốc khai báo NOT NULL.
    nam_ap_dung: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Năm tuyển sinh áp dụng.",
    )

    van_ban_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dm_van_ban.id",
            name="fk_dm_doi_tuong_uu_tien_van_ban_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="ID văn bản quy định, nếu có bảng văn bản.",
    )

    thu_tu_hien_thi: Mapped[int | None] = mapped_column(
        SMALLINT(unsigned=True),
        comment="Thứ tự hiển thị.",
    )
