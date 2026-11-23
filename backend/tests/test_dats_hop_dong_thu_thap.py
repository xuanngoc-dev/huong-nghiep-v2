"""Hợp đồng JSON tải xuống của CMS theo mẫu XDA."""

import json
import unittest
from pathlib import Path

from sqlalchemy import select

import app.models as M
from app.services.dats_hop_dong_thu_thap import (
    hoan_thien_cau_truc_cms,
    hop_dong_cau_truc_cms,
    kiem_tra_cau_truc_cms,
    mau_rut_gon_cms,
)
from app.services.dats_import import DatsImportError
from app.services.thu_thap_tuyen_sinh_import import import_approved_admission, validate_admission_payload
from tests.hoi_quy_xet_tuyen import DANH_MUC_MA, tao_csdl

_MAU_XDA = Path(__file__).resolve().parents[2] / "docs/de-an-tuyen-sinh/chuan_du_lieu/du_lieu_mau_da_sua.json"


class HopDongThuThapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mau = json.loads(_MAU_XDA.read_text(encoding="utf-8"))

    def _tao_ban_nhap(self):
        return hoan_thien_cau_truc_cms({
            **self.mau,
            "dats_tuyen_sinh": {**self.mau["dats_tuyen_sinh"], "trang_thai": "nhap", "trang_thai_xet_tuyen": 1},
        })

    def test_hoan_thien_mau_xda_giu_gia_tri_nguon_va_cho_phep_id_lap_giua_hai_chuong_trinh(self):
        ban_nhap = self._tao_ban_nhap()
        self.assertEqual(kiem_tra_cau_truc_cms(ban_nhap), [])
        self.assertEqual(len(ban_nhap["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]), 44)
        self.assertEqual(ban_nhap["quy_tac_xet_tuyen"]["cong_thuc"][0]["thanh_phan"], [])
        self.assertNotIn("thanh_phan", self.mau["quy_tac_xet_tuyen"]["cong_thuc"][0])
        self.assertIsNone(ban_nhap["quy_tac_xet_tuyen"]["diem_cong"][7]["khoa"])
        self.assertEqual(self.mau["quy_tac_xet_tuyen"]["diem_cong"][7]["khoa"], "")

    def test_chan_thieu_khoa_url_khong_hop_le_va_mang_bat_buoc_rong(self):
        ban_nhap = self._tao_ban_nhap()
        del ban_nhap["dats_tuyen_sinh"]["dats_nhan_su"]
        ban_nhap["quy_tac_xet_tuyen"]["de_an"]["nguon_du_lieu_url"] = "chuoi bat ky"
        ban_nhap["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"] = []
        loi = kiem_tra_cau_truc_cms(ban_nhap)
        self.assertEqual(len(loi), 3)
        self.assertTrue(any(i.startswith("/dats_tuyen_sinh/dats_nhan_su:") for i in loi))
        self.assertTrue(any(i.startswith("/quy_tac_xet_tuyen/de_an/nguon_du_lieu_url:") for i in loi))
        self.assertTrue(any(i.startswith("/quy_tac_xet_tuyen/chuong_trinh/0/phuong_an:") for i in loi))

    def test_giu_url_thieu_va_phat_hien_id_trung_trong_cung_mang(self):
        ban_nhap = self._tao_ban_nhap()
        dats = ban_nhap["dats_tuyen_sinh"]
        del dats["nguon_du_lieu_url"]
        dats["dats_tru_so"][1]["id"] = dats["dats_tru_so"][0]["id"]
        chuan_hoa = hoan_thien_cau_truc_cms(ban_nhap)
        self.assertIsNone(chuan_hoa["dats_tuyen_sinh"]["nguon_du_lieu_url"])
        loi = kiem_tra_cau_truc_cms(chuan_hoa)
        self.assertEqual(len(loi), 1)
        self.assertTrue(loi[0].startswith("/dats_tuyen_sinh/dats_tru_so/1/id:"))

    def test_mau_gui_ai_chi_chua_bo_cuc(self):
        mau = mau_rut_gon_cms(self.mau)
        self.assertEqual(set(mau), {"thong_tin_import", "dats_tuyen_sinh", "quy_tac_xet_tuyen"})
        self.assertIsNone(mau["thong_tin_import"]["ma_truong"])
        self.assertEqual(len(mau["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]), 1)
        hop_dong = hop_dong_cau_truc_cms()
        self.assertIn("phien_ban", hop_dong["/quy_tac_xet_tuyen"]["gia_tri"])
        self.assertIn("thanh_phan", hop_dong["/quy_tac_xet_tuyen/cong_thuc"]["danh_sach"])

    def test_bang_tuy_chon_co_khoa_nhap_ke_ca_khi_mau_rong(self):
        hop_dong = hop_dong_cau_truc_cms()
        for cha, khoi in hop_dong.items():
            for con in khoi.get("danh_sach", []):
                if con.startswith("dats_"):
                    self.assertIn(f"{cha}/{con}", hop_dong)
        viec_lam = hop_dong["/dats_tuyen_sinh/dats_ty_le_viec_lam"]["truong_tuy_chon_va_kieu"]
        self.assertEqual(viec_lam["ty_le_co_viec_lam"], "decimal")
        self.assertEqual(viec_lam["ma_nganh"], "text")
        self.assertTrue({"id", "de_an_id", "nganh_dao_tao_id"}.isdisjoint(viec_lam))

    def test_bang_quy_doi_cap_truong_tuy_chon_va_co_du_cot_nguon_dich(self):
        hop_dong = hop_dong_cau_truc_cms()
        ban_cu = self._tao_ban_nhap()
        for bang in ("dats_quy_doi_nguong_dau_vao", "dats_quy_doi_diem_trung_tuyen"):
            with self.subTest(bang=bang):
                self.assertNotIn(bang, ban_cu["dats_tuyen_sinh"])
                self.assertIn(bang, hop_dong["/dats_tuyen_sinh"]["danh_sach_neu_co"])
                cot = hop_dong[f"/dats_tuyen_sinh/{bang}"]["truong_tuy_chon_va_kieu"]
                self.assertEqual(cot, hop_dong[f"/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/{bang}"]["truong_tuy_chon_va_kieu"])
                for khoa in ("ma_phuong_thuc_nguon", "ma_phuong_thuc_dich", "ma_to_hop_nguon", "ma_to_hop_dich",
                             "cong_thuc_noi_suy", "nguon_du_lieu_url", "dieu_kien_ap_dung"):
                    self.assertEqual(cot[khoa], "text")
                for khoa in ("diem_moc_nguon", "diem_moc_dich", "thang_diem_nguon", "thang_diem_dich"):
                    self.assertEqual(cot[khoa], "decimal")
                self.assertEqual(cot["nam_tuyen_sinh"], "int")
        self.assertEqual(kiem_tra_cau_truc_cms(ban_cu), [])
        validate_admission_payload(ban_cu, "XDA", 2026)

    def test_bang_quy_doi_cap_truong_khac_nam_bi_bao_dung_vi_tri(self):
        ban_nhap = self._tao_ban_nhap()
        for bang in ("dats_quy_doi_nguong_dau_vao", "dats_quy_doi_diem_trung_tuyen"):
            ban_nhap["dats_tuyen_sinh"][bang] = [{"nam_tuyen_sinh": 2025}]
        with self.assertRaises(DatsImportError) as caught:
            validate_admission_payload(ban_nhap, "XDA", 2026)
        self.assertEqual(caught.exception.loi, [
            "dats_tuyen_sinh/dats_quy_doi_nguong_dau_vao/0/nam_tuyen_sinh: phải là 2026",
            "dats_tuyen_sinh/dats_quy_doi_diem_trung_tuyen/0/nam_tuyen_sinh: phải là 2026",
        ])

    def test_duyet_va_nhap_hai_bang_quy_doi_chung_mot_lan_cho_de_an(self):
        db, _ = tao_csdl("XDA")
        self.addCleanup(db.close)
        danh_muc = json.loads(DANH_MUC_MA.read_text(encoding="utf-8"))
        for model in (M.DmPhuongThucTuyenSinh, M.DmThanhTichHocTapNghienCuu):
            model.__table__.create(db.get_bind())
        db.add_all(M.DmPhuongThucTuyenSinh(ma_phuong_thuc=x["ma"], ten_phuong_thuc=x["ten"])
                   for x in danh_muc["phuong_thuc_cua_bo"])
        db.add_all(M.DmThanhTichHocTapNghienCuu(ma_thanh_tich=x["ma"], ten_thanh_tich=x["ten"])
                   for x in danh_muc["thanh_tich"])
        db.add_all(M.DmNganhDaoTao(ma_nhom_nganh=x["ma"][:5], ma_nganh=x["ma"], ten_nganh=x["ten"],
                                   ten_tieng_anh="", trinh_do="ĐH") for x in danh_muc["nganh"])

        ban_nhap = self._tao_ban_nhap()
        moc = {
            "nam_tuyen_sinh": 2026, "ma_phuong_thuc_nguon": "402", "ma_phuong_thuc_dich": "100",
            "ma_to_hop_dich": "A00", "diem_moc_nguon": 75.5, "diem_moc_dich": 24,
            "thang_diem_nguon": 100, "thang_diem_dich": 30, "cong_thuc_noi_suy": "y = 24 + 0.3 (x - 75.5)",
            "dieu_kien_ap_dung": "Toàn trường", "nguon_du_lieu_url": "https://example.edu.vn/quy-doi",
        }
        models = (M.DatsQuyDoiNguongDauVao, M.DatsQuyDoiDiemTrungTuyen)
        for model in models:
            ban_nhap["dats_tuyen_sinh"][model.__tablename__] = [moc.copy()]
        self.assertEqual(kiem_tra_cau_truc_cms(ban_nhap), [])
        de_an_id, counts, _ = import_approved_admission(db, ban_nhap, "XDA", 2026, 1)
        phuong_thuc = dict(db.execute(select(M.DmPhuongThucTuyenSinh.ma_phuong_thuc, M.DmPhuongThucTuyenSinh.id)).all())
        to_hop_dich_id = db.scalar(select(M.DmToHopMonHoc.id).where(M.DmToHopMonHoc.ma_to_hop == "A00"))
        for model in models:
            with self.subTest(bang=model.__tablename__):
                self.assertEqual(counts[model.__tablename__], 1)
                dong = db.scalars(select(model).where(model.de_an_id == de_an_id)).one()
                self.assertIsNone(dong.de_an_chuong_trinh_id)
                self.assertIsNone(dong.to_hop_nguon_id)
                self.assertEqual(dong.to_hop_dich_id, to_hop_dich_id)
                self.assertEqual((dong.phuong_thuc_nguon_id, dong.phuong_thuc_dich_id), (phuong_thuc["402"], phuong_thuc["100"]))
                for khoa in ("nam_tuyen_sinh", "diem_moc_nguon", "diem_moc_dich", "thang_diem_nguon",
                             "thang_diem_dich", "cong_thuc_noi_suy", "dieu_kien_ap_dung", "nguon_du_lieu_url"):
                    self.assertEqual(getattr(dong, khoa), moc[khoa])
