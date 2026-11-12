"""Đọc cấu hình tra cứu đang áp dụng."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ht_cau_hinh_tra_cuu import HtCauHinhTraCuu


def cau_hinh_dang_ap_dung(db: Session) -> HtCauHinhTraCuu:
    """Cấu hình có trạng thái áp dụng. Bảng trống thì dùng giá trị mặc định của model (không lưu)."""
    item = db.scalar(
        select(HtCauHinhTraCuu)
        .where(HtCauHinhTraCuu.trang_thai == 1)
        .order_by(HtCauHinhTraCuu.updated_at.desc(), HtCauHinhTraCuu.id.desc())
        .limit(1)
    )
    if item is not None:
        return item
    return HtCauHinhTraCuu(
        so_luot_tra_cuu_khach_ngay=1,
        so_luot_tra_cuu_thanh_vien_ngay=5,
        so_luot_tu_van_ai_ngay=10,
        so_luot_phan_tich_truong_ngay=3,
        bat_tinh_nang_holland=True,
        bat_thanh_toan=False,
        gia_bao_cao_chuyen_sau=0,
        trang_thai=1,
    )
