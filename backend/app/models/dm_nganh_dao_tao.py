from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DmNganhDaoTao(Base):
    """Danh mục ngành đào tạo, thuộc một nhóm ngành."""

    __tablename__ = "dm_nganh_dao_tao"
    __table_args__ = (
        Index("idx_dm_nganh_dao_tao_ngay_hieu_luc_tu", "ngay_hieu_luc_tu"),
        Index("idx_dm_nganh_dao_tao_nganh_cha_id", "nganh_cha_id"),
        Index("idx_dm_nganh_dao_tao_van_ban_id", "van_ban_id"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
        },
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_nhom_nganh: Mapped[str] = mapped_column(
        String(20),
        ForeignKey("dm_nhom_nganh_dao_tao.ma_nhom_nganh", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ma_nganh: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    ten_nganh: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    ten_tieng_anh: Mapped[str] = mapped_column(String(255), nullable=False)
    trinh_do: Mapped[str] = mapped_column(String(100), nullable=False)
    # Danh sách mã nhóm Holland, ví dụ ["R", "I"]. Không bắt buộc.
    ma_holand: Mapped[list[str] | None] = mapped_column(JSON)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    hinh_anh_mo_ta: Mapped[str | None] = mapped_column(String(500))
    muc_luong_tham_khao: Mapped[str | None] = mapped_column(String(255))
    nhan_dan: Mapped[str | None] = mapped_column(String(100))
    thoi_gian_dao_tao: Mapped[str | None] = mapped_column(String(100))
    chi_tiet: Mapped[str | None] = mapped_column(Text)
    # 0: ngừng sử dụng, 1: hoạt động
    trang_thai: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Bổ sung theo docs/tuyen_sinh_mysql_dm.sql.
    cap_danh_muc: Mapped[str | None] = mapped_column(
        String(20),
        comment="Cấp của bản ghi trong hệ thống phân cấp.",
    )

    nganh_cha_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "dm_nganh_dao_tao.id",
            name="fk_dm_nganh_dao_tao_nganh_cha_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="ID lĩnh vực hoặc nhóm ngành cấp trên; tham chiếu dm_nganh_dao_tao.id. Để NULL nếu là cấp cao nhất.",
    )

    trinh_do_ap_dung: Mapped[dict | list | None] = mapped_column(
        JSON,
        comment="Các trình độ áp dụng theo danh mục hoặc dữ liệu đối chiếu.",
    )

    ngay_hieu_luc_tu: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày bắt đầu hiệu lực của mã hoặc tên ngành.",
    )

    ngay_hieu_luc_den: Mapped[date | None] = mapped_column(
        Date,
        comment="Ngày kết thúc hiệu lực, nếu có; để NULL nếu chưa xác định.",
    )

    ghi_chu_theo_thong_tu: Mapped[str | None] = mapped_column(
        Text,
        comment="Ghi chú được nêu trong phụ lục danh mục ngành.",
    )

    van_ban_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "dm_van_ban.id",
            name="fk_dm_nganh_dao_tao_van_ban_id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        comment="ID văn bản nguồn; tham chiếu bảng văn bản pháp lý nếu có.",
    )

    thu_tu_hien_thi: Mapped[int | None] = mapped_column(
        INTEGER(unsigned=True),
        comment="Thứ tự sắp xếp trong danh mục.",
    )

    tao_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm tạo bản ghi.",
    )

    cap_nhat_luc: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Thời điểm cập nhật gần nhất.",
    )
