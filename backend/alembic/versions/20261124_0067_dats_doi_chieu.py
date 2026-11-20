"""Lưu căn cứ đối chiếu mã xét tuyển và xác nhận của từng bản nháp."""

import sqlalchemy as sa
from alembic import op

revision = "20261124_0067"
down_revision = "20261123_0066"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dats_ban_nhap_thu_thap", sa.Column("doi_chieu", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("dats_ban_nhap_thu_thap", "doi_chieu")
