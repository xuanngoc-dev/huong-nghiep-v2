"""Cung co luu de an tuyen sinh theo nam (buoc 1.2 KE_HOACH_TRIEN_KHAI.md).

- dats_tuyen_sinh: ma_truong + nam_tuyen_sinh duy nhat; them de_an_nam_truoc_id, trang_thai_xet_tuyen.
- dats_tru_so: them tinh_thanh_id, tu dien tu ten/dia chi co so.
- dats_chuong_trinh_dao_tao: them ma_xet_tuyen_nam_truoc.

Revision ID: 20261116_0056
Revises: 20261115_0055
Create Date: 2026-11-16 09:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.mysql import BIGINT

revision: str = "20261116_0056"
down_revision: Union[str, Sequence[str], None] = "20261115_0055"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DE_AN = "dats_tuyen_sinh"
_TRU_SO = "dats_tru_so"
_CHUONG_TRINH = "dats_chuong_trinh_dao_tao"

_UQ_DE_AN = "uq_dats_tuyen_sinh_ma_truong_nam_tuyen_sinh"
_IDX_DE_AN_CU = "idx_dats_tuyen_sinh_ma_truong_nam_tuyen_sinh"
_FK_NAM_TRUOC = "fk_dats_tuyen_sinh_de_an_nam_truoc_id"
_IDX_NAM_TRUOC = "idx_dats_tuyen_sinh_de_an_nam_truoc_id"
_FK_TINH = "fk_dats_tru_so_tinh_thanh_id"
_IDX_TINH = "idx_dats_tru_so_tinh_thanh_id"

_TIEN_TO_TINH = ("thành phố ", "tp. ", "tp ", "tỉnh ")


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _indexes(table: str) -> set[str]:
    inspector = sa.inspect(op.get_bind())
    names = {index["name"] for index in inspector.get_indexes(table)}
    names |= {uq["name"] for uq in inspector.get_unique_constraints(table)}
    return names


def _foreign_keys(table: str) -> set[str]:
    return {fk["name"] for fk in sa.inspect(op.get_bind()).get_foreign_keys(table)}


def _chan_neu_de_an_trung() -> None:
    trung = op.get_bind().execute(
        sa.text(
            f"SELECT ma_truong, nam_tuyen_sinh, COUNT(*) AS so FROM {_DE_AN} "
            "GROUP BY ma_truong, nam_tuyen_sinh HAVING COUNT(*) > 1"
        )
    ).all()
    if trung:
        ds = ", ".join(f"{r.ma_truong}/{r.nam_tuyen_sinh} ({r.so})" for r in trung)
        raise RuntimeError(
            f"Còn đề án trùng trường + năm: {ds}. Gộp đề án trùng (bước 1.1) trước khi chạy migration này."
        )


def _ten_khop(ten_tinh: str) -> str:
    ten = ten_tinh.strip().lower()
    for tien_to in _TIEN_TO_TINH:
        if ten.startswith(tien_to):
            return ten[len(tien_to):]
    return ten


def _dien_tinh_cho_co_so() -> None:
    """Điền tinh_thanh_id cho cơ sở có tên tỉnh trong tên hoặc địa chỉ; chọn tên tỉnh dài nhất khớp được."""
    bind = op.get_bind()
    ds_tinh = [
        (r.id, _ten_khop(r.ten_tinh))
        for r in bind.execute(sa.text("SELECT id, ten_tinh FROM dm_tinh_thanh WHERE trang_thai = 1"))
        if r.ten_tinh
    ]
    ds_tinh.sort(key=lambda t: len(t[1]), reverse=True)
    co_so = bind.execute(
        sa.text(f"SELECT id, ten_co_so, dia_chi FROM {_TRU_SO} WHERE tinh_thanh_id IS NULL")
    ).all()
    for cs in co_so:
        noi_dung = f"{cs.ten_co_so or ''} {cs.dia_chi or ''}".lower()
        tinh_id = next((tid for tid, ten in ds_tinh if ten and ten in noi_dung), None)
        if tinh_id is not None:
            bind.execute(
                sa.text(f"UPDATE {_TRU_SO} SET tinh_thanh_id = :tinh_id WHERE id = :id"),
                {"tinh_id": tinh_id, "id": cs.id},
            )


def upgrade() -> None:
    # dats_tuyen_sinh
    _chan_neu_de_an_trung()
    if _UQ_DE_AN not in _indexes(_DE_AN):
        op.create_unique_constraint(_UQ_DE_AN, _DE_AN, ["ma_truong", "nam_tuyen_sinh"])
    # Index cũ trùng cột với ràng buộc unique; bỏ sau khi đã có unique để khóa ngoại ma_truong vẫn có index.
    if _IDX_DE_AN_CU in _indexes(_DE_AN):
        op.drop_index(_IDX_DE_AN_CU, table_name=_DE_AN)

    cot_de_an = _columns(_DE_AN)
    if "de_an_nam_truoc_id" not in cot_de_an:
        op.add_column(
            _DE_AN,
            sa.Column(
                "de_an_nam_truoc_id",
                BIGINT(unsigned=True),
                nullable=True,
                comment="Đề án năm trước của cùng trường (nguồn sao chép, đối chiếu điểm chuẩn).",
            ),
        )
        op.create_index(_IDX_NAM_TRUOC, _DE_AN, ["de_an_nam_truoc_id"])
        op.create_foreign_key(
            _FK_NAM_TRUOC, _DE_AN, _DE_AN, ["de_an_nam_truoc_id"], ["id"], ondelete="SET NULL"
        )
    if "trang_thai_xet_tuyen" not in cot_de_an:
        op.add_column(
            _DE_AN,
            sa.Column(
                "trang_thai_xet_tuyen",
                sa.SmallInteger(),
                server_default="0",
                nullable=False,
                comment="Quy tắc xét tuyển: 0 chưa chuẩn hóa, 1 thử nghiệm, 2 đang áp dụng.",
            ),
        )

    # dats_tru_so
    if "tinh_thanh_id" not in _columns(_TRU_SO):
        op.add_column(
            _TRU_SO,
            sa.Column(
                "tinh_thanh_id",
                sa.Integer(),
                nullable=True,
                comment="Tỉnh/thành của cơ sở; FK dm_tinh_thanh.id.",
            ),
        )
        op.create_index(_IDX_TINH, _TRU_SO, ["tinh_thanh_id"])
        op.create_foreign_key(_FK_TINH, _TRU_SO, "dm_tinh_thanh", ["tinh_thanh_id"], ["id"])
    _dien_tinh_cho_co_so()

    # dats_chuong_trinh_dao_tao
    if "ma_xet_tuyen_nam_truoc" not in _columns(_CHUONG_TRINH):
        op.add_column(
            _CHUONG_TRINH,
            sa.Column(
                "ma_xet_tuyen_nam_truoc",
                sa.String(length=20),
                nullable=True,
                comment="Mã xét tuyển của chương trình tương ứng năm trước (khi trường đổi mã).",
            ),
        )


def downgrade() -> None:
    if "ma_xet_tuyen_nam_truoc" in _columns(_CHUONG_TRINH):
        op.drop_column(_CHUONG_TRINH, "ma_xet_tuyen_nam_truoc")

    if "tinh_thanh_id" in _columns(_TRU_SO):
        if _FK_TINH in _foreign_keys(_TRU_SO):
            op.drop_constraint(_FK_TINH, _TRU_SO, type_="foreignkey")
        if _IDX_TINH in _indexes(_TRU_SO):
            op.drop_index(_IDX_TINH, table_name=_TRU_SO)
        op.drop_column(_TRU_SO, "tinh_thanh_id")

    cot_de_an = _columns(_DE_AN)
    if "trang_thai_xet_tuyen" in cot_de_an:
        op.drop_column(_DE_AN, "trang_thai_xet_tuyen")
    if "de_an_nam_truoc_id" in cot_de_an:
        if _FK_NAM_TRUOC in _foreign_keys(_DE_AN):
            op.drop_constraint(_FK_NAM_TRUOC, _DE_AN, type_="foreignkey")
        if _IDX_NAM_TRUOC in _indexes(_DE_AN):
            op.drop_index(_IDX_NAM_TRUOC, table_name=_DE_AN)
        op.drop_column(_DE_AN, "de_an_nam_truoc_id")

    if _IDX_DE_AN_CU not in _indexes(_DE_AN):
        op.create_index(_IDX_DE_AN_CU, _DE_AN, ["ma_truong", "nam_tuyen_sinh"])
    if _UQ_DE_AN in _indexes(_DE_AN):
        op.drop_constraint(_UQ_DE_AN, _DE_AN, type_="unique")
