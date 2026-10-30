"""Giữ revision 20261014_0024 trong chuỗi migration.

Không tạo dm_truong_dai_hoc. Danh mục trường là dm_truong, tạo ở
20261030_0028. Bản đã áp dụng revision này trước khi gộp không chạy lại
upgrade, nên dữ liệu đã chuyển sang dm_truong không bị ảnh hưởng.

Revision ID: 20261014_0024
Revises: 20261012_0023
Create Date: 2026-10-14 15:54:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261014_0024"
down_revision: Union[str, Sequence[str], None] = "20261012_0023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Không tạo dm_truong_dai_hoc."""


def downgrade() -> None:
    """Xóa bảng cũ nếu bản rollback của 0029 vừa tạo lại."""
    if sa.inspect(op.get_bind()).has_table("dm_truong_dai_hoc"):
        op.drop_table("dm_truong_dai_hoc")
