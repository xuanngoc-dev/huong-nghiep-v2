"""Lưu thời điểm bắt đầu và tiến độ tạo bản nháp đề án."""

import sqlalchemy as sa
from alembic import op

revision = "20261125_0068"
down_revision = "20261124_0067"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dats_phien_thu_thap", sa.Column("bat_dau_tao_ban_nhap_luc", sa.DateTime(), nullable=True))
    op.add_column("dats_phien_thu_thap", sa.Column("tien_do_tao_ban_nhap", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("dats_phien_thu_thap", "tien_do_tao_ban_nhap")
    op.drop_column("dats_phien_thu_thap", "bat_dau_tao_ban_nhap_luc")
