"""Tao bang dm_muc_diem_uu_tien: muc diem cong khu vuc / doi tuong uu tien theo nam (buoc 5.1 KE_HOACH_TRIEN_KHAI.md).

dm_khu_vuc_uu_tien.ma_khu_vuc va dm_doi_tuong_uu_tien.ma_doi_tuong la UNIQUE va duoc hs_ho_so,
nguoi_dung_thong_tin tham chieu bang id, nen khong them dong moi cho tung nam duoc. Bang nay ghi muc diem theo
khoang nam; bo tinh lay dong khop nam tuyen sinh, khong co thi dung diem_cong cua danh muc.

Revision ID: 20261120_0061
Revises: 20261119_0060
Create Date: 2026-11-20 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT

revision: str = "20261120_0061"
down_revision: Union[str, Sequence[str], None] = "20261119_0060"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BANG = "dm_muc_diem_uu_tien"


def upgrade() -> None:
    # Chạy lại được sau khi lỗi giữa chừng (MySQL không rollback DDL).
    if sa.inspect(op.get_bind()).has_table(_BANG):
        return
    op.create_table(
        _BANG,
        sa.Column("id", BIGINT(unsigned=True), autoincrement=True, nullable=False, primary_key=True),
        sa.Column("loai", sa.Enum("KHU_VUC", "DOI_TUONG", name="loai_uu_tien"), nullable=False),
        sa.Column("ma", sa.String(20), nullable=False, comment="ma_khu_vuc hoặc ma_doi_tuong."),
        sa.Column("nam_ap_dung_tu", SMALLINT(unsigned=True), nullable=False),
        sa.Column("nam_ap_dung_den", SMALLINT(unsigned=True), comment="NULL = đến nay."),
        sa.Column("diem_cong", sa.Numeric(5, 2), nullable=False, comment="Điểm cộng thang 30."),
        sa.Column("can_cu", sa.String(255), comment="Văn bản quy định, ví dụ Thông tư 06/2026/TT-BGDĐT."),
        sa.Column("ghi_chu", sa.Text()),
        sa.Column("tao_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("cap_nhat_luc", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("loai", "ma", "nam_ap_dung_tu", name="uk_dm_muc_diem_uu_tien"),
        comment="Mức điểm cộng khu vực / đối tượng ưu tiên theo năm tuyển sinh",
        mysql_charset="utf8mb4",
        mysql_collate="utf8mb4_unicode_ci",
        mysql_engine="InnoDB",
    )


def downgrade() -> None:
    if sa.inspect(op.get_bind()).has_table(_BANG):
        op.drop_table(_BANG)
