from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.mysql import MEDIUMTEXT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


class TinTucNhomTin(Base):
    """Nhóm tin tức (chuyên mục) của trang tin."""

    __tablename__ = "tin_tuc_nhom_tin"
    __table_args__ = _BANG

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ma_nhom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ten_nhom: Mapped[str] = mapped_column(String(255), nullable=False)
    # Đường dẫn thân thiện, ví dụ "huong-nghiep".
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    mo_ta: Mapped[str | None] = mapped_column(Text)
    # Thứ tự hiển thị, nhỏ đứng trước.
    thu_tu: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    # 0: ẩn, 1: hiển thị
    trang_thai: Mapped[int] = mapped_column(TINYINT, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TinTucBaiViet(Base):
    """Bài viết tin tức thuộc một nhóm tin."""

    __tablename__ = "tin_tuc_bai_viet"
    __table_args__ = (
        # Danh sách bài đã xuất bản, mới nhất trước.
        Index("ix_tin_tuc_bai_viet_trang_thai_created_at", "trang_thai", "created_at"),
        _BANG,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # RESTRICT: không xóa được nhóm khi còn bài viết.
    nhom_tin_tuc_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tin_tuc_nhom_tin.id", name="fk_tin_tuc_bai_viet_nhom_tin_tuc_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tieu_de: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    tom_tat: Mapped[str | None] = mapped_column(Text)
    # Nội dung HTML. MEDIUMTEXT trên MySQL (bài dài), TEXT trên SQLite khi chạy test.
    noi_dung: Mapped[str | None] = mapped_column(Text().with_variant(MEDIUMTEXT(), "mysql"))
    # URL ảnh đại diện (tuyệt đối hoặc đường dẫn tương đối của Thư viện ảnh).
    anh_dai_dien: Mapped[str | None] = mapped_column(String(500))
    tac_gia: Mapped[str | None] = mapped_column(String(255))
    # 0: nháp / ẩn, 1: xuất bản
    trang_thai: Mapped[int] = mapped_column(TINYINT, nullable=False, default=1, server_default="1")
    # 1: bài nổi bật (ưu tiên hiện ở đầu trang tin).
    is_noi_bat: Mapped[int] = mapped_column(TINYINT, nullable=False, default=0, server_default="0")
    luot_xem: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
