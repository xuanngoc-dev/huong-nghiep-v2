"""Thống kê tài chính từ lịch sử nạp tiền cho dashboard quản trị.

Doanh thu chỉ tính giao dịch thành công, số tiền lấy theo sao kê (`so_tien_thuc_nhan`, chưa có thì
`so_tien_nap`), thời điểm lấy theo lúc xác nhận (chưa có thì lúc tạo).
"""

from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.thoi_gian import bay_gio
from app.models.ht_lich_su_nap_tien import HtLichSuNapTien
from app.services.nap_tien import CHO_THANH_TOAN, THANH_CONG

SO_NGAY_GAN_DAY = 30


def _dau_thang(d: date, lui: int = 0) -> date:
    """Ngày đầu tháng của `d`, lùi thêm `lui` tháng."""
    thang = d.year * 12 + d.month - 1 - lui
    return date(thang // 12, thang % 12 + 1, 1)


def _cac_ky(now: datetime) -> list[tuple[str, datetime, datetime]]:
    """(mã kỳ, đầu kỳ này, đầu kỳ trước). Tuần bắt đầu từ thứ Hai."""
    hom_nay = now.date()
    dau = {
        "hom_nay": (hom_nay, hom_nay - timedelta(days=1)),
        "tuan_nay": (hom_nay - timedelta(days=hom_nay.weekday()), hom_nay - timedelta(days=hom_nay.weekday() + 7)),
        "thang_nay": (_dau_thang(hom_nay), _dau_thang(hom_nay, 1)),
        "nam_nay": (date(hom_nay.year, 1, 1), date(hom_nay.year - 1, 1, 1)),
    }
    return [(ma, datetime.combine(a, datetime.min.time()), datetime.combine(b, datetime.min.time())) for ma, (a, b) in dau.items()]


def tong_hop(giao_dich: Iterable[tuple[datetime, int, str]], now: datetime) -> dict:
    """Tổng hợp các giao dịch thành công `(thời điểm, số tiền, loại áp dụng)` thành số liệu dashboard.

    Mỗi kỳ (hôm nay, tuần, tháng, năm) so với cùng kỳ trước: từ đầu kỳ trước đến cùng khoảng thời gian
    đã trôi qua của kỳ này, để so sánh công bằng khi kỳ này chưa hết.
    """
    giao_dich = list(giao_dich)
    ky = []
    for ma, dau_ky, dau_ky_truoc in _cac_ky(now):
        cuoi_ky_truoc = dau_ky_truoc + (now - dau_ky)
        nay = [tien for t, tien, _ in giao_dich if dau_ky <= t <= now]
        truoc = [tien for t, tien, _ in giao_dich if dau_ky_truoc <= t < min(cuoi_ky_truoc, dau_ky)]
        ky.append(
            {
                "ma": ma,
                "so_tien": sum(nay),
                "so_giao_dich": len(nay),
                "so_tien_ky_truoc": sum(truoc),
                "so_giao_dich_ky_truoc": len(truoc),
            }
        )

    hom_nay = now.date()
    ngay_dau = hom_nay - timedelta(days=SO_NGAY_GAN_DAY - 1)
    theo_ngay = {ngay_dau + timedelta(days=i): [0, 0] for i in range(SO_NGAY_GAN_DAY)}
    theo_thang = {thang: [0, 0] for thang in range(1, 13)}
    theo_loai: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for t, tien, loai in giao_dich:
        if t > now:
            continue
        if t.date() in theo_ngay:
            theo_ngay[t.date()][0] += tien
            theo_ngay[t.date()][1] += 1
        if t.year == hom_nay.year:
            theo_thang[t.month][0] += tien
            theo_thang[t.month][1] += 1
            theo_loai[loai][0] += tien
            theo_loai[loai][1] += 1

    return {
        "ky": ky,
        "theo_ngay": [{"ngay": d, "so_tien": v[0], "so_giao_dich": v[1]} for d, v in theo_ngay.items()],
        "theo_thang": [{"thang": m, "so_tien": v[0], "so_giao_dich": v[1]} for m, v in theo_thang.items()],
        "theo_loai": sorted(
            ({"loai_ap_dung": loai, "so_tien": v[0], "so_giao_dich": v[1]} for loai, v in theo_loai.items()),
            key=lambda x: -x["so_tien"],
        ),
    }


def thong_ke(db: Session, now: datetime | None = None) -> dict:
    """Số liệu tài chính cho dashboard: doanh thu theo kỳ, 30 ngày, 12 tháng, theo loại và giao dịch chờ."""
    now = now or bay_gio()
    thoi_diem = func.coalesce(HtLichSuNapTien.thoi_gian_xac_nhan, HtLichSuNapTien.created_at)
    so_tien = func.coalesce(HtLichSuNapTien.so_tien_thuc_nhan, HtLichSuNapTien.so_tien_nap)
    # Kỳ trước xa nhất là đầu năm ngoái.
    tu = datetime(now.year - 1, 1, 1)
    rows = db.execute(
        select(thoi_diem, so_tien, HtLichSuNapTien.loai_ap_dung).where(
            HtLichSuNapTien.trang_thai == THANH_CONG, thoi_diem >= tu, thoi_diem <= now
        )
    ).all()
    ket_qua = tong_hop(((t, int(tien or 0), loai) for t, tien, loai in rows), now)

    so_cho, tien_cho = db.execute(
        select(func.count(), func.coalesce(func.sum(HtLichSuNapTien.so_tien_nap), 0)).where(
            HtLichSuNapTien.trang_thai == CHO_THANH_TOAN
        )
    ).one()
    ket_qua["cho_xac_nhan"] = {"so_tien": int(tien_cho or 0), "so_giao_dich": so_cho or 0}
    return ket_qua
