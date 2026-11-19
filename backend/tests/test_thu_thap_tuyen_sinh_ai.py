import importlib.util
import json
import socket
import ssl
import unittest
from io import BytesIO
from unittest.mock import patch

import httpx

from app.services import thu_thap_tuyen_sinh_ai as ai

_TRUONG = {"ma_truong": "XDA", "ten_truong": "Trường Đại học Xây dựng Hà Nội", "website": "https://huce.edu.vn"}
_URL = "https://tuyensinh.huce.edu.vn/de-an-2026"
_URL_SUA = "https://tuyensinh.huce.edu.vn/phu-luc-2026.pdf"
_MUC = "Mục: Chỉ tiêu"
_XAC_MINH = "Trường Đại học Xây dựng Hà Nội (XDA) tuyển sinh 2026"
_PATH = "/dats_tuyen_sinh/chi_tieu"


def _thong_tin(url=_URL, **gia_tri):
    return {
        "url": url,
        "tieu_de": "Đề án 2026",
        "co_quan": _TRUONG["ten_truong"],
        "loai": "de_an",
        "chinh_thuc": True,
        "dung_truong_co_so": True,
        "nam_ap_dung": 2026,
        **gia_tri,
    }


class TestThuThapTuyenSinhAI(unittest.TestCase):
    def test_openai_dung_model_cau_hinh_va_bat_buoc_tim_kiem(self):
        yeu_cau = []
        client = httpx.Client

        def tra_loi(request):
            payload = json.loads(request.content)
            yeu_cau.append(payload)
            if "text" in payload:
                return httpx.Response(
                    400,
                    json={
                        "error": {
                            "param": "response_format",
                            "message": "Web Search cannot be used with JSON mode.",
                        }
                    },
                )
            return httpx.Response(
                200,
                json={
                    "status": "completed",
                    "output": [
                        {"type": "web_search_call", "action": {"sources": [{"url": _URL}]}},
                        {
                            "type": "message",
                            "content": [{"type": "output_text", "text": '```json\n{"nguon": []}\n```'}],
                        },
                    ],
                },
            )

        with (
            patch.object(ai.settings, "openai_model", "model-cau-hinh"),
            patch.object(ai.settings, "openai_api_key", "key-gia"),
            patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(tra_loi), **kw)),
        ):
            ai.search_sources(_TRUONG, 2026)

        self.assertEqual(yeu_cau[0]["model"], "model-cau-hinh")
        self.assertEqual(yeu_cau[0]["tools"], [{"type": "web_search"}])
        self.assertEqual(yeu_cau[0]["tool_choice"], "required")
        self.assertIn("JSON", yeu_cau[0]["input"])
        self.assertNotIn("text", yeu_cau[0])

    def test_openai_dung_che_do_json_cho_trich_xuat_khong_tim_kiem(self):
        yeu_cau = []
        client = httpx.Client

        def tra_loi(request):
            payload = json.loads(request.content)
            yeu_cau.append(payload)
            if "json" not in payload["input"].lower():
                return httpx.Response(
                    400,
                    json={
                        "error": {
                            "param": "text.format",
                            "message": "Response input messages must contain the word 'json' in some form.",
                        }
                    },
                )
            return httpx.Response(
                200,
                json={
                    "status": "completed",
                    "output": [{"type": "message", "content": [{"type": "output_text", "text": '{"muc": []}'}]}],
                },
            )

        with (
            patch.object(ai.settings, "openai_api_key", "key-gia"),
            patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(tra_loi), **kw)),
        ):
            data, _ = ai._openai("Trích xuất bản nháp.", {"nam_tuyen_sinh": 2026}, 1000)

        self.assertEqual(data, {"muc": []})
        self.assertEqual(yeu_cau[0]["text"], {"format": {"type": "json_object"}})
        self.assertNotIn("tools", yeu_cau[0])

    def test_openai_ghi_ma_chan_doan_va_khong_ghi_noi_dung_loi_goc(self):
        client = httpx.Client

        def tra_loi(_request):
            return httpx.Response(
                400,
                headers={"x-request-id": "req_abc123"},
                json={
                    "error": {
                        "code": "unsupported_value",
                        "param": "tools[0].type",
                        "message": "token-gia-private-noi-dung-loi-goc",
                    }
                },
            )

        with (
            patch.object(ai.settings, "openai_api_key", "token-gia-khong-duoc-ghi"),
            patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(tra_loi), **kw)),
            self.assertLogs(ai.logger, level="WARNING") as nhat_ky,
            self.assertRaisesRegex(ai.AdmissionAIError, "từ chối cấu hình tìm kiếm web") as loi,
        ):
            ai.search_sources(_TRUONG, 2026)

        self.assertIn("req_abc123", str(loi.exception))
        self.assertIn("code=unsupported_value param=tools[0].type request_id=req_abc123", nhat_ky.output[0])
        self.assertNotIn("token-gia", nhat_ky.output[0] + str(loi.exception))

    def test_tim_nguon_xac_minh_link_chinh_thuc_va_tep_dinh_kem(self):
        drive = "https://drive.google.com/file/d/ma_file/view"
        data = {
            "nguon": [
                _thong_tin(),
                _thong_tin(drive, url_trang_cong_bo=_URL, loai="phu_luc"),
                _thong_tin("https://tuyensinh.huce.edu.vn/khong-co-trong-ket-qua"),
                _thong_tin("https://bao.example.com/tin-tuyen-sinh"),
            ],
        }
        output = [
            {
                "type": "web_search_call",
                "action": {
                    "sources": [{"url": _URL}, {"url": "https://bao.example.com/tin-tuyen-sinh"}],
                },
            }
        ]
        tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, _XAC_MINH)], [drive])
        with (
            patch.object(ai, "_openai", return_value=(data, output)),
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
        ):
            nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)
        self.assertEqual([n["url"] for n in nguon], [_URL, drive, "https://bao.example.com/tin-tuyen-sinh"])
        self.assertEqual([n["phu_hop"] for n in nguon], [True, True, False])
        self.assertEqual(nguon[1]["url_trang_cong_bo"], _URL)
        self.assertTrue(any("khong-co-trong-ket-qua" in note for note in ghi_chu))

    def test_gioi_han_tim_nguon_ap_dung_sau_khi_xac_minh_va_loai_trung(self):
        urls = [f"{_URL}/tai-lieu-{so}" for so in range(12)]
        data = {
            "nguon": [
                _thong_tin(f"{_URL}/khong-co-trong-ket-qua"),
                _thong_tin(urls[0]),
                _thong_tin(f"{urls[0]}#chi-tieu"),
                *(_thong_tin(url) for url in urls[1:]),
            ],
        }
        output = [{"type": "web_search_call", "action": {"sources": [{"url": url} for url in urls]}}]

        with patch.object(ai, "_openai", return_value=(data, output)) as mo_hinh:
            nguon, _ = ai.search_sources(_TRUONG, 2026)

        self.assertEqual([n["url"] for n in nguon], urls)
        self.assertIn("Tự quyết định số tài liệu cần tìm", mo_hinh.call_args.args[0])

    def test_tim_nguon_giu_de_an_chinh_thuc_khi_trung_url(self):
        nguon_kem_uu_tien = (
            _thong_tin(f"{_URL}#diem-chuan", loai="diem_lich_su", nam_ap_dung=2025),
            _thong_tin(f"{_URL}#thong-tin-tom-tat", chinh_thuc=False),
            _thong_tin(f"{_URL}#phu-luc", loai="phu_luc"),
        )
        de_an = _thong_tin(f"{_URL}#de-an", tieu_de="Đề án chính thức năm 2026")
        output = [{"type": "web_search_call", "action": {"sources": [{"url": _URL}, {"url": _URL_SUA}]}}]

        for nguon_dau in nguon_kem_uu_tien:
            data = {"nguon": [nguon_dau, _thong_tin(_URL_SUA), de_an, nguon_kem_uu_tien[0]]}
            with (
                self.subTest(nguon_dau=nguon_dau["url"]),
                patch.object(ai, "_openai", return_value=(data, output)),
            ):
                nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)
                self.assertEqual(len(nguon), 2)
                self.assertEqual(nguon[0]["tieu_de"], de_an["tieu_de"])
                self.assertEqual(nguon[0]["loai"], "de_an")
                self.assertEqual(nguon[0]["nam_ap_dung"], 2026)
                self.assertTrue(nguon[0]["phu_hop"])
                self.assertFalse(nguon[0]["chi_diem_lich_su"])
                self.assertEqual(ghi_chu, [])

    def test_them_nguon_doi_chieu_noi_dung_da_tai(self):
        tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, _XAC_MINH)], [])
        data = _thong_tin(vi_tri_xac_minh=_MUC, trich_dan_xac_minh=_XAC_MINH)
        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", return_value=(data, [])),
        ):
            self.assertTrue(ai.inspect_source(_TRUONG, 2026, _URL)["phu_hop"])
            data["trich_dan_xac_minh"] = "Đoạn không xuất hiện"
            self.assertFalse(ai.inspect_source(_TRUONG, 2026, _URL)["phu_hop"])

    def test_trich_xuat_bao_tung_nguon_khong_doc_duoc_hoac_chuyen_huong_sai(self):
        url_chuyen_huong = "https://outside.example.org/redirected"
        sources = [
            {"id": 1, "url": _URL, "tieu_de": "Thông tin tuyển sinh"},
            {"id": 2, "url": _URL_SUA, "tieu_de": "Thông tin tuyển sinh"},
            {"id": 3, "url": f"{_URL}?ban=chinh-thuc"},
        ]

        def doc_gia_lap(url):
            if url == _URL:
                raise ai.AdmissionAIError("Trang không có nội dung văn bản đọc được.")
            url_cuoi = url_chuyen_huong if url == _URL_SUA else url
            return ai._TaiLieu(url_cuoi, "", [(_MUC, _XAC_MINH)], [])

        data = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}},
            "nguon_xac_minh": [{
                "nguon_id": 3, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                "vi_tri": _MUC, "trich_dan": _XAC_MINH,
            }],
            "muc": [],
        }
        with (
            patch.object(ai, "_doc_tai_lieu", side_effect=doc_gia_lap) as doc,
            patch.object(ai, "_openai", return_value=(data, [])) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources)
        self.assertEqual(doc.call_count, 3)
        self.assertEqual(ket_qua["nguon_ids"], [3])
        self.assertEqual(list(ket_qua["loi_nguon"]), [1, 2])
        self.assertIn("văn bản đọc được", ket_qua["loi_nguon"][1])
        self.assertIn("chưa được xác minh", ket_qua["loi_nguon"][2])
        self.assertEqual(ket_qua["ghi_chu"], list(ket_qua["loi_nguon"].values()))
        self.assertEqual([n["id"] for n in openai.call_args.args[1]["nguon_da_chon"]], [3])

    def test_trich_xuat_lai_chi_dung_nguon_da_xac_minh(self):
        sources = [{"id": 1, "url": _URL}, {"id": 2, "url": _URL_SUA}]
        tai_lieu = ai._TaiLieu(_URL, "", [(_MUC, _XAC_MINH)], [])
        danh_muc = [{"ma_phuong_thuc": "100", "ten_phuong_thuc": "Xét điểm thi tốt nghiệp THPT"}]

        def trich_xuat(_huong_dan, payload, _so_token):
            self.assertEqual(payload["danh_muc_phuong_thuc"], danh_muc)
            ids = [n["id"] for n in payload["nguon_da_chon"]]
            return {
                "du_lieu": {
                    "thong_tin_import": {},
                    "dats_tuyen_sinh": {"chi_tieu": 999 if 2 in ids else 90},
                    "quy_tac_xet_tuyen": {},
                },
                "muc": [],
                "nguon_xac_minh": [{
                    "nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                    "vi_tri": _MUC, "trich_dan": _XAC_MINH,
                }],
            }, []

        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", side_effect=trich_xuat) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources, danh_muc_phuong_thuc=danh_muc)

        self.assertEqual(openai.call_count, 2)
        self.assertEqual(ket_qua["du_lieu"]["dats_tuyen_sinh"]["chi_tieu"], 90)
        self.assertEqual(ket_qua["nguon_ids"], [1])
        self.assertIn("chưa trả kết quả xác minh", ket_qua["loi_nguon"][2])

    def test_trich_xuat_nhieu_nhom_giu_ma_va_dan_chung_dung_vi_tri(self):
        sources = [{"id": i, "url": f"{_URL}?id={i}"} for i in range(1, 24)]
        tai_lieu = ai._TaiLieu(_URL, "", [(_MUC, _XAC_MINH + "\n" + "Dữ liệu khác.\n" * 2600)], [])

        def trich_xuat(_huong_dan, payload, _so_token):
            ids = [n["id"] for n in payload["nguon_da_chon"]]
            return {
                "du_lieu": {
                    "thong_tin_import": {},
                    "dats_tuyen_sinh": {
                        "dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": f"CT{i}"} for i in ids],
                    },
                    "quy_tac_xet_tuyen": {},
                },
                "nguon_xac_minh": [
                    {"nguon_id": i, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                     "vi_tri": _MUC, "trich_dan": _XAC_MINH}
                    for i in ids
                ],
                "muc": [
                    {"duong_dan": f"/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/{vi_tri}/ma_xet_tuyen",
                     "dan_chung": [{"nguon_id": i, "vi_tri": _MUC, "trich_dan": _XAC_MINH, "gia_tri": f"CT{i}"}]}
                    for vi_tri, i in enumerate(ids)
                ],
            }, []

        tien_do = []
        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", side_effect=trich_xuat) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources, bao_tien_do=lambda *buoc: tien_do.append(buoc))

        self.assertGreater(openai.call_count, 1)
        self.assertEqual(ket_qua["nguon_ids"], list(range(1, 24)))
        self.assertEqual(len(ket_qua["du_lieu"]["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]), 23)
        self.assertEqual(ket_qua["muc"][-1]["duong_dan"], "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/22/ma_xet_tuyen")
        self.assertEqual(ket_qua["muc"][-1]["dan_chung"][0]["nguon_id"], 23)
        self.assertIn(("doc_nguon", 23, 23), tien_do)


    def test_trich_xuat_chia_nhom_lai_khi_model_bao_het_ngu_canh(self):
        sources = [{"id": 1, "url": _URL}, {"id": 2, "url": _URL_SUA}]
        tai_lieu = ai._TaiLieu(_URL, "", [(_MUC, _XAC_MINH)], [])
        danh_muc = [
            {"ma_phuong_thuc": "401", "ten_phuong_thuc": "Dùng bài thi đánh giá tư duy do trường tổ chức"},
            {"ma_phuong_thuc": "402", "ten_phuong_thuc": "Dùng bài thi đánh giá tư duy do đơn vị khác tổ chức"},
        ]

        def trich_xuat(huong_dan, payload, _so_token):
            self.assertEqual(payload["danh_muc_phuong_thuc"], danh_muc)
            for noi_dung in ("danh_muc_phuong_thuc", "ma_phuong_thuc_cua_truong", "null", "500"):
                self.assertIn(noi_dung, huong_dan)
            nhom = payload["nguon_da_chon"]
            if len(nhom) > 1:
                raise ai._LoiDungLuongModel("Hết ngữ cảnh.")
            ma = nhom[0]["id"]
            return {
                "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}},
                "muc": [],
                "nguon_xac_minh": [{
                    "nguon_id": ma, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                    "vi_tri": _MUC, "trich_dan": _XAC_MINH,
                }],
            }, []

        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", side_effect=trich_xuat) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources, danh_muc_phuong_thuc=danh_muc)

        self.assertEqual(openai.call_count, 3)
        self.assertEqual(ket_qua["nguon_ids"], [1, 2])
        self.assertEqual(ket_qua["loi_nguon"], {})

    def test_ban_nhap_giu_tung_dien_va_ly_do_khi_chua_xac_dinh_ma_bo(self):
        danh_muc = [
            {"ma_phuong_thuc": "401", "ten_phuong_thuc": "Thi đánh giá tư duy do trường tổ chức"},
            {"ma_phuong_thuc": "500", "ten_phuong_thuc": "Phương thức khác"},
        ]
        ly_do = "Diện XTTN-1.3 chưa đủ căn cứ phân loại vì phỏng vấn chỉ là một bước."
        cac_dien = [("DGT-01", "401"), ("DGT-02", "401"), ("XTTN-1.3", None)]
        phuong_thuc = [
            {
                "ma_phuong_thuc_cua_truong": dien,
                "ma_phuong_thuc_cua_bo": ma_bo,
                "cong_thuc_tinh_diem": dien,
                "ghi_chu": ly_do if ma_bo is None else None,
            }
            for dien, ma_bo in cac_dien
        ]
        cong_thuc = [
            {"ma_cong_thuc": dien, "ma_phuong_thuc_cua_bo": ma_bo, "ghi_chu": ly_do if ma_bo is None else None}
            for dien, ma_bo in cac_dien
        ]
        muc_chua_ro = {
            "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_phuong_thuc/2/ma_phuong_thuc_cua_bo",
            "/quy_tac_xet_tuyen/cong_thuc/2/ma_phuong_thuc_cua_bo",
        }
        tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, _XAC_MINH)], [])
        data = {
            "du_lieu": {
                "thong_tin_import": {},
                "dats_tuyen_sinh": {
                    "dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": "IT1", "dats_phuong_thuc": phuong_thuc}],
                },
                "quy_tac_xet_tuyen": {"cong_thuc": cong_thuc},
            },
            "nguon_xac_minh": [{
                "nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                "vi_tri": _MUC, "trich_dan": _XAC_MINH,
            }],
            "muc": [{"duong_dan": p, "dan_chung": [], "ghi_chu": ly_do} for p in sorted(muc_chua_ro)],
            "ghi_chu": [ly_do],
        }
        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", return_value=(data, [])),
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, [{"id": 1, "url": _URL}], danh_muc_phuong_thuc=danh_muc)

        nhanh = ket_qua["du_lieu"]
        phuong_thuc = nhanh["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"]
        self.assertEqual(
            [(pt["ma_phuong_thuc_cua_truong"], pt["ma_phuong_thuc_cua_bo"]) for pt in phuong_thuc], cac_dien,
        )
        self.assertEqual(
            [(ct["ma_cong_thuc"], ct["ma_phuong_thuc_cua_bo"]) for ct in nhanh["quy_tac_xet_tuyen"]["cong_thuc"]],
            cac_dien,
        )
        self.assertIn(ly_do, ket_qua["ghi_chu"])
        self.assertTrue(muc_chua_ro.issubset({dong["duong_dan"] for dong in ket_qua["muc"] if dong["ghi_chu"] == ly_do}))

    def test_ban_nhap_chi_giu_500_khi_nguon_neu_ro_ma_phuong_thuc(self):
        danh_muc = [{"ma_phuong_thuc": "500", "ten_phuong_thuc": "Phương thức khác"}]
        khoa = "ma_phuong_thuc_cua_bo"
        muc_phuong_thuc = f"/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_phuong_thuc/0/{khoa}"
        muc_cong_thuc = f"/quy_tac_xet_tuyen/cong_thuc/0/{khoa}"
        truong_hop = [
            ({khoa: "500"}, "Mã phương thức: 500", "500"),
            ({khoa: "500"}, "500 chỉ tiêu", None),
            ({khoa: "699"}, "Mã phương thức: 699", None),
            ({}, "", None),
        ]
        for bo, trich_dan, mong_doi in truong_hop:
            with self.subTest(ma_bo=bo.get(khoa), trich_dan=trich_dan):
                phuong_thuc = {"ma_phuong_thuc_cua_truong": "PT-RIENG", "cong_thuc_tinh_diem": "CT1", **bo}
                cong_thuc = {"ma_cong_thuc": "CT1", **bo}
                tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, f"{_XAC_MINH}\n{trich_dan}")], [])
                data = {
                    "du_lieu": {
                        "thong_tin_import": {},
                        "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [{
                            "ma_xet_tuyen": "IT1", "dats_phuong_thuc": [phuong_thuc],
                        }]},
                        "quy_tac_xet_tuyen": {"cong_thuc": [cong_thuc]},
                    },
                    "nguon_xac_minh": [{
                        "nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                        "vi_tri": _MUC, "trich_dan": _XAC_MINH,
                    }],
                    "muc": [
                        {"duong_dan": duong_dan, "dan_chung": [{
                            "nguon_id": 1, "vi_tri": _MUC, "trich_dan": trich_dan, "gia_tri": bo[khoa],
                        }]}
                        for duong_dan in (muc_phuong_thuc, muc_cong_thuc) if trich_dan
                    ],
                }
                with (
                    patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
                    patch.object(ai, "_openai", return_value=(data, [])),
                ):
                    ket_qua = ai.extract_draft(_TRUONG, 2026, [{"id": 1, "url": _URL}], danh_muc_phuong_thuc=danh_muc)

                nhanh = ket_qua["du_lieu"]
                chuong_trinh = nhanh["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]
                self.assertEqual(chuong_trinh["dats_phuong_thuc"][0][khoa], mong_doi)
                self.assertEqual(nhanh["quy_tac_xet_tuyen"]["cong_thuc"][0][khoa], mong_doi)
                if mong_doi is None:
                    self.assertTrue(ket_qua["ghi_chu"])
                    can_xem_lai = {dong["duong_dan"] for dong in ket_qua["muc"] if dong.get("ghi_chu")}
                    self.assertTrue({muc_phuong_thuc, muc_cong_thuc}.issubset(can_xem_lai))

    def test_trich_xuat_giu_hai_gia_tri_va_loai_dan_chung_sai(self):
        def dc(nguon_id, vi_tri, trich_dan, gia_tri):
            return dict(nguon_id=nguon_id, vi_tri=vi_tri, trich_dan=trich_dan, gia_tri=gia_tri)

        tai_lieu = {
            _URL: ai._TaiLieu(_URL, "", [(_MUC, f"{_XAC_MINH}\nTổng 80 chỉ tiêu")], []),
            _URL_SUA: ai._TaiLieu(_URL_SUA, "", [("Trang PDF 2", f"{_XAC_MINH}\nĐiều chỉnh thành 95 chỉ tiêu")], []),
        }
        sources = [
            {"id": 10, "url": _URL, "nam_ap_dung": 2026},
            {"id": 11, "url": _URL_SUA, "nam_ap_dung": 2026},
        ]
        data = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {"chi_tieu": 95}, "quy_tac_xet_tuyen": {}},
            "nguon_xac_minh": [
                {
                    "nguon_id": 10,
                    "vi_tri": _MUC,
                    "trich_dan": _XAC_MINH,
                    "dung_truong_co_so": True,
                    "nam_ap_dung": 2026,
                },
                {
                    "nguon_id": 11,
                    "vi_tri": "Trang PDF 1",
                    "trich_dan": _XAC_MINH,
                    "dung_truong_co_so": True,
                    "nam_ap_dung": 2026,
                },
            ],
            "muc": [
                {
                    "duong_dan": _PATH,
                    "dan_chung": [
                        dc(10, _MUC, "Tổng 80 chỉ tiêu", 80),
                        dc(11, "Trang PDF 2", "Điều chỉnh thành 95 chỉ tiêu", 95),
                        dc(11, "Trang PDF 1", "Điều chỉnh thành 95 chỉ tiêu", 95),
                        dc(10, _MUC, "100 chỉ tiêu", 100),
                        dc(99, _MUC, "Tổng 80 chỉ tiêu", 80),
                        dc(11, "Trang PDF 1", "Điều chỉnh thành 95 chỉ tiêu", 95),
                    ],
                }
            ],
        }
        with (
            patch.object(ai, "_doc_tai_lieu", side_effect=tai_lieu.__getitem__) as tai,
            patch.object(ai, "_openai", return_value=(data, [])) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources)
        self.assertEqual({call.args[0] for call in tai.call_args_list}, {_URL, _URL_SUA})
        self.assertFalse(openai.call_args.kwargs.get("tim_kiem", False))
        self.assertEqual({s["url"] for s in openai.call_args.args[1]["nguon_da_chon"]}, {_URL, _URL_SUA})
        self.assertEqual([n["gia_tri"] for n in ket_qua["muc"][0]["dan_chung"]], [80, 95])
        self.assertTrue(ket_qua["muc"][0]["mau_thuan"])
        self.assertIn("4 dẫn chứng", ket_qua["ghi_chu"][0])

    def test_xac_minh_nguon_bao_dung_ma_va_nguyen_nhan_khong_dat(self):
        sources = [{"id": i, "url": _URL} for i in range(1, 9)]
        phu_luc = "Phụ lục 1"
        tai_lieu = ai._TaiLieu(
            _URL, "Đề án 2026", [(_MUC, _XAC_MINH), (phu_luc, "Đoạn chỉ có trong phụ lục")], [],
            url_dan_chung={phu_luc: _URL_SUA},
        )
        xac_minh = {"vi_tri": _MUC, "trich_dan": _XAC_MINH, "dung_truong_co_so": True, "nam_ap_dung": 2026}
        data = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}},
            "nguon_xac_minh": [
                {**xac_minh, "nguon_id": 2, "dung_truong_co_so": False},
                {**xac_minh, "nguon_id": 3, "nam_ap_dung": 2025},
                {**xac_minh, "nguon_id": 4, "vi_tri": None},
                {**xac_minh, "nguon_id": 5, "trich_dan": "Đoạn do AI tạo"},
                {**xac_minh, "nguon_id": 6, "trich_dan": "Đoạn chỉ có trong phụ lục"},
                {**xac_minh, "nguon_id": 7, "vi_tri": phu_luc, "trich_dan": "Đoạn chỉ có trong phụ lục"},
                {**xac_minh, "nguon_id": 8, "ma_doan": 999},
            ],
        }
        with (
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
            patch.object(ai, "_openai", return_value=(data, [])),
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources)

        self.assertEqual(ket_qua["nguon_ids"], [])
        self.assertEqual(ket_qua["du_lieu"], data["du_lieu"])
        self.assertEqual(list(ket_qua["loi_nguon"]), list(range(1, 9)))
        for i, ly_do in enumerate((
            "chưa trả kết quả", "đúng trường hoặc cơ sở", "đúng năm áp dụng 2026", "nhãn mục",
            "không khớp văn bản", "không khớp văn bản", "không khớp văn bản", "đoạn xác minh có trong nguồn gốc",
        ), start=1):
            self.assertIn(f"#{i}", ket_qua["loi_nguon"][i])
            self.assertIn(ly_do, ket_qua["loi_nguon"][i])

    def test_xac_minh_phenikaa_chon_doan_goc_khi_tieu_de_tim_kiem_khac(self):
        url = "https://psidt.phenikaa-uni.edu.vn/vi/post/tuyen-sinh/dai-hoc-phenikaa-cong-bo-tuyen-sinh-nam-2026-du-kien"
        tieu_de_goc = "Đại học Phenikaa công bố thông tin tuyển sinh năm 2026 (dự kiến)"
        tieu_de_tim_kiem = "Đại học Phenikaa công bố thông tin tuyển sinh hệ Đại học chính quy năm 2026 (dự kiến)"
        truong = {"ma_truong": "PKA", "ten_truong": "Trường Đại học Phenikaa", "website": "https://phenikaa-uni.edu.vn"}
        nguon = {"id": 3, "url": url, "tieu_de": tieu_de_tim_kiem, "nam_ap_dung": 2026}
        tai_lieu = ai._TaiLieu(url, tieu_de_goc, [("Tiêu đề bài viết", tieu_de_goc), ("Nội dung trang", "Mã trường: PKA")], [])
        self.assertFalse(tai_lieu.co_trich_dan_trong_nguon_goc(tieu_de_tim_kiem))

        def tra_loi_chon_doan(_, payload, __):
            du_lieu_nguon = payload["nguon_da_chon"][0]
            self.assertEqual(du_lieu_nguon["tieu_de"], tieu_de_goc)
            cac_doan = du_lieu_nguon["doan_xac_minh"]
            ma_doan = next(d["ma_doan"] for d in cac_doan if d["trich_dan"] == tieu_de_goc)
            return {
                "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}},
                "nguon_xac_minh": [{"nguon_id": 3, "dung_truong_co_so": True, "nam_ap_dung": 2026, "ma_doan": ma_doan}],
                "muc": [],
            }, []

        with patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu), patch.object(ai, "_openai", side_effect=tra_loi_chon_doan):
            ket_qua = ai.extract_draft(truong, 2026, [nguon])
        self.assertEqual(ket_qua["doi_chieu_chuong_trinh"], [])

    def test_trich_xuat_giu_chuong_trinh_va_cong_thuc_khi_thieu_mot_ma(self):
        tieu_de = "Thông tin tuyển sinh năm 2026"
        tong = "Toàn trường tuyển sinh 2 mã xét tuyển."
        dong = "IT1 | Khoa học máy tính | Điểm thi THPT"
        tai_lieu = ai._TaiLieu(_URL, tieu_de, [(_MUC, f"{tieu_de}\n{tong}\n{dong}")], [])
        nguon = {**_thong_tin(_URL), "id": 1, "phu_hop": True}
        data = {
            "du_lieu": {
                "thong_tin_import": {},
                "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "Khoa học máy tính"}]},
                "quy_tac_xet_tuyen": {
                    "chuong_trinh": [{"ma_xet_tuyen": "IT1", "phuong_an": [{"ma_cong_thuc": "THPT"}]}],
                    "cong_thuc": [{"ma_cong_thuc": "THPT", "ten_cong_thuc": "Điểm thi THPT"}],
                },
            },
            "nguon_xac_minh": [{"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                               "vi_tri": _MUC, "trich_dan": tieu_de}],
            "muc": [{"duong_dan": "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/ma_xet_tuyen", "dan_chung": [
                {"nguon_id": 1, "vi_tri": _MUC, "trich_dan": dong, "gia_tri": "IT1"},
            ]}],
            "ghi_chu": ["Đã xác minh 1/2 mã. Còn thiếu 1 mã chưa xác định."],
            "doi_chieu_chuong_trinh": [
                {"nguon_id": 1, "vi_tri": _MUC, "trich_dan": tong, "cac_ma": [],
                 "tong_cong_bo": 2, "pham_vi": "toan_truong"},
                {"nguon_id": 1, "vi_tri": _MUC, "trich_dan": dong, "cac_ma": ["IT1"], "pham_vi": "toan_truong"},
            ],
        }
        with patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu), patch.object(ai, "_openai", return_value=(data, [])) as mo_hinh:
            ket_qua = ai.extract_draft(_TRUONG, 2026, [nguon])
        self.assertIn("Giữ tất cả chương trình, công thức và phương án", mo_hinh.call_args.args[0])
        self.assertEqual(ket_qua["du_lieu"], data["du_lieu"])
        self.assertEqual(ket_qua["doi_chieu_chuong_trinh"][0]["tong_cong_bo"], 2)
        self.assertTrue(any("thiếu 1 mã" in chu for chu in ket_qua["ghi_chu"]))
        self.assertEqual(ket_qua["muc"][0]["dan_chung"][0]["gia_tri"], "IT1")

    def test_doi_chieu_ma_chuong_trinh_dung_doan_va_tong_dung_pham_vi(self):
        du_kien = "https://tuyensinh.huce.edu.vn/thong-bao-du-kien"
        noi_dung = "Toàn trường tuyển sinh 2 mã xét tuyển.\nIT10 | Tin học\nIT2 | Kỹ thuật\nCó 95 chỉ tiêu."
        tai_lieu = {
            10: ai._TaiLieu(_URL, "Đề án chính thức", [(_MUC, noi_dung)], []),
            11: ai._TaiLieu(du_kien, "Đề án dự kiến", [(_MUC, noi_dung)], []),
        }
        sources = [dict(_thong_tin(doc.url), id=i, phu_hop=True) for i, doc in tai_lieu.items()]
        sources[1].update(thay_the_url=_URL, pham_vi_dieu_chinh="Toàn bộ đề án")

        def de_xuat(nguon_id, trich_dan, ma, tong=None):
            return {"nguon_id": nguon_id, "vi_tri": _MUC, "trich_dan": trich_dan, "cac_ma": ma,
                    "tong_cong_bo": tong, "pham_vi": "toan_truong"}

        ds = ai._doi_chieu_chuong_trinh([
            de_xuat(10, "Toàn trường tuyển sinh 2 mã xét tuyển.", [], 2),
            de_xuat(10, "IT10 | Tin học", ["IT1", "IT10", "IT10"]),
            de_xuat(10, "IT2 | Kỹ thuật", ["IT2"]),
            de_xuat(10, "Có 95 chỉ tiêu.", [], 95),
            de_xuat(10, "Không có trong tài liệu", ["IT99"], 999),
            de_xuat(11, "Toàn trường tuyển sinh 2 mã xét tuyển.", [], 2),
            de_xuat(11, "IT10 | Tin học", ["IT10"]),
        ], sources, tai_lieu, 2026)

        self.assertEqual([(d["cac_ma"], d["tong_cong_bo"], d["pham_vi"]) for d in ds], [
            ([], 2, "toan_truong"), (["IT10"], None, "toan_truong"), (["IT2"], None, "toan_truong"),
            (["IT10"], None, "phan_pham_vi"),
        ])

    def test_bo_sung_chi_lay_dan_chung_cong_thuc_co_trong_nguon(self):
        tien_to = "/quy_tac_xet_tuyen/cong_thuc/0"
        exact = "Điểm xét tuyển lấy tổng điểm ba môn thi THPT, theo thang điểm 30."
        doc = ai._TaiLieu(_URL, "Đề án chính thức", [(_MUC, exact)], [])
        du_lieu = {"quy_tac_xet_tuyen": {"cong_thuc": [{"thang_diem": 30, "he_so_nhan": 1}]}}
        loi = []
        with patch.object(ai, "_openai", return_value=({"dan_chung": [
            {"duong_dan": f"{tien_to}/thang_diem", "nguon_id": 1, "vi_tri": _MUC, "trich_dan": exact, "gia_tri": 100},
            {"duong_dan": f"{tien_to}/he_so_nhan", "nguon_id": 1, "vi_tri": _MUC, "trich_dan": "hệ số nhân là 1"},
            {"duong_dan": f"{tien_to}/diem_san", "nguon_id": 1, "vi_tri": _MUC, "trich_dan": exact},
        ]}, [])):
            muc = ai._bo_sung_dan_chung_cong_thuc(du_lieu, [], {1: doc}, loi)
        theo_path = {m["duong_dan"]: m["dan_chung"] for m in muc}
        self.assertEqual(theo_path[f"{tien_to}/thang_diem"][0]["gia_tri"], 30)
        self.assertEqual(theo_path[f"{tien_to}/he_so_nhan"], [])
        self.assertNotIn(f"{tien_to}/diem_san", theo_path)
        self.assertTrue(any("1 công thức còn trường chưa có dẫn chứng" in chu for chu in loi))

    def test_tai_tai_lieu_khoa_ip_da_xac_minh_va_kiem_tra_lai_chuyen_huong(self):
        yeu_cau = []
        tuy_chon_client = []
        client = httpx.Client

        def chuyen_huong(request):
            yeu_cau.append(request)
            return httpx.Response(302, headers={"Location": "https://may-chu-noi-bo.example.com/de-an"})

        def tra_dns(host, port, **_):
            ip = "9.9.9.9" if host == "tuyensinh.huce.edu.vn" else "10.0.0.10"
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]

        def tao_client(**kw):
            tuy_chon_client.append(kw)
            return client(transport=httpx.MockTransport(chuyen_huong), **kw)

        with (
            patch.object(ai.socket, "getaddrinfo", side_effect=tra_dns),
            patch.object(ai.httpx, "Client", side_effect=tao_client),
            patch.object(
                ssl.SSLContext, "load_default_certs", autospec=True, side_effect=ssl.SSLContext.load_default_certs
            ) as nap_chung_chi,
            self.assertRaisesRegex(ai.AdmissionAIError, "địa chỉ công khai"),
        ):
            ai._doc_tai_lieu(_URL)

        self.assertEqual(len(yeu_cau), 1)
        self.assertEqual(yeu_cau[0].url.host, "9.9.9.9")
        self.assertEqual(yeu_cau[0].headers["Host"], "tuyensinh.huce.edu.vn")
        self.assertEqual(yeu_cau[0].extensions["sni_hostname"], "tuyensinh.huce.edu.vn")
        tls = tuy_chon_client[0]["verify"]
        self.assertEqual(tls.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(tls.check_hostname)
        self.assertFalse(tls.verify_flags & getattr(ssl, "VERIFY_X509_PARTIAL_CHAIN", 0))
        self.assertFalse(tuy_chon_client[0]["trust_env"])
        nap_chung_chi.assert_called_once_with(tls, ssl.Purpose.SERVER_AUTH)

    def test_tai_tai_lieu_bao_loi_xac_minh_chung_chi(self):
        client = httpx.Client

        def loi_tls(_request):
            raise httpx.ConnectError("Lỗi khi bắt tay TLS") from ssl.SSLCertVerificationError("Issuer test")

        with (
            patch.object(ai, "_dia_chi_cong_khai", return_value=["9.9.9.9"]),
            patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(loi_tls), **kw)),
            self.assertRaisesRegex(ai.AdmissionAIError, "Không xác minh được chứng chỉ HTTPS"),
        ):
            ai._doc_tai_lieu(_URL)

    def test_doc_html_lay_de_muc_va_bo_noi_dung_khong_hien_thi(self):
        html = (
            "<title>Đề án</title><script>Chỉ tiêu 80</script>"
            "<h2>Chỉ tiêu</h2><table><tr><td>Chương trình A</td><td>95</td></tr></table>"
        )
        with patch.object(
            ai, "_tai_tai_lieu", return_value=(httpx.URL(_URL), html.encode(), "text/html; charset=UTF-8")
        ):
            doc = ai._doc_tai_lieu(_URL)
        self.assertEqual(doc.tieu_de, "Đề án")
        self.assertTrue(doc.doi_chieu(_MUC, "Chương trình A 95"))
        self.assertFalse(doc.doi_chieu(_MUC, "Chỉ tiêu 80"))

    def test_doc_html_next_data_lay_dung_bai_viet_va_dan_chung(self):
        modules = [
            {"content": "<p>Nội dung mẫu thông tin cuối trang</p>"},
            {
                "newsData": {
                    "data": [
                        {"title": "Đề án tuyển sinh năm 2025", "slug": "de-an-2025", "content": "<p>Chỉ tiêu 80</p>"},
                        {
                            "title": "Thông tin tuyển sinh năm 2026",
                            "slug": "de-an-2026",
                            "content": (
                                '<h2>Chỉ tiêu</h2><p>Chương trình A có 95 chỉ tiêu.</p><img src="/bang.png">'
                                '<a href="/phu-luc.pdf">Phụ lục</a><script>Chỉ tiêu sai 120</script>'
                            ),
                        },
                    ]
                }
            },
        ]
        du_lieu = {"props": {"initialProps": {"pageProps": {"page": {"data": {"pageData": {"modules": modules}}}}}}}
        script = json.dumps(du_lieu).replace("<", r"\u003c")
        raw = (
            '<title>Đề án năm 2026</title><div id="__next"><div>Loading...</div></div>'
            f'<script id="__NEXT_DATA__" type="application/json">{script}</script>'
        )
        with patch.object(ai, "_tai_tai_lieu", return_value=(httpx.URL(_URL), raw.encode(), "text/html")):
            doc = ai._doc_tai_lieu(_URL)
        self.assertEqual(doc.tieu_de, "Thông tin tuyển sinh năm 2026")
        self.assertTrue(doc.doi_chieu(_MUC, "Chương trình A có 95 chỉ tiêu."))
        self.assertEqual(doc.lien_ket, ["/phu-luc.pdf"])
        self.assertEqual(doc.lien_ket_co_nhan, [("/phu-luc.pdf", "Phụ lục")])
        self.assertEqual(doc.anh_bang[0][:2], ("/bang.png", ""))
        self.assertIn("Chương trình A có 95 chỉ tiêu.", doc.anh_bang[0][2])
        self.assertIn("Bài viết có ảnh", doc.canh_bao)
        tong_noi_dung = " ".join(text for _, text in doc.doan)
        for khong_phai_noi_dung in ("Chỉ tiêu 80", "Chỉ tiêu sai 120", "Nội dung mẫu thông tin cuối trang"):
            self.assertNotIn(khong_phai_noi_dung, tong_noi_dung)

    def test_doc_html_tu_choi_trang_chi_co_tieu_de(self):
        raw = '<title>Đề án 2026</title><div id="__next">Đang tải…</div><script src="/app.js"></script>'
        with (
            patch.object(ai, "_tai_tai_lieu", return_value=(httpx.URL(_URL), raw.encode(), "text/html")),
            self.assertRaisesRegex(ai.AdmissionAIError, "Trang không có nội dung văn bản đọc được"),
        ):
            ai._doc_tai_lieu(_URL)

    def test_doc_phu_luc_uu_tien_lien_ket_bai_viet_va_khu_trung_tep_drive(self):
        drive = "https://drive.google.com/file/d/tepphuluc/view"
        drive_download = "https://drive.usercontent.google.com/download?export=download&id=tepphuluc"
        tai_lieu = ai._TaiLieu(
            _URL,
            "Đề án 2026",
            [(_MUC, _XAC_MINH)],
            [],
            lien_ket_co_nhan=[
                ("/khac", "Xem thêm"),
                ("#doc", "Phụ lục trong trang"),
                ("/phu-luc1", "Phụ lục 1"),
                (drive, "Phụ lục 2: Bảng quy đổi điểm"),
                (drive_download, "Phụ lục 2: Bảng quy đổi"),
            ],
        )
        doc = ai._TaiLieu(drive_download, "", [("Trang PDF 2", "IELTS 6.5: 9.5 điểm")], [])
        da_doc = set()
        with patch.object(ai, "_doc_tai_lieu", return_value=doc) as doc_file:
            ket_qua, ghi_chu = ai._doc_phu_luc(
                {"chinh_thuc": True, "phu_hop": True},
                tai_lieu,
                toi_da=1,
                bo_qua=da_doc,
            )
        doc_file.assert_called_once_with(drive)
        self.assertEqual(len(ket_qua), 1)
        self.assertEqual(ket_qua[0].url_goc, drive)
        self.assertTrue(ket_qua[0].tai_lieu.doi_chieu("Trang PDF 2", "IELTS 6.5: 9.5 điểm"))
        self.assertEqual(da_doc, {ai._url_so_sanh(drive)})
        self.assertIn("1 phụ lục ngoài phạm vi", ghi_chu[0])

    def test_doc_phu_luc_bao_loi_tai_va_chuyen_huong_khac_ten_mien(self):
        tai_lieu = ai._TaiLieu(
            _URL,
            "Đề án 2026",
            [(_MUC, _XAC_MINH)],
            [],
            lien_ket_co_nhan=[("/phu-luc1", "Phụ lục 1"), ("/phu-luc2.pdf", "Phụ lục 2")],
        )

        def tai(url):
            if url.endswith("phu-luc1"):
                raise ai.AdmissionAIError("Không tải được.")
            return ai._TaiLieu("https://tam.example.com/phu-luc.pdf", "", [("Trang PDF 2", "Sai nguồn")], [])

        with patch.object(ai, "_doc_tai_lieu", side_effect=tai) as doc_file:
            self.assertEqual(ai._doc_phu_luc({"chinh_thuc": False}, tai_lieu), ([], []))
            doc_file.assert_not_called()
            ket_qua, ghi_chu = ai._doc_phu_luc({"chinh_thuc": True, "phu_hop": True}, tai_lieu)
        self.assertEqual(ket_qua, [])
        self.assertEqual(len(ghi_chu), 2)
        self.assertTrue(any("Phụ lục 1" in note and "Không tải được" in note for note in ghi_chu))
        self.assertTrue(any("Phụ lục 2" in note and "chuyển hướng sang tên miền khác" in note for note in ghi_chu))

    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "pypdf chưa được cài đặt")
    def test_doc_pdf_giu_so_trang_khi_co_hon_240_trang(self):
        from pypdf import PdfWriter
        from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

        writer = PdfWriter()
        for _ in range(240):
            writer.add_blank_page(width=200, height=100)
        page = writer.add_blank_page(width=200, height=100)
        font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject({NameObject("/F1"): font}),
            }
        )
        contents = DecodedStreamObject()
        contents.set_data(b"BT /F1 10 Tf 10 30 Td (XDA 2026 - 95) Tj ET")
        page.replace_contents(contents)
        data = BytesIO()
        writer.write(data)
        doc = ai._doc_pdf(data.getvalue(), httpx.URL(_URL_SUA))
        self.assertTrue(doc.doi_chieu("Trang PDF 241", "XDA 2026 - 95"))
        self.assertFalse(doc.doi_chieu("Trang PDF 1", "XDA 2026 - 95"))
        self.assertIn("1", doc.canh_bao)


    @unittest.skipUnless(importlib.util.find_spec("pypdf"), "pypdf chưa được cài đặt")
    def test_doc_pdf_nhan_dang_trang_quet_khong_co_lop_van_ban(self):
        from PIL import Image

        tep = BytesIO()
        Image.new("RGB", (450, 300), "white").save(tep, format="PDF")
        with patch.object(ai, "_openai", return_value=({"van_ban": _XAC_MINH}, [])) as mo_hinh:
            doc = ai._doc_pdf(tep.getvalue(), httpx.URL(_URL_SUA))

        self.assertTrue(doc.doi_chieu("Trang PDF 1", _XAC_MINH))
        self.assertIn("nhận dạng từ ảnh", doc.canh_bao)
        self.assertTrue(mo_hinh.call_args.kwargs["anh"])
