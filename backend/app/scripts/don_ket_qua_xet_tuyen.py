"""Dọn kết quả đánh giá xét tuyển cũ (bước 5.3 KE_HOACH_TRIEN_KHAI.md).

Cách dùng (đặt cron trên máy chủ, ví dụ 3 giờ sáng mỗi ngày):
    cd backend && .venv/bin/python -m app.scripts.don_ket_qua_xet_tuyen            # chạy thử: chỉ đếm
    cd backend && .venv/bin/python -m app.scripts.don_ket_qua_xet_tuyen --xoa      # xóa thật
Tùy chọn: --khach-ngay=30 --thanh-vien-ngay=180 --lo=500

Quy tắc giữ lại:
- Khách (không đăng nhập): xóa lần đánh giá cũ hơn `khach_ngay` ngày.
- Thành viên: xóa lần cũ hơn `thanh_vien_ngay` ngày, nhưng luôn giữ lần mới nhất của mỗi người cho mỗi năm tuyển sinh
  (để lịch sử tìm trường gần nhất vẫn xem được chi tiết).
Kết quả phương án / chương trình xóa theo lần đánh giá. Xóa theo lô, mỗi lô một transaction.
"""

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core import thoi_gian
from app.db.session import SessionLocal
from app.models.xt_ket_qua import XtKetQuaChuongTrinh, XtKetQuaPhuongAn, XtLanDanhGia


@dataclass
class KetQuaDon:
    so_lan_khach: int
    so_lan_thanh_vien: int
    so_dong_ket_qua: int

    @property
    def so_lan(self) -> int:
        return self.so_lan_khach + self.so_lan_thanh_vien


def chon_lan_can_xoa(db: Session, *, bay_gio: datetime, khach_ngay: int, thanh_vien_ngay: int) -> tuple[list[int], list[int]]:
    """Id lần đánh giá của khách và của thành viên cần xóa."""
    khach = list(
        db.scalars(
            select(XtLanDanhGia.id).where(
                XtLanDanhGia.nguoi_dung_id.is_(None), XtLanDanhGia.tao_luc < bay_gio - timedelta(days=khach_ngay)
            )
        )
    )
    moi_nhat = (
        select(func.max(XtLanDanhGia.id))
        .where(XtLanDanhGia.nguoi_dung_id.is_not(None))
        .group_by(XtLanDanhGia.nguoi_dung_id, XtLanDanhGia.nam_tuyen_sinh)
    )
    thanh_vien = list(
        db.scalars(
            select(XtLanDanhGia.id).where(
                XtLanDanhGia.nguoi_dung_id.is_not(None),
                XtLanDanhGia.tao_luc < bay_gio - timedelta(days=thanh_vien_ngay),
                XtLanDanhGia.id.not_in(moi_nhat),
            )
        )
    )
    return khach, thanh_vien


def _dem_ket_qua(db: Session, ids: list[int], lo: int) -> int:
    tong = 0
    for i in range(0, len(ids), lo):
        phan = ids[i : i + lo]
        for model in (XtKetQuaPhuongAn, XtKetQuaChuongTrinh):
            tong += db.scalar(select(func.count()).select_from(model).where(model.lan_danh_gia_id.in_(phan))) or 0
    return tong


def don(
    db: Session,
    *,
    xoa: bool,
    bay_gio: datetime | None = None,
    khach_ngay: int = 30,
    thanh_vien_ngay: int = 180,
    lo: int = 500,
) -> KetQuaDon:
    khach, thanh_vien = chon_lan_can_xoa(
        db, bay_gio=bay_gio or thoi_gian.bay_gio(), khach_ngay=khach_ngay, thanh_vien_ngay=thanh_vien_ngay
    )
    ids = khach + thanh_vien
    so_dong = _dem_ket_qua(db, ids, lo)
    if xoa:
        for i in range(0, len(ids), lo):
            phan = ids[i : i + lo]
            # Xóa con trước (không dựa vào ON DELETE CASCADE); kết quả chương trình tham chiếu kết quả phương án.
            db.execute(delete(XtKetQuaChuongTrinh).where(XtKetQuaChuongTrinh.lan_danh_gia_id.in_(phan)))
            db.execute(delete(XtKetQuaPhuongAn).where(XtKetQuaPhuongAn.lan_danh_gia_id.in_(phan)))
            db.execute(delete(XtLanDanhGia).where(XtLanDanhGia.id.in_(phan)))
            db.commit()
    return KetQuaDon(len(khach), len(thanh_vien), so_dong)


def _so(argv: list[str], ten: str, mac_dinh: int) -> int:
    for a in argv:
        if a.startswith(f"--{ten}="):
            return int(a.split("=", 1)[1])
    return mac_dinh


def main(argv: list[str]) -> int:
    xoa = "--xoa" in argv
    db = SessionLocal()
    try:
        kq = don(
            db,
            xoa=xoa,
            khach_ngay=_so(argv, "khach-ngay", 30),
            thanh_vien_ngay=_so(argv, "thanh-vien-ngay", 180),
            lo=_so(argv, "lo", 500),
        )
        if not xoa:
            db.rollback()
    finally:
        db.close()
    hanh_dong = "Đã xóa" if xoa else "Sẽ xóa (chạy thử, thêm --xoa để xóa thật)"
    print(
        f"{thoi_gian.bay_gio():%d/%m/%Y %H:%M} {hanh_dong}: {kq.so_lan} lần đánh giá "
        f"({kq.so_lan_khach} của khách, {kq.so_lan_thanh_vien} của thành viên), {kq.so_dong_ket_qua} dòng kết quả."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
