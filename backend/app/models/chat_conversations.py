from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatConversation(Base):
    """Phiên trò chuyện với trợ lý (của thành viên hoặc khách vãng lai)."""

    __tablename__ = "chat_conversations"
    __table_args__ = (
        Index("idx_chat_conversations_user_id", "user_id"),
        Index("idx_chat_conversations_ma_khach_vang_lai", "ma_khach_vang_lai"),
        Index("idx_chat_conversations_trang_thai", "trang_thai"),
        Index("idx_chat_conversations_tin_nhan_cuoi_luc", "tin_nhan_cuoi_luc"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Phiên trò chuyện với trợ lý",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    # Null: khách vãng lai (nhận diện bằng ma_khach_vang_lai).
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nguoi_dung.id", name="fk_chat_conversations_user_id", ondelete="SET NULL")
    )
    ma_dinh_danh: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, comment="UUID định danh phiên")
    ma_khach_vang_lai: Mapped[str | None] = mapped_column(String(64), comment="Mã thiết bị / trình duyệt của khách")
    tieu_de: Mapped[str | None] = mapped_column(String(255))
    trang_thai: Mapped[str] = mapped_column(
        Enum("dang_hoat_dong", "da_dong", name="trang_thai_chat"),
        nullable=False,
        default="dang_hoat_dong",
        server_default="dang_hoat_dong",
    )
    model_ai: Mapped[str | None] = mapped_column(String(100), comment="Model AI dùng cho phiên")
    so_tin_nhan: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    tin_nhan_cuoi_luc: Mapped[datetime | None] = mapped_column(DateTime, comment="Thời điểm tin nhắn gần nhất")
    du_lieu_bo_sung: Mapped[Any | None] = mapped_column(JSON, comment="Thông tin thêm (nguồn, ngữ cảnh...)")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
