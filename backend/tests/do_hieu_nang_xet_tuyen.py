"""Đo hiệu năng bộ tính xét tuyển với khoảng 300 trường giả lập (bước 3.5). Không phải unittest.

Chạy: cd backend && .venv/bin/python -m tests.do_hieu_nang_xet_tuyen
Nhân bản quy tắc FTU + BKA của trang test_xet_tuyen.html thành 150 cặp trường (300 trường), rồi đo:
- tính toàn bộ phương án của mọi trường (trường hợp xấu nhất: không lọc ngành);
- tính sau khi lọc theo ngành (giả lập 2 chương trình mỗi trường, như một lượt tìm thật).
"""

import copy
import time

from app.services.xet_tuyen.bo_tinh import theo_truong, tinh_phuong_an, xep_hang
from app.services.xet_tuyen.mo_hinh import QuyTacXetTuyen
from tests.test_xet_tuyen_bo_tinh import DIEM_CHUAN, HOM_NAY, KET_QUA_JS, NAM, QUY_TAC, ho_so_tu_preset

SO_CAP_TRUONG = 150


def nhan_ban(qt: QuyTacXetTuyen, so_cap: int) -> tuple[QuyTacXetTuyen, list]:
    """Mỗi bản sao đổi id (cộng bước) và mã trường, giữ nguyên nội dung quy tắc."""
    buoc = 100_000
    kq = QuyTacXetTuyen(
        to_hop=qt.to_hop, mon=qt.mon, khu_vuc=qt.khu_vuc, doi_tuong=qt.doi_tuong, trong_so=qt.trong_so, muc_phu_hop=qt.muc_phu_hop
    )
    diem_chuan = []
    for i in range(so_cap):
        d = i * buoc

        def sao(x, **doi):
            y = copy.copy(x)
            for k, v in doi.items():
                setattr(y, k, v)
            return y

        kq.cong_thuc += [sao(c, id=c.id + d, de_an_id=c.de_an_id + d, bang_ngoai_ngu_id=c.bang_ngoai_ngu_id and c.bang_ngoai_ngu_id + d) for c in qt.cong_thuc]
        kq.chuong_trinh += [sao(c, id=c.id + d, de_an_id=c.de_an_id + d, ma_truong=f"{c.ma_truong}{i}") for c in qt.chuong_trinh]
        kq.he_so_mon += [sao(h, cong_thuc_id=h.cong_thuc_id + d) for h in qt.he_so_mon]
        kq.thanh_phan += [
            sao(t, id=t.id + d, cong_thuc_id=t.cong_thuc_id + d, bang_id=t.bang_id and t.bang_id + d) for t in qt.thanh_phan
        ]
        kq.quy_doi += [sao(q, bang_id=q.bang_id + d) for q in qt.quy_doi]
        kq.phuong_an += [
            sao(p, id=p.id + d, chuong_trinh_id=p.chuong_trinh_id + d, cong_thuc_id=p.cong_thuc_id + d) for p in qt.phuong_an
        ]
        kq.nhom_dieu_kien += [
            sao(n, id=n.id + d, de_an_id=n.de_an_id + d, cong_thuc_id=n.cong_thuc_id and n.cong_thuc_id + d,
                chuong_trinh_id=n.chuong_trinh_id and n.chuong_trinh_id + d)
            for n in qt.nhom_dieu_kien
        ]
        kq.dieu_kien += [sao(x, nhom_id=x.nhom_id + d) for x in qt.dieu_kien]
        kq.diem_cong += [
            sao(x, de_an_id=x.de_an_id + d, cong_thuc_id=x.cong_thuc_id and x.cong_thuc_id + d) for x in qt.diem_cong
        ]
        diem_chuan += [sao(x, ma_truong=f"{x.ma_truong}{i}") for x in DIEM_CHUAN]
    return kq, diem_chuan


def do(ten: str, ham, lan: int = 3) -> float:
    tot = None
    for _ in range(lan):
        bat_dau = time.perf_counter()
        ham()
        da = time.perf_counter() - bat_dau
        tot = da if tot is None else min(tot, da)
    print(f"{ten}: {tot * 1000:.0f} ms")
    return tot


def main() -> None:
    qt, diem_chuan = nhan_ban(QUY_TAC, SO_CAP_TRUONG)
    hs = ho_so_tu_preset(KET_QUA_JS["ho_so"]["A"]["ho_so"])
    print(
        f"{len({c.ma_truong for c in qt.chuong_trinh})} trường, {len(qt.chuong_trinh)} chương trình, "
        f"{len(qt.phuong_an)} phương án"
    )
    # Chương trình thứ 1 và thứ 30 của mỗi trường, giả lập "cùng ngành".
    theo_truong_ct: dict[str, list[int]] = {}
    for c in qt.chuong_trinh:
        theo_truong_ct.setdefault(c.ma_truong, []).append(c.id)
    cung_nganh = {ds[i] for ds in theo_truong_ct.values() for i in (0, min(29, len(ds) - 1))}

    def tinh(ids=None):
        kq = tinh_phuong_an(qt, hs, NAM, HOM_NAY, diem_chuan, chuong_trinh_ids=ids)
        theo_truong(xep_hang(qt, hs, kq))
        return kq

    do("Lần đầu (dựng chỉ mục) + lọc ngành", lambda: tinh(cung_nganh), lan=1)
    do(f"Lọc ngành ({len(cung_nganh)} chương trình)", lambda: tinh(cung_nganh))
    do("Không lọc ngành (mọi chương trình)", lambda: tinh())


if __name__ == "__main__":
    main()
