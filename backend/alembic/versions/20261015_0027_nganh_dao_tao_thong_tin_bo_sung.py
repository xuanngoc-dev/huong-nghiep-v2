"""nganh_dao_tao_thong_tin_bo_sung

Revision ID: 20261015_0027
Revises: 20261015_0026
Create Date: 2026-10-15 13:50:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261015_0027"
down_revision: Union[str, Sequence[str], None] = "20261015_0026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("hinh_anh_mo_ta", sa.String(length=500), nullable=True, comment="URL hình ảnh mô tả"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("muc_luong_tham_khao", sa.String(length=255), nullable=True, comment="Mức lương tham khảo"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("nhan_dan", sa.String(length=100), nullable=True, comment="Nhãn dán nổi bật"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("thoi_gian_dao_tao", sa.String(length=100), nullable=True, comment="Thời gian đào tạo"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("chi_tiet", sa.Text(), nullable=True, comment="Chi tiết ngành"),
    )


def downgrade() -> None:
    op.drop_column("dm_nganh_dao_tao", "chi_tiet")
    op.drop_column("dm_nganh_dao_tao", "thoi_gian_dao_tao")
    op.drop_column("dm_nganh_dao_tao", "nhan_dan")
    op.drop_column("dm_nganh_dao_tao", "muc_luong_tham_khao")
    op.drop_column("dm_nganh_dao_tao", "hinh_anh_mo_ta")
