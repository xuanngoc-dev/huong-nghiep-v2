import unittest
from io import BytesIO
from unittest.mock import patch

from PIL import Image

from app.services import thu_thap_tuyen_sinh_ai as ai
from app.services.thu_thap_tuyen_sinh_anh import chuan_bi_anh


class TestBangAnhTuyenSinh(unittest.TestCase):
    def test_chia_anh_dai(self):
        buf = BytesIO()
        Image.new("RGB", (700, 1800), "white").save(buf, format="PNG")
        anh = chuan_bi_anh(buf.getvalue())
        self.assertEqual(len(anh), 2)
        self.assertTrue(all(phan.startswith("data:image/jpeg;base64,") for phan in anh))

    def test_cong_kho_anh_phenikaa_chi_hop_le_tu_trang_cong_bo(self):
        image = "https://phenikaa-uni.edu.vn:3600/pu/bang-1.jpg"
        self.assertEqual(ai._url_anh_bang("https://www.phenikaa-uni.edu.vn/tin", image).port, 3600)
        with self.assertRaises(ai.AdmissionAIError):
            ai._url_anh_bang("https://example.edu.vn/tin", image)
        with self.assertRaises(ai.AdmissionAIError):
            ai._url_cong_khai(image)

    def test_dua_bang_va_phu_luc_vao_tai_lieu_va_gin_lien_ket_dan_chung(self):
        trang = ai._TaiLieu("https://truong.example.edu.vn/bai", "Tuyển sinh", [("Bài viết", "Thông báo 2026")], [])
        trang.anh_bang = [("/logo.png", "Trang chủ", ""), ("/scan.png", "", "Lộ trình Omega")]
        pdf_url = "https://truong.example.edu.vn/phu-luc.pdf"
        pdf = ai._TaiLieu(pdf_url, "Phụ lục", [("Trang PDF 2", "Quy đổi IELTS 6.0")], [])
        tep = ai._PhuLuc("Phụ lục 2", pdf_url, pdf)
        sources = [{"id": 1, "url": trang.url}]
        with (
            patch.object(ai, "_doc_phu_luc", return_value=([tep], [])),
            patch.object(ai, "_openai", return_value=({"ids": [2]}, [])) as doc_anh,
            patch.object(ai, "_tai_bang_anh", return_value=("hash", ["anh-gia"])),
            patch.object(ai, "_nhan_dang_bang_anh", return_value="7510101 | Công nghệ kỹ thuật | 120"),
        ):
            ghi_chu = ai._bo_sung_noi_dung(sources, {1: trang})

        self.assertEqual(doc_anh.call_args.args[1]["tai_nguyen"][1]["ngu_canh"], "Lộ trình Omega")
        self.assertIn("1 bảng ảnh và 1 phụ lục", ghi_chu[0])
        self.assertTrue(trang.doi_chieu("Bảng ảnh 1", "Công nghệ kỹ thuật | 120"))
        muc = ai._chuan_hoa_dan_chung([{
            "duong_dan": "/dats_tuyen_sinh/chi_tieu",
            "dan_chung": [{"nguon_id": 1, "vi_tri": "Bảng ảnh 1", "trich_dan": "Công nghệ kỹ thuật | 120", "gia_tri": 120}],
        }], {1: trang}, [])
        self.assertEqual(muc[0]["dan_chung"][0]["url_tai_lieu"], "https://truong.example.edu.vn/scan.png")
        self.assertEqual(trang.url_dan_chung["Phụ lục liên kết 1 · Phụ lục 2 · Trang PDF 2"], pdf_url)
