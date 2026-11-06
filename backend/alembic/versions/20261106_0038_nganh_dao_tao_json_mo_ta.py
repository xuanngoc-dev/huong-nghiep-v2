"""nganh dao tao: mo ta cong viec, lo trinh va muc luong dang JSON.

Revision ID: 20261106_0038
Revises: 20261105_0037
Create Date: 2026-11-06 08:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261106_0038"
down_revision: Union[str, Sequence[str], None] = "20261105_0037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COMMENT = "Mảng object {name, value}"


def upgrade() -> None:
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("mo_ta_cong_viec", sa.JSON(), nullable=True, comment=f"Mô tả công việc. {_COMMENT}"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("lo_trinh_phat_trien", sa.JSON(), nullable=True, comment=f"Lộ trình phát triển. {_COMMENT}"),
    )
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("muc_luong_tham_khao_json", sa.JSON(), nullable=True, comment=f"Mức lương tham khảo. {_COMMENT}"),
    )
    op.execute(
        sa.text(
            """
            UPDATE dm_nganh_dao_tao
            SET muc_luong_tham_khao_json = CASE
                WHEN muc_luong_tham_khao IS NULL OR TRIM(muc_luong_tham_khao) = '' THEN NULL
                ELSE JSON_ARRAY(JSON_OBJECT('name', 'Tham khảo', 'value', muc_luong_tham_khao))
            END
            """
        )
    )
    op.drop_column("dm_nganh_dao_tao", "muc_luong_tham_khao")
    op.alter_column(
        "dm_nganh_dao_tao",
        "muc_luong_tham_khao_json",
        new_column_name="muc_luong_tham_khao",
        existing_type=sa.JSON(),
        existing_nullable=True,
        comment=f"Mức lương tham khảo. {_COMMENT}",
    )


def downgrade() -> None:
    op.add_column(
        "dm_nganh_dao_tao",
        sa.Column("muc_luong_tham_khao_text", sa.String(length=255), nullable=True, comment="Mức lương tham khảo"),
    )
    op.execute(
        sa.text(
            """
            UPDATE dm_nganh_dao_tao
            SET muc_luong_tham_khao_text = NULLIF(
                LEFT(COALESCE(JSON_UNQUOTE(JSON_EXTRACT(muc_luong_tham_khao, '$[0].value')), ''), 255),
                ''
            )
            """
        )
    )
    op.drop_column("dm_nganh_dao_tao", "muc_luong_tham_khao")
    op.alter_column(
        "dm_nganh_dao_tao",
        "muc_luong_tham_khao_text",
        new_column_name="muc_luong_tham_khao",
        existing_type=sa.String(length=255),
        existing_nullable=True,
        comment="Mức lương tham khảo",
    )
    op.drop_column("dm_nganh_dao_tao", "lo_trinh_phat_trien")
    op.drop_column("dm_nganh_dao_tao", "mo_ta_cong_viec")
