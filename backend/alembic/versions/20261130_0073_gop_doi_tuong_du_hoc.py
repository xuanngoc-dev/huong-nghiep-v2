"""Gộp đối tượng áp dụng 4 (du học) vào 3 (du học nghề): hai hướng đi giờ chung một nhóm "Du học".

- dm_loai_cau_hoi.doi_tuong_ap_dung: mảng chứa 4 đổi thành 3 (bỏ trùng, sắp xếp tăng dần như schema).
- tn_phien_khao_sat.dinh_huong: 4 → 3.

Downgrade không tách lại được (không biết bản ghi nào vốn là 4) nên để trống.

Revision ID: 20261130_0073
Revises: 20261129_0072
Create Date: 2026-11-30 10:00:00.000000
"""

import json

import sqlalchemy as sa
from alembic import op

revision = "20261130_0073"
down_revision = "20261129_0072"
branch_labels = None
depends_on = None

MA_CU = 4
MA_MOI = 3


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text("SELECT id, doi_tuong_ap_dung FROM dm_loai_cau_hoi WHERE JSON_CONTAINS(doi_tuong_ap_dung, :ma) = 1"),
        {"ma": str(MA_CU)},
    ).all()
    for item_id, gia_tri in rows:
        ds = json.loads(gia_tri) if isinstance(gia_tri, str) else gia_tri
        moi = sorted({MA_MOI if ma == MA_CU else ma for ma in ds})
        bind.execute(
            sa.text("UPDATE dm_loai_cau_hoi SET doi_tuong_ap_dung = CAST(:gia_tri AS JSON) WHERE id = :id"),
            {"gia_tri": json.dumps(moi), "id": item_id},
        )

    op.execute(f"UPDATE tn_phien_khao_sat SET dinh_huong = {MA_MOI} WHERE dinh_huong = {MA_CU}")


def downgrade() -> None:
    pass
