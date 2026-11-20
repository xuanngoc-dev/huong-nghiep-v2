from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Index, Integer, SmallInteger, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChatMessage(Base):
    """Một tin nhắn trong phiên trò chuyện."""

    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("idx_chat_messages_phien_chat_id_created_at", "phien_chat_id", "created_at"),
        Index("idx_chat_messages_nguoi_gui_id", "nguoi_gui_id"),
        Index("idx_chat_messages_ma_khach_vang_lai", "ma_khach_vang_lai"),
        {
            "mysql_charset": "utf8mb4",
            "mysql_collate": "utf8mb4_unicode_ci",
            "mysql_engine": "InnoDB",
            "comment": "Tin nhắn trong phiên trò chuyện với trợ lý",
        },
    )

    id: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    phien_chat_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("chat_conversations.id", name="fk_chat_messages_phien_chat_id", ondelete="CASCADE"),
        nullable=False,
    )
    # user: người dùng; bot: trợ lý AI; agent: nhân viên tư vấn.
    loai_nguoi_gui: Mapped[str] = mapped_column(Enum("user", "bot", "agent", name="loai_nguoi_gui"), nullable=False)
    # Null: khách vãng lai hoặc bot.
    nguoi_gui_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("nguoi_dung.id", name="fk_chat_messages_nguoi_gui_id", ondelete="SET NULL")
    )
    ma_khach_vang_lai: Mapped[str | None] = mapped_column(String(64))
    # MEDIUMTEXT trên MySQL (tin nhắn dài), TEXT trên SQLite khi chạy test.
    noi_dung_tin_nhan: Mapped[str | None] = mapped_column(Text().with_variant(MEDIUMTEXT(), "mysql"))
    noi_dung_phan_hoi: Mapped[str | None] = mapped_column(Text().with_variant(MEDIUMTEXT(), "mysql"))
    nguon_tham_khao: Mapped[Any | None] = mapped_column(JSON, comment="Tài liệu / nguồn dùng để trả lời")
    model_ai: Mapped[str | None] = mapped_column(String(100))
    so_token_vao: Mapped[int | None] = mapped_column(Integer)
    so_token_ra: Mapped[int | None] = mapped_column(Integer)
    # Tổng token cả lượt (bước lập kế hoạch tra cứu + bước trả lời), dùng để trừ token / tính hạn mức khách vãng lai.
    tong_token: Mapped[int | None] = mapped_column(Integer, comment="Tổng token cả lượt (lập kế hoạch + trả lời)")
    thoi_gian_phan_hoi_ms: Mapped[int | None] = mapped_column(Integer)
    trang_thai: Mapped[str] = mapped_column(
        Enum("dang_xu_ly", "thanh_cong", "loi", name="trang_thai_tin_nhan"),
        nullable=False,
        default="thanh_cong",
        server_default="thanh_cong",
    )
    loi_chi_tiet: Mapped[str | None] = mapped_column(Text)
    danh_gia: Mapped[int | None] = mapped_column(SmallInteger, comment="1: hữu ích, -1: không hữu ích")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
