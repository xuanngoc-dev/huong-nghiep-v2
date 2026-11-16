"""Bước 5.5: độ phủ dữ liệu xét tuyển."""

import unittest

from sqlalchemy import select

import app.models as M
from app.api.v1.endpoints.xt_do_phu import get_do_phu
from tests import test_xet_tuyen_danh_gia as danh_gia


class DoPhuTests(unittest.TestCase):
    # CSDL đã import BKA, NTH 2026 (cả hai đang áp dụng, có điểm chuẩn mẫu).
    setUpClass = classmethod(danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__)
    tearDownClass = classmethod(danh_gia.DanhGiaTuCsdlTests.tearDownClass.__func__)

    def _goi(self, **kw):
        args = {"nam": 2026, "q": None, "trang_thai_xet_tuyen": None, "page": 1, "page_size": 20, "db": self.db}
        args.update(kw)
        return get_do_phu(**args)

    def test_dem_theo_dinh_nghia_bo_tinh(self):
        ctr = list(self.db.scalars(select(M.DatsChuongTrinhDaoTao)))
        bka = self.db.scalars(select(M.DatsTuyenSinh).where(M.DatsTuyenSinh.ma_truong == "BKA")).one()
        so_ctr_bka = sum(1 for c in ctr if c.de_an_id == bka.id)
        # Mã xét tuyển của BKA có trong điểm chuẩn mẫu.
        co_diem_chuan = {
            ma
            for ma in self.db.scalars(select(M.XtDiemChuan.ma_xet_tuyen).where(M.XtDiemChuan.ma_truong == "BKA"))
        }
        mong_doi_diem_chuan = sum(1 for c in ctr if c.de_an_id == bka.id and c.ma_xet_tuyen in co_diem_chuan)

        kq = self._goi()
        self.assertEqual((kq.nam, kq.total, kq.tong.so_de_an, kq.tong.theo_trang_thai), (2026, 2, 2, {"0": 0, "1": 0, "2": 2}))
        self.assertEqual(kq.tong.so_chuong_trinh, len(ctr))
        dong = {d.ma_truong: d for d in kq.items}["BKA"]
        self.assertEqual(dong.so_chuong_trinh, so_ctr_bka)
        self.assertEqual(dong.co_diem_chuan, mong_doi_diem_chuan)
        self.assertGreater(dong.co_diem_chuan, 0)
        self.assertEqual(dong.co_ma_nganh, 0)
        self.assertGreater(dong.so_cong_thuc, 0)

        # Gắn ngành cho một chương trình; trường có tỉnh thì mọi chương trình có vị trí.
        mot = next(c for c in ctr if c.de_an_id == bka.id)
        nganh = M.DmNganhDaoTao(ma_nhom_nganh="74802", ma_nganh="7480299", ten_nganh="Thử", ten_tieng_anh="", trinh_do="ĐH")
        self.db.add(nganh)
        self.db.flush()
        mot.nganh_dao_tao_id = nganh.id
        truong = self.db.scalars(select(M.DmTruong).where(M.DmTruong.ma_truong == "BKA")).one()
        truong.ma_tinh_thanh = "01"
        self.db.flush()
        try:
            dong = {d.ma_truong: d for d in self._goi().items}["BKA"]
            self.assertEqual((dong.co_ma_nganh, dong.co_vi_tri), (1, so_ctr_bka))
        finally:
            self.db.rollback()

    def test_loc_va_nam_rong(self):
        kq = self._goi(q="bk", trang_thai_xet_tuyen=2)
        self.assertEqual([d.ma_truong for d in kq.items], ["BKA"])
        self.assertEqual(kq.tong.so_de_an, 2)  # tổng không theo bộ lọc
        rong = self._goi(nam=2030)
        self.assertEqual((rong.items, rong.total, rong.tong.so_de_an, rong.tong.so_chuong_trinh), ([], 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
