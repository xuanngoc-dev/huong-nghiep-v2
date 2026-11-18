"""Nhận diện trường nhắc tới trong câu hỏi chat để báo "chưa có dữ liệu" (tên đầy đủ, tên cụt, viết tắt)."""

import json
import unittest
from pathlib import Path

from app.services.chat_catalog import school_catalog
from app.services.nhan_dien_truong import chuan_hoa, truong_chua_co_du_lieu, viet_tat_bo_sung

DANH_MUC = [
    {"ma_truong": "TMU", "ten_truong": "Trường Đại học Thương mại", "ten_khac": ["TMU"]},
    {"ma_truong": "CDTM", "ten_truong": "Cao đẳng Thương mại", "ten_khac": []},
    {"ma_truong": "HTC", "ten_truong": "Học viện Tài chính", "ten_khac": ["AOF"]},
    {"ma_truong": "KHA", "ten_truong": "Trường Đại học Kinh tế Quốc dân", "ten_khac": ["NEU"]},
    {"ma_truong": "KTA", "ten_truong": "Đại học Kiến trúc Hà Nội", "ten_khac": []},
    {"ma_truong": "QSC", "ten_truong": "Trường Đại học Công nghệ Thông tin - Đại học Quốc gia TP.HCM", "ten_khac": ["UIT"]},
    {"ma_truong": "DCN", "ten_truong": "Trường Đại học Công nghiệp Hà Nội", "ten_khac": ["HaUI"]},
    {"ma_truong": "C05", "ten_truong": "Trường có mã trùng tổ hợp", "ten_khac": []},
]
CO_DU_LIEU = [{"ma_truong": "DCN", "ten_truong": "Trường Đại học Công nghiệp Hà Nội", "ten_khac": []}]
NGANH = {chuan_hoa(n) for n in ("Công nghệ thông tin", "Kiến trúc", "Thương mại điện tử", "Marketing")}


def thieu(cau_hoi):
    return truong_chua_co_du_lieu(cau_hoi, DANH_MUC, CO_DU_LIEU, NGANH)


class NhanDienTruongTests(unittest.TestCase):
    def test_ten_day_du_ten_cut_va_viet_tat(self):
        for cau in ("Trường Đại học Thương mại tuyển ngành nào?", "trường Thương mại tuyển ngành nào",
                    "ĐH Thương mại học phí?", "ĐHTM có ngành marketing không", "TMU có ngành gì"):
            with self.subTest(cau=cau):
                self.assertEqual(thieu(cau), ["Trường Đại học Thương mại"])
        self.assertEqual(thieu("HVTC điểm chuẩn"), ["Học viện Tài chính"])
        self.assertEqual(thieu("Kinh tế Quốc dân có ngành gì"), ["Trường Đại học Kinh tế Quốc dân"])
        self.assertEqual(thieu("Cao đẳng Thương mại tuyển ngành gì"), ["Cao đẳng Thương mại"])
        # Bỏ địa danh cuối tên; tên riêng trùng tên ngành phải có "đại học / học viện" đứng trước.
        self.assertEqual(thieu("ĐH Kiến trúc tuyển ngành nào"), ["Đại học Kiến trúc Hà Nội"])
        self.assertEqual(thieu("Đại học Công nghệ Thông tin có ngành gì"),
                         ["Trường Đại học Công nghệ Thông tin - Đại học Quốc gia TP.HCM"])

    def test_khong_nham_ten_nganh_tu_thuong_ma_to_hop_va_truong_co_du_lieu(self):
        for cau in ("Ngành công nghệ thông tin học gì?", "trường nào có ngành công nghệ thông tin",
                    "trường Kiến trúc tuyển ngành nào", "Ngành thương mại điện tử ra làm gì", "Điểm chuẩn khối C05",
                    "neu tôi được 25 điểm", "Đại học Công nghiệp Hà Nội tuyển ngành nào", "HaUI có ngành CNTT không"):
            with self.subTest(cau=cau):
                self.assertEqual(thieu(cau), [])

    def test_file_viet_tat_tro_dung_ma_truong_trong_danh_muc(self):
        ma_danh_muc = {str(r["ma_truong"]) for r in school_catalog()}
        # TMA là mã trong bảng dm_truong (danh mục JSON dùng TMU) nên không bắt buộc có trong file JSON.
        self.assertEqual(set(viet_tat_bo_sung()) - ma_danh_muc - {"TMA"}, set())
        data = json.loads((Path(__file__).resolve().parents[1] / "data" / "ten_viet_tat_truong.json").read_text("utf-8"))
        self.assertTrue(all(isinstance(v, list) and v for k, v in data.items() if not k.startswith("_")))


if __name__ == "__main__":
    unittest.main()
