"""Diem cong doi tuong uu tien tu nam 2026 theo Thong tu 06/2026/TT-BGDDT (buoc 5.2 KE_HOACH_TRIEN_KHAI.md).

Chu du an da duyet: tu 2026, UT1 = doi tuong 01-03 cong 2,0; UT2 = 04-06 cong 1,0; doi tuong 07 khong con duoc cong.
Danh muc dm_doi_tuong_uu_tien giu nguyen (01-04 = 2,0; 05-07 = 1,0) de cac nam <= 2025 van tinh nhu cu; chi them
muc theo nam vao dm_muc_diem_uu_tien cho cac ma doi gia tri (04, 07). Khu vuc uu tien khong doi.

Revision ID: 20261120_0062
Revises: 20261120_0061
Create Date: 2026-11-20 10:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20261120_0062"
down_revision: Union[str, Sequence[str], None] = "20261120_0061"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

CAN_CU = "Thông tư 06/2026/TT-BGDĐT, Phụ lục II"
NAM = 2026
# (mã đối tượng, điểm cộng từ năm 2026)
MUC = [("04", 1.0), ("07", 0.0)]

_bang = sa.table(
    "dm_muc_diem_uu_tien",
    sa.column("loai", sa.String),
    sa.column("ma", sa.String),
    sa.column("nam_ap_dung_tu", sa.Integer),
    sa.column("diem_cong", sa.Numeric),
    sa.column("can_cu", sa.String),
    sa.column("ghi_chu", sa.Text),
)


def upgrade() -> None:
    bind = op.get_bind()
    for ma, diem in MUC:
        # Chạy lại được: bỏ qua mã đã có mức từ năm 2026 (kể cả do quản trị viên tự nhập).
        da_co = bind.execute(
            sa.select(sa.func.count())
            .select_from(_bang)
            .where(_bang.c.loai == "DOI_TUONG", _bang.c.ma == ma, _bang.c.nam_ap_dung_tu == NAM)
        ).scalar()
        if not da_co:
            op.bulk_insert(
                _bang,
                [
                    {
                        "loai": "DOI_TUONG",
                        "ma": ma,
                        "nam_ap_dung_tu": NAM,
                        "diem_cong": diem,
                        "can_cu": CAN_CU,
                        "ghi_chu": "Thêm bởi migration 20261120_0062",
                    }
                ],
            )


def downgrade() -> None:
    op.execute(
        _bang.delete().where(
            _bang.c.loai == "DOI_TUONG",
            _bang.c.ma.in_([ma for ma, _ in MUC]),
            _bang.c.nam_ap_dung_tu == NAM,
            _bang.c.can_cu == CAN_CU,
        )
    )
