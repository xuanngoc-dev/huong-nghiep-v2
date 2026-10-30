"""Gop dm_chung_chi_ngoai_ngu vao dm_bang_cap_chung_chi roi xoa bang cu.

Bang gop giu ten dm_bang_cap_chung_chi. Cot rieng cua bang cu
(ten_chi_tiet, linh_vuc, mon, thang_diem) duoc them vao. Ma va ten
duoc noi rong de khong cat du lieu cu. Trang thai 1/0 chuyen thanh
Hoat dong / Ngung su dung. created_at/updated_at sang tao_luc/cap_nhat_luc.

Revision ID: 20261030_0031
Revises: 20261030_0030
Create Date: 2026-10-30 10:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0031"
down_revision: Union[str, Sequence[str], None] = "20261030_0030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_bang_cap_chung_chi"
_LEGACY = "dm_chung_chi_ngoai_ngu"
_ADDED_COLUMNS = (
    (
        "ten_chi_tiet",
        sa.String(length=500),
        "Tên đầy đủ hoặc mô tả ngắn của chứng chỉ.",
    ),
    (
        "linh_vuc",
        sa.String(length=150),
        "Lĩnh vực của chứng chỉ.",
    ),
    (
        "mon",
        sa.String(length=150),
        "Môn hoặc nội dung được đánh giá.",
    ),
    (
        "thang_diem",
        sa.String(length=100),
        "Mô tả thang điểm bằng chữ, ví dụ 0-9 hoặc Bậc 1-6.",
    ),
)


def _columns(table: str) -> dict[str, dict]:
    return {item["name"]: item for item in sa.inspect(op.get_bind()).get_columns(table)}


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _widen(column: str, length: int, comment: str) -> None:
    current = _columns(_TABLE).get(column)
    if current is None:
        return
    current_length = getattr(current["type"], "length", None)
    if current_length is not None and current_length >= length:
        return
    op.alter_column(
        _TABLE,
        column,
        existing_type=sa.String(length=current_length or length),
        type_=sa.String(length=length),
        existing_nullable=current["nullable"],
        existing_comment=current.get("comment"),
        comment=comment,
    )


def _ensure_merged_columns() -> None:
    existing = _columns(_TABLE)
    for name, col_type, comment in _ADDED_COLUMNS:
        if name in existing:
            continue
        op.add_column(
            _TABLE,
            sa.Column(name, col_type, nullable=True, comment=comment),
        )
    _widen("ma_chung_chi", 50, "Mã định danh chứng chỉ trong hệ thống.")
    _widen("ten_chung_chi", 255, "Tên chứng chỉ.")
    op.execute(
        sa.text(
            "ALTER TABLE dm_bang_cap_chung_chi "
            "MODIFY tao_luc DATETIME NULL DEFAULT CURRENT_TIMESTAMP "
            "COMMENT 'Thời điểm tạo bản ghi.', "
            "MODIFY cap_nhat_luc DATETIME NULL DEFAULT CURRENT_TIMESTAMP "
            "ON UPDATE CURRENT_TIMESTAMP "
            "COMMENT 'Thời điểm cập nhật bản ghi gần nhất.'"
        )
    )


def _copy_legacy_certificates() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO dm_bang_cap_chung_chi (
                ma_chung_chi,
                ten_chung_chi,
                ten_chi_tiet,
                linh_vuc,
                mon,
                don_vi_cap,
                loai_chung_chi,
                thang_diem,
                trang_thai,
                ghi_chu,
                tao_luc,
                cap_nhat_luc
            )
            SELECT
                LEFT(ma_chung_chi, 50),
                LEFT(ten_chung_chi, 255),
                NULLIF(TRIM(ten_chi_tiet), ''),
                NULLIF(TRIM(linh_vuc), ''),
                NULLIF(TRIM(mon), ''),
                NULLIF(TRIM(don_vi_cap), ''),
                NULLIF(TRIM(loai_chung_chi), ''),
                NULLIF(TRIM(thang_diem), ''),
                CASE trang_thai
                    WHEN 0 THEN 'Ngừng sử dụng'
                    WHEN 1 THEN 'Hoạt động'
                    ELSE NULL
                END,
                ghi_chu,
                created_at,
                updated_at
            FROM dm_chung_chi_ngoai_ngu
            WHERE ma_chung_chi NOT IN (
                SELECT ma_chung_chi FROM (
                    SELECT ma_chung_chi
                    FROM dm_bang_cap_chung_chi
                    WHERE ma_chung_chi IS NOT NULL
                ) AS da_co
            )
            """
        )
    )


def _restore_legacy_table() -> None:
    if not _has_table(_LEGACY):
        op.create_table(
            _LEGACY,
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("ma_chung_chi", sa.String(length=50), nullable=False),
            sa.Column("ten_chung_chi", sa.String(length=255), nullable=False),
            sa.Column("ten_chi_tiet", sa.String(length=500), nullable=True),
            sa.Column("linh_vuc", sa.String(length=150), nullable=True),
            sa.Column("mon", sa.String(length=150), nullable=True),
            sa.Column(
                "loai_chung_chi",
                sa.String(length=20),
                nullable=False,
                comment="trong_nuoc hoặc quoc_te",
            ),
            sa.Column("thang_diem", sa.String(length=100), nullable=True),
            sa.Column("don_vi_cap", sa.String(length=255), nullable=True),
            sa.Column(
                "trang_thai",
                sa.SmallInteger(),
                server_default="1",
                nullable=False,
                comment="0: ngừng sử dụng, 1: hoạt động",
            ),
            sa.Column("ghi_chu", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("ma_chung_chi", name="uq_dm_chung_chi_ngoai_ngu_ma"),
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
            mysql_engine="InnoDB",
        )
        op.create_index("ix_dm_chung_chi_ngoai_ngu_ma", _LEGACY, ["ma_chung_chi"])
        op.create_index("ix_dm_chung_chi_ngoai_ngu_ten", _LEGACY, ["ten_chung_chi"])
    op.execute(
        sa.text(
            """
            INSERT INTO dm_chung_chi_ngoai_ngu (
                ma_chung_chi,
                ten_chung_chi,
                ten_chi_tiet,
                linh_vuc,
                mon,
                loai_chung_chi,
                thang_diem,
                don_vi_cap,
                trang_thai,
                ghi_chu,
                created_at,
                updated_at
            )
            SELECT
                LEFT(ma_chung_chi, 50),
                LEFT(ten_chung_chi, 255),
                ten_chi_tiet,
                linh_vuc,
                mon,
                COALESCE(NULLIF(LEFT(loai_chung_chi, 20), ''), 'trong_nuoc'),
                thang_diem,
                don_vi_cap,
                CASE
                    WHEN trang_thai IN ('Ngừng sử dụng', '0') THEN 0
                    ELSE 1
                END,
                ghi_chu,
                COALESCE(tao_luc, CURRENT_TIMESTAMP),
                COALESCE(cap_nhat_luc, CURRENT_TIMESTAMP)
            FROM dm_bang_cap_chung_chi
            WHERE ma_chung_chi IS NOT NULL
              AND ma_chung_chi NOT IN (
                SELECT ma_chung_chi FROM (
                    SELECT ma_chung_chi FROM dm_chung_chi_ngoai_ngu
                ) AS da_co
              )
            """
        )
    )


def _shrink(column: str, length: int, comment: str, nullable: bool) -> None:
    current = _columns(_TABLE).get(column)
    if current is None:
        return
    current_length = getattr(current["type"], "length", None)
    if current_length is None or current_length <= length:
        return
    too_long = op.get_bind().execute(
        sa.text(
            f"SELECT COUNT(*) FROM {_TABLE} WHERE CHAR_LENGTH({column}) > :limit"
        ),
        {"limit": length},
    ).scalar()
    if too_long:
        return
    op.alter_column(
        _TABLE,
        column,
        existing_type=sa.String(length=current_length),
        type_=sa.String(length=length),
        existing_nullable=nullable,
        existing_comment=current.get("comment"),
        comment=comment,
        nullable=nullable,
    )


def upgrade() -> None:
    """Them cot con thieu, chuyen du lieu bang cu, roi xoa bang khong dung."""
    if not _has_table(_TABLE):
        return
    _ensure_merged_columns()
    if _has_table(_LEGACY):
        _copy_legacy_certificates()
        op.drop_table(_LEGACY)


def downgrade() -> None:
    """Tao lai bang cu, copy du lieu da map, roi bo cot da gop."""
    if not _has_table(_TABLE):
        return
    present = _columns(_TABLE)
    if "ten_chi_tiet" in present:
        _restore_legacy_table()
    for name, _col_type, _comment in reversed(_ADDED_COLUMNS):
        if name in _columns(_TABLE):
            op.drop_column(_TABLE, name)
    _shrink("ma_chung_chi", 30, "Mã định danh chứng chỉ trong hệ thống.", True)
    _shrink("ten_chung_chi", 150, "Tên chứng chỉ.", False)
    op.execute(
        sa.text(
            "ALTER TABLE dm_bang_cap_chung_chi "
            "MODIFY tao_luc DATETIME NULL DEFAULT NULL "
            "COMMENT 'Thời điểm tạo bản ghi.', "
            "MODIFY cap_nhat_luc DATETIME NULL DEFAULT NULL "
            "COMMENT 'Thời điểm cập nhật bản ghi gần nhất.'"
        )
    )
