"""Hợp đồng JSON tải xuống của CMS theo mẫu XDA."""

import json
import unittest
from pathlib import Path

from app.services.dats_hop_dong_thu_thap import (
    hoan_thien_cau_truc_cms,
    hop_dong_cau_truc_cms,
    kiem_tra_cau_truc_cms,
    mau_rut_gon_cms,
)

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
        self.assertNotIn("nguon_du_lieu_url", chuan_hoa["dats_tuyen_sinh"])
        loi = kiem_tra_cau_truc_cms(chuan_hoa)
        self.assertEqual(len(loi), 2)
        self.assertTrue(any(i.startswith("/dats_tuyen_sinh/dats_tru_so/1/id:") for i in loi))
        self.assertTrue(any(i.startswith("/dats_tuyen_sinh/nguon_du_lieu_url:") for i in loi))

    def test_mau_gui_ai_chi_chua_bo_cuc(self):
        mau = mau_rut_gon_cms(self.mau)
        self.assertEqual(set(mau), {"thong_tin_import", "dats_tuyen_sinh", "quy_tac_xet_tuyen"})
        self.assertIsNone(mau["thong_tin_import"]["ma_truong"])
        self.assertEqual(len(mau["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]), 1)
        hop_dong = hop_dong_cau_truc_cms()
        self.assertIn("phien_ban", hop_dong["/quy_tac_xet_tuyen"]["gia_tri"])
        self.assertIn("thanh_phan", hop_dong["/quy_tac_xet_tuyen/cong_thuc"]["danh_sach"])
