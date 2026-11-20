"""dm_loai_cau_hoi: thêm cột doi_tuong_ap_dung và cho phép trùng thu_tu_uu_tien.

- doi_tuong_ap_dung: mảng JSON mã đối tượng theo app/constants/doi_tuong_ap_dung.py. Các loại câu hỏi
  đã có đang dùng cho luồng thi đại học & cao đẳng nên gán [1].
- thu_tu_uu_tien: bỏ ràng buộc unique (giữ index ix_dm_loai_cau_hoi_thu_tu để sắp xếp); trùng thứ tự thì
  loại tạo trước đứng trước.

Revision ID: 20261127_0070
Revises: 20261126_0069
Create Date: 2026-11-27 10:00:00.000000
"""

import sqlalchemy as sa
from alembic import op

revision = "20261127_0070"
down_revision = "20261126_0069"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dm_loai_cau_hoi", sa.Column("doi_tuong_ap_dung", sa.JSON(), nullable=True))
    op.execute("UPDATE dm_loai_cau_hoi SET doi_tuong_ap_dung = JSON_ARRAY(1) WHERE doi_tuong_ap_dung IS NULL")
    op.drop_constraint("uq_dm_loai_cau_hoi_thu_tu", "dm_loai_cau_hoi", type_="unique")


def downgrade() -> None:
    # Lỗi nếu đang có thu_tu_uu_tien trùng: sửa cho khác nhau trước khi downgrade.
    op.create_unique_constraint("uq_dm_loai_cau_hoi_thu_tu", "dm_loai_cau_hoi", ["thu_tu_uu_tien"])
    op.drop_column("dm_loai_cau_hoi", "doi_tuong_ap_dung")
