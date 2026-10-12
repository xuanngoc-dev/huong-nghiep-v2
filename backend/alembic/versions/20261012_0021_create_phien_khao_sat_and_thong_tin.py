"""create_phien_khao_sat_chi_tiet_tra_loi_nguoi_dung_thong_tin

Revision ID: 20261012_0021
Revises: 20261010_0020
Create Date: 2026-10-12 17:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261012_0021"
down_revision: Union[str, Sequence[str], None] = "20261010_0020"
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


def upgrade() -> None:
    op.create_table(
        "tn_phien_khao_sat",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ssid", sa.String(length=64), nullable=False),
        sa.Column("nguoi_khao_sat_id", sa.Integer(), nullable=True),
        sa.Column("ma_giao_dich", sa.String(length=64), nullable=True),
        sa.Column("chi_tiet_ket_qua", sa.JSON(), nullable=True),
        sa.Column("thong_tin_thanh_toan", sa.JSON(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ssid", name="uq_tn_phien_khao_sat_ssid"),
        sa.UniqueConstraint("ma_giao_dich", name="uq_tn_phien_khao_sat_ma_gd"),
        sa.ForeignKeyConstraint(
            ["nguoi_khao_sat_id"],
            ["nguoi_dung.id"],
            name="fk_tn_phien_khao_sat_nguoi_dung",
            ondelete="SET NULL",
        ),
        **_TABLE_KW,
    )
    op.create_index(
        "ix_tn_phien_khao_sat_nguoi",
        "tn_phien_khao_sat",
        ["nguoi_khao_sat_id"],
    )

    op.create_table(
        "tn_chi_tiet_tra_loi",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("ssid", sa.String(length=64), nullable=False),
        sa.Column("loai_cau_hoi_id", sa.Integer(), nullable=False),
        sa.Column("cau_hoi_id", sa.Integer(), nullable=False),
        sa.Column("cau_tra_loi_id", sa.Integer(), nullable=False),
        sa.Column("diem_dat_duoc", sa.Integer(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["ssid"],
            ["tn_phien_khao_sat.ssid"],
            name="fk_tn_chi_tiet_tra_loi_phien",
            onupdate="CASCADE",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["loai_cau_hoi_id"],
            ["dm_loai_cau_hoi.id"],
            name="fk_tn_chi_tiet_tra_loi_loai",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cau_hoi_id"],
            ["tn_cau_hoi_trac_nghiem.id"],
            name="fk_tn_chi_tiet_tra_loi_cau_hoi",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["cau_tra_loi_id"],
            ["tn_cau_tra_loi.id"],
            name="fk_tn_chi_tiet_tra_loi_tra_loi",
            ondelete="RESTRICT",
        ),
        **_TABLE_KW,
    )
    op.create_index("ix_tn_chi_tiet_tra_loi_ssid", "tn_chi_tiet_tra_loi", ["ssid"])
    op.create_index("ix_tn_chi_tiet_tra_loi_loai", "tn_chi_tiet_tra_loi", ["loai_cau_hoi_id"])
    op.create_index("ix_tn_chi_tiet_tra_loi_cau_hoi", "tn_chi_tiet_tra_loi", ["cau_hoi_id"])
    op.create_index(
        "ix_tn_chi_tiet_tra_loi_tra_loi",
        "tn_chi_tiet_tra_loi",
        ["cau_tra_loi_id"],
    )

    op.create_table(
        "nguoi_dung_thong_tin",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nguoi_dung_id", sa.Integer(), nullable=False),
        sa.Column(
            "gioi_tinh",
            sa.SmallInteger(),
            nullable=True,
            comment="1: nam, 2: nữ, 3: khác",
        ),
        sa.Column("ngay_sinh", sa.Date(), nullable=True),
        sa.Column("dan_toc", sa.String(length=150), nullable=True),
        sa.Column("ton_giao", sa.String(length=150), nullable=True),
        sa.Column("trinh_do_hoc_van", sa.JSON(), nullable=True),
        sa.Column("suc_khoe_the_chat", sa.JSON(), nullable=True),
        sa.Column("kha_nang_tai_chinh", sa.JSON(), nullable=True),
        sa.Column("tinh_thanh_id", sa.Integer(), nullable=True),
        sa.Column("edu_coin", sa.Integer(), server_default="0", nullable=False),
        sa.Column("xu_he_thong", sa.Integer(), server_default="0", nullable=False),
        sa.Column("mat_khau_thanh_toan", sa.String(length=255), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nguoi_dung_id", name="uq_nguoi_dung_thong_tin_user"),
        sa.ForeignKeyConstraint(
            ["nguoi_dung_id"],
            ["nguoi_dung.id"],
            name="fk_nguoi_dung_thong_tin_user",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tinh_thanh_id"],
            ["dm_tinh_thanh.id"],
            name="fk_nguoi_dung_thong_tin_tinh",
            ondelete="SET NULL",
        ),
        **_TABLE_KW,
    )
    op.create_index(
        "ix_nguoi_dung_thong_tin_tinh",
        "nguoi_dung_thong_tin",
        ["tinh_thanh_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_nguoi_dung_thong_tin_tinh", table_name="nguoi_dung_thong_tin")
    op.drop_table("nguoi_dung_thong_tin")

    op.drop_index("ix_tn_chi_tiet_tra_loi_tra_loi", table_name="tn_chi_tiet_tra_loi")
    op.drop_index("ix_tn_chi_tiet_tra_loi_cau_hoi", table_name="tn_chi_tiet_tra_loi")
    op.drop_index("ix_tn_chi_tiet_tra_loi_loai", table_name="tn_chi_tiet_tra_loi")
    op.drop_index("ix_tn_chi_tiet_tra_loi_ssid", table_name="tn_chi_tiet_tra_loi")
    op.drop_table("tn_chi_tiet_tra_loi")

    op.drop_index("ix_tn_phien_khao_sat_nguoi", table_name="tn_phien_khao_sat")
    op.drop_table("tn_phien_khao_sat")
