"""Bộ tính xét tuyển bằng Python (bước 3.1 KE_HOACH_TRIEN_KHAI.md).

Chuyển từ khối //<ENGINE> trong docs/de-an-tuyen-sinh/test_xet_tuyen.html (bản đã đối chiếu với thủ tục MySQL
trên 986 phương án). Giữ đúng thứ tự phép tính, cách làm tròn và cách so sánh của bản gốc để kết quả khớp tuyệt
đối; tests/test_xet_tuyen_bo_tinh.py so từng phương án với kết quả của bản JavaScript.

Ba hàm chính, đều thuần (không đụng CSDL):
- `tinh_phuong_an(quy_tac, ho_so, nam, hom_nay, diem_chuan)`: điểm xét, điều kiện, điểm chuẩn tham chiếu từng phương án.
- `xep_hang(quy_tac, ho_so, ket_qua, loc=None)`: chọn phương án tốt nhất mỗi chương trình và chấm điểm phù hợp.
- `theo_truong(dong)`: xếp hạng trường.

Không có điều kiện theo mã trường: mọi khác biệt giữa các trường nằm trong dữ liệu quy tắc.
"""

import math
from collections.abc import Callable
from decimal import ROUND_HALF_UP, Decimal
from functools import cmp_to_key

from app.services.xet_tuyen.mo_hinh import (
    ChuongTrinhTinh,
    CongThucTinh,
    DiemChuanTinh,
    DongXepHang,
    HoSoXetTuyen,
    KetQuaPhuongAn,
    KetQuaTinh,
    KetQuaTruong,
    MonTinh,
    MucQuyDoiTinh,
    NhomDieuKienTinh,
    QuyTacXetTuyen,
)

NHOM_NGOAI_NGU = "Ngoại ngữ"
_THU_TU_KIEU = {"TO_HOP_MON": 0, "THANH_PHAN": 1, "CHI_DIEU_KIEN": 2, "THU_CONG": 3}


def lam_tron(x: float | None, so_le: int) -> float | None:
    """Làm tròn như Math.round của JavaScript (nửa lên) sau khi bù 1e-9 để tránh sai số dấu phẩy động."""
    if x is None:
        return None
    f = 10**so_le
    return math.floor((x + (1e-9 if x >= 0 else -1e-9)) * f + 0.5) / f


def _so_sanh(gia_tri: float | None, toan_tu: str, nguong: float | None) -> bool:
    if gia_tri is None or nguong is None:
        return False
    if toan_tu == ">=":
        return gia_tri >= nguong
    if toan_tu == ">":
        return gia_tri > nguong
    if toan_tu == "=":
        return gia_tri == nguong
    if toan_tu == "<=":
        return gia_tri <= nguong
    if toan_tu == "<":
        return gia_tri < nguong
    if toan_tu == "!=":
        return gia_tri != nguong
    return False


def _lon_hon(a: float | None, b: float | None) -> float | None:
    if a is None:
        return b
    if b is None:
        return a
    return max(a, b)


def _so_js(x: float) -> str:
    """Chuỗi số giống String(number) của JavaScript (9 → "9", 8.75 → "8.75")."""
    if x == int(x) and abs(x) < 1e21:
        return str(int(x))
    return repr(x)


def _hai_le(x: float | None) -> str:
    """Giống Number.toFixed(2) của JavaScript: làm tròn trên giá trị nhị phân chính xác, hòa thì lấy số lớn hơn."""
    if x is None:
        return ""
    return str(Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class _ChiMuc:
    """Bảng tra dựng một lần cho mỗi bộ quy tắc (tương đương index() của bản JS)."""

    def __init__(self, qt: QuyTacXetTuyen):
        self.qt = qt
        self.cong_thuc = {c.id: c for c in qt.cong_thuc}
        self.chuong_trinh = {c.id: c for c in qt.chuong_trinh}
        self.he_so: dict[int, tuple[dict[str, float], dict[str, float]]] = {}
        for h in qt.he_so_mon:
            theo_mon, theo_nhom = self.he_so.setdefault(h.cong_thuc_id, ({}, {}))
            if h.ma_mon:
                theo_mon[h.ma_mon] = h.he_so
            else:
                theo_nhom[h.nhom_mon] = h.he_so
        self.thanh_phan: dict[int, list] = {}
        for t in qt.thanh_phan:
            self.thanh_phan.setdefault(t.cong_thuc_id, []).append(t)
        self.quy_doi: dict[int, list[MucQuyDoiTinh]] = {}
        for q in qt.quy_doi:
            self.quy_doi.setdefault(q.bang_id, []).append(q)
        self.dieu_kien: dict[int, list] = {}
        for d in qt.dieu_kien:
            self.dieu_kien.setdefault(d.nhom_id, []).append(d)


_CHI_MUC_CACHE: dict[int, _ChiMuc] = {}


def _chi_muc(qt: QuyTacXetTuyen) -> _ChiMuc:
    cm = _CHI_MUC_CACHE.get(id(qt))
    if cm is None or cm.qt is not qt:
        cm = _ChiMuc(qt)
        _CHI_MUC_CACHE.clear()
        _CHI_MUC_CACHE[id(qt)] = cm
    return cm


def tinh_chi_so(hs: HoSoXetTuyen, hom_nay: str) -> dict[tuple[str, str], float]:
    """Các chỉ số của học sinh dùng để xét điều kiện và điểm cộng, khóa (mã chỉ số, khóa)."""
    cs: dict[tuple[str, str], float] = {}

    def dat(ma: str, khoa: str, v) -> None:
        if v is not None:
            cs[(ma, khoa)] = lam_tron(float(v), 3)

    dat("DA_TOT_NGHIEP_THPT", "", 1 if hs.da_tot_nghiep else 0)
    dat("NAM_TOT_NGHIEP", "", hs.nam_tot_nghiep)
    dat("HE_CHUYEN", "", 1 if hs.he_chuyen else 0)
    if hs.he_chuyen and hs.mon_chuyen:
        dat("MON_CHUYEN", hs.mon_chuyen, 1)
    for ma, thuoc_tinh in (("TBC", "tbc"), ("HOC_LUC", "hoc_luc"), ("REN_LUYEN", "ren_luyen")):
        gia_tri = []
        for lop in (10, 11, 12):
            nam_hoc = hs.nam_hoc.get(lop)
            v = getattr(nam_hoc, thuoc_tinh) if nam_hoc else None
            if v is not None:
                dat(f"{ma}_LOP", str(lop), v)
                gia_tri.append(v)
        if len(gia_tri) == 3:
            dat(f"{ma}_MIN_3_NAM", "", min(gia_tri))
    for mon, v in hs.diem_thpt.items():
        dat("DIEM_THI_THPT", mon, v)
    for mon, theo_lop in hs.hoc_ba.items():
        if all(theo_lop.get(lop) is not None for lop in (10, 11, 12)):
            dat("DIEM_HOC_BA_TB", mon, (theo_lop[10] + theo_lop[11] + theo_lop[12]) / 3)
    for b in hs.bai_thi:
        if b.diem is not None:
            dat("DIEM_BAI_THI", b.ma, _lon_hon(cs.get(("DIEM_BAI_THI", b.ma)), b.diem))
    for c in hs.chung_chi:
        if c.het_han and c.het_han < hom_nay:
            continue
        dat("CO_CHUNG_CHI", c.ma, 1)
        if c.diem is not None:
            dat("DIEM_CHUNG_CHI", c.ma, _lon_hon(cs.get(("DIEM_CHUNG_CHI", c.ma)), c.diem))
    for t in hs.thanh_tich:
        khoa = ("THANH_TICH", t.ma)
        cs[khoa] = min(cs[khoa], t.muc_giai) if khoa in cs else t.muc_giai
    return cs


def _khop_muc(q: MucQuyDoiTinh, diem: float | None, cap_do: str | None) -> bool:
    return (
        (q.cap_do is None or q.cap_do == cap_do)
        and (q.tu is None or (diem is not None and diem >= q.tu))
        and (q.den is None or (diem is not None and diem <= q.den))
    )


def _quy_doi(q: MucQuyDoiTinh, diem: float | None) -> float:
    return q.quy_doi + (q.he_so_noi_suy * (diem - q.tu) if q.tu is not None and diem is not None else 0)


def tinh_phuong_an(
    qt: QuyTacXetTuyen,
    hs: HoSoXetTuyen,
    nam: int,
    hom_nay: str,
    diem_chuan: list[DiemChuanTinh] | None = None,
) -> KetQuaTinh:
    """Tính điểm xét và xét điều kiện mọi phương án của năm `nam` (tương đương sp_xt_tinh_diem).

    Chỉ trả phương án học sinh đủ dữ liệu để tính điểm, hoặc phương án không tính điểm mà học sinh đạt hết điều kiện.
    """
    cm = _chi_muc(qt)
    cs = tinh_chi_so(hs, hom_nay)

    def con_han(c) -> bool:
        return not c.het_han or c.het_han >= hom_nay

    muc_kv = qt.khu_vuc.get(hs.khu_vuc, 0) if hs.khu_vuc else 0
    if hs.nam_tot_nghiep is not None and nam > hs.nam_tot_nghiep + 1:
        muc_kv = 0
    muc_ut = muc_kv + (qt.doi_tuong.get(hs.doi_tuong, 0) if hs.doi_tuong else 0)

    # 1. Điểm môn: thi THPT và học bạ trung bình 3 năm.
    thpt = hs.diem_thpt
    hoc_ba: dict[str, float] = {}
    for mon, theo_lop in hs.hoc_ba.items():
        if all(theo_lop.get(lop) is not None for lop in (10, 11, 12)):
            hoc_ba[mon] = lam_tron((theo_lop[10] + theo_lop[11] + theo_lop[12]) / 3, 4)

    # 2. Ngoại ngữ quy đổi từ chứng chỉ theo từng bảng: {bảng: {mã môn: điểm}}.
    ngoai_ngu: dict[int, dict[str, float]] = {}
    for bang_id, cac_muc in cm.quy_doi.items():
        theo_mon: dict[str, float] = {}
        for q in cac_muc:
            if not q.ma_chung_chi or not q.ma_mon or not q.dat_nguong:
                continue
            for c in hs.chung_chi:
                if c.ma != q.ma_chung_chi or not con_han(c) or not _khop_muc(q, c.diem, c.cap_do):
                    continue
                theo_mon[q.ma_mon] = _lon_hon(theo_mon.get(q.ma_mon), lam_tron(_quy_doi(q, c.diem), 3))
        ngoai_ngu[bang_id] = theo_mon

    # 3. Giá trị từng thành phần (bài thi / chứng chỉ đã quy đổi).
    gia_tri_tp: dict[int, float] = {}
    for tp in qt.thanh_phan:
        v = None
        if tp.loai == "BAI_THI":
            for b in hs.bai_thi:
                if b.ma != tp.ma_bai_thi or b.diem is None:
                    continue
                if tp.nam_tu is not None and not (b.nam is not None and b.nam >= tp.nam_tu):
                    continue
                if tp.nam_den is not None and not (b.nam is not None and b.nam <= tp.nam_den):
                    continue
                if tp.phan_tu_chon is not None and b.phan_tu_chon != tp.phan_tu_chon:
                    continue
                if tp.bang_id is None:
                    v = _lon_hon(v, b.diem)
                    continue
                for q in cm.quy_doi.get(tp.bang_id, []):
                    if q.ma_bai_thi == b.ma and q.dat_nguong and _khop_muc(q, b.diem, None):
                        v = _lon_hon(v, _quy_doi(q, b.diem))
        else:
            for q in cm.quy_doi.get(tp.bang_id, []):
                if not q.ma_chung_chi or not q.dat_nguong or (tp.ma_mon is not None and q.ma_mon != tp.ma_mon):
                    continue
                for c in hs.chung_chi:
                    if c.ma == q.ma_chung_chi and con_han(c) and _khop_muc(q, c.diem, c.cap_do):
                        v = _lon_hon(v, _quy_doi(q, c.diem))
        if v is not None:
            gia_tri_tp[tp.id] = lam_tron(v, 4)

    # 4. Nhóm điều kiện: đạt khi một điều kiện trong nhóm đạt.
    nhom_dat = {
        n.id: any(_so_sanh(cs.get((d.chi_so, d.khoa)), d.toan_tu, d.gia_tri) for d in cm.dieu_kien.get(n.id, []))
        for n in qt.nhom_dieu_kien
    }

    def nhom_cua(cong_thuc_id: int, ctr: ChuongTrinhTinh) -> list[NhomDieuKienTinh]:
        return [
            n
            for n in qt.nhom_dieu_kien
            if n.de_an_id == ctr.de_an_id
            and (n.cong_thuc_id is None or n.cong_thuc_id == cong_thuc_id)
            and (n.chuong_trinh_id is None or n.chuong_trinh_id == ctr.id)
        ]

    # 6. Điểm cộng theo công thức: cùng nhóm lấy mức cao nhất, khác nhóm cộng dồn, có trần.
    diem_cong_cache: dict[int, float] = {}

    def tinh_diem_cong(ct: CongThucTinh) -> float:
        if ct.id in diem_cong_cache:
            return diem_cong_cache[ct.id]
        tong = 0.0
        if ct.ap_dung_diem_cong:
            theo_nhom: dict[str, float] = {}
            for d in qt.diem_cong:
                if d.de_an_id != ct.de_an_id or (d.cong_thuc_id is not None and d.cong_thuc_id != ct.id):
                    continue
                if _so_sanh(cs.get((d.chi_so, d.khoa)), d.toan_tu, d.gia_tri):
                    theo_nhom[d.nhom] = _lon_hon(theo_nhom.get(d.nhom), d.diem)
            for v in theo_nhom.values():
                tong += v
        v = lam_tron(min(tong, 30 * ct.tran_diem_cong) * ct.thang / 30, 2)
        diem_cong_cache[ct.id] = v
        return v

    ket_qua: list[KetQuaPhuongAn] = []
    for pa in qt.phuong_an:
        ct = cm.cong_thuc.get(pa.cong_thuc_id)
        ctr = cm.chuong_trinh.get(pa.chuong_trinh_id)
        if ct is None or ctr is None or not ct.trang_thai or ctr.nam != nam:
            continue
        r = KetQuaPhuongAn(
            phuong_an_id=pa.id,
            chuong_trinh_id=pa.chuong_trinh_id,
            cong_thuc_id=pa.cong_thuc_id,
            ma_to_hop=pa.ma_to_hop,
            kieu=ct.kieu,
            thang=ct.thang,
        )
        nhom = nhom_cua(pa.cong_thuc_id, ctr)

        if ct.kieu == "TO_HOP_MON":
            if not _tinh_to_hop(r, ct, qt, cm, pa.ma_to_hop, thpt, hoc_ba, ngoai_ngu):
                continue
        elif ct.kieu == "THANH_PHAN":
            if not _tinh_thanh_phan(r, ct, cm, gia_tri_tp):
                continue
        else:
            # CHI_DIEU_KIEN / THU_CONG: chỉ giữ khi đạt mọi nhóm và có nhóm riêng của công thức.
            if not nhom or not all(nhom_dat[n.id] for n in nhom) or not any(n.cong_thuc_id is not None for n in nhom):
                continue
            r.chi_tiet = "Không tính điểm" if ct.kieu == "CHI_DIEU_KIEN" else "Hệ thống chưa tự tính điểm"

        ly_do = [n.ten for n in nhom if not nhom_dat[n.id]]
        r.so_nhom = len(nhom)
        r.so_nhom_dat = len(nhom) - len(ly_do)

        if r.diem_goc is not None:
            r.diem_cong = tinh_diem_cong(ct)
            t30 = min(ct.thang, r.diem_goc + r.diem_cong) * 30 / ct.thang
            r.diem_uu_tien = (
                lam_tron(muc_ut * ct.thang / 30 * ((30 - t30) / 7.5 if t30 >= 22.5 else 1), 2) if ct.ap_dung_uu_tien else 0
            )
            r.diem_xet = lam_tron(min(ct.thang, r.diem_goc + r.diem_cong + r.diem_uu_tien), ct.so_le)
            tb_lam_tron = None if r.tb_mon is None else lam_tron(r.tb_mon, 2)
            thpt_uu_tien = (
                None
                if r.tong_thpt is None
                else r.tong_thpt + muc_ut * ((30 - r.tong_thpt) / 7.5 if r.tong_thpt >= 22.5 else 1)
            )
            hong_san = ct.diem_san is not None and r.diem_xet < ct.diem_san
            hong_tb = ct.nguong_tb_mon is not None and not (tb_lam_tron is not None and tb_lam_tron >= ct.nguong_tb_mon)
            hong_thpt = ct.nguong_thpt_to_hop is not None and not (
                thpt_uu_tien is not None and thpt_uu_tien >= ct.nguong_thpt_to_hop - 1e-9
            )
            r.dat_nguong = not (hong_san or hong_tb or hong_thpt)
            if hong_san:
                ly_do.append(f"Điểm xét {_hai_le(r.diem_xet)} dưới ngưỡng nhận hồ sơ {_hai_le(ct.diem_san)}")
            if hong_tb:
                tb = "?" if tb_lam_tron is None else _hai_le(tb_lam_tron)
                ly_do.append(f"Trung bình các môn xét {tb} dưới ngưỡng {_hai_le(ct.nguong_tb_mon)}")
            if hong_thpt:
                ly_do.append(
                    "Thiếu điểm thi THPT của tổ hợp để xét ngưỡng"
                    if r.tong_thpt is None
                    else f"Tổng điểm thi THPT theo tổ hợp (gồm ưu tiên) dưới ngưỡng {_hai_le(ct.nguong_thpt_to_hop)}"
                )
        r.du_dieu_kien = r.so_nhom == r.so_nhom_dat and r.dat_nguong is not False
        r.ly_do = "; ".join(ly_do)

        # 10. Điểm chuẩn tham chiếu: năm gần nhất, ưu tiên dòng khớp tổ hợp rồi khớp phương thức.
        if r.diem_xet is not None:
            _gan_diem_chuan(r, ct, ctr, pa.ma_to_hop, nam, diem_chuan or [])
        ket_qua.append(r)
    return KetQuaTinh(chi_so=cs, phuong_an=ket_qua, muc_uu_tien=muc_ut)


def _tinh_to_hop(r, ct, qt, cm, ma_to_hop, thpt, hoc_ba, ngoai_ngu) -> bool:
    """Điểm gốc công thức TO_HOP_MON; False nếu tổ hợp không có cấu trúc hoặc thiếu điểm một vị trí."""
    vi_tri = qt.to_hop.get(ma_to_hop) if ma_to_hop else None
    if vi_tri is None:
        return False
    theo_mon, theo_nhom = cm.he_so.get(ct.id, ({}, {}))
    tong = tong_mon = tong_thpt = 0.0
    so_mon = 0
    du_thpt = True
    phan: list[str] = []
    for cac_mon in vi_tri:
        tot = None
        mo_ta = ""
        diem_mon = diem_thpt = None
        for m in cac_mon:
            mon = qt.mon.get(m) or MonTinh(ten=m, nhom="")
            w = theo_mon.get(m)
            if w is None:
                w = theo_nhom.get(mon.nhom)
            if w is None:
                w = 1
            nguon = thpt.get(m) if ct.nguon == "THI_THPT" else hoc_ba.get(m)
            la_ngoai_ngu = mon.nhom == NHOM_NGOAI_NGU
            chung_chi = ngoai_ngu.get(ct.bang_ngoai_ngu_id, {}).get(m) if ct.bang_ngoai_ngu_id is not None else None
            dung_chung_chi = False
            if la_ngoai_ngu and ct.thay_ngoai_ngu == "BAT_BUOC":
                diem = chung_chi
                dung_chung_chi = True
            elif la_ngoai_ngu and ct.thay_ngoai_ngu == "DUOC_PHEP":
                diem = _lon_hon(nguon, chung_chi)
                dung_chung_chi = chung_chi is not None and (nguon is None or chung_chi > nguon)
            else:
                diem = nguon
            dm = None if la_ngoai_ngu and ct.thay_ngoai_ngu == "BAT_BUOC" else nguon
            if la_ngoai_ngu and ct.thay_ngoai_ngu == "BAT_BUOC":
                dn = chung_chi
            elif la_ngoai_ngu and ct.thay_ngoai_ngu == "DUOC_PHEP":
                dn = _lon_hon(thpt.get(m), chung_chi)
            else:
                dn = thpt.get(m)
            if diem is not None and (tot is None or w * diem > tot):
                tot = w * diem
                mo_ta = (
                    mon.ten
                    + (" (chứng chỉ)" if dung_chung_chi else "")
                    + " "
                    + _so_js(lam_tron(diem, 2))
                    + (" × " + _so_js(w) if w != 1 else "")
                )
            diem_mon = _lon_hon(diem_mon, dm)
            diem_thpt = _lon_hon(diem_thpt, dn)
        if tot is None:
            return False
        tong += tot
        phan.append(mo_ta)
        if diem_mon is not None:
            tong_mon += diem_mon
            so_mon += 1
        if diem_thpt is not None:
            tong_thpt += diem_thpt
        else:
            du_thpt = False
    r.diem_goc = lam_tron(tong * ct.he_so_nhan, 4)
    r.tb_mon = lam_tron(tong_mon / so_mon, 3) if so_mon else None
    r.tong_thpt = lam_tron(tong_thpt, 2) if du_thpt else None
    r.chi_tiet = _chi_tiet(phan, ct.he_so_nhan)
    return True


def _tinh_thanh_phan(r, ct, cm, gia_tri_tp) -> bool:
    """Điểm gốc công thức THANH_PHAN; các thành phần cùng vị trí thay thế nhau, lấy giá trị cao nhất."""
    theo_vi_tri: dict[int, tuple[float | None, str]] = {}
    for tp in cm.thanh_phan.get(ct.id, []):
        co = tp.id in gia_tri_tp
        v = tp.he_so * gia_tri_tp[tp.id] if co else None
        hien_tai = theo_vi_tri.get(tp.vi_tri)
        if hien_tai is None or (v is not None and (hien_tai[0] is None or v > hien_tai[0])):
            mo_ta = (
                (tp.ten or tp.loai)
                + " "
                + (_so_js(lam_tron(gia_tri_tp[tp.id], 2)) if co else "?")
                + (" × " + _so_js(tp.he_so) if tp.he_so != 1 else "")
            )
            theo_vi_tri[tp.vi_tri] = (v if v is not None else (hien_tai[0] if hien_tai else None), mo_ta)
    if not theo_vi_tri or any(v is None for v, _mo_ta in theo_vi_tri.values()):
        return False
    tong = 0.0
    for v, _mo_ta in theo_vi_tri.values():
        tong += v
    r.diem_goc = lam_tron(tong * ct.he_so_nhan, 4)
    r.chi_tiet = _chi_tiet([theo_vi_tri[k][1] for k in sorted(theo_vi_tri)], ct.he_so_nhan)
    return True


def _chi_tiet(phan: list[str], he_so_nhan: float) -> str:
    if he_so_nhan != 1:
        return "(" + " + ".join(phan) + ") × " + _so_js(lam_tron(he_so_nhan, 4))
    return " + ".join(phan)


def _gan_diem_chuan(r, ct, ctr, ma_to_hop, nam, diem_chuan: list[DiemChuanTinh]) -> None:
    tot = None
    tot_khoa = None
    for d in diem_chuan:
        if d.ma_truong != ctr.ma_truong or d.ma_xet_tuyen != ctr.ma_xet_tuyen or not (d.nam <= nam):
            continue
        if d.diem is None or not d.thang:
            continue
        if d.ma_phuong_thuc and d.ma_phuong_thuc != ct.ma_phuong_thuc:
            continue
        if d.ma_to_hop and d.ma_to_hop != ma_to_hop:
            continue
        khoa = (d.nam, 1 if d.ma_to_hop else 0, 1 if d.ma_phuong_thuc else 0)
        if tot is None or khoa > tot_khoa:
            tot, tot_khoa = d, khoa
    if tot is not None:
        r.diem_chuan = tot.diem
        r.diem_chuan_id = tot.id
        r.nam_diem_chuan = tot.nam
        r.thang_diem_chuan = tot.thang
        r.chenh_lech_30 = lam_tron(r.diem_xet * 30 / r.thang - tot.diem * 30 / tot.thang, 2)


def _tot_hon(a: KetQuaPhuongAn, b: KetQuaPhuongAn) -> bool:
    """Phương án a tốt hơn b khi chọn đại diện cho chương trình."""
    xa = 1 if a.kieu == "CHI_DIEU_KIEN" else 0
    xb = 1 if b.kieu == "CHI_DIEU_KIEN" else 0
    if xa != xb:
        return xa > xb
    if (a.chenh_lech_30 is None) != (b.chenh_lech_30 is None):
        return a.chenh_lech_30 is not None
    if a.chenh_lech_30 is not None and a.chenh_lech_30 != b.chenh_lech_30:
        return a.chenh_lech_30 > b.chenh_lech_30
    ra = -1 if a.diem_xet is None else a.diem_xet / a.thang
    rb = -1 if b.diem_xet is None else b.diem_xet / b.thang
    if abs(ra - rb) > 1e-12:
        return ra > rb
    if _THU_TU_KIEU[a.kieu] != _THU_TU_KIEU[b.kieu]:
        return _THU_TU_KIEU[a.kieu] < _THU_TU_KIEU[b.kieu]
    return a.phuong_an_id < b.phuong_an_id


def _giam_dan(a: float | None, b: float | None) -> float:
    """So sánh giảm dần, None xuống cuối (giống hàm dn của bản JS)."""
    if (a is None) != (b is None):
        return 1 if a is None else -1
    return 0 if a is None else b - a


def xep_hang(
    qt: QuyTacXetTuyen,
    hs: HoSoXetTuyen,
    ket_qua: KetQuaTinh,
    loc: Callable[[KetQuaPhuongAn], bool] | None = None,
) -> list[DongXepHang]:
    """Chọn phương án tốt nhất mỗi chương trình và chấm điểm phù hợp; `loc` giới hạn phương án trước khi chọn."""
    cm = _chi_muc(qt)
    w = qt.trong_so
    tot: dict[int, KetQuaPhuongAn] = {}
    for p in ket_qua.phuong_an:
        if not p.du_dieu_kien or not (p.diem_xet is not None or p.kieu == "CHI_DIEU_KIEN"):
            continue
        if loc is not None and not loc(p):
            continue
        hien_tai = tot.get(p.chuong_trinh_id)
        if hien_tai is None or _tot_hon(p, hien_tai):
            tot[p.chuong_trinh_id] = p

    def muc(loai: str, v: float | None):
        if v is None:
            return None
        return next(
            (
                m
                for m in qt.muc_phu_hop
                if m.loai == loai and (m.tu is None or v >= m.tu) and (m.den is None or v < m.den)
            ),
            None,
        )

    co_vi_tri = bool(hs.mong_muon_tinh) or bool(hs.mong_muon_vung)
    dong: list[DongXepHang] = []
    for ctr_id, p in tot.items():
        ctr = cm.chuong_trinh[ctr_id]
        xet_thang = p.kieu == "CHI_DIEU_KIEN"
        m = muc("KHA_NANG_TRUNG_TUYEN", p.chenh_lech_30)
        kn = 100 if xet_thang else (m.diem if m else None)
        hp = None
        if hs.ngan_sach and hs.ngan_sach > 0 and ctr.hoc_phi_tu is not None:
            hp = (
                100
                if ctr.hoc_phi_tu <= hs.ngan_sach
                else max(0, lam_tron(100 - (ctr.hoc_phi_tu - hs.ngan_sach) / hs.ngan_sach * 200, 2))
            )
        vt = None
        if co_vi_tri and ctr.ma_tinh is not None:
            vt = 100 if ctr.ma_tinh in hs.mong_muon_tinh else 70 if ctr.vung in hs.mong_muon_vung else 20
        ph = None
        if kn is not None:
            tu = kn * w["KHA_NANG_TRUNG_TUYEN"] + (hp * w["HOC_PHI"] if hp is not None else 0) + (
                vt * w["VI_TRI"] if vt is not None else 0
            )
            mau = w["KHA_NANG_TRUNG_TUYEN"] + (w["HOC_PHI"] if hp is not None else 0) + (w["VI_TRI"] if vt is not None else 0)
            ph = lam_tron(tu / mau, 2) if mau > 0 else None
        ml = muc("TONG_HOP", ph)
        dong.append(
            DongXepHang(
                thu_hang=0,
                chuong_trinh_id=ctr_id,
                ma_truong=ctr.ma_truong,
                phuong_an=p,
                la_xet_thang=xet_thang,
                diem_kha_nang=kn,
                nhan_kha_nang="Xét thẳng" if xet_thang else (m.nhan if m else None),
                diem_hoc_phi=hp,
                diem_vi_tri=vt,
                diem_phu_hop=ph,
                xep_loai=ml.nhan if ml else "Chưa có điểm chuẩn tham chiếu",
            )
        )

    def so_sanh(a: DongXepHang, b: DongXepHang) -> float:
        for x, y in (
            (a.diem_phu_hop, b.diem_phu_hop),
            (a.phuong_an.chenh_lech_30, b.phuong_an.chenh_lech_30),
            (_ty_le(a.phuong_an), _ty_le(b.phuong_an)),
        ):
            kq = _giam_dan(x, y)
            if kq:
                return kq
        return a.chuong_trinh_id - b.chuong_trinh_id

    dong.sort(key=cmp_to_key(so_sanh))
    for i, d in enumerate(dong, start=1):
        d.thu_hang = i
    return dong


def _ty_le(p: KetQuaPhuongAn) -> float | None:
    return None if p.diem_xet is None else p.diem_xet / p.thang


def theo_truong(dong: list[DongXepHang]) -> list[KetQuaTruong]:
    """Xếp hạng trường: điểm trường = trung bình điểm phù hợp của tối đa 3 chương trình tốt nhất."""
    nhom: dict[str, dict] = {}
    for d in dong:
        t = nhom.setdefault(
            d.ma_truong, {"so": 0, "da_cham": 0, "phu_hop": 0, "cao_nhat": None, "top": [], "hang_tot": d.thu_hang}
        )
        t["so"] += 1
        if d.diem_phu_hop is not None:
            t["da_cham"] += 1
            if d.diem_phu_hop >= 65:
                t["phu_hop"] += 1
            t["cao_nhat"] = _lon_hon(t["cao_nhat"], d.diem_phu_hop)
        if len(t["top"]) < 3:
            t["top"].append(d.diem_phu_hop)
    ket_qua = []
    for ma, t in nhom.items():
        co = [x for x in t["top"] if x is not None]
        tong = 0.0
        for x in co:
            tong += x
        ket_qua.append(
            KetQuaTruong(
                ma_truong=ma,
                so_chuong_trinh=t["so"],
                so_da_cham=t["da_cham"],
                so_phu_hop=t["phu_hop"],
                diem_cao_nhat=t["cao_nhat"],
                diem_truong=lam_tron(tong / len(co), 2) if co else None,
                hang_tot_nhat=t["hang_tot"],
            )
        )

    def so_sanh(a: KetQuaTruong, b: KetQuaTruong) -> float:
        kq = (a.diem_truong is None) - (b.diem_truong is None)
        if kq:
            return kq
        kq = (b.diem_truong or 0) - (a.diem_truong or 0)
        if kq:
            return kq
        return a.hang_tot_nhat - b.hang_tot_nhat

    ket_qua.sort(key=cmp_to_key(so_sanh))
    return ket_qua
