"""Gop dm_bai_thi_danh_gia_nang_luc vao dm_bai_thi_danh_gia roi xoa bang cu.

Bang gop giu ten dm_bai_thi_danh_gia. Cot rieng cua bang cu
(ten_chi_tiet, linh_vuc, mon, loai_chung_chi) duoc them vao.
thang_diem dang la so o bang moi, chu o bang cu, nen doi sang VARCHAR
de giu mo ta nhu 0-150. Ma duoc noi rong. Trang thai 1/0 chuyen thanh
Hoat dong / Ngung su dung. created_at/updated_at sang tao_luc/cap_nhat_luc.

Revision ID: 20261030_0032
Revises: 20261030_0031
Create Date: 2026-10-30 10:20:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261030_0032"
down_revision: Union[str, Sequence[str], None] = "20261030_0031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_bai_thi_danh_gia"
_LEGACY = "dm_bai_thi_danh_gia_nang_luc"
_UNIQUE = "uk_dm_bai_thi_danh_gia_ma_bai_thi"
_ADDED_COLUMNS = (
    (
        "ten_chi_tiet",
        sa.String(length=500),
        "Tên đầy đủ hoặc mô tả ngắn của bài thi.",
    ),
    (
        "linh_vuc",
        sa.String(length=150),
        "Lĩnh vực của bài thi.",
    ),
    (
        "mon",
        sa.String(length=150),
        "Môn hoặc nội dung được đánh giá.",
    ),
    (
        "loai_chung_chi",
        sa.String(length=50),
        "Nhóm trong nước hoặc quốc tế: trong_nuoc, quoc_te.",
    ),
)


def _columns(table: str) -> dict[str, dict]:
    return {item["name"]: item for item in sa.inspect(op.get_bind()).get_columns(table)}


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _is_text_type(column_type: object) -> bool:
    name = type(column_type).__name__.lower()
    return "char" in name or "string" in name or "text" in name


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


def _ensure_text_score() -> None:
    current = _columns(_TABLE).get("thang_diem")
    if current is None or _is_text_type(current["type"]):
        return
    op.execute(
        sa.text(
            "ALTER TABLE dm_bai_thi_danh_gia "
            "MODIFY thang_diem VARCHAR(100) NULL "
            "COMMENT 'Mô tả thang điểm bằng chữ, ví dụ 0-150 hoặc 400-1600.'"
        )
    )


def _ensure_unique_code() -> None:
    inspector = sa.inspect(op.get_bind())
    names = {item["name"] for item in inspector.get_unique_constraints(_TABLE)}
    if _UNIQUE in names:
        return
    duplicated = op.get_bind().execute(
        sa.text(
            "SELECT ma_bai_thi FROM dm_bai_thi_danh_gia "
            "WHERE ma_bai_thi IS NOT NULL "
            "GROUP BY ma_bai_thi HAVING COUNT(*) > 1 "
            "LIMIT 1"
        )
    ).scalar()
    if duplicated:
        raise RuntimeError(f"Không gộp được vì mã bài thi bị trùng: {duplicated}")
    op.create_unique_constraint(_UNIQUE, _TABLE, ["ma_bai_thi"])


def _ensure_merged_columns() -> None:
    existing = _columns(_TABLE)
    for name, col_type, comment in _ADDED_COLUMNS:
        if name in existing:
            continue
        op.add_column(
            _TABLE,
            sa.Column(name, col_type, nullable=True, comment=comment),
        )
    _widen("ma_bai_thi", 50, "Mã định danh bài thi trong hệ thống.")
    _ensure_text_score()
    _ensure_unique_code()
    op.execute(
        sa.text(
            "ALTER TABLE dm_bai_thi_danh_gia "
            "MODIFY tao_luc DATETIME NULL DEFAULT CURRENT_TIMESTAMP "
            "COMMENT 'Thời điểm tạo bản ghi.', "
            "MODIFY cap_nhat_luc DATETIME NULL DEFAULT CURRENT_TIMESTAMP "
            "ON UPDATE CURRENT_TIMESTAMP "
            "COMMENT 'Thời điểm cập nhật bản ghi gần nhất.'"
        )
    )


def _copy_legacy_exams() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO dm_bai_thi_danh_gia (
                ma_bai_thi,
                ten_bai_thi,
                ten_chi_tiet,
                linh_vuc,
                mon,
                loai_chung_chi,
                thang_diem,
                trang_thai,
                ghi_chu,
                tao_luc,
                cap_nhat_luc
            )
            SELECT
                LEFT(ma_bai_thi, 50),
                LEFT(ten_bai_thi, 255),
                NULLIF(TRIM(ten_chi_tiet), ''),
                NULLIF(TRIM(linh_vuc), ''),
                NULLIF(TRIM(mon), ''),
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
            FROM dm_bai_thi_danh_gia_nang_luc
            WHERE ma_bai_thi NOT IN (
                SELECT ma_bai_thi FROM (
                    SELECT ma_bai_thi
                    FROM dm_bai_thi_danh_gia
                    WHERE ma_bai_thi IS NOT NULL
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
            sa.Column("ma_bai_thi", sa.String(length=50), nullable=False),
            sa.Column("ten_bai_thi", sa.String(length=255), nullable=False),
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
            sa.UniqueConstraint("ma_bai_thi", name="uq_dm_bai_thi_danh_gia_nang_luc_ma"),
            mysql_charset="utf8mb4",
            mysql_collate="utf8mb4_unicode_ci",
            mysql_engine="InnoDB",
        )
        op.create_index("ix_dm_bai_thi_danh_gia_nang_luc_ma", _LEGACY, ["ma_bai_thi"])
        op.create_index("ix_dm_bai_thi_danh_gia_nang_luc_ten", _LEGACY, ["ten_bai_thi"])
    op.execute(
        sa.text(
            """
            INSERT INTO dm_bai_thi_danh_gia_nang_luc (
                ma_bai_thi,
                ten_bai_thi,
                ten_chi_tiet,
                linh_vuc,
                mon,
                loai_chung_chi,
                thang_diem,
                trang_thai,
                ghi_chu,
                created_at,
                updated_at
            )
            SELECT
                LEFT(ma_bai_thi, 50),
                LEFT(ten_bai_thi, 255),
                ten_chi_tiet,
                linh_vuc,
                mon,
                COALESCE(NULLIF(LEFT(loai_chung_chi, 20), ''), 'trong_nuoc'),
                thang_diem,
                CASE
                    WHEN trang_thai IN ('Ngừng sử dụng', '0') THEN 0
                    ELSE 1
                END,
                ghi_chu,
                COALESCE(tao_luc, CURRENT_TIMESTAMP),
                COALESCE(cap_nhat_luc, CURRENT_TIMESTAMP)
            FROM dm_bai_thi_danh_gia
            WHERE ma_bai_thi IS NOT NULL
              AND ma_bai_thi NOT IN (
                SELECT ma_bai_thi FROM (
                    SELECT ma_bai_thi FROM dm_bai_thi_danh_gia_nang_luc
                ) AS da_co
              )
            """
        )
    )


def _restore_numeric_score() -> None:
    current = _columns(_TABLE).get("thang_diem")
    if current is None or not _is_text_type(current["type"]):
        return
    op.execute(
        sa.text(
            "UPDATE dm_bai_thi_danh_gia "
            "SET thang_diem = NULL "
            "WHERE thang_diem IS NOT NULL "
            "AND thang_diem NOT REGEXP '^[0-9]+(\\\\.[0-9]+)?$'"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE dm_bai_thi_danh_gia "
            "MODIFY thang_diem DECIMAL(8,2) NULL "
            "COMMENT 'Điểm tối đa của bài thi.'"
        )
    )


def _drop_unique_code() -> None:
    names = {item["name"] for item in sa.inspect(op.get_bind()).get_unique_constraints(_TABLE)}
    if _UNIQUE not in names:
        return
    op.drop_constraint(_UNIQUE, _TABLE, type_="unique")


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
        _copy_legacy_exams()
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
    _restore_numeric_score()
    _drop_unique_code()
    _shrink("ma_bai_thi", 30, "Mã định danh bài thi trong hệ thống.", True)
    op.execute(
        sa.text(
            "ALTER TABLE dm_bai_thi_danh_gia "
            "MODIFY tao_luc DATETIME NULL DEFAULT NULL "
            "COMMENT 'Thời điểm tạo bản ghi.', "
            "MODIFY cap_nhat_luc DATETIME NULL DEFAULT NULL "
            "COMMENT 'Thời điểm cập nhật bản ghi gần nhất.'"
        )
    )
