"""Biểu thức SQL dùng chung khi hiển thị trường trong danh sách công khai."""

from sqlalchemy import and_, case, func, or_
from sqlalchemy.sql import FromClause

from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_truong import DmTruong


def join_tinh_thanh(source: FromClause) -> FromClause:
    """Nối thêm tỉnh thành của trường, ưu tiên khớp theo mã tỉnh rồi mới đến tên tỉnh."""
    return source.outerjoin(
        DmTinhThanh,
        or_(
            and_(
                DmTruong.ma_tinh_thanh.isnot(None),
                DmTruong.ma_tinh_thanh != "",
                DmTruong.ma_tinh_thanh == DmTinhThanh.ma_tinh,
            ),
            and_(
                or_(DmTruong.ma_tinh_thanh.is_(None), DmTruong.ma_tinh_thanh == ""),
                DmTruong.ten_tinh_thanh == DmTinhThanh.ten_tinh,
            ),
        ),
    )


def khu_vuc_hien_thi():
    """Khu vực của trường, lấy theo tỉnh khi trường chưa khai báo."""
    return func.coalesce(func.nullif(DmTruong.vung_mien, ""), DmTinhThanh.khu_vuc)


def loai_hien_thi():
    """Loại cơ sở của trường, đoán từ tên trường khi chưa khai báo."""
    return case(
        (and_(DmTruong.loai_co_so.isnot(None), DmTruong.loai_co_so != ""), DmTruong.loai_co_so),
        (DmTruong.ten_truong.like("%Học viện%"), "Học viện"),
        (DmTruong.ten_truong.like("%Cao đẳng%"), "Cao đẳng"),
        (DmTruong.ten_truong.like("%Đại học%"), "Đại học"),
        else_=None,
    )
