"""Lưu phiên nguồn, các bản nháp có dẫn chứng và nhật ký xét duyệt trong CMS."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

revision = "20261123_0066"
down_revision = "20261122_0065"
branch_labels = None
depends_on = None

_MYSQL = {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}


def upgrade() -> None:
    op.create_table(
        "dats_phien_thu_thap",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ma_truong", sa.String(20), sa.ForeignKey("dm_truong.ma_truong", onupdate="CASCADE"), nullable=False),
        sa.Column("nam_tuyen_sinh", sa.SmallInteger(), nullable=False),
        sa.Column("trang_thai", sa.String(24), nullable=False),
        sa.Column("tao_boi", sa.Integer(), sa.ForeignKey("nguoi_dung.id", ondelete="SET NULL")),
        sa.Column("tao_luc", sa.DateTime(), nullable=False),
        sa.Column("cap_nhat_luc", sa.DateTime(), nullable=False),
        sa.Column("sua_lan", sa.Integer(), nullable=False),
        sa.Column("phien_ban", sa.Integer()),
        sa.Column("nguon", sa.JSON(), nullable=False),
        sa.Column("canh_bao_nguon", sa.JSON(), nullable=False),
        sa.Column("yeu_cau_bo_sung", sa.JSON()),
        sa.Column("de_an_id", mysql.BIGINT(unsigned=True), sa.ForeignKey("dats_tuyen_sinh.id", ondelete="SET NULL")),
        sa.Column("duyet_boi", sa.Integer(), sa.ForeignKey("nguoi_dung.id", ondelete="SET NULL")),
        sa.Column("duyet_luc", sa.DateTime()),
        **_MYSQL,
    )
    op.create_index("idx_dats_thu_thap_trang_thai", "dats_phien_thu_thap", ["trang_thai", "cap_nhat_luc"])
    op.create_index("idx_dats_thu_thap_truong_nam", "dats_phien_thu_thap", ["ma_truong", "nam_tuyen_sinh"])
    op.create_table(
        "dats_ban_nhap_thu_thap",
        sa.Column("phien_id", sa.Integer(), sa.ForeignKey("dats_phien_thu_thap.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("phien_ban", sa.Integer(), primary_key=True),
        sa.Column("tao_luc", sa.DateTime(), nullable=False),
        sa.Column("ten_nguoi_tao", sa.String(150), nullable=False),
        sa.Column("du_lieu", sa.JSON(), nullable=False),
        sa.Column("muc", sa.JSON(), nullable=False),
        sa.Column("ghi_chu", sa.JSON(), nullable=False),
        sa.Column("nguon", sa.JSON(), nullable=False),
        **_MYSQL,
    )
    op.create_table(
        "dats_nhat_ky_thu_thap",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("phien_id", sa.Integer(), sa.ForeignKey("dats_phien_thu_thap.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phien_ban", sa.Integer()),
        sa.Column("hanh_dong", sa.String(30), nullable=False),
        sa.Column("nguoi_dung_id", sa.Integer(), sa.ForeignKey("nguoi_dung.id", ondelete="SET NULL")),
        sa.Column("nguoi_dung", sa.String(150), nullable=False),
        sa.Column("tao_luc", sa.DateTime(), nullable=False),
        sa.Column("chi_tiet", sa.JSON(), nullable=False),
        **_MYSQL,
    )
    op.create_index("idx_dats_nhat_ky_thu_thap_phien", "dats_nhat_ky_thu_thap", ["phien_id", "id"])


def downgrade() -> None:
    op.drop_table("dats_nhat_ky_thu_thap")
    op.drop_table("dats_ban_nhap_thu_thap")
    op.drop_table("dats_phien_thu_thap")
