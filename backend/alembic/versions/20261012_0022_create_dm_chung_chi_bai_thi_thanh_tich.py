"""create_dm_bai_thi_thanh_tich

Chứng chỉ ngoại ngữ không tạo ở revision này. Danh mục đó dùng
dm_bang_cap_chung_chi.

Revision ID: 20261012_0022
Revises: 20261012_0021
Create Date: 2026-10-12 18:55:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261012_0022"
down_revision: Union[str, Sequence[str], None] = "20261012_0021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE_KW = {
    "mysql_charset": "utf8mb4",
    "mysql_collate": "utf8mb4_unicode_ci",
    "mysql_engine": "InnoDB",
}


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    ]


def _common_tail(include_loai: bool, include_don_vi: bool) -> list[sa.Column]:
    columns = [
        sa.Column("ten_chi_tiet", sa.String(length=500), nullable=True),
        sa.Column("linh_vuc", sa.String(length=150), nullable=True),
        sa.Column("mon", sa.String(length=150), nullable=True),
    ]
    if include_loai:
        columns.append(
            sa.Column(
                "loai_chung_chi",
                sa.String(length=20),
                nullable=False,
                comment="trong_nuoc hoặc quoc_te",
            )
        )
    columns.append(sa.Column("thang_diem", sa.String(length=100), nullable=True))
    if include_don_vi:
        columns.append(sa.Column("don_vi_cap", sa.String(length=255), nullable=True))
    columns.extend(
        [
            sa.Column(
                "trang_thai",
                sa.SmallInteger(),
                server_default="1",
                nullable=False,
                comment="0: ngừng sử dụng, 1: hoạt động",
            ),
            sa.Column("ghi_chu", sa.Text(), nullable=True),
            *_timestamps(),
        ]
    )
    return columns


def upgrade() -> None:
    op.create_table(
        "dm_bai_thi_danh_gia_nang_luc",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_bai_thi", sa.String(length=50), nullable=False),
        sa.Column("ten_bai_thi", sa.String(length=255), nullable=False),
        *_common_tail(include_loai=True, include_don_vi=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_bai_thi", name="uq_dm_bai_thi_danh_gia_nang_luc_ma"),
        **_TABLE_KW,
    )
    op.create_index("ix_dm_bai_thi_danh_gia_nang_luc_ma", "dm_bai_thi_danh_gia_nang_luc", ["ma_bai_thi"])
    op.create_index("ix_dm_bai_thi_danh_gia_nang_luc_ten", "dm_bai_thi_danh_gia_nang_luc", ["ten_bai_thi"])

    op.create_table(
        "dm_thanh_tich_hoc_tap_nghien_cuu",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ma_thanh_tich", sa.String(length=50), nullable=False),
        sa.Column("ten_thanh_tich", sa.String(length=255), nullable=False),
        *_common_tail(include_loai=False, include_don_vi=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ma_thanh_tich", name="uq_dm_thanh_tich_hoc_tap_nghien_cuu_ma"),
        **_TABLE_KW,
    )
    op.create_index(
        "ix_dm_thanh_tich_hoc_tap_nghien_cuu_ma",
        "dm_thanh_tich_hoc_tap_nghien_cuu",
        ["ma_thanh_tich"],
    )
    op.create_index(
        "ix_dm_thanh_tich_hoc_tap_nghien_cuu_ten",
        "dm_thanh_tich_hoc_tap_nghien_cuu",
        ["ten_thanh_tich"],
    )


def downgrade() -> None:
    op.drop_index("ix_dm_thanh_tich_hoc_tap_nghien_cuu_ten", table_name="dm_thanh_tich_hoc_tap_nghien_cuu")
    op.drop_index("ix_dm_thanh_tich_hoc_tap_nghien_cuu_ma", table_name="dm_thanh_tich_hoc_tap_nghien_cuu")
    op.drop_table("dm_thanh_tich_hoc_tap_nghien_cuu")
    op.drop_index("ix_dm_bai_thi_danh_gia_nang_luc_ten", table_name="dm_bai_thi_danh_gia_nang_luc")
    op.drop_index("ix_dm_bai_thi_danh_gia_nang_luc_ma", table_name="dm_bai_thi_danh_gia_nang_luc")
    op.drop_table("dm_bai_thi_danh_gia_nang_luc")
    if sa.inspect(op.get_bind()).has_table("dm_chung_chi_ngoai_ngu"):
        op.drop_index("ix_dm_chung_chi_ngoai_ngu_ten", table_name="dm_chung_chi_ngoai_ngu")
        op.drop_index("ix_dm_chung_chi_ngoai_ngu_ma", table_name="dm_chung_chi_ngoai_ngu")
        op.drop_table("dm_chung_chi_ngoai_ngu")
