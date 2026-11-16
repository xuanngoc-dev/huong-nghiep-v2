import unittest
from decimal import Decimal

from app.scripts.kiem_tra_truoc_tich_hop_de_an import (
    BO_SUNG,
    CANH_BAO,
    CHAN,
    THONG_TIN,
    phan_tich,
    xuat_markdown,
)


def _du_lieu(**kwargs):
    """Dữ liệu thu thập giả: hai trường, đề án 2026 của NTH bị trùng."""
    data = {
        "de_an": [
            {"id": 1, "ma_truong": "NTH", "nam_tuyen_sinh": 2026},
            {"id": 2, "ma_truong": "NTH", "nam_tuyen_sinh": 2026},
            {"id": 3, "ma_truong": "BKA", "nam_tuyen_sinh": 2026},
        ],
        "chuong_trinh": [
            {"id": 10, "de_an_id": 1, "ma_xet_tuyen": "NTH01", "nganh_dao_tao_id": None, "co_so_id": 5},
            {"id": 11, "de_an_id": 1, "ma_xet_tuyen": "NTH01", "nganh_dao_tao_id": 7, "co_so_id": None},
            {"id": 12, "de_an_id": 3, "ma_xet_tuyen": "BF1", "nganh_dao_tao_id": 8, "co_so_id": 6},
        ],
        "tru_so": [
            {"id": 5, "de_an_id": 1, "ten_co_so": "Trụ sở chính", "dia_chi": "91 Chùa Láng, Hà Nội"},
            {"id": 6, "de_an_id": 3, "ten_co_so": "Cơ sở 2", "dia_chi": "Số 1 Đại Cồ Việt"},
        ],
        "truong": [
            {"ma_truong": "NTH", "ma_tinh_thanh": "01", "ten_tinh_thanh": "Hà Nội", "vung_mien": "Bắc"},
            {"ma_truong": "BKA", "ma_tinh_thanh": None, "ten_tinh_thanh": "HN", "vung_mien": None},
            {"ma_truong": "KHAC", "ma_tinh_thanh": None, "ten_tinh_thanh": None, "vung_mien": None},
        ],
        "tinh_thanh": [{"id": 1, "ma_tinh": "01", "ten_tinh": "Hà Nội"}],
        "to_hop": [
            {"id": 1, "ma_to_hop": "A00", "ds_mon_hoc": ["TOAN", "LY", "HOA"], "trang_thai": 1,
             "nam_ap_dung_tu": None, "nam_ap_dung_den": None},
            {"id": 2, "ma_to_hop": "K01", "ds_mon_hoc": '["TOAN", "VAN", "XYZ"]', "trang_thai": 1,
             "nam_ap_dung_tu": 2025, "nam_ap_dung_den": None},
            {"id": 3, "ma_to_hop": "M00", "ds_mon_hoc": ["TOAN", "LY", "HOA", "VAN"], "trang_thai": 1,
             "nam_ap_dung_tu": None, "nam_ap_dung_den": None},
        ],
        "to_hop_chi_tiet": [{"to_hop_id": 1}],
        "mon_hoc": [
            {"ma_mon_hoc": "TOAN", "ma_mon": None, "ten_mon_hoc": "Toán", "nhom_mon": "Tự nhiên"},
            {"ma_mon_hoc": "LY", "ma_mon": None, "ten_mon_hoc": "Vật lí", "nhom_mon": "Tự nhiên"},
            {"ma_mon_hoc": "HOA", "ma_mon": None, "ten_mon_hoc": "Hóa học", "nhom_mon": "Tự nhiên"},
            {"ma_mon_hoc": "VAN", "ma_mon": None, "ten_mon_hoc": "Ngữ văn", "nhom_mon": "Xã hội"},
            {"ma_mon_hoc": "ANH", "ma_mon": None, "ten_mon_hoc": "Tiếng Anh", "nhom_mon": "Ngoại ngữ"},
        ],
        "doi_tuong": [
            {"ma_doi_tuong": "01", "ten_doi_tuong": "ĐT01", "diem_cong": Decimal("2.00"), "nam_ap_dung": None,
             "trang_thai": 1},
            {"ma_doi_tuong": "04", "ten_doi_tuong": "ĐT04", "diem_cong": Decimal("2.00"), "nam_ap_dung": None,
             "trang_thai": 1},
            {"ma_doi_tuong": "07", "ten_doi_tuong": "ĐT07", "diem_cong": Decimal("1.00"), "nam_ap_dung": None,
             "trang_thai": 1},
        ],
        "khu_vuc": [{"ma_khu_vuc": "KV1", "diem_cong": Decimal("0.75"), "nam_ap_dung": 2026, "trang_thai": 1}],
        "bai_thi": ["HSA"],
        "chung_chi": ["IELTS"],
        "nganh": ["7480201"],
    }
    data.update(kwargs)
    return data


FILE_MAU = {
    "mau_BKA_2026.json": {
        "ma_truong": "BKA",
        "nam_tuyen_sinh": 2026,
        "to_hop_rieng": [{"ma_to_hop": "K01", "vi_tri": [["TOAN"], ["VAN"], ["LY", "HOA", "TIN"]]}],
        "cong_thuc": [{"thanh_phan": [{"ma_bai_thi": "TSA"}], "he_so_mon": [{"ma_mon": "TOAN", "vi_tri": 1}]}],
        "chuong_trinh": [{"ma_nganh": "7480201", "phuong_an": [{"to_hop": ["A00", "K01", "D07"]}]}],
    },
    "mau_XYZ_2027.json": {"ma_truong": "XYZ", "nam_tuyen_sinh": 2027},
}


def _muc(ds, ma):
    return next(m for m in ds if m.ma == ma)


class TestPhanTich(unittest.TestCase):
    def setUp(self):
        self.ds = phan_tich(_du_lieu(), FILE_MAU)

    def test_de_an_trung_la_muc_chan(self):
        muc = _muc(self.ds, "de_an_trung")
        self.assertEqual(muc.muc_do, CHAN)
        self.assertEqual(muc.dong, [["NTH", 2026, "1 (2), 2 (0)"]])

    def test_khong_trung_thi_chi_la_thong_tin(self):
        du_lieu = _du_lieu(de_an=[{"id": 1, "ma_truong": "NTH", "nam_tuyen_sinh": 2026}])
        self.assertEqual(_muc(phan_tich(du_lieu, {}), "de_an_trung").muc_do, THONG_TIN)

    def test_chuong_trinh_thieu_nganh_va_co_so(self):
        muc = _muc(self.ds, "chuong_trinh_thieu")
        self.assertEqual(muc.muc_do, BO_SUNG)
        self.assertEqual(muc.dong, [["NTH", 2026, 2, 1, 1, 0]])

    def test_ma_xet_tuyen_trung_trong_de_an(self):
        muc = _muc(self.ds, "ma_xet_tuyen_trung")
        self.assertEqual(muc.muc_do, CANH_BAO)
        self.assertEqual(muc.dong, [["NTH", 2026, 1, "NTH01", 2]])

    def test_chi_kiem_dia_diem_truong_co_de_an(self):
        muc = _muc(self.ds, "truong_thieu_dia_diem")
        self.assertEqual([r[0] for r in muc.dong], ["BKA"])
        self.assertIn("không khớp dm_tinh_thanh", muc.dong[0][1])

    def test_co_so_khong_doan_duoc_tinh(self):
        muc = _muc(self.ds, "co_so_doan_tinh")
        self.assertEqual([r[0] for r in muc.dong], [6])

    def test_to_hop_thieu_chi_tiet_va_sai_mon(self):
        self.assertIn("2/3", _muc(self.ds, "to_hop_chi_tiet").tom_tat)
        loi = dict(_muc(self.ds, "to_hop_ds_mon").dong)
        self.assertIn("XYZ", loi["K01"])
        self.assertIn("4 môn", loi["M00"])
        self.assertNotIn("A00", loi)

    def test_doi_tuong_uu_tien_doi_chieu_thong_tu(self):
        muc = _muc(self.ds, "doi_tuong_uu_tien")
        doi_chieu = {r[0]: r[-1] for r in muc.dong}
        self.assertEqual(doi_chieu["01"], "khớp")
        self.assertIn("lệch", doi_chieu["04"])
        self.assertIn("không có", doi_chieu["07"])

    def test_thieu_nhom_ngoai_ngu_la_muc_chan(self):
        mon = [dict(m, nhom_mon="Khác") for m in _du_lieu()["mon_hoc"]]
        self.assertEqual(_muc(phan_tich(_du_lieu(mon_hoc=mon), {}), "nhom_ngoai_ngu").muc_do, CHAN)

    def test_file_mau_de_an_va_ma_thieu(self):
        de_an = {r[0]: r[3] for r in _muc(self.ds, "file_mau_de_an").dong}
        self.assertEqual(de_an, {"mau_BKA_2026.json": "có", "mau_XYZ_2027.json": "CHƯA CÓ"})
        thieu = {(r[0], r[1]): r[3] for r in _muc(self.ds, "file_mau_ma_thieu").dong}
        # K01 là tổ hợp riêng nên không tính là thiếu; D07 và TSA thì thiếu.
        self.assertEqual(thieu[("mau_BKA_2026.json", "Tổ hợp")], "D07")
        self.assertEqual(thieu[("mau_BKA_2026.json", "Bài thi")], "TSA")
        # Môn trong vi_tri (list lồng nhau) của tổ hợp riêng cũng được kiểm; vi_tri dạng số thứ tự thì bỏ qua.
        self.assertEqual(thieu[("mau_BKA_2026.json", "Môn học")], "TIN")
        self.assertNotIn(("mau_BKA_2026.json", "Ngành"), thieu)

    def test_to_hop_rieng_gan_tien_to_va_bao_dung(self):
        muc = _muc(self.ds, "to_hop_rieng")
        self.assertEqual(muc.dong[0][:3], ["mau_BKA_2026.json", "K01", "BKA-K01"])
        self.assertIn("sẽ đụng", muc.dong[0][3])

    def test_xuat_markdown_co_tom_tat_va_chi_tiet(self):
        bao_cao = xuat_markdown(self.ds)
        self.assertIn("| CHẶN |", bao_cao)
        self.assertIn("## 1. Đề án trùng trường + năm", bao_cao)


if __name__ == "__main__":
    unittest.main()
