"""Import đề án đầy đủ một trường, một năm: bảng dats_ và khối quy_tac_xet_tuyen trong cùng một lần gọi.

Chạy file mẫu docs/de-an-tuyen-sinh/chuan_du_lieu/mau_import_day_du.json qua bộ import thật để file mẫu luôn
import được.
"""

import copy
import json
import unittest
from pathlib import Path

from sqlalchemy import func, select

import app.models as M
from app.services.dats_import import DatsImportError, import_day_du
from tests.hoi_quy_xet_tuyen import DANH_MUC_MA, tao_csdl

MAU = Path(__file__).resolve().parents[2] / "docs" / "de-an-tuyen-sinh" / "chuan_du_lieu" / "mau_import_day_du.json"


class ImportDayDuTests(unittest.TestCase):
    def setUp(self):
        self.db, _danh_muc = tao_csdl("BKA")
        bind = self.db.get_bind()
        for model in (M.DmPhuongThucTuyenSinh, M.DmThanhTichHocTapNghienCuu):
            model.__table__.create(bind)
        dm = json.loads(DANH_MUC_MA.read_text(encoding="utf-8"))
        self.db.add_all(M.DmPhuongThucTuyenSinh(ma_phuong_thuc=x["ma"], ten_phuong_thuc=x["ten"]) for x in dm["phuong_thuc_cua_bo"])
        self.db.add_all(M.DmThanhTichHocTapNghienCuu(ma_thanh_tich=x["ma"], ten_thanh_tich=x["ten"]) for x in dm["thanh_tich"])
        self.db.add_all(
            M.DmNganhDaoTao(ma_nhom_nganh=x["ma"][:5], ma_nganh=x["ma"], ten_nganh=x["ten"], ten_tieng_anh="", trinh_do="ĐH")
            for x in dm["nganh"]
        )
        self.db.commit()
        self.mau = json.loads(MAU.read_text(encoding="utf-8"))

    def tearDown(self):
        self.db.close()

    def _dem(self, model) -> int:
        return self.db.scalar(select(func.count()).select_from(model))

    def test_file_mau_import_du_moi_bang(self):
        info = self.mau["thong_tin_import"]
        de_an_id, counts, quy_tac = import_day_du(self.db, info["ma_truong"], info["nam_tuyen_sinh"], self.mau)
        self.db.commit()
        # Đủ 23 bảng dats_ có trong file.
        self.assertEqual(len(counts), 23, sorted(counts))
        self.assertEqual(counts["dats_chuong_trinh_dao_tao"], 3)
        self.assertEqual(counts["dats_phuong_thuc"], 7)
        # Khối quy tắc khớp đúng chương trình, cơ sở của phần dats_ (không tạo thêm, không cảnh báo).
        self.assertEqual(quy_tac.canh_bao, [])
        self.assertNotIn("dats_chuong_trinh_dao_tao", quy_tac.so_dong)
        self.assertNotIn("dats_tru_so", quy_tac.so_dong)
        self.assertEqual(self._dem(M.DatsChuongTrinhDaoTao), 3)
        for bang, so in {"xt_cong_thuc": 6, "dats_hoc_phi": 3, "xt_diem_chuan": 4, "xt_bang_quy_doi": 2}.items():
            self.assertEqual(quy_tac.so_dong.get(bang), so, bang)
        self.assertGreater(quy_tac.so_dong["xt_phuong_an"], 0)

        de_an = self.db.get(M.DatsTuyenSinh, de_an_id)
        self.assertEqual((de_an.ma_truong, de_an.nam_tuyen_sinh, de_an.trang_thai_xet_tuyen), ("BKA", 2027, 1))
        # Mã danh mục dùng thay id.
        tinh = dict(self.db.execute(select(M.DmTinhThanh.id, M.DmTinhThanh.ma_tinh)).all())
        nganh = dict(self.db.execute(select(M.DmNganhDaoTao.id, M.DmNganhDaoTao.ma_nganh)).all())
        self.assertEqual(
            {(c.ten_co_so, tinh[c.tinh_thanh_id]) for c in self.db.scalars(select(M.DatsTruSo))},
            {("Trụ sở chính Hà Nội", "01"), ("Cơ sở Hải Phòng", "31")},
        )
        self.assertEqual(
            {(c.ma_xet_tuyen, nganh[c.nganh_dao_tao_id]) for c in self.db.scalars(select(M.DatsChuongTrinhDaoTao))},
            {("IT1", "7480101"), ("ME1", "7520103"), ("IT-HP", "7480201")},
        )
        quy_doi = self.db.scalars(select(M.DatsQuyDoiNguongDauVao)).one()
        self.assertIsNotNone(quy_doi.phuong_thuc_nguon_id)
        self.assertIsNotNone(quy_doi.to_hop_dich_id)
        # Bảng con lồng trong phương thức nhận đủ khóa ngoại phương thức, chương trình, đề án.
        dk = self.db.scalars(select(M.DatsDieuKienDuTuyen)).one()
        self.assertTrue(dk.de_an_phuong_thuc_id and dk.de_an_chuong_trinh_id and dk.doi_tuong_du_tuyen_id)
        lich_su = self.db.scalars(select(M.XtLichSuImport)).one()
        self.assertEqual((lich_su.de_an_id, lich_su.ten_file), (de_an_id, "de-an-tuyen-sinh/import"))

    def test_khong_co_quy_tac_van_import_nhu_cu(self):
        du_lieu = copy.deepcopy(self.mau)
        del du_lieu["quy_tac_xet_tuyen"]
        _id, counts, quy_tac = import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIsNone(quy_tac)
        self.assertEqual(self._dem(M.XtCongThuc), 0)
        self.assertEqual(counts["dats_tuyen_sinh"], 1)

    def test_quy_tac_loi_bao_ro_dong_loi(self):
        du_lieu = copy.deepcopy(self.mau)
        du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"][0]["ma_cong_thuc"] = "KHONG_CO"
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("quy_tac_xet_tuyen", str(ctx.exception))
        self.assertIn("KHONG_CO", str(ctx.exception))

    def test_quy_tac_sai_truong_nam(self):
        du_lieu = copy.deepcopy(self.mau)
        du_lieu["quy_tac_xet_tuyen"]["nam_tuyen_sinh"] = 2026
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("không khớp", str(ctx.exception))

    def test_chuong_trinh_khong_khop_co_canh_bao(self):
        du_lieu = copy.deepcopy(self.mau)
        du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][1]["ten_chuong_trinh"] = "Kỹ thuật Cơ khí (tên khác)"
        du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][1]["ma_xet_tuyen"] = "ME9"
        _id, _counts, quy_tac = import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertTrue(any("không khớp dats_chuong_trinh_dao_tao" in c for c in quy_tac.canh_bao), quy_tac.canh_bao)

    def test_ma_danh_muc_khong_co(self):
        du_lieu = copy.deepcopy(self.mau)
        du_lieu["dats_tuyen_sinh"]["dats_tru_so"][0]["ma_tinh"] = "99"
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("ma_tinh = 99", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
