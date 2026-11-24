"""Nghề cụ thể đi làm: lộ trình phát triển chuyển từ chữ sang danh sách giai đoạn (JSON).

- dm_nghe_cu_the_di_lam.lo_trinh_phat_trien: TEXT → JSON, mảng
  [{giai_doan, mo_ta_cong_viec, luong_trung_binh_min, luong_trung_binh_max, ghi_chu}] (lương: số nguyên VND).
- Dữ liệu cũ "Thợ phụ → Thợ hàn 3G → Tổ trưởng." được tách theo "→" / "->" / "=>" thành các giai đoạn (chỉ có tên,
  phần chi tiết để trống chờ quản trị nhập). Chuỗi rỗng → NULL.
- Downgrade: JSON → TEXT, ghép lại tên giai đoạn bằng " → " (mất mô tả, lương, ghi chú của từng giai đoạn).

Revision ID: 20261213_0086
Revises: 20261212_0085
Create Date: 2026-12-13 10:00:00.000000
"""

import json
import re

import sqlalchemy as sa
from alembic import op

revision = "20261213_0086"
down_revision = "20261212_0085"
branch_labels = None
depends_on = None

BANG = "dm_nghe_cu_the_di_lam"
COT = "lo_trinh_phat_trien"


def _tach(value: str) -> list[dict]:
    buoc = [phan.strip().rstrip(".").strip() for phan in re.split(r"→|->|=>", value)]
    return [
        {"giai_doan": ten, "mo_ta_cong_viec": None, "luong_trung_binh_min": None, "luong_trung_binh_max": None,
         "ghi_chu": None}
        for ten in buoc
        if ten
    ]


def _ghep(value) -> str | None:
    if isinstance(value, str):
        value = json.loads(value)
    ten = [str(buoc.get("giai_doan") or "").strip() for buoc in value or [] if isinstance(buoc, dict)]
    return " → ".join(t for t in ten if t) or None


def upgrade() -> None:
    conn = op.get_bind()
    bang = sa.table(BANG, sa.column("id", sa.Integer), sa.column(COT, sa.Text))
    rows = conn.execute(sa.select(bang.c.id, bang.c[COT]).where(bang.c[COT].is_not(None))).all()
    # Đổi nội dung sang chuỗi JSON hợp lệ trước, rồi mới đổi kiểu cột (MySQL kiểm tra JSON khi ALTER).
    for row_id, value in rows:
        buoc = _tach(value)
        conn.execute(
            sa.update(bang)
            .where(bang.c.id == row_id)
            .values({COT: json.dumps(buoc, ensure_ascii=False) if buoc else None})
        )
    op.alter_column(BANG, COT, existing_type=sa.Text(), type_=sa.JSON(), existing_nullable=True)


def downgrade() -> None:
    op.alter_column(BANG, COT, existing_type=sa.JSON(), type_=sa.Text(), existing_nullable=True)
    conn = op.get_bind()
    bang = sa.table(BANG, sa.column("id", sa.Integer), sa.column(COT, sa.Text))
    rows = conn.execute(sa.select(bang.c.id, bang.c[COT]).where(bang.c[COT].is_not(None))).all()
    for row_id, value in rows:
        conn.execute(sa.update(bang).where(bang.c.id == row_id).values({COT: _ghep(value)}))
