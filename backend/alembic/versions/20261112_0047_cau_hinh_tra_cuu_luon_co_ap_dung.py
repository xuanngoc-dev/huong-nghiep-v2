"""Dam bao luon co mot cau hinh tra cuu dang ap dung.

Neu bang co du lieu ma khong co dong nao trang_thai = 1 thi bat dong cap nhat gan nhat.

Revision ID: 20261112_0047
Revises: 20261112_0046
Create Date: 2026-11-12 17:00:00.000000
"""

from typing import Sequence, Union

from alembic import op

revision: str = "20261112_0047"
down_revision: Union[str, Sequence[str], None] = "20261112_0046"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # MySQL không cho UPDATE kèm subquery trên chính bảng đó, nên bọc thêm một lớp bảng dẫn xuất.
    op.execute(
        """
        UPDATE ht_cau_hinh_tra_cuu
        SET trang_thai = 1
        WHERE id = (
            SELECT id FROM (
                SELECT id FROM ht_cau_hinh_tra_cuu ORDER BY updated_at DESC, id DESC LIMIT 1
            ) AS gan_nhat
        )
        AND NOT EXISTS (
            SELECT 1 FROM (SELECT id FROM ht_cau_hinh_tra_cuu WHERE trang_thai = 1) AS dang_ap_dung
        )
        """
    )


def downgrade() -> None:
    # Chỉ sửa dữ liệu, không có gì để hoàn tác.
    pass
