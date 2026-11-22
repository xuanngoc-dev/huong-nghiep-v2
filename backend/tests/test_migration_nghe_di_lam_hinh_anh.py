"""Migration 20261211_0084: hinh_anh_mo_ta cho nhóm nghề / nghề cụ thể đi làm, nghề bắt buộc đào tạo chính quy."""

import unittest

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.test_migration_nhom_nghe_gioi_thieu import _nap, _tao_bang_truoc_0083


class MigrationNgheDiLamHinhAnhTests(unittest.TestCase):
    def setUp(self):
        self.goc = _nap("20261126_0069_dm_nhom_nghe_di_lam.py")
        self.truoc = _nap("20261210_0083_nhom_nghe_gioi_thieu_bang_cap.py")
        self.mod = _nap("20261211_0084_nghe_di_lam_hinh_anh_chinh_quy.py")
        self.engine = sa.create_engine("sqlite://")

    def _dem(self, conn, bang):
        return conn.scalar(sa.text(f"SELECT COUNT(*) FROM {bang}"))

    def test_upgrade_hai_lan_roi_downgrade(self):
        with self.engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
            _tao_bang_truoc_0083(conn, self.goc)
            self.truoc.upgrade()
            so_nhom_goc = self._dem(conn, "dm_nhom_nghe_di_lam")
            so_nghe_goc = self._dem(conn, "dm_nghe_cu_the_di_lam")
            tieu_chi_goc = self._dem(conn, "dm_nhom_nghe_tieu_chi")

            self.mod.upgrade()
            # Quản trị đã thay ảnh thật: chạy lại không được ghi đè.
            conn.execute(sa.text(
                "UPDATE dm_nghe_cu_the_di_lam SET hinh_anh_mo_ta = 'https://anh.that/bac-si.jpg'"
                " WHERE ten_nghe = 'Bác sĩ'"
            ))
            self.mod.upgrade()

            self.assertEqual(self._dem(conn, "dm_nhom_nghe_di_lam"), so_nhom_goc + len(self.mod.NHOM_MOI))
            tong_nghe_moi = sum(len(ds) for ds in self.mod.NGHE.values())
            self.assertEqual(self._dem(conn, "dm_nghe_cu_the_di_lam"), so_nghe_goc + tong_nghe_moi)
            self.assertGreater(self._dem(conn, "dm_nhom_nghe_tieu_chi"), tieu_chi_goc)
            # Mọi bản ghi đều có ảnh.
            for bang in ("dm_nhom_nghe_di_lam", "dm_nghe_cu_the_di_lam"):
                self.assertEqual(conn.scalar(sa.text(f"SELECT COUNT(*) FROM {bang} WHERE hinh_anh_mo_ta IS NULL")), 0)
            self.assertEqual(conn.scalar(sa.text(
                "SELECT hinh_anh_mo_ta FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Bác sĩ'"
            )), "https://anh.that/bac-si.jpg")
            self.assertEqual(conn.scalar(sa.text(
                "SELECT bat_buoc_dao_tao_chinh_quy FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Luật sư'"
            )), 1)

            self.mod.downgrade()
            self.assertEqual(self._dem(conn, "dm_nhom_nghe_di_lam"), so_nhom_goc)
            self.assertEqual(self._dem(conn, "dm_nghe_cu_the_di_lam"), so_nghe_goc)
            self.assertEqual(self._dem(conn, "dm_nhom_nghe_tieu_chi"), tieu_chi_goc)
            for bang in ("dm_nhom_nghe_di_lam", "dm_nghe_cu_the_di_lam"):
                self.assertNotIn("hinh_anh_mo_ta", {c["name"] for c in sa.inspect(conn).get_columns(bang)})

    def test_du_lieu_mau_hop_le(self):
        ma_moi = {n["ma_nhom"] for n in self.mod.NHOM_MOI}
        self.assertEqual(set(self.mod.GIOI_THIEU), ma_moi)
        self.assertEqual(set(self.mod.TIEU_CHI), ma_moi)
        # Nghề thêm vào nhóm đã có không được trùng nghề của migration 0083.
        for ma, ds in self.mod.NGHE.items():
            self.assertTrue(ma in ma_moi or ma in self.truoc.NGHE, f"Nhóm {ma} không tồn tại")
            ten = [n[0] for n in ds]
            self.assertEqual(len(ten), len(set(ten)), f"Trùng tên nghề trong {ma}")
            ten_cu = {n[0] for n in self.truoc.NGHE.get(ma, [])}
            self.assertFalse(set(ten) & ten_cu, f"Nghề đã có trong 0083: {set(ten) & ten_cu}")
            for _, _, _, bang_cap, chinh_quy in ds:
                self.assertIn(chinh_quy, (None, 1))
                if chinh_quy:
                    self.assertTrue(bang_cap, "Nghề bắt buộc chính quy phải ghi bằng cấp")
                self.assertTrue(bang_cap is None or len(bang_cap) <= 255)
        for nhom in self.mod.NHOM_MOI:
            self.assertLessEqual(len(nhom["danh_gia_trien_vong"]), 255)
            self.assertLessEqual(len(nhom["muc_luong_text"]), 100)
            self.assertLessEqual(len(nhom["thoi_gian_dao_tao_text"]), 100)
            self.assertLessEqual(nhom["luong_khoi_diem_min"], nhom["luong_khoi_diem_max"])
            self.assertLessEqual(len(self.mod.anh_placeholder(nhom["ten_nhom"])), 500)


if __name__ == "__main__":
    unittest.main()
