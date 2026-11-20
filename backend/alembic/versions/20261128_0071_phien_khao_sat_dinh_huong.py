"""Thêm cột dinh_huong cho tn_phien_khao_sat: người dùng làm bài với định hướng nào.

Mã theo app/constants/doi_tuong_ap_dung.py (1: thi ĐH & CĐ, 2: đi làm ngay, ...). Trước đây chỉ có luồng khảo sát
của hướng thi đại học & cao đẳng nên các phiên đã có gán 1.

Revision ID: 20261128_0071
Revises: 20261127_0070
Create Date: 2026-11-28 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261128_0071"
down_revision = "20261127_0070"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tn_phien_khao_sat", sa.Column("dinh_huong", sa.SmallInteger(), nullable=True))
    op.create_index("ix_tn_phien_khao_sat_dinh_huong", "tn_phien_khao_sat", ["dinh_huong"])
    op.execute("UPDATE tn_phien_khao_sat SET dinh_huong = 1 WHERE dinh_huong IS NULL")


def downgrade() -> None:
    op.drop_index("ix_tn_phien_khao_sat_dinh_huong", table_name="tn_phien_khao_sat")
    op.drop_column("tn_phien_khao_sat", "dinh_huong")
