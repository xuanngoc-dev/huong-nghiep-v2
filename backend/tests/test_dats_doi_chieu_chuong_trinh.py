from unittest import TestCase

from app.services.dats_doi_chieu_chuong_trinh import ghi_chu_doi_chieu_chuong_trinh, kiem_tra_doi_chieu


_NAM = 2026
_URL = "https://daihoc.example.edu/tuyen-sinh-2026"


def _nguon(nguon_id=1, **cap_nhat):
    return {
        "id": nguon_id, "url": _URL, "loai": "de_an", "lua_chon": "su_dung", "chinh_thuc": True,
        "phu_hop": True, "nam_ap_dung": _NAM, **cap_nhat,
    }


def _ban_nhap(*cac_ma):
    return {
        "dats_tuyen_sinh": {
            "nguon_du_lieu_url": _URL,
            "dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": ma} for ma in cac_ma],
        },
        "quy_tac_xet_tuyen": {"de_an": {"nguon_du_lieu_url": _URL}},
    }


def _dong_kiem(nguon_id, trich_dan, *, tong=None, cac_ma=(), pham_vi="toan_truong"):
    return {
        "nguon_id": nguon_id, "pham_vi": pham_vi, "trich_dan": trich_dan,
        "tong_cong_bo": tong, "cac_ma": list(cac_ma),
    }


class DoiChieuChuongTrinhTests(TestCase):
    def test_bao_84_tren_85_va_khong_bia_ma_thieu(self):
        ma_hop_le = [f"CT{i:03d}" for i in range(1, 85)]
        ban_nhap = _ban_nhap(*ma_hop_le)
        doi_chieu = {"nguon": [_dong_kiem(1, "Tuyển sinh 85 ngành/chương trình.", tong=85, cac_ma=ma_hop_le[:2])]}
        loi, can_xac_nhan = kiem_tra_doi_chieu(ban_nhap, [_nguon()], _NAM, doi_chieu)
        ghi_chu = ghi_chu_doi_chieu_chuong_trinh(ban_nhap, doi_chieu, [_nguon()], _NAM)
        self.assertEqual(len(ban_nhap["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]), 84)
        self.assertEqual(can_xac_nhan, {})
        self.assertEqual(len(loi), 1)
        self.assertEqual(len(ghi_chu), 1)
        for thong_bao in (*loi, *ghi_chu):
            self.assertIn("84/85 chương trình", thong_bao)
            self.assertIn("thiếu 1", thong_bao)
            self.assertIn("Chưa xác minh được mã cụ thể", thong_bao)
            self.assertNotIn("CT085", thong_bao)

    def test_bao_ten_ma_thieu_khi_co_can_cu(self):
        ban_nhap = _ban_nhap("CT01")
        doi_chieu = {"nguon": [_dong_kiem(1, "Có 2 mã xét tuyển: CT01, CT02.", tong=2, cac_ma=("CT01", "CT02"))]}
        loi, can_xac_nhan = kiem_tra_doi_chieu(ban_nhap, [_nguon()], _NAM, doi_chieu)
        self.assertEqual(can_xac_nhan, {})
        self.assertIn("thiếu mã công bố ở nguồn #1: CT02", loi[0])
        ghi_chu = ghi_chu_doi_chieu_chuong_trinh(ban_nhap, doi_chieu, [_nguon()], _NAM)
        self.assertIn("1/2 mã xét tuyển", ghi_chu[0])
        self.assertIn("Mã công bố còn thiếu: CT02", ghi_chu[0])
        self.assertNotIn("Chưa xác minh được mã cụ thể", ghi_chu[0])

    def test_dem_rieng_ma_va_chuong_trinh_cung_ma(self):
        ban_nhap = _ban_nhap("CT01", "ct01")
        doi_chieu = {"nguon": [
            _dong_kiem(1, "Có 1 mã xét tuyển: CT01.", tong=1, cac_ma=("CT01",)),
            _dong_kiem(1, "Có 2 chương trình đào tạo.", tong=2),
        ]}
        self.assertEqual(kiem_tra_doi_chieu(ban_nhap, [_nguon()], _NAM, doi_chieu), ([], {}))
        self.assertEqual(ghi_chu_doi_chieu_chuong_trinh(ban_nhap, doi_chieu, [_nguon()], _NAM), [])

    def test_tong_mau_thuan_va_tong_ngoai_pham_vi(self):
        ban_nhap = _ban_nhap("CT01")
        doi_chieu = {"nguon": [
            _dong_kiem(1, "Tuyển sinh 85 chương trình.", tong=85, cac_ma=("CT01",)),
            _dong_kiem(2, "Tuyển sinh 84 chương trình.", tong=84),
            _dong_kiem(3, "Tuyển sinh 10 chương trình.", tong=10, pham_vi="phan_pham_vi"),
        ]}
        ds_nguon = [_nguon(), _nguon(2), _nguon(3)]
        loi, can_xac_nhan = kiem_tra_doi_chieu(ban_nhap, ds_nguon, _NAM, doi_chieu)
        self.assertEqual(loi, [])
        self.assertIn("84, 85", can_xac_nhan["chuong_trinh"])
        self.assertNotIn("10", can_xac_nhan["chuong_trinh"])
