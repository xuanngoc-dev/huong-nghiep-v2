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
from app.services.thu_thap_tuyen_sinh_import import import_approved_admission, validate_admission_payload
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

    def test_cms_nhap_mau_xda_va_chan_thieu_chuong_trinh(self):
        mau = json.loads((MAU.parent / "du_lieu_mau_da_sua.json").read_text(encoding="utf-8"))
        validate_admission_payload(mau, "XDA", 2026)
        _, counts, quy_tac = import_approved_admission(self.db, mau, "XDA", 2026, 1)
        self.db.commit()
        self.assertEqual(counts["dats_chuong_trinh_dao_tao"], 44)
        self.assertEqual(quy_tac.so_dong["xt_diem_chuan"], 44)
        self.assertEqual(quy_tac.so_dong["xt_phuong_an"], 642)
        self.assertIsNone(self.db.scalar(select(M.DmToHopMonHoc.id).where(M.DmToHopMonHoc.ma_to_hop == "TT")))
        theo_cong_thuc = dict(self.db.execute(
            select(M.XtCongThuc.ma_cong_thuc, M.DatsPhuongThuc.ma_phuong_thuc_cua_truong)
            .join(M.XtPhuongAn, M.XtPhuongAn.cong_thuc_id == M.XtCongThuc.id)
            .join(M.DatsPhuongThuc, M.DatsPhuongThuc.id == M.XtPhuongAn.de_an_phuong_thuc_id)
            .where(M.XtCongThuc.ma_cong_thuc.in_(("HUCE_TSA_2026", "HUCE_SPT_2026")))
            .distinct()
        ).all())
        self.assertEqual(theo_cong_thuc, {"HUCE_TSA_2026": "402_TSA", "HUCE_SPT_2026": "402_SPT"})
        mau["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"].pop()
        with self.assertRaisesRegex(DatsImportError, "Thiếu chương trình trong đề án"):
            validate_admission_payload(mau, "XDA", 2026)

    def test_luu_diem_chi_tieu_va_chuong_trinh_doc_lap_nguoi_duyet_da_chot(self):
        mau = json.loads((MAU.parent / "du_lieu_mau_da_sua.json").read_text(encoding="utf-8"))
        mau["dats_tuyen_sinh"]["chi_tieu"] = 1
        quy_tac = mau["quy_tac_xet_tuyen"]
        quy_tac["chuong_trinh"].pop()
        quy_tac["chuong_trinh"][0]["hoc_phi"].update(hoc_phi_tu=21000000, hoc_phi_den=20000000)
        quy_tac["cong_thuc"][0]["thang_diem"] = 45
        quy_tac["diem_chuan"] = [{
            "ma_xet_tuyen": "MA-CU", "nam_tuyen_sinh": 2025, "diem_chuan": 31.5, "thang_diem": 30,
        }]
        with self.assertRaisesRegex(DatsImportError, "diem_chuan lớn hơn thang_diem"):
            import_day_du(self.db, "XDA", 2026, mau)
        self.db.rollback()
        _, counts, ket_qua = import_approved_admission(self.db, mau, "XDA", 2026, 1)
        self.db.commit()
        self.assertEqual(counts["dats_chuong_trinh_dao_tao"], 44)
        diem = self.db.scalars(select(M.XtDiemChuan).where(M.XtDiemChuan.ma_xet_tuyen == "MA-CU")).one()
        self.assertEqual((float(diem.diem_chuan), float(diem.thang_diem), diem.nguon_du_lieu_url), (31.5, 30, None))
        self.assertTrue(any("diem_chuan lớn hơn thang_diem" in msg for msg in ket_qua.canh_bao))
        self.assertTrue(any("hoc_phi_den nhỏ hơn hoc_phi_tu" in msg for msg in ket_qua.canh_bao))
        cong_thuc = self.db.scalars(select(M.XtCongThuc).where(M.XtCongThuc.ma_cong_thuc == "HUCE_THPT_2026")).one()
        self.assertEqual(cong_thuc.thang_diem, 45)

    def test_cms_nhap_to_hop_rieng_giu_diem_chuan_ngoai_file(self):
        de_an = self.mau["dats_tuyen_sinh"]
        de_an["trang_thai_xet_tuyen"] = 2
        phuong_thuc = de_an["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"][0]
        phuong_thuc["cong_thuc_tinh_diem"] = "BKA_THPT"
        phuong_thuc["to_hop_mon_hoc"].append("K01")
        phuong_thuc["dats_phuong_thuc_to_hop"].append({"ma_to_hop": "K01"})
        phuong_an = self.mau["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"][0]
        phuong_an["to_hop"] = ["BKA-K01" if ma == "K01" else ma for ma in phuong_an["to_hop"]]
        de_an["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"].extend([
            {"ma_phuong_thuc_cua_bo": "415", "cong_thuc_tinh_diem": "BKA_SAT"},
            {"ma_phuong_thuc_cua_bo": "414", "cong_thuc_tinh_diem": "BKA_PHONG_VAN"},
        ])
        for diem in self.mau["quy_tac_xet_tuyen"]["diem_chuan"]:
            diem.setdefault("nguon_du_lieu_url", f"https://ts.hust.edu.vn/diem-chuan-{diem['nam_tuyen_sinh']}")

        self.db.add(M.XtDiemChuan(ma_truong="BKA", nam_tuyen_sinh=2026, ma_xet_tuyen="MA-CU", diem_chuan=21))
        self.db.commit()
        de_an_id, _, _ = import_approved_admission(self.db, self.mau, "BKA", 2027, 1)
        self.db.commit()
        ban_ghi = self.db.get(M.DatsTuyenSinh, de_an_id)
        self.assertEqual((ban_ghi.trang_thai, ban_ghi.trang_thai_xet_tuyen), ("nhap", 1))
        self.assertEqual(de_an["trang_thai_xet_tuyen"], 2)
        self.assertEqual(self._dem(M.XtDiemChuan), 5)
        phuong_thuc_db = self.db.scalar(select(M.DatsPhuongThuc).where(M.DatsPhuongThuc.cong_thuc_tinh_diem == "BKA_THPT"))
        self.assertIn("BKA-K01", phuong_thuc_db.to_hop_mon_hoc)
        ma_to_hop = self.db.scalar(select(M.DmToHopMonHoc).where(M.DmToHopMonHoc.ma_to_hop == "BKA-K01"))
        self.assertTrue(self.db.scalar(select(func.count()).where(M.DmToHopMonHocChiTiet.to_hop_id == ma_to_hop.id)))

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

    def test_id_trong_file_khong_bi_kiem_tra(self):
        """Id bản ghi do CSDL tự sinh; id trong file trùng, sai kiểu hay thiếu đều không lỗi."""
        du_lieu = copy.deepcopy(self.mau)
        de_an = du_lieu["dats_tuyen_sinh"]
        de_an["id"] = 999
        for ct in de_an["dats_chuong_trinh_dao_tao"]:
            for pt in ct["dats_phuong_thuc"]:
                pt["id"] = 1  # mỗi chương trình đều đánh số phương thức từ 1
        de_an["dats_chuong_trinh_dao_tao"][1]["id"] = "abc"
        de_an["dats_chuong_trinh_dao_tao"][2]["id"] = None
        de_an["dats_website"][0]["id"] = 1
        de_an["dats_lien_he_tuyen_sinh"][0]["id"] = 1
        de_an_id, counts, _quy_tac = import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertEqual((counts["dats_phuong_thuc"], counts["dats_phuong_thuc_to_hop"]), (7, 2))
        self.assertNotEqual(de_an_id, 999)
        # Phương thức gắn đúng chương trình chứa nó.
        theo_ct = {
            ct.ma_xet_tuyen: sorted(
                pt.ma_phuong_thuc_cua_bo
                for pt in self.db.scalars(select(M.DatsPhuongThuc).where(M.DatsPhuongThuc.de_an_chuong_trinh_id == ct.id))
            )
            for ct in self.db.scalars(select(M.DatsChuongTrinhDaoTao))
        }
        self.assertEqual(theo_ct, {"IT1": ["100", "301", "401"], "ME1": ["100", "200"], "IT-HP": ["100", "200"]})
        # Bảng con lồng trong phương thức id 1 đầu tiên vẫn gắn đúng phương thức đó.
        dk = self.db.scalars(select(M.DatsDieuKienDuTuyen)).one()
        self.assertEqual(self.db.get(M.DatsPhuongThuc, dk.de_an_phuong_thuc_id).ma_phuong_thuc_cua_bo, "100")
        self.assertEqual(self.db.get(M.DatsChuongTrinhDaoTao, dk.de_an_chuong_trinh_id).ma_xet_tuyen, "IT1")

    def test_tham_chieu_toi_id_trung_thi_bao_loi(self):
        du_lieu = copy.deepcopy(self.mau)
        for co_so in du_lieu["dats_tuyen_sinh"]["dats_tru_so"]:
            co_so["id"] = 1
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("nhiều dòng dats_tru_so cùng id 1", str(ctx.exception))
        du_lieu["dats_tuyen_sinh"]["dats_tru_so"][1]["id"] = 2
        du_lieu["dats_tuyen_sinh"]["dats_co_so_vat_chat"][0]["co_so_id"] = 7
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("co_so_id = 7", str(ctx.exception))

    def test_null_la_gia_tri_mac_dinh(self):
        """Ô null mà trường có mặc định thì dùng mặc định; cơ sở bỏ trống tỉnh giữ tỉnh của dats_tru_so."""
        du_lieu = copy.deepcopy(self.mau)
        quy_tac = du_lieu["quy_tac_xet_tuyen"]
        quy_tac["co_so"][1]["ma_tinh"] = None
        for ct in quy_tac["cong_thuc"]:
            ct.update(he_so_nhan=None, so_le_lam_tron=None, ty_le_diem_cong_toi_da=None, thay_ngoai_ngu=ct.get("thay_ngoai_ngu"))
        xet_thang = next(ct for ct in quy_tac["cong_thuc"] if ct["kieu_tinh"] == "CHI_DIEU_KIEN")
        xet_thang.update(thang_diem=None, nguon_diem_mon="HO_SO", he_so_mon=None)
        import_day_du(self.db, "BKA", 2027, du_lieu)
        ct = self.db.scalars(select(M.XtCongThuc).where(M.XtCongThuc.ma_cong_thuc == "BKA_THPT")).one()
        self.assertEqual((float(ct.he_so_nhan), ct.so_le_lam_tron, float(ct.ty_le_diem_cong_toi_da)), (1.0, 2, 0.1))
        hp = self.db.scalars(select(M.DatsTruSo).where(M.DatsTruSo.ten_co_so == "Cơ sở Hải Phòng")).one()
        self.assertEqual(self.db.get(M.DmTinhThanh, hp.tinh_thanh_id).ma_tinh, "31")

    def test_thieu_ma_phuong_thuc_cua_bo_la_phuong_thuc_khac(self):
        du_lieu = copy.deepcopy(self.mau)
        ct = du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
        pt_me1 = ct[1]["dats_phuong_thuc"]
        pt_me1[0].pop("ma_phuong_thuc_cua_bo")  # không có mã của trường -> 500
        pt_me1[1]["ma_phuong_thuc_cua_bo"] = ""
        pt_me1[1]["ma_phuong_thuc_cua_truong"] = "HB_RIENG"  # mã của trường ngoài danh mục -> 500
        pt_it_hp = ct[2]["dats_phuong_thuc"][0]
        pt_it_hp["ma_phuong_thuc_cua_bo"] = None
        pt_it_hp["ma_phuong_thuc_cua_truong"] = "100"  # mã của trường có trong danh mục -> dùng mã đó
        cong_thuc = du_lieu["quy_tac_xet_tuyen"]["cong_thuc"]
        phong_van = next(c for c in cong_thuc if c["ma_cong_thuc"] == "BKA_PHONG_VAN")
        del phong_van["ma_phuong_thuc_cua_bo"]
        import_day_du(self.db, "BKA", 2027, du_lieu)
        theo_ct = {}
        for pt in self.db.scalars(select(M.DatsPhuongThuc)):
            ma_xt = self.db.get(M.DatsChuongTrinhDaoTao, pt.de_an_chuong_trinh_id).ma_xet_tuyen
            theo_ct.setdefault(ma_xt, []).append(pt.ma_phuong_thuc_cua_bo)
        self.assertEqual(sorted(theo_ct["ME1"]), ["500", "500"])
        self.assertEqual(sorted(theo_ct["IT-HP"]), ["100", "200"])
        ct_pv = self.db.scalars(select(M.XtCongThuc).where(M.XtCongThuc.ma_cong_thuc == "BKA_PHONG_VAN")).one()
        self.assertEqual(ct_pv.ma_phuong_thuc_cua_bo, "500")

    def test_ma_phuong_thuc_cua_bo_sai_van_bao_loi(self):
        du_lieu = copy.deepcopy(self.mau)
        du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][1]["dats_phuong_thuc"][0]["ma_phuong_thuc_cua_bo"] = "999"
        with self.assertRaises(DatsImportError) as ctx:
            import_day_du(self.db, "BKA", 2027, du_lieu)
        self.assertIn("ma_phuong_thuc_cua_bo = 999", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
