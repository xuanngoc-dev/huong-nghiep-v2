"""Them loai_tra_loi va danh_sach_tieu_de_cau_tra_loi vao dm_loai_cau_hoi.

- loai_tra_loi: diem_so (chon muc diem) | tinh_huong (chon phuong an theo tinh huong); mac dinh diem_so.
- danh_sach_tieu_de_cau_tra_loi: JSON mang [{tieu_de, diem}] cac cau tra loi dung chung cho loai, vd. thang muc do.

Revision ID: 20261121_0063
Revises: 20261120_0062
Create Date: 2026-11-21 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261121_0063"
down_revision: Union[str, Sequence[str], None] = "20261120_0062"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = "dm_loai_cau_hoi"


def _columns() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(_TABLE)}


def upgrade() -> None:
    existing = _columns()
    if "loai_tra_loi" not in existing:
        op.add_column(
            _TABLE,
            sa.Column(
                "loai_tra_loi",
                sa.Enum("diem_so", "tinh_huong", name="loai_tra_loi"),
                nullable=False,
                server_default="diem_so",
                comment="Loại trả lời: diem_so (chọn mức điểm), tinh_huong (chọn phương án theo tình huống)",
            ),
        )
    if "danh_sach_tieu_de_cau_tra_loi" not in existing:
        op.add_column(
            _TABLE,
            sa.Column(
                "danh_sach_tieu_de_cau_tra_loi",
                sa.JSON(),
                nullable=True,
                comment="Mảng câu trả lời dùng chung cho loại câu hỏi: [{tieu_de, diem}]",
            ),
        )


def downgrade() -> None:
    existing = _columns()
    for name in ("danh_sach_tieu_de_cau_tra_loi", "loai_tra_loi"):
        if name in existing:
            op.drop_column(_TABLE, name)
