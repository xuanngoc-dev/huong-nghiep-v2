"""Đổi dats_phuong_thuc.phuong_thuc_id thành mã phương thức của Bộ.

Cột mới ma_phuong_thuc_cua_bo tham chiếu dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc.
Dữ liệu cũ được đối chiếu từ id sang mã trước khi xoá cột số.

Revision ID: 20261030_0034
Revises: 20261030_0033
Create Date: 2026-10-30 13:45:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0034"
down_revision: Union[str, Sequence[str], None] = "20261030_0033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_COMMENT = "Mã phương thức của Bộ; FK dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc."
_OLD_COMMENT = "Danh mục phương thức; FK dm_phuong_thuc_tuyen_sinh.id."


def _column_type(table: str, column: str) -> tuple[str, str, str]:
    row = op.get_bind().execute(
        sa.text(
            """
            SELECT COLUMN_TYPE, CHARACTER_SET_NAME, COLLATION_NAME
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
            """
        ),
        {"table_name": table, "column_name": column},
    ).one()
    return row[0], row[1], row[2]


def _ensure_ma_phuong_thuc_unique() -> None:
    inspector = sa.inspect(op.get_bind())
    unique_columns = [item.get("column_names") for item in inspector.get_unique_constraints("dm_phuong_thuc_tuyen_sinh")]
    unique_indexes = [
        item.get("column_names")
        for item in inspector.get_indexes("dm_phuong_thuc_tuyen_sinh")
        if item.get("unique")
    ]
    if ["ma_phuong_thuc"] in unique_columns or ["ma_phuong_thuc"] in unique_indexes:
        return
    op.create_unique_constraint(
        "uq_dm_phuong_thuc_tuyen_sinh_ma",
        "dm_phuong_thuc_tuyen_sinh",
        ["ma_phuong_thuc"],
    )


def _require_mapped(column: str, *, text: bool) -> None:
    blank = f" OR {column} = ''" if text else ""
    missing = op.get_bind().execute(
        sa.text(f"SELECT COUNT(*) FROM dats_phuong_thuc WHERE {column} IS NULL{blank}")
    ).scalar()
    if missing:
        raise RuntimeError(f"{missing} dòng dats_phuong_thuc không đối chiếu được {column}")


def _drop_fk_if_exists(name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item["name"] for item in inspector.get_foreign_keys("dats_phuong_thuc")}
    if name in names:
        op.drop_constraint(name, "dats_phuong_thuc", type_="foreignkey")


def _drop_index_if_exists(name: str) -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item["name"] for item in inspector.get_indexes("dats_phuong_thuc")}
    if name in names:
        op.drop_index(name, table_name="dats_phuong_thuc")


def _restore_program_fk() -> None:
    op.create_foreign_key(
        "fk_dats_phuong_thuc_de_an_chuong_trinh_id",
        "dats_phuong_thuc",
        "dats_chuong_trinh_dao_tao",
        ["de_an_chuong_trinh_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )


def upgrade() -> None:
    _ensure_ma_phuong_thuc_unique()
    column_type, charset, collation = _column_type("dm_phuong_thuc_tuyen_sinh", "ma_phuong_thuc")
    if not column_type.lower().startswith("varchar(") or not charset.replace("_", "").isalnum() or not collation.replace("_", "").isalnum():
        raise RuntimeError("Không đọc được kiểu cột dm_phuong_thuc_tuyen_sinh.ma_phuong_thuc")
    comment = _COMMENT.replace("'", "''")
    _drop_fk_if_exists("fk_dats_phuong_thuc_phuong_thuc_id")
    _drop_index_if_exists("idx_dats_phuong_thuc_phuong_thuc_id")
    op.execute(
        f"""
        ALTER TABLE dats_phuong_thuc
        ADD COLUMN ma_phuong_thuc_cua_bo {column_type}
        CHARACTER SET {charset} COLLATE {collation}
        NULL
        COMMENT '{comment}'
        AFTER de_an_chuong_trinh_id
        """
    )
    op.execute(
        sa.text(
            """
            UPDATE dats_phuong_thuc AS pt
            INNER JOIN dm_phuong_thuc_tuyen_sinh AS dm ON pt.phuong_thuc_id = dm.id
            SET pt.ma_phuong_thuc_cua_bo = dm.ma_phuong_thuc
            """
        )
    )
    _require_mapped("ma_phuong_thuc_cua_bo", text=True)
    op.alter_column(
        "dats_phuong_thuc",
        "ma_phuong_thuc_cua_bo",
        existing_type=sa.String(20),
        nullable=False,
        existing_comment=_COMMENT,
    )
    _drop_fk_if_exists("fk_dats_phuong_thuc_de_an_chuong_trinh_id")
    _drop_index_if_exists("idx_dats_phuong_thuc_de_an_chuong_trinh_id_phuong_thuc_id")
    op.drop_column("dats_phuong_thuc", "phuong_thuc_id")
    op.create_index(
        "idx_dats_phuong_thuc_de_an_chuong_trinh_id_ma_bo",
        "dats_phuong_thuc",
        ["de_an_chuong_trinh_id", "ma_phuong_thuc_cua_bo"],
    )
    op.create_index(
        "idx_dats_phuong_thuc_ma_phuong_thuc_cua_bo",
        "dats_phuong_thuc",
        ["ma_phuong_thuc_cua_bo"],
    )
    _restore_program_fk()
    op.create_foreign_key(
        "fk_dats_phuong_thuc_ma_phuong_thuc_cua_bo",
        "dats_phuong_thuc",
        "dm_phuong_thuc_tuyen_sinh",
        ["ma_phuong_thuc_cua_bo"],
        ["ma_phuong_thuc"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    _drop_fk_if_exists("fk_dats_phuong_thuc_ma_phuong_thuc_cua_bo")
    _drop_fk_if_exists("fk_dats_phuong_thuc_de_an_chuong_trinh_id")
    _drop_index_if_exists("idx_dats_phuong_thuc_de_an_chuong_trinh_id_ma_bo")
    _drop_index_if_exists("idx_dats_phuong_thuc_ma_phuong_thuc_cua_bo")
    op.add_column(
        "dats_phuong_thuc",
        sa.Column("phuong_thuc_id", sa.Integer(), nullable=True, comment=_OLD_COMMENT),
    )
    op.execute(
        sa.text(
            """
            UPDATE dats_phuong_thuc AS pt
            INNER JOIN dm_phuong_thuc_tuyen_sinh AS dm ON pt.ma_phuong_thuc_cua_bo = dm.ma_phuong_thuc
            SET pt.phuong_thuc_id = dm.id
            """
        )
    )
    _require_mapped("phuong_thuc_id", text=False)
    op.alter_column(
        "dats_phuong_thuc",
        "phuong_thuc_id",
        existing_type=sa.Integer(),
        nullable=False,
        existing_comment=_OLD_COMMENT,
    )
    op.drop_column("dats_phuong_thuc", "ma_phuong_thuc_cua_bo")
    op.create_index(
        "idx_dats_phuong_thuc_de_an_chuong_trinh_id_phuong_thuc_id",
        "dats_phuong_thuc",
        ["de_an_chuong_trinh_id", "phuong_thuc_id"],
    )
    op.create_index("idx_dats_phuong_thuc_phuong_thuc_id", "dats_phuong_thuc", ["phuong_thuc_id"])
    _restore_program_fk()
    op.create_foreign_key(
        "fk_dats_phuong_thuc_phuong_thuc_id",
        "dats_phuong_thuc",
        "dm_phuong_thuc_tuyen_sinh",
        ["phuong_thuc_id"],
        ["id"],
        onupdate="RESTRICT",
        ondelete="RESTRICT",
    )
