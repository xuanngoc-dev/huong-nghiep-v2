"""Bước 5.1: điểm ưu tiên và tổ hợp chọn theo năm tuyển sinh."""

import unittest

from sqlalchemy import delete, select

import app.models as M
from app.services.xet_tuyen.bo_tinh import tinh_phuong_an
from app.services.xet_tuyen.danh_gia import muc_diem_uu_tien, tai_quy_tac
from tests import test_xet_tuyen_danh_gia as danh_gia


class TheoNamTests(unittest.TestCase):
    # Dùng lại CSDL đã import BKA, NTH 2026 (không kế thừa để các test kia không chạy lại ở đây).
    setUpClass = classmethod(danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__)
    tearDownClass = classmethod(danh_gia.DanhGiaTuCsdlTests.tearDownClass.__func__)

    def tearDown(self):
        self.db.execute(delete(M.DmMucDiemUuTien))
        for th in self.db.scalars(select(M.DmToHopMonHoc)):
            th.nam_ap_dung_tu = th.nam_ap_dung_den = None
        self.db.commit()

    def _tinh(self):
        qtn = tai_quy_tac(self.db, 2026)
        return qtn, tinh_phuong_an(qtn.quy_tac, self.ho_so, 2026, danh_gia.HOM_NAY.isoformat(), qtn.diem_chuan)

    def test_muc_diem_uu_tien_theo_nam(self):
        self.assertEqual(muc_diem_uu_tien(self.db, 2026)[0]["KV2-NT"], 0.5)  # chưa có mức theo năm: dùng danh mục
        self.db.add_all(
            [
                M.DmMucDiemUuTien(loai="KHU_VUC", ma="KV2-NT", nam_ap_dung_tu=2020, nam_ap_dung_den=2025, diem_cong=1),
                M.DmMucDiemUuTien(loai="KHU_VUC", ma="KV2-NT", nam_ap_dung_tu=2026, diem_cong=0.75),
                M.DmMucDiemUuTien(loai="DOI_TUONG", ma="04", nam_ap_dung_tu=2026, diem_cong=1),
            ]
        )
        self.db.commit()
        kv_2025, dt_2025 = muc_diem_uu_tien(self.db, 2025)
        kv_2026, dt_2026 = muc_diem_uu_tien(self.db, 2026)
        self.assertEqual((kv_2025["KV2-NT"], kv_2026["KV2-NT"], muc_diem_uu_tien(self.db, 2030)[0]["KV2-NT"]), (1, 0.75, 0.75))
        self.assertEqual((dt_2025["04"], dt_2026["04"]), (2, 1))
        self.assertEqual(kv_2026["KV1"], 0.75)  # mã không có mức theo năm giữ điểm danh mục
        self.assertEqual(muc_diem_uu_tien(self.db, 2019)[0]["KV2-NT"], 0.5)

    def test_bo_tinh_dung_muc_cua_nam_tuyen_sinh(self):
        qtn_cu, cu = self._tinh()
        self.db.add(M.DmMucDiemUuTien(loai="KHU_VUC", ma="KV2-NT", nam_ap_dung_tu=2026, diem_cong=0.75))
        self.db.commit()
        qtn_moi, moi = self._tinh()
        self.assertIsNot(qtn_moi, qtn_cu)  # cache làm mới khi thêm mức điểm
        self.assertEqual(qtn_moi.quy_tac.khu_vuc["KV2-NT"], 0.75)
        tang = [
            (a.diem_uu_tien, b.diem_uu_tien)
            for a, b in zip(cu.phuong_an, moi.phuong_an, strict=True)
            if a.diem_uu_tien is not None and b.diem_uu_tien != a.diem_uu_tien
        ]
        self.assertTrue(tang)
        self.assertTrue(all(b > a for a, b in tang))

    def test_to_hop_het_han_khong_tinh_duoc(self):
        _qtn, cu = self._tinh()
        dung = {p.ma_to_hop for p in cu.phuong_an if p.ma_to_hop and p.ma_to_hop.startswith("A")}
        ma = sorted(dung)[0]
        self.db.scalars(select(M.DmToHopMonHoc).where(M.DmToHopMonHoc.ma_to_hop == ma)).one().nam_ap_dung_den = 2025
        self.db.commit()
        qtn, moi = self._tinh()
        self.assertNotIn(ma, qtn.quy_tac.to_hop)
        self.assertIn(ma, qtn.to_hop_id)  # vẫn đổi được mã → id khi lưu kết quả
        self.assertFalse(any(p.ma_to_hop == ma for p in moi.phuong_an))
        self.assertTrue(any(p.ma_to_hop == ma for p in cu.phuong_an))


if __name__ == "__main__":
    unittest.main()
