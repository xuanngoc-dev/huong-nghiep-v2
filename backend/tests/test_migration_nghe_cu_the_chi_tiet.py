"""Migration 20261212_0085: thông tin chi tiết của nghề cụ thể đi làm và dữ liệu mẫu 60 nghề."""

import unittest

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from tests.test_migration_nhom_nghe_gioi_thieu import _nap, _tao_bang_truoc_0083

# Giới hạn độ dài của các cột VARCHAR mới.
_DO_DAI = {
    "hinh_thuc_dao_tao": 255, "trinh_do_toi_thieu": 100, "ghi_chu_luong": 500, "dac_thu_thoi_gian": 500,
    "yeu_cau_suc_khoe": 500, "nhom_holland": 20, "tu_khoa_tim_kiem": 500,
}


class MigrationNgheCuTheChiTietTests(unittest.TestCase):
    def setUp(self):
        self.goc = _nap("20261126_0069_dm_nhom_nghe_di_lam.py")
        self.m0083 = _nap("20261210_0083_nhom_nghe_gioi_thieu_bang_cap.py")
        self.m0084 = _nap("20261211_0084_nghe_di_lam_hinh_anh_chinh_quy.py")
        self.mod = _nap("20261212_0085_nghe_cu_the_thong_tin_chi_tiet.py")
        self.engine = sa.create_engine("sqlite://")

    def test_upgrade_hai_lan_roi_downgrade(self):
        with self.engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
            _tao_bang_truoc_0083(conn, self.goc)
            self.m0083.upgrade()
            self.m0084.upgrade()
            so_nghe = conn.scalar(sa.text("SELECT COUNT(*) FROM dm_nghe_cu_the_di_lam"))

            self.mod.upgrade()
            # Quản trị đã sửa một ô: chạy lại không được ghi đè.
            conn.execute(sa.text(
                "UPDATE dm_nghe_cu_the_di_lam SET ky_nang_mem = 'Quản trị đã sửa' WHERE ten_nghe = 'Thợ hàn'"
            ))
            self.mod.upgrade()

            # Mọi nghề mẫu đã có sẵn từ 0083: không thêm dòng mới.
            self.assertEqual(conn.scalar(sa.text("SELECT COUNT(*) FROM dm_nghe_cu_the_di_lam")), so_nghe)
            self.assertEqual(conn.scalar(sa.text(
                "SELECT COUNT(*) FROM dm_nghe_cu_the_di_lam WHERE mo_ta_cong_viec IS NOT NULL"
            )), len(self.mod.NGHE_MAU))
            self.assertEqual(conn.scalar(sa.text(
                "SELECT ky_nang_mem FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Thợ hàn'"
            )), "Quản trị đã sửa")
            dong = conn.execute(sa.text(
                "SELECT luong_khoi_diem_min, don_vi_tien_te, chu_ky_luong, muc_do_ap_luc"
                " FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Lái xe container'"
            )).one()
            self.assertEqual(int(dong[0]), 14_000_000)
            self.assertEqual(tuple(dong[1:]), ("VND", "thang", "cao"))
            # Nghề không có dữ liệu mẫu vẫn nhận giá trị mặc định đơn vị tiền tệ, chu kỳ lương.
            self.assertEqual(conn.scalar(sa.text(
                "SELECT COUNT(*) FROM dm_nghe_cu_the_di_lam WHERE don_vi_tien_te <> 'VND' OR chu_ky_luong <> 'thang'"
            )), 0)

            self.mod.downgrade()
            cot = {c["name"] for c in sa.inspect(conn).get_columns("dm_nghe_cu_the_di_lam")}
            self.assertFalse(set(self.mod.COT_MOI) & cot)
            self.assertEqual(conn.scalar(sa.text("SELECT COUNT(*) FROM dm_nghe_cu_the_di_lam")), so_nghe)

    def test_du_lieu_mau_hop_le(self):
        mau = self.mod.NGHE_MAU
        self.assertEqual(len(mau), 60)
        khoa = [(n["ma_nhom"], n["ten_nghe"]) for n in mau]
        self.assertEqual(len(khoa), len(set(khoa)), "Trùng nghề mẫu")
        # Nghề mẫu là nghề đi làm được ngay đã có ở 0083 (không bắt buộc chính quy).
        nghe_0083 = {(ma, n[0]): n[4] for ma, ds in self.m0083.NGHE.items() for n in ds}
        for ma_nhom, ten in khoa:
            self.assertIn((ma_nhom, ten), nghe_0083, f"Không có nghề {ten} trong nhóm {ma_nhom}")
            self.assertIsNone(nghe_0083[(ma_nhom, ten)], f"{ten} là nghề bắt buộc chính quy")
        self.assertEqual(len({n["ma_nhom"] for n in mau}), len(self.m0083.NGHE))
        for n in mau:
            for cot, toi_da in _DO_DAI.items():
                self.assertTrue(n[cot] is None or len(n[cot]) <= toi_da, f"{n['ten_nghe']}: {cot} quá dài")
            self.assertIn(n["muc_do_ap_luc"], ("thap", "trung_binh", "cao"))
            for cot_min, cot_max in (
                ("luong_khoi_diem_min", "luong_khoi_diem_max"), ("luong_trung_binh_min", "luong_trung_binh_max"),
                ("luong_cao_min", "luong_cao_max"),
            ):
                self.assertLessEqual(n[cot_min], n[cot_max], f"{n['ten_nghe']}: {cot_min} > {cot_max}")
            self.assertLessEqual(n["luong_khoi_diem_min"], n["luong_trung_binh_min"])
            self.assertLessEqual(n["luong_trung_binh_max"], n["luong_cao_max"])


if __name__ == "__main__":
    unittest.main()
