"""Bước 3.1 + 3.2: bộ tính Python khớp tuyệt đối bản JavaScript trong docs/de-an-tuyen-sinh/test_xet_tuyen.html.

Kết quả mong đợi (`ket_qua_js.json.gz`) sinh bằng `node tests/du_lieu/xet_tuyen/xuat_ket_qua_js.mjs
<đường dẫn test_xet_tuyen.html> ket_qua_js.json du_lieu_html.json` rồi nén gzip: chạy chính bản JS với dữ liệu nhúng
của trang (quy tắc FTU + BKA 2026, điểm chuẩn giả định) và ba hồ sơ mẫu A, B, C, ngày cố định 2026-07-01.
"""

import gzip
import json
import unittest
from pathlib import Path

from app.services.xet_tuyen.bo_tinh import lam_tron, theo_truong, tinh_phuong_an, xep_hang
from app.services.xet_tuyen.mo_hinh import (
    BaiThiTinh,
    ChuongTrinhTinh,
    ChungChiTinh,
    CongThucTinh,
    DiemChuanTinh,
    DiemCongTinh,
    DieuKienTinh,
    HeSoMonTinh,
    HoSoXetTuyen,
    KetQuaNamHocTinh,
    MonTinh,
    MucPhuHopTinh,
    MucQuyDoiTinh,
    NhomDieuKienTinh,
    PhuongAnTinh,
    QuyTacXetTuyen,
    ThanhPhanTinh,
    ThanhTichTinh,
)

DU_LIEU = Path(__file__).resolve().parent / "du_lieu" / "xet_tuyen"


def _doc_gz(ten: str):
    with gzip.open(DU_LIEU / ten, "rt", encoding="utf-8") as f:
        return json.load(f)


def quy_tac_tu_du_lieu_html(d: dict) -> QuyTacXetTuyen:
    """Chuyển DATA của trang test_xet_tuyen.html sang QuyTacXetTuyen."""
    return QuyTacXetTuyen(
        cong_thuc=[
            CongThucTinh(
                id=c["id"],
                ma=c["ma"],
                de_an_id=c["deAn"],
                ma_phuong_thuc=c["pt"],
                kieu=c["kieu"],
                thang=c["thang"],
                nguon=c["nguon"],
                he_so_nhan=c["heSoNhan"],
                bang_ngoai_ngu_id=c["bangNn"],
                thay_ngoai_ngu=c["thayNn"],
                ap_dung_diem_cong=bool(c["cong"]),
                ap_dung_uu_tien=bool(c["uuTien"]),
                tran_diem_cong=c["tranCong"],
                so_le=c["soLe"],
                diem_san=c["diemSan"],
                nguong_tb_mon=c["nguongTb"],
                nguong_thpt_to_hop=c["nguongThpt"],
                trang_thai=bool(c["trangThai"]),
            )
            for c in d["congThuc"]
        ],
        chuong_trinh=[
            ChuongTrinhTinh(
                id=c["id"],
                de_an_id=c["deAn"],
                nam=c["nam"],
                ma_truong=c["truong"],
                ma_xet_tuyen=c["maXt"],
                ma_tinh=c["tinh"],
                vung=c["vung"],
                hoc_phi_tu=c["hocPhiTu"],
            )
            for c in d["chuongTrinh"]
        ],
        he_so_mon=[HeSoMonTinh(cong_thuc_id=h["ct"], he_so=h["heSo"], ma_mon=h["mon"], nhom_mon=h["nhom"]) for h in d["heSoMon"]],
        thanh_phan=[
            ThanhPhanTinh(
                id=t["id"],
                cong_thuc_id=t["ct"],
                vi_tri=t["viTri"],
                loai=t["loai"],
                ten=t["ten"],
                ma_bai_thi=t["baiThi"],
                bang_id=t["bang"],
                ma_mon=t["mon"],
                he_so=t["heSo"],
                nam_tu=t["namTu"],
                nam_den=t["namDen"],
                phan_tu_chon=t["phan"],
            )
            for t in d["thanhPhan"]
        ],
        quy_doi=[
            MucQuyDoiTinh(
                bang_id=q["bang"],
                quy_doi=q["qd"],
                ma_chung_chi=q["cc"],
                ma_bai_thi=q["bt"],
                ma_mon=q["mon"],
                cap_do=q["capDo"],
                tu=q["tu"],
                den=q["den"],
                he_so_noi_suy=q["hs"],
                dat_nguong=bool(q["dat"]),
            )
            for q in d["quyDoi"]
        ],
        phuong_an=[PhuongAnTinh(id=i, chuong_trinh_id=ctr, cong_thuc_id=ct, ma_to_hop=th) for i, ctr, ct, th in d["phuongAn"]],
        nhom_dieu_kien=[
            NhomDieuKienTinh(id=n["id"], de_an_id=n["deAn"], ten=n["ten"], cong_thuc_id=n["ct"], chuong_trinh_id=n["ctr"])
            for n in d["nhomDk"]
        ],
        dieu_kien=[
            DieuKienTinh(nhom_id=x["nhom"], chi_so=x["chiSo"], toan_tu=x["tt"], gia_tri=x["gt"], khoa=x["khoa"])
            for x in d["dieuKien"]
        ],
        diem_cong=[
            DiemCongTinh(
                de_an_id=x["deAn"],
                nhom=x["nhom"],
                chi_so=x["chiSo"],
                toan_tu=x["tt"],
                gia_tri=x["gt"],
                diem=x["diem"],
                khoa=x["khoa"],
                cong_thuc_id=x["ct"],
            )
            for x in d["diemCong"]
        ],
        to_hop={ma: th["viTri"] for ma, th in d["toHop"].items()},
        mon={m["ma"]: MonTinh(ten=m["ten"], nhom=m["nhom"]) for m in d["mon"]},
        khu_vuc={k["ma"]: k["diem"] for k in d["khuVuc"]},
        doi_tuong={k["ma"]: k["diem"] for k in d["doiTuong"]},
        trong_so=d["trongSo"],
        muc_phu_hop=[MucPhuHopTinh(loai=m["loai"], nhan=m["nhan"], tu=m["tu"], den=m["den"], diem=m["diem"]) for m in d["mucPhuHop"]],
    )


def diem_chuan_tu_du_lieu_html(ds: list[dict]) -> list[DiemChuanTinh]:
    return [
        DiemChuanTinh(
            ma_truong=x["truong"],
            ma_xet_tuyen=x["maXt"],
            nam=x["nam"],
            diem=x["diem"],
            thang=x["thang"],
            ma_phuong_thuc=x["pt"],
            ma_to_hop=x["toHop"],
        )
        for x in ds
    ]


def ho_so_tu_preset(p: dict) -> HoSoXetTuyen:
    """Chuyển hồ sơ mẫu (PRESETS của trang HTML) sang HoSoXetTuyen."""
    return HoSoXetTuyen(
        nam_tot_nghiep=p["namTotNghiep"],
        da_tot_nghiep=p["daTotNghiep"],
        he_chuyen=p["heChuyen"],
        mon_chuyen=p["monChuyen"] or None,
        khu_vuc=p["khuVuc"] or None,
        doi_tuong=p["doiTuong"] or None,
        ngan_sach=p["nganSach"],
        mong_muon_tinh=p["mongMuon"]["tinh"],
        mong_muon_vung=p["mongMuon"]["vung"],
        nam_hoc={
            int(lop): KetQuaNamHocTinh(tbc=v.get("tbc"), hoc_luc=v.get("hocLuc"), ren_luyen=v.get("renLuyen"))
            for lop, v in p["namHoc"].items()
        },
        diem_thpt=p["thpt"],
        hoc_ba={mon: {int(lop): v for lop, v in theo_lop.items()} for mon, theo_lop in p["hocBa"].items()},
        bai_thi=[BaiThiTinh(ma=b["ma"], diem=b["diem"], nam=b["nam"], phan_tu_chon=b["phan"]) for b in p["baiThi"]],
        chung_chi=[ChungChiTinh(ma=c["ma"], diem=c["diem"], cap_do=c["capDo"], het_han=c["hetHan"]) for c in p["chungChi"]],
        thanh_tich=[ThanhTichTinh(ma=t["ma"], muc_giai=t["mucGiai"]) for t in p["thanhTich"]],
    )


DATA = _doc_gz("du_lieu_html.json.gz")
KET_QUA_JS = _doc_gz("ket_qua_js.json.gz")
QUY_TAC = quy_tac_tu_du_lieu_html(DATA)
DIEM_CHUAN = diem_chuan_tu_du_lieu_html(DATA["diemChuanDemo"])
NAM, HOM_NAY = KET_QUA_JS["tuy_chon"]["nam"], KET_QUA_JS["tuy_chon"]["homNay"]
TEN_CONG_THUC = {c.id: c.ma for c in QUY_TAC.cong_thuc}
MA_XET_TUYEN = {c.id: c.ma_xet_tuyen for c in QUY_TAC.chuong_trinh}


def _tinh(ten: str):
    hs = ho_so_tu_preset(KET_QUA_JS["ho_so"][ten]["ho_so"])
    kq = tinh_phuong_an(QUY_TAC, hs, NAM, HOM_NAY, DIEM_CHUAN)
    return hs, kq


# Trường của kết quả JS → thuộc tính của KetQuaPhuongAn.
_TRUONG_PA = {
    "ctr": "chuong_trinh_id",
    "ct": "cong_thuc_id",
    "toHop": "ma_to_hop",
    "kieu": "kieu",
    "goc": "diem_goc",
    "tb": "tb_mon",
    "thpt": "tong_thpt",
    "cong": "diem_cong",
    "ut": "diem_uu_tien",
    "xet": "diem_xet",
    "datNguong": "dat_nguong",
    "du": "du_dieu_kien",
    "lyDo": "ly_do",
    "soNhom": "so_nhom",
    "soDat": "so_nhom_dat",
    "dc": "diem_chuan",
    "namDc": "nam_diem_chuan",
    "chenh": "chenh_lech_30",
    "chiTiet": "chi_tiet",
}
_TRUONG_XH = {
    "hang": "thu_hang",
    "ctr": "chuong_trinh_id",
    "xetThang": "la_xet_thang",
    "kn": "diem_kha_nang",
    "nhanKn": "nhan_kha_nang",
    "hp": "diem_hoc_phi",
    "vt": "diem_vi_tri",
    "ph": "diem_phu_hop",
    "loai": "xep_loai",
}


class DoiChieuBanJavaScriptTests(unittest.TestCase):
    """So từng phương án, từng dòng xếp hạng và xếp hạng trường với bản JS: phải khớp tuyệt đối."""

    def _doi_chieu(self, ten: str):
        mong_doi = KET_QUA_JS["ho_so"][ten]
        hs, kq = _tinh(ten)
        self.assertEqual(kq.muc_uu_tien, mong_doi["muc_uu_tien"])
        self.assertEqual([p.phuong_an_id for p in kq.phuong_an], [p["paId"] for p in mong_doi["phuong_an"]])
        for thuc, js in zip(kq.phuong_an, mong_doi["phuong_an"], strict=True):
            for khoa_js, thuoc_tinh in _TRUONG_PA.items():
                self.assertEqual(
                    getattr(thuc, thuoc_tinh), js[khoa_js], f"hồ sơ {ten}, phương án {js['paId']}, {thuoc_tinh}"
                )
        dong = xep_hang(QUY_TAC, hs, kq)
        self.assertEqual(len(dong), len(mong_doi["xep_hang"]))
        for thuc, js in zip(dong, mong_doi["xep_hang"], strict=True):
            self.assertEqual(thuc.phuong_an.phuong_an_id, js["paId"], f"hồ sơ {ten}, hạng {js['hang']}")
            for khoa_js, thuoc_tinh in _TRUONG_XH.items():
                self.assertEqual(getattr(thuc, thuoc_tinh), js[khoa_js], f"hồ sơ {ten}, hạng {js['hang']}, {thuoc_tinh}")
        truong = theo_truong(dong)
        self.assertEqual(
            [(t.ma_truong, t.so_chuong_trinh, t.so_da_cham, t.so_phu_hop, t.diem_cao_nhat, t.diem_truong, t.hang_tot_nhat)
             for t in truong],
            [(t["truong"], t["so"], t["daCham"], t["phuHop"], t["caoNhat"], t["diem"], t["hangTot"])
             for t in mong_doi["theo_truong"]],
        )
        return kq, dong

    def test_ho_so_a(self):
        kq, dong = self._doi_chieu("A")
        self.assertEqual((len(kq.phuong_an), len(dong)), (890, 119))

    def test_ho_so_b(self):
        kq, dong = self._doi_chieu("B")
        self.assertEqual((len(kq.phuong_an), len(dong)), (96, 44))

    def test_ho_so_c(self):
        self._doi_chieu("C")


class SoLieuTaiLieuTests(unittest.TestCase):
    """Các số đã đối chiếu tay trong IMPLEMENT.md mục 7."""

    @classmethod
    def setUpClass(cls):
        cls.kq = {ten: _tinh(ten)[1] for ten in ("A", "B")}

    def _pa(self, ten: str, ma_cong_thuc: str, to_hop: str | None = None):
        return next(
            p
            for p in self.kq[ten].phuong_an
            if TEN_CONG_THUC[p.cong_thuc_id] == ma_cong_thuc and (to_hop is None or p.ma_to_hop == to_hop)
        )

    def test_ftu_thi_thpt_a00(self):
        p = self._pa("A", "FTU_THPT_30", "A00")
        self.assertEqual((p.diem_goc, p.diem_uu_tien, p.diem_xet), (26.25, 0.25, 26.5))

    def test_ftu_hoc_ba(self):
        p = self._pa("A", "FTU_HB_30", "A00")
        self.assertEqual((p.diem_goc, p.diem_xet, lam_tron(p.tb_mon, 2)), (27.5, 27.67, 9.17))
        d01 = self._pa("A", "FTU_HB_30", "D01")
        self.assertFalse(d01.du_dieu_kien)
        self.assertIn("Trung bình các môn xét 8.93 dưới ngưỡng 9.00", d01.ly_do)

    def test_ftu_hsa_va_thang_40(self):
        p = self._pa("A", "FTU_HSA_30")
        self.assertEqual((p.diem_goc, p.diem_xet), (27.72, 27.87))
        it40 = self._pa("A", "FTU_HB_IT40", "A01")
        self.assertEqual((it40.diem_xet, it40.thang), (37.29, 40))

    def test_bka(self):
        k01 = self._pa("A", "BKA_THPT_K01")
        self.assertEqual((k01.diem_goc, k01.diem_xet), (26.25, 26.5))
        self.assertEqual((self._pa("A", "BKA_TSA").diem_xet, self._pa("A", "BKA_TSA").thang), (74.17, 100))

    def test_ho_so_b_khong_dat_nguong(self):
        p = self._pa("B", "FTU_THPT_30", "A00")
        self.assertEqual(p.diem_xet, 22.25)
        self.assertFalse(p.du_dieu_kien)
        self.assertIn("dưới ngưỡng 24.00", p.ly_do)


class LamTronTests(unittest.TestCase):
    def test_nua_len_nhu_javascript(self):
        # Giá trị đã đối chiếu với hàm rnd của bản JS (node): 2.675 thực chất là 2.67499..., bù 1e-9 nên vẫn lên;
        # số âm được bù -1e-9 nên -2.5 thành -3.
        self.assertEqual(lam_tron(2.675, 2), 2.68)
        self.assertEqual(lam_tron(-2.5, 0), -3)
        self.assertEqual(lam_tron(-1.005, 2), -1.01)
        self.assertIsNone(lam_tron(None, 2))


if __name__ == "__main__":
    unittest.main()
