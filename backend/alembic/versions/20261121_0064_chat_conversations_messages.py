"""Tao bang chat_conversations (phien tro chuyen) va chat_messages (tin nhan).

- chat_conversations: user_id null = khach vang lai (nhan dien bang ma_khach_vang_lai), ma_dinh_danh la UUID.
- chat_messages: thuoc mot phien (xoa phien thi xoa tin nhan); loai_nguoi_gui user / bot / agent.

Revision ID: 20261121_0064
Revises: 20261121_0063
Create Date: 2026-11-21 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, MEDIUMTEXT

revision: str = "20261121_0064"
down_revision: Union[str, Sequence[str], None] = "20261121_0063"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PHIEN = "chat_conversations"
_TIN_NHAN = "chat_messages"
_BANG = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci", "mysql_engine": "InnoDB"}


def _thoi_gian() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
        ),
    ]


def upgrade() -> None:
    # Chạy lại được sau khi lỗi giữa chừng (MySQL không rollback DDL).
    inspector = sa.inspect(op.get_bind())
    if not inspector.has_table(_PHIEN):
        op.create_table(
            _PHIEN,
            sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
            sa.Column(
                "user_id",
                sa.Integer(),
                sa.ForeignKey("nguoi_dung.id", name="fk_chat_conversations_user_id", ondelete="SET NULL"),
                comment="Null: khách vãng lai",
            ),
            sa.Column("ma_dinh_danh", sa.String(36), nullable=False, comment="UUID định danh phiên"),
            sa.Column("ma_khach_vang_lai", sa.String(64), comment="Mã thiết bị / trình duyệt của khách"),
            sa.Column("tieu_de", sa.String(255)),
            sa.Column(
                "trang_thai",
                sa.Enum("dang_hoat_dong", "da_dong", "luu_tru", name="trang_thai_chat"),
                nullable=False,
                server_default="dang_hoat_dong",
            ),
            sa.Column("model_ai", sa.String(100), comment="Model AI dùng cho phiên"),
            sa.Column("so_tin_nhan", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("tin_nhan_cuoi_luc", sa.DateTime(), comment="Thời điểm tin nhắn gần nhất"),
            sa.Column("du_lieu_bo_sung", sa.JSON(), comment="Thông tin thêm (nguồn, ngữ cảnh...)"),
            *_thoi_gian(),
            sa.UniqueConstraint("ma_dinh_danh", name="uq_chat_conversations_ma_dinh_danh"),
            comment="Phiên trò chuyện với trợ lý",
            **_BANG,
        )
        op.create_index("idx_chat_conversations_user_id", _PHIEN, ["user_id"])
        op.create_index("idx_chat_conversations_ma_khach_vang_lai", _PHIEN, ["ma_khach_vang_lai"])
        op.create_index("idx_chat_conversations_trang_thai", _PHIEN, ["trang_thai"])
        op.create_index("idx_chat_conversations_tin_nhan_cuoi_luc", _PHIEN, ["tin_nhan_cuoi_luc"])

    if not inspector.has_table(_TIN_NHAN):
        op.create_table(
            _TIN_NHAN,
            sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
            sa.Column(
                "phien_chat_id",
                BIGINT(unsigned=True),
                sa.ForeignKey(f"{_PHIEN}.id", name="fk_chat_messages_phien_chat_id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "loai_nguoi_gui",
                sa.Enum("user", "bot", "agent", name="loai_nguoi_gui"),
                nullable=False,
                comment="user: người dùng, bot: trợ lý AI, agent: nhân viên tư vấn",
            ),
            sa.Column(
                "nguoi_gui_id",
                sa.Integer(),
                sa.ForeignKey("nguoi_dung.id", name="fk_chat_messages_nguoi_gui_id", ondelete="SET NULL"),
                comment="Null: khách vãng lai hoặc bot",
            ),
            sa.Column("ma_khach_vang_lai", sa.String(64)),
            sa.Column("noi_dung_tin_nhan", sa.Text().with_variant(MEDIUMTEXT(), "mysql")),
            sa.Column("noi_dung_phan_hoi", sa.Text().with_variant(MEDIUMTEXT(), "mysql")),
            sa.Column("nguon_tham_khao", sa.JSON(), comment="Tài liệu / nguồn dùng để trả lời"),
            sa.Column("model_ai", sa.String(100)),
            sa.Column("so_token_vao", sa.Integer()),
            sa.Column("so_token_ra", sa.Integer()),
            sa.Column("thoi_gian_phan_hoi_ms", sa.Integer()),
            sa.Column(
                "trang_thai",
                sa.Enum("dang_xu_ly", "thanh_cong", "loi", name="trang_thai_tin_nhan"),
                nullable=False,
                server_default="thanh_cong",
            ),
            sa.Column("loi_chi_tiet", sa.Text()),
            sa.Column("danh_gia", sa.SmallInteger(), comment="1: hữu ích, -1: không hữu ích"),
            *_thoi_gian(),
            comment="Tin nhắn trong phiên trò chuyện với trợ lý",
            **_BANG,
        )
        op.create_index("idx_chat_messages_phien_chat_id_created_at", _TIN_NHAN, ["phien_chat_id", "created_at"])
        op.create_index("idx_chat_messages_nguoi_gui_id", _TIN_NHAN, ["nguoi_gui_id"])
        op.create_index("idx_chat_messages_ma_khach_vang_lai", _TIN_NHAN, ["ma_khach_vang_lai"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    for bang in (_TIN_NHAN, _PHIEN):
        if inspector.has_table(bang):
            op.drop_table(bang)
