"""nguoi_dung_utf8mb4

Revision ID: 20261009_0002
Revises: 20261009_0001
Create Date: 2026-10-09 16:55:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20261009_0002"
down_revision: Union[str, Sequence[str], None] = "20261009_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE nguoi_dung "
        "CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE nguoi_dung "
        "CONVERT TO CHARACTER SET latin1 COLLATE latin1_swedish_ci"
    )
