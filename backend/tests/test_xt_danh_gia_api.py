"""Bước 3.6: API xem kết quả đánh giá và kiểm tra quyền xem lần đánh giá."""

import unittest

from fastapi import HTTPException

import app.models as M
from app.api.v1.endpoints.xt_danh_gia import (
    get_lan_danh_gia,
    list_ket_qua_chuong_trinh,
    list_ket_qua_truong,
    list_phuong_an_chuong_trinh,
)
from app.services.xet_tuyen.bo_tinh import theo_truong, tinh_phuong_an, xep_hang
from app.services.xet_tuyen.chuyen_ho_so import KetQuaChuyenHoSo
from app.services.xet_tuyen.danh_gia import chay_danh_gia, tai_quy_tac
from tests import test_xet_tuyen_danh_gia as danh_gia

THIET_BI = "thiet-bi-khach-a1"
KHACH_KHAC = "thiet-bi-khach-b2"


def _nguoi_dung(id_: int, vai_tro: int = 0) -> M.NguoiDung:
    return M.NguoiDung(id=id_, ho_ten=f"Người {id_}", email=f"u{id_}@vd.vn", mat_khau="x", vai_tro=vai_tro)


CHU, NGUOI_KHAC, QUAN_TRI = _nguoi_dung(5), _nguoi_dung(6), _nguoi_dung(1, vai_tro=1)


class XtDanhGiaApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Dùng lại CSDL của test bước 3.5 (không import thẳng lớp test để các test đó không chạy lại ở đây).
        danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__(cls)
        ho_so = KetQuaChuyenHoSo(ho_so=cls.ho_so, gia_dinh=["Coi như tốt nghiệp THPT năm 2026"])
        cls.lan_khach = chay_danh_gia(cls.db, ho_so, nam=2026, ma_thiet_bi=THIET_BI, hom_nay=danh_gia.HOM_NAY).lan_danh_gia_id
        cls.lan_thanh_vien = chay_danh_gia(cls.db, ho_so, nam=2026, nguoi_dung_id=CHU.id, hom_nay=danh_gia.HOM_NAY).lan_danh_gia_id
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _ds(self, lan, ma_thiet_bi=THIET_BI, user=None, **loc):
        tham_so = dict(
            q=None, ma_truong=None, ma_tinh=None, xep_loai=None, chenh_tu=None, hoc_phi_den=None,
            ma_phuong_thuc=None, ma_to_hop=None, page=1, page_size=20,
        )
        tham_so.update(loc)
        return list_ket_qua_chuong_trinh(lan, ma_thiet_bi, db=self.db, user=user, **tham_so)

    def _ma_loi(self, ham, *args, **kwargs) -> tuple[int, str]:
        with self.assertRaises(HTTPException) as caught:
            ham(*args, **kwargs)
        return caught.exception.status_code, caught.exception.detail

    def test_quyen_xem_cua_khach(self):
        lan = get_lan_danh_gia(self.lan_khach, THIET_BI, self.db, None)
        self.assertEqual((lan.so_chuong_trinh, lan.so_truong), (119, 2))
        self.assertEqual(lan.gia_dinh, ["Coi như tốt nghiệp THPT năm 2026"])
        self.assertEqual(self._ma_loi(get_lan_danh_gia, self.lan_khach, KHACH_KHAC, self.db, None)[0], 403)
        self.assertEqual(self._ma_loi(get_lan_danh_gia, self.lan_khach, None, self.db, None)[0], 403)
        # Thành viên không xem được lần của khách, kể cả gửi đúng mã thiết bị.
        self.assertEqual(self._ma_loi(get_lan_danh_gia, self.lan_khach, THIET_BI, self.db, NGUOI_KHAC)[0], 403)

    def test_quyen_xem_cua_thanh_vien_va_quan_tri(self):
        self.assertEqual(get_lan_danh_gia(self.lan_thanh_vien, None, self.db, CHU).id, self.lan_thanh_vien)
        self.assertEqual(self._ma_loi(get_lan_danh_gia, self.lan_thanh_vien, None, self.db, NGUOI_KHAC)[0], 403)
        # Khách không xem được lần của thành viên dù đoán mã thiết bị.
        self.assertEqual(self._ma_loi(get_lan_danh_gia, self.lan_thanh_vien, THIET_BI, self.db, None)[0], 403)
        self.assertEqual(get_lan_danh_gia(self.lan_thanh_vien, None, self.db, QUAN_TRI).id, self.lan_thanh_vien)
        for ham, args in (
            (list_ket_qua_truong, (self.lan_thanh_vien, None)),
            (list_phuong_an_chuong_trinh, (self.lan_thanh_vien, 1, None)),
        ):
            with self.subTest(ham=ham.__name__):
                self.assertEqual(self._ma_loi(ham, *args, db=self.db, user=NGUOI_KHAC)[0], 403)

    def test_lan_khong_ton_tai_tra_400(self):
        ma, detail = self._ma_loi(get_lan_danh_gia, 99999, THIET_BI, self.db, None)
        self.assertEqual(ma, 400)
        self.assertIn("id = 99999", detail)

    def test_danh_sach_chuong_trinh_theo_thu_hang(self):
        trang = self._ds(self.lan_khach)
        self.assertEqual((trang.total, len(trang.items)), (119, 20))
        self.assertEqual([x.thu_hang for x in trang.items], list(range(1, 21)))
        dau = trang.items[0]
        self.assertIn(dau.ma_truong, {"BKA", "NTH"})
        self.assertIsNotNone(dau.phuong_an.ma_cong_thuc)
        trang_2 = self._ds(self.lan_khach, page=6)
        self.assertEqual([x.thu_hang for x in trang_2.items], list(range(101, 120)))

    def test_loc_chuong_trinh(self):
        bka = self._ds(self.lan_khach, ma_truong="BKA", page_size=200)
        self.assertTrue(bka.total and all(x.ma_truong == "BKA" for x in bka.items))
        self.assertEqual(self._ds(self.lan_khach, ma_truong="NTH", page_size=200).total + bka.total, 119)
        tsa = self._ds(self.lan_khach, ma_phuong_thuc="402", page_size=200)
        self.assertLessEqual(tsa.total, 119)
        self.assertEqual(self._ds(self.lan_khach, q="khong-co-chuong-trinh-nay").total, 0)
        chenh = self._ds(self.lan_khach, chenh_tu=0, page_size=200)
        self.assertTrue(all(x.chenh_lech_30 is not None and x.chenh_lech_30 >= 0 for x in chenh.items))

    def test_xep_hang_truong_giong_bo_tinh(self):
        qtn = tai_quy_tac(self.db, 2026)
        kq = tinh_phuong_an(qtn.quy_tac, self.ho_so, 2026, danh_gia.HOM_NAY.isoformat(), qtn.diem_chuan)
        mong_doi = theo_truong(xep_hang(qtn.quy_tac, self.ho_so, kq))
        thuc = list_ket_qua_truong(self.lan_khach, THIET_BI, db=self.db, user=None)
        self.assertEqual(
            [(t.ma_truong, t.so_chuong_trinh, t.diem_truong, t.hang_tot_nhat) for t in thuc],
            [(t.ma_truong, t.so_chuong_trinh, t.diem_truong, t.hang_tot_nhat) for t in mong_doi],
        )

    def test_phuong_an_cua_chuong_trinh(self):
        dau = self._ds(self.lan_khach).items[0]
        ds = list_phuong_an_chuong_trinh(self.lan_khach, dau.chuong_trinh_id, THIET_BI, db=self.db, user=None)
        self.assertTrue(ds[0].la_tot_nhat)
        self.assertEqual(sum(p.la_tot_nhat for p in ds), 1)
        self.assertEqual((ds[0].ma_cong_thuc, ds[0].diem_xet), (dau.phuong_an.ma_cong_thuc, dau.diem_xet))
        khong_dat = [p for p in ds if not p.du_dieu_kien]
        self.assertTrue(all(p.ly_do_khong_dat for p in khong_dat))


if __name__ == "__main__":
    unittest.main()
