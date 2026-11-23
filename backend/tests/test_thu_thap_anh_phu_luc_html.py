import unittest
from io import BytesIO
from unittest.mock import patch

import httpx
from PIL import Image

from app.services import thu_thap_tuyen_sinh_ai as ai


class TestAnhTrongPhuLucHTML(unittest.TestCase):
    def test_doc_phu_luc_chi_co_anh_va_giu_url_anh_theo_dia_chi_sau_chuyen_huong(self):
        goc = "https://ts.example.edu.vn/tin/"
        ann = goc + "thong-bao-2"
        cuoi = "https://ts.example.edu.vn/ky-2026/phu-luc/"
        img = cuoi + "hinh/phan-vi.png"
        source = {"id": 7, "url": goc, "chinh_thuc": True, "phu_hop": True}
        bo_nho = ai.BoNhoNguonThuThap()

        def tai_trang(url, *, chi_html):
            self.assertTrue(chi_html)
            if str(url) == goc:
                html = '<p>Trường A công bố tuyển sinh năm 2026</p><a href="thong-bao-2">Trang bổ sung</a>'
                return url, html.encode(), "text/html"
            self.assertEqual(str(url), ann)
            html = '<title>Biểu 2</title><img src="data:image/svg+xml,placeholder" data-lazy-src="hinh/phan-vi.png">'
            return httpx.URL(cuoi), html.encode(), "text/html"

        with (
            patch.object(ai, "_tai_tai_lieu", side_effect=tai_trang) as tai,
            patch.object(ai, "_openai", return_value=({"ids": [1]}, [])),
            patch.object(ai, "_tai_bang_anh", return_value=("noi-dung-1", ["anh"])) as tai_anh,
            patch.object(ai, "_nhan_dang_bang_anh", return_value="A00 | 27 | 64,64") as doc_anh,
        ):
            for _ in range(2):
                doc = ai._doc_cac_nguon([source], {}, ai._bo_qua_tien_do, chi_html=True, bo_nho=bo_nho)[7]
                self.assertEqual(doc.url_dan_chung, {})
                ai._bo_sung_noi_dung([source], {7: doc}, bo_nho=bo_nho)
                nhan = "Phụ lục liên kết 1 · Trang bổ sung · Bảng ảnh 1"
                self.assertTrue(doc.doi_chieu(nhan, "A00 | 27 | 64,64"))
                self.assertEqual(doc.url_dan_chung[nhan], img)
        self.assertEqual(tai.call_count, 2)
        self.assertEqual(str(tai_anh.call_args.args[0].url), img)
        tai_anh.assert_called_once()
        doc_anh.assert_called_once()

    def test_ocr_cung_anh_ton_trong_url_goc_va_pham_vi_cua_moi_nguon(self):
        urls = ["https://ts.example.edu.vn/2025/", "https://ts.example.edu.vn/2026/"]
        sources = [{"id": i, "url": url} for i, url in enumerate(urls, 1)]
        docs = {s["id"]: ai._TaiLieu(s["url"], "Bảng quy đổi", [("Mở đầu", "Thông tin")], [],
                                     anh_bang=[("anh/bang.png", "", "")]) for s in sources}
        with (
            patch.object(ai, "_tai_bang_anh", return_value=("same-hash", ["anh"])) as tai,
            patch.object(ai, "_nhan_dang_bang_anh", return_value="x | y") as ocr,
        ):
            ai._bo_sung_noi_dung(sources, docs)
        self.assertEqual(tai.call_count, 2)
        ocr.assert_called_once()
        for src in sources:
            doc = docs[src["id"]]
            self.assertTrue(doc.doi_chieu("Bảng ảnh 1", "x | y"))
            self.assertEqual(doc.url_dan_chung["Bảng ảnh 1"], doc.url + "anh/bang.png")

    def test_loi_tam_thoi_tai_trang_va_doc_anh_duoc_thu_lai(self):
        url = "https://ts.example.edu.vn/de-an"
        source = {"id": 1, "url": url}
        doc = ai._TaiLieu(url, "", [("Mục A", "Mục tuyển sinh 2026")], [], anh_bang=[("/bang.png", "", "")])
        bo_nho = ai.BoNhoNguonThuThap()
        with (
            patch.object(ai, "_doc_tai_lieu", side_effect=[ai.AdmissionAIError("HTTP 503"), doc]) as tai,
            patch.object(ai, "_tai_bang_anh", return_value=("hash", ["anh"])),
            patch.object(ai, "_nhan_dang_bang_anh", side_effect=[ai.AdmissionAIError("timeout"), "Điều 1"]) as ocr,
        ):
            with self.assertRaises(ai.AdmissionAIError):
                bo_nho.doc(url, chi_html=True)
            lan_dau = bo_nho.doc(url, chi_html=True)
            ghi_chu = ai._bo_sung_noi_dung([source], {1: lan_dau}, bo_nho=bo_nho)
            self.assertTrue(any("timeout" in s for s in ghi_chu))
            lan_sau = bo_nho.doc(url, chi_html=True)
            ai._bo_sung_noi_dung([source], {1: lan_sau}, bo_nho=bo_nho)
            self.assertTrue(lan_sau.doi_chieu("Bảng ảnh 1", "Điều 1"))
        self.assertEqual(tai.call_count, 2)
        self.assertEqual(ocr.call_count, 2)

    def test_cong_thuc_mot_dong_nam_trong_anh_thap(self):
        bang = ai._BangAnh(1, httpx.URL("https://ts.example.edu.vn/cong-thuc.png"), "Bảng ảnh 1", "")
        buf = BytesIO()
        Image.new("RGB", (510, 55), "white").save(buf, format="PNG")
        with patch.object(ai, "_tai_tai_lieu", return_value=(bang.url, buf.getvalue(), "image/png")):
            _, cac_phan = ai._tai_bang_anh(bang)
        self.assertEqual(len(cac_phan), 1)

    def test_bang_con_o_khong_ro_duoc_doc_lai(self):
        url = "https://ts.example.edu.vn/tin"
        bo_nho = ai.BoNhoNguonThuThap()
        with (
            patch.object(ai, "_tai_bang_anh", return_value=("hash", ["anh"])),
            patch.object(ai, "_nhan_dang_bang_anh", side_effect=["A00 | [không rõ]", "A00 | 27"]) as ocr,
        ):
            for gia_tri in ("A00 | [không rõ]", "A00 | 27", "A00 | 27"):
                trang = ai._TaiLieu(url, "Thông tin", [], [], anh_bang=[("/anh.png", "", "")])
                ai._bo_sung_noi_dung([{"id": 1, "url": url}], {1: trang}, bo_nho=bo_nho)
                self.assertTrue(trang.doi_chieu("Bảng ảnh 1", gia_tri))
        self.assertEqual(ocr.call_count, 2)

    def test_ai_chon_phu_luc_va_anh_theo_muc_con_thieu_bo_qua_url_nguoi_dung_loai(self):
        url = "https://ts.example.edu.vn/tin/"
        nguon = {"id": 5, "url": url, "chinh_thuc": True, "phu_hop": True}
        trang = ai._TaiLieu(url, "Hướng dẫn", [("Mở đầu", "Thông tin 2026")], [],
                            lien_ket_co_nhan=[("bai-loai?utm_source=ts", "Thông tin cũ"), ("phu-luc", "Phụ lục")])
        phu_luc = ai._TaiLieu(url + "phu-luc", "Phụ lục", [], [], anh_bang=[
            ("bang-2.png", "", ""), ("mot-anh-khac.png", "", ""), ("anh-loai.png", "", ""),
        ])
        muc_thieu = ["Bảng quy đổi bách phân vị cho mã A"]
        bo_nho = ai.BoNhoNguonThuThap()
        bo_nho.bo_qua_url([url + "bai-loai", url + "anh-loai.png"])

        def chon(_, payload, __):
            self.assertEqual(payload["muc_can_bo_sung"], muc_thieu)
            danh_sach = [t["url"] for t in payload["tai_nguyen"]]
            self.assertEqual(danh_sach, [url + "phu-luc"] if payload["loai"] == "liên kết HTML" else
                             [url + "bang-2.png", url + "mot-anh-khac.png"])
            return {"ids": [1]}, []

        with (
            patch.object(ai, "_openai", side_effect=chon) as goi_ai,
            patch.object(ai, "_doc_tai_lieu", return_value=phu_luc) as doc,
            patch.object(ai, "_tai_bang_anh", return_value=("hash", ["anh"])),
            patch.object(ai, "_nhan_dang_bang_anh", return_value="Bách phân vị 80"),
        ):
            ai._bo_sung_noi_dung([nguon], {5: trang}, bo_nho=bo_nho, muc_can_bo_sung=muc_thieu)
            doc.assert_called_once_with(url + "phu-luc", chi_html=True)
            self.assertEqual(goi_ai.call_count, 2)
            self.assertIn(url + "bang-2.png", trang.url_dan_chung.values())

    def test_lien_ket_chuyen_huong_vao_nguon_da_bo_chon(self):
        url = "https://ts.example.edu.vn/phu-luc"
        dich = url + "-da-loai"
        bo_nho = ai.BoNhoNguonThuThap()
        bo_nho.bo_qua_url([dich])
        with patch.object(ai, "_doc_tai_lieu", return_value=ai._TaiLieu(dich, "", [], [])) as doc:
            with self.assertRaisesRegex(ai.AdmissionAIError, "bỏ chọn"):
                bo_nho.doc(url, chi_html=True)
            with self.assertRaisesRegex(ai.AdmissionAIError, "bỏ chọn"):
                bo_nho.doc(dich + "?utm_source=abc", chi_html=True)
            doc.assert_called_once_with(url, chi_html=True)
