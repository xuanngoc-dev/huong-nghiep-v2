"""dats_tuyen_sinh: dùng ma_truong thay cho truong_id.

Revision ID: 20261106_0039
Revises: 20261106_0038
Create Date: 2026-11-06 10:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT

revision: str = "20261106_0039"
down_revision: Union[str, Sequence[str], None] = "20261106_0038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dats_tuyen_sinh",
        sa.Column(
            "ma_truong",
            sa.String(length=20),
            nullable=True,
            comment="Mã trường; khóa ngoại đến dm_truong.ma_truong.",
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE dats_tuyen_sinh AS de_an
            JOIN dm_truong AS truong ON de_an.truong_id = truong.id
            SET de_an.ma_truong = truong.ma_truong
            """
        )
    )
    missing = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM dats_tuyen_sinh WHERE ma_truong IS NULL OR ma_truong = ''")
    ).scalar()
    if missing:
        raise RuntimeError(f"Không gán được mã trường cho {missing} đề án tuyển sinh")

    op.drop_constraint("fk_dats_tuyen_sinh_truong_id", "dats_tuyen_sinh", type_="foreignkey")
    op.drop_index("idx_dats_tuyen_sinh_truong_id_nam_tuyen_sinh", table_name="dats_tuyen_sinh")
    op.drop_column("dats_tuyen_sinh", "truong_id")
    op.alter_column(
        "dats_tuyen_sinh",
        "ma_truong",
        existing_type=sa.String(length=20),
        nullable=False,
        existing_comment="Mã trường; khóa ngoại đến dm_truong.ma_truong.",
    )
    op.create_index(
        "idx_dats_tuyen_sinh_ma_truong_nam_tuyen_sinh",
        "dats_tuyen_sinh",
        ["ma_truong", "nam_tuyen_sinh"],
    )
    op.create_foreign_key(
        "fk_dats_tuyen_sinh_ma_truong",
        "dats_tuyen_sinh",
        "dm_truong",
        ["ma_truong"],
        ["ma_truong"],
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.add_column(
        "dats_tuyen_sinh",
        sa.Column(
            "truong_id",
            BIGINT(unsigned=True),
            nullable=True,
            comment="Đơn vị đào tạo; khóa ngoại đến dm_truong.id.",
        ),
    )
    op.execute(
        sa.text(
            """
            UPDATE dats_tuyen_sinh AS de_an
            JOIN dm_truong AS truong ON de_an.ma_truong = truong.ma_truong
            SET de_an.truong_id = truong.id
            """
        )
    )
    op.drop_constraint("fk_dats_tuyen_sinh_ma_truong", "dats_tuyen_sinh", type_="foreignkey")
    op.drop_index("idx_dats_tuyen_sinh_ma_truong_nam_tuyen_sinh", table_name="dats_tuyen_sinh")
    op.drop_column("dats_tuyen_sinh", "ma_truong")
    op.alter_column(
        "dats_tuyen_sinh",
        "truong_id",
        existing_type=sa.BigInteger(),
        nullable=False,
        existing_comment="Đơn vị đào tạo; khóa ngoại đến dm_truong.id.",
    )
    op.create_index(
        "idx_dats_tuyen_sinh_truong_id_nam_tuyen_sinh",
        "dats_tuyen_sinh",
        ["truong_id", "nam_tuyen_sinh"],
    )
    op.create_foreign_key(
        "fk_dats_tuyen_sinh_truong_id",
        "dats_tuyen_sinh",
        "dm_truong",
        ["truong_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
