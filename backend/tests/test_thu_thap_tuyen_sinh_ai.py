import importlib.util
import json
import socket
import ssl
import unittest
from io import BytesIO
from unittest.mock import patch

import httpx

from app.schemas.dats_thu_thap import SuaMucBanNhap
from app.services.dats_ban_nhap_thu_thap import canh_bao_dan_chung, lap_muc_ban_nhap, sua_muc_ban_nhap
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
    def test_diem_va_cho_can_lam_ro_do_ai_quyet_dinh_tu_bang(self):
        html = f"""<title>Điểm chuẩn 2026</title><h2>Điểm trúng tuyển năm 2026</h2><p>{_XAC_MINH}</p>
        <table><tr><th>Mã xét tuyển</th><th>Mã phương thức của Bộ</th><th>Tổ hợp</th>
        <th>Điểm trúng tuyển (thang điểm 30)</th><th>Điểm tương đương TSA</th></tr>
        <tr><td rowspan="2">IT1</td><td>100</td><td>A00</td><td>27,5</td><td>80</td></tr>
        <tr><td>200</td><td>D01</td><td>28</td><td>85</td></tr></table>"""
        nhanh = {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {"diem_chuan": [{
            "nam_tuyen_sinh": 2026, "ma_xet_tuyen": "IT1", "ma_phuong_thuc_cua_bo": "100", "ma_to_hop": "A00",
            "diem_chuan": 27.5, "thang_diem": 30, "nguon_du_lieu_url": _URL,
        }]}}
        vi_tri = "Mục: Điểm trúng tuyển năm 2026 · Bảng 1"
        dau = "| IT1 | 100 | A00 | 27,5 | 80 |"
        duong_dan = "/quy_tac_xet_tuyen/diem_chuan/0/"
        cau_hoi = {"pham_vi": "IT1 D01", "ly_do": "Cần đối chiếu phạm vi cột.",
                   "vi_tri": vi_tri, "trich_dan": "D01"}
        data = {"du_lieu": nhanh, "ra_soat_diem_chuan": [
            {"nguon_id": 1, "da_doc_het": True, "can_lam_ro": [cau_hoi]},
        ], "muc": [
            {"duong_dan": duong_dan + khoa, "phan_loai_ma_bo": "cong_bo",
             "dan_chung": [{"nguon_id": 1, "vi_tri": vi_tri, "trich_dan": dau, "gia_tri": value}]}
            for khoa, value in (("diem_chuan", 27.5), ("ma_phuong_thuc_cua_bo", "100"))
        ], "nguon_xac_minh": [{"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                                "vi_tri": "Mục: Điểm trúng tuyển năm 2026", "trich_dan": _XAC_MINH}]}
        nguon = {**_thong_tin(), "id": 1, "phu_hop": True, "lua_chon": "su_dung"}
        with (patch.object(ai, "_tai_tai_lieu", return_value=(httpx.URL(_URL), html.encode(), "text/html")) as tai,
              patch.object(ai, "_openai", return_value=(data, [])) as model):
            kq = ai.extract_draft(_TRUONG, 2026, [nguon], chi_html=True)
        self.assertEqual((tai.call_count, model.call_count), (1, 1))
        ds_diem = kq["du_lieu"]["quy_tac_xet_tuyen"]["diem_chuan"]
        self.assertEqual([(r["ma_xet_tuyen"], r["ma_to_hop"], r["diem_chuan"]) for r in ds_diem],
                         [("IT1", "A00", 27.5)])
        self.assertEqual(kq["ra_soat_diem_chuan"]["can_lam_ro"], [{"nguon_id": 1, **cau_hoi}])
        muc = lap_muc_ban_nhap(kq["du_lieu"], kq["muc"], [nguon], 2026)
        o = next(m for m in muc if m["duong_dan"] == "/quy_tac_xet_tuyen/diem_chuan/0/diem_chuan")
        self.assertTrue(o["dan_chung_ids"])

    def test_ma_bo_diem_chuan_dung_nam_va_url_cua_tung_dong(self):
        khoa = "ma_phuong_thuc_cua_bo"
        nam_cu, nam_moi = 2026, 2027
        urls = {nam: f"https://huce.edu.vn/diem-chuan-{nam}" for nam in (nam_cu, nam_moi)}
        sources = [
            {"id": nam, "url": url, "nam_ap_dung": nam, "chi_diem_lich_su": nam == nam_cu}
            for nam, url in urls.items()
        ]
        tieu_de = {nam: f"Trường Đại học Xây dựng Hà Nội (XDA) công bố điểm chuẩn {nam}" for nam in urls}
        trich_dan = "IT1 xét theo kết quả SAT. Điểm chuẩn 1500 trên thang 1600."
        muc_hoi_cuu = "Mục: Điểm chuẩn trúng tuyển năm 2026"
        docs = {
            url: ai._TaiLieu(url, tieu_de[nam], [(_MUC, tieu_de[nam] + "\n" + trich_dan)], [])
            for nam, url in urls.items()
        }
        docs[urls[2027]].doan.append((muc_hoi_cuu, trich_dan))
        # Năm của điểm, mã đề xuất, năm của URL khai báo, nguồn và mục dẫn chứng, mã được giữ.
        cac_ca = [
            (2026, "415", 2026, 2026, _MUC, "415"),
            (2027, "500", 2027, 2027, _MUC, "500"),
            (2026, "500", 2026, 2026, _MUC, None),
            (2027, "415", 2027, 2027, _MUC, None),
            (2026, "415", 2027, 2026, _MUC, None),
            (2026, "415", 2026, 2027, _MUC, None),
            (None, "415", 2026, 2026, _MUC, None),
            (2026, "415", 2027, 2027, muc_hoi_cuu, "415"),
            (2027, "500", 2027, 2027, muc_hoi_cuu, None),
        ]
        dong, muc = [], []
        for i, (nam, ma, nam_url, nguon_id, vi_tri, _) in enumerate(cac_ca):
            dong.append({"nam_tuyen_sinh": nam, "ma_xet_tuyen": "IT1", "diem_chuan": 1500, "thang_diem": 1600,
                         "nguon_du_lieu_url": urls[nam_url], khoa: ma})
            muc.append({
                "duong_dan": f"/quy_tac_xet_tuyen/diem_chuan/{i}/{khoa}", "phan_loai_ma_bo": "suy_luan",
                "ghi_chu": "Trường dùng điểm SAT để xếp hạng diện này.",
                "dan_chung": [{"nguon_id": nguon_id, "vi_tri": vi_tri, "trich_dan": trich_dan, "gia_tri": ma}],
            })
        data = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {"diem_chuan": dong}},
            "muc": muc,
            "nguon_xac_minh": [{"nguon_id": nam, "dung_truong_co_so": True, "nam_ap_dung": nam,
                                "vi_tri": _MUC, "trich_dan": tieu_de[nam]} for nam in urls],
        }
        # Mã khai là công bố phải xuất hiện trong đoạn dẫn. Bảng hồi cứu có phần dẫn riêng về năm.
        muc[2]["phan_loai_ma_bo"] = "cong_bo"
        for i, (nam, ma, nam_url, nguon_id, vi_tri, _) in enumerate(cac_ca):
            if vi_tri == muc_hoi_cuu:
                muc[i]["dan_chung"][0]["can_cu_nam"] = {
                    "nam_tuyen_sinh": 2026, "vi_tri": muc_hoi_cuu, "trich_dan": trich_dan,
                }
        danh_muc_cu = {2026: [{"ma_phuong_thuc": ma} for ma in ("415", "500")]}
        with (
            patch.object(ai, "_doc_tai_lieu", side_effect=docs.__getitem__),
            patch.object(ai, "_openai", return_value=(data, [])) as openai,
        ):
            ban_nhap = ai.extract_draft(_TRUONG, 2027, sources, danh_muc_lich_su=danh_muc_cu)

        payload = openai.call_args.args[1]
        self.assertEqual(payload["danh_muc_lich_su"], danh_muc_cu)
        self.assertIn("415", payload["bang_ma_bo_2026"])
        de_xuat_dung_danh_muc = ["415", "500", "500", None, "415", "415", None, "415", "500"]
        self.assertEqual([r[khoa] for r in ban_nhap["du_lieu"]["quy_tac_xet_tuyen"]["diem_chuan"]], de_xuat_dung_danh_muc)
        for i, item in enumerate(ban_nhap["muc"]):
            if cac_ca[i][-1] is not None:
                self.assertEqual(item["dan_chung"][0]["phan_loai_ma_bo"], "suy_luan")
                self.assertIn("ly_do_suy_luan_ma_bo", item["dan_chung"][0])
            else:
                self.assertTrue(item["ghi_chu"])
                self.assertFalse(item["dan_chung"])

    def test_huong_dan_ma_bo_2026_chi_ap_dung_cho_dung_nam(self):
        danh_muc_nam_truoc = [{"ma_phuong_thuc": "101", "ten_phuong_thuc": "Phương thức năm trước"}]
        with patch.object(ai, "_openai", return_value=({}, [])) as openai:
            ai._trich_xuat_nhom(_TRUONG, 2026, [], None)
            ai._trich_xuat_nhom(_TRUONG, 2025, [], None, danh_muc_phuong_thuc=danh_muc_nam_truoc)

        huong_dan, du_lieu, _ = openai.call_args_list[0].args
        self.assertEqual(
            set(du_lieu["bang_ma_bo_2026"]),
            set("100 200 301 401 402 403 404 405 406 407 409 410 411 413 414 415 416 417 500".split()),
        )
        for noi_dung in ("phan_loai_ma_bo", "suy_luan", "1.1, 1.2, 1.3", "TO_HOP_MON", "PT100"):
            self.assertIn(noi_dung, huong_dan)
        du_lieu_nam_truoc = openai.call_args_list[1].args[1]
        self.assertNotIn("bang_ma_bo_2026", du_lieu_nam_truoc)
        self.assertEqual(du_lieu_nam_truoc["danh_muc_phuong_thuc"], danh_muc_nam_truoc)

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
            self.assertIsNone(request.extensions["timeout"]["read"])
            self.assertEqual(request.extensions["timeout"]["connect"], 10)
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
            patch.object(ai.settings, "openai_model", "model-cau-hinh"),
            patch.object(ai.settings, "openai_api_key", "key-gia"),
            patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(tra_loi), **kw)),
        ):
            data = ai._trich_xuat_nhom(_TRUONG, 2026, [], None)

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

    def test_tim_nguon_giu_trang_web_va_tam_bo_pdf(self):
        drive = "https://drive.google.com/file/d/ma_file/view"
        trang_lien_ket = "https://tuyensinh.example.com/thong-tin-tuyen-sinh"
        bai_bao = "https://bao.example.com/tin-tuyen-sinh"
        pdf = f"{_URL}/PHU-LUC.PDF?nam=2026"
        tai_pdf = f"{_URL}/tai-tep?id=42"
        data = {
            "nguon": [
                _thong_tin(),
                _thong_tin(trang_lien_ket, url_trang_cong_bo=_URL, loai="thong_bao"),
                _thong_tin(drive, url_trang_cong_bo=_URL, loai="phu_luc"),
                _thong_tin(pdf, loai="phu_luc"),
                _thong_tin(tai_pdf, loai="phu_luc", dinh_dang="pdf"),
                _thong_tin("https://tuyensinh.huce.edu.vn/khong-co-trong-ket-qua"),
                _thong_tin(bai_bao),
            ],
        }
        output = [
            {
                "type": "web_search_call",
                "action": {
                    "sources": [{"url": url} for url in (_URL, drive, pdf, tai_pdf, bai_bao)],
                },
            }
        ]
        tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, _XAC_MINH)], [drive, trang_lien_ket])
        with (
            patch.object(ai, "_openai", return_value=(data, output)),
            patch.object(ai, "_doc_tai_lieu", return_value=tai_lieu),
        ):
            nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)
        theo_url = {n["url"]: n for n in nguon}
        self.assertEqual(set(theo_url), {_URL, trang_lien_ket, bai_bao})
        self.assertTrue(theo_url[_URL]["phu_hop"])
        self.assertTrue(theo_url[trang_lien_ket]["phu_hop"])
        self.assertFalse(theo_url[bai_bao]["phu_hop"])
        self.assertEqual(theo_url[trang_lien_ket]["url_trang_cong_bo"], _URL)
        self.assertTrue(any("khong-co-trong-ket-qua" in note for note in ghi_chu))

    def test_ai_tu_dat_huong_tim_tu_web_va_hop_dong_cua_truong(self):
        huong = ["Quy định ban nghệ thuật biển của phân hiệu X", "Danh mục học bổng riêng kỳ mùa thu"]
        khoa = {huong[0]: _URL + "/bien", huong[1]: _URL + "/thu"}

        def tra_loi(_chi_dan, payload, _gioi_han, *, tim_kiem):
            self.assertTrue(tim_kiem)
            if "hop_dong_cms" in payload:
                self.assertIn("/quy_tac_xet_tuyen/cong_thuc", payload["hop_dong_cms"])
                url = _URL
                data = {"nguon": [_thong_tin(url)], "huong_tim_tiep": huong}
            else:
                self.assertIn(_URL, payload["url_da_co"])
                url = khoa[payload["noi_dung_can_tim"]]
                data = {"nguon": [_thong_tin(url)]}
            return data, [{"type": "web_search_call", "action": {"sources": [{"url": url}]}}]

        with patch.object(ai, "_openai", side_effect=tra_loi) as model:
            nguon, _ = ai.search_sources(_TRUONG, 2026)
        self.assertEqual(model.call_count, 3)
        self.assertCountEqual([n["url"] for n in nguon], [_URL, *khoa.values()])

    def test_ai_co_the_dung_tim_va_giu_nguon_da_xac_minh_khi_huong_sau_loi(self):
        output = [{"type": "web_search_call", "action": {"sources": [{"url": _URL}]}}]
        for huong in ([], ["Tài liệu bổ sung riêng của khoa"]):
            with self.subTest(huong=huong), patch.object(ai, "_openai", side_effect=[
                ({"nguon": [_thong_tin()], "huong_tim_tiep": huong}, output), ai.AdmissionAIError("Hết thời gian"),
            ]) as model:
                nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)
                self.assertEqual(model.call_count, 1 + len(huong))
                self.assertEqual([n["url"] for n in nguon], [_URL])
                self.assertEqual(bool(ghi_chu), bool(huong))

    def test_tim_bo_sung_dung_khoang_trong_va_chi_tra_trang_html_moi_dung_pham_vi(self):
        gaps = ["IT1 thiếu tổ hợp", "Học phí chương trình IT2", "Tỷ lệ việc làm"]
        cu, moi, sai_nam, lich_su, pdf = _URL, f"{_URL}/viec-lam", f"{_URL}/2024", f"{_URL}/diem-2024", _URL_SUA
        data = {"nguon": [
            _thong_tin(cu), _thong_tin(moi), _thong_tin(sai_nam, nam_ap_dung=2024),
            _thong_tin(lich_su, nam_ap_dung=2024, loai="diem_lich_su"), _thong_tin(pdf),
        ]}
        output = [{"type": "web_search_call", "action": {"sources": [{"url": n["url"]} for n in data["nguon"]]}}]
        with patch.object(ai, "_openai", return_value=(data, output)) as model:
            self.assertEqual(ai.search_missing_sources(_TRUONG, 2026, [], [cu]), ([], []))
            model.assert_not_called()
            rows, _ = ai.search_missing_sources(_TRUONG, 2026, gaps, [cu + "?utm_source=test"])
        self.assertCountEqual([row["url"] for row in rows], [moi, lich_su])
        self.assertEqual(model.call_count, 1)
        inputs = [call.args[1] for call in model.call_args_list]
        for gap in gaps:
            self.assertTrue(any(gap in arg["noi_dung_can_tim"] for arg in inputs))
        self.assertTrue(all(cu in arg["url_da_co"] for arg in inputs))

    def test_tim_nguon_bo_tham_so_theo_doi_khi_so_sanh_url(self):
        url = f"{_URL}?bai=42"
        url_khac = f"{_URL}?bai=43"
        data = {"nguon": [_thong_tin(url), _thong_tin(f"{url}&utm_campaign=trung#hoc-phi"), _thong_tin(url_khac)]}
        output = [{
            "type": "web_search_call",
            "action": {"sources": [{"url": f"{url}&utm_source=tim-kiem"}, {"url": url_khac}]},
        }]

        with patch.object(ai, "_openai", return_value=(data, output)):
            nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)

        self.assertCountEqual([n["url"] for n in nguon], [url, url_khac])
        self.assertEqual(ghi_chu, [])

    def test_tim_nguon_giu_day_du_ket_qua_sau_khi_xac_minh_va_loai_trung(self):
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

        with patch.object(ai, "_openai", return_value=(data, output)):
            nguon, _ = ai.search_sources(_TRUONG, 2026)

        self.assertCountEqual([n["url"] for n in nguon], urls)

    def test_trung_url_uu_tien_nguon_hop_le_va_giu_phan_loai_ai_khi_cung_pham_vi(self):
        nguon_kem_uu_tien = (
            _thong_tin(f"{_URL}#diem-chuan", loai="diem_lich_su", nam_ap_dung=2025),
            _thong_tin(f"{_URL}#thong-tin-tom-tat", chinh_thuc=False),
            _thong_tin(f"{_URL}#phu-luc", loai="phu_luc"),
        )
        de_an = _thong_tin(f"{_URL}#de-an", tieu_de="Đề án chính thức năm 2026")
        trang_phu_luc = f"{_URL}/phu-luc"
        output = [{"type": "web_search_call", "action": {"sources": [{"url": _URL}, {"url": trang_phu_luc}]}}]

        for nguon_dau in nguon_kem_uu_tien:
            data = {"nguon": [nguon_dau, _thong_tin(trang_phu_luc, loai="phu_luc"), de_an, nguon_kem_uu_tien[0]]}
            with (
                self.subTest(nguon_dau=nguon_dau["url"]),
                patch.object(ai, "_openai", return_value=(data, output)),
            ):
                nguon, ghi_chu = ai.search_sources(_TRUONG, 2026)
                self.assertEqual(len(nguon), 2)
                ket_luan_ai = nguon_dau if nguon_dau["loai"] == "phu_luc" else de_an
                self.assertEqual(nguon[0]["tieu_de"], ket_luan_ai["tieu_de"])
                self.assertEqual(nguon[0]["loai"], ket_luan_ai["loai"])
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

        def trich_xuat(_huong_dan, payload, _so_token, **_tuy_chon):
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

        def trich_xuat(_huong_dan, payload, _so_token, **_tuy_chon):
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


    def test_gop_nhieu_nhom_giu_chuong_trinh_cung_ma_khac_ten_hoac_co_so(self):
        def nhom(ten_chuong_trinh, co_so_id=None, ma_co_so=None, **them):
            chuong_trinh = {"ma_xet_tuyen": "101A", "ten_chuong_trinh": ten_chuong_trinh, **them}
            return {
                "du_lieu": {
                    "thong_tin_import": {},
                    "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [{**chuong_trinh, "co_so_id": co_so_id}]},
                    "quy_tac_xet_tuyen": {"chuong_trinh": [{**chuong_trinh, "ma_co_so": ma_co_so}]},
                },
                "muc": [{"duong_dan": "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/ten_chuong_trinh"}],
            }

        du_lieu, muc, _ = ai._gop_ket_qua([
            nhom("Công nghệ thông tin", 1, "HN"),
            nhom("Công nghệ thông tin", 2, "DN"),
            nhom("Khoa học máy tính", 2, "DN"),
            nhom("Khoa học máy tính", ma_nganh="7480101"),
        ], [])

        chuong_trinh = du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
        self.assertEqual([(ct["ten_chuong_trinh"], ct["co_so_id"]) for ct in chuong_trinh], [
            ("Công nghệ thông tin", 1), ("Công nghệ thông tin", 2), ("Khoa học máy tính", 2),
        ])
        quy_tac = du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"]
        self.assertEqual([(ct["ten_chuong_trinh"], ct["ma_co_so"]) for ct in quy_tac], [
            ("Công nghệ thông tin", "HN"), ("Công nghệ thông tin", "DN"), ("Khoa học máy tính", "DN"),
        ])
        self.assertEqual(chuong_trinh[2]["ma_nganh"], "7480101")
        self.assertEqual(quy_tac[2]["ma_nganh"], "7480101")
        self.assertEqual([m["duong_dan"].split("/")[-2] for m in muc], ["0", "1", "2", "2"])

    def test_gop_nguon_bo_sung_giu_lien_ket_khi_id_co_so_cuc_bo_trung(self):
        path = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/co_so_id"

        def phan(ten, ma):
            return {
                "du_lieu": {
                    "thong_tin_import": {}, "quy_tac_xet_tuyen": {},
                    "dats_tuyen_sinh": {
                        "dats_tru_so": [{"ten_co_so": ten, "id": ma}],
                        "dats_chuong_trinh_dao_tao": [{"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "CNTT", "co_so_id": ma}],
                        "dats_co_so_vat_chat": [{"ten_hang_muc": "Phòng máy", "co_so_id": ma}],
                    },
                },
                "muc": [{"duong_dan": path, "dan_chung": [{"gia_tri": ma, "trich_dan": ten}]}],
            }

        them = phan("Phân hiệu B", 1)
        du_lieu, muc, _ = ai._gop_ket_qua([phan("Trụ sở A", 1), them, phan("Phân hiệu B", 4)], [])
        dats = du_lieu["dats_tuyen_sinh"]
        self.assertEqual([row["id"] for row in dats["dats_tru_so"]], [1, 2])
        self.assertEqual([row["co_so_id"] for row in dats["dats_chuong_trinh_dao_tao"]], [1, 2])
        self.assertEqual([row["co_so_id"] for row in dats["dats_co_so_vat_chat"]], [1, 2])
        self.assertEqual([item["dan_chung"][0]["gia_tri"] for item in muc], [1, 2, 2])
        self.assertEqual(muc[1]["duong_dan"], path.replace("/0/", "/1/"))
        self.assertEqual(them["muc"][0]["dan_chung"][0]["gia_tri"], 1)

    def test_gop_nhieu_nhom_giu_cong_thuc_khac_nhau_cua_cung_phuong_thuc(self):
        def nhom(ma_cong_thuc, ma_phuong_thuc, to_hop):
            de_an = {
                "ma_xet_tuyen": "IT1",
                "dats_phuong_thuc": [{
                    "ma_phuong_thuc_cua_truong": ma_phuong_thuc,
                    "cong_thuc_tinh_diem": ma_cong_thuc,
                    "to_hop_mon_hoc": to_hop,
                }],
            }
            quy_tac = {
                "ma_xet_tuyen": "IT1",
                "phuong_an": [{
                    "ma_phuong_thuc_cua_truong": ma_phuong_thuc,
                    "ma_cong_thuc": ma_cong_thuc,
                    "to_hop": to_hop,
                }],
            }
            return {
                "du_lieu": {
                    "thong_tin_import": {},
                    "dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [de_an]},
                    "quy_tac_xet_tuyen": {"chuong_trinh": [quy_tac]},
                },
                "muc": [],
            }

        du_lieu, _, _ = ai._gop_ket_qua([
            nhom("THPT_30", "PT1", ["A00"]),
            nhom("THPT_40", "PT1", []),
            nhom("THPT_40", None, ["D01"]),
        ], [])

        phuong_thuc = du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"][0]["dats_phuong_thuc"]
        self.assertEqual([(pt["cong_thuc_tinh_diem"], pt["to_hop_mon_hoc"]) for pt in phuong_thuc],
                         [("THPT_30", ["A00"]), ("THPT_40", ["D01"])])
        phuong_an = du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"]
        self.assertEqual([(pa["ma_cong_thuc"], pa["to_hop"]) for pa in phuong_an],
                         [("THPT_30", ["A00"]), ("THPT_40", ["D01"])])

    def test_trich_xuat_chia_nhom_lai_khi_model_bao_het_ngu_canh(self):
        sources = [{"id": 1, "url": _URL}, {"id": 2, "url": _URL_SUA}]
        tai_lieu = ai._TaiLieu(_URL, "", [(_MUC, _XAC_MINH)], [])
        danh_muc = [
            {"ma_phuong_thuc": "401", "ten_phuong_thuc": "Dùng bài thi đánh giá tư duy do trường tổ chức"},
            {"ma_phuong_thuc": "402", "ten_phuong_thuc": "Dùng bài thi đánh giá tư duy do đơn vị khác tổ chức"},
        ]

        def trich_xuat(huong_dan, payload, _so_token, **_tuy_chon):
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
        trich_dan = [
            f"Diện {dien}: Mã phương thức của Bộ GD&ĐT: {ma_bo}"
            for dien, ma_bo in cac_dien if ma_bo is not None
        ]
        tai_lieu = ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, _XAC_MINH + "\n" + "\n".join(trich_dan))], [])
        muc_da_ro = [
            {
                "duong_dan": f"{duong_dan}/{vi_tri}/ma_phuong_thuc_cua_bo",
                "phan_loai_ma_bo": "cong_bo",
                "dan_chung": [{"nguon_id": 1, "vi_tri": _MUC, "trich_dan": noi_dung, "gia_tri": "401"}],
            }
            for duong_dan in ("/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_phuong_thuc", "/quy_tac_xet_tuyen/cong_thuc")
            for vi_tri, noi_dung in enumerate(trich_dan)
        ]
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
            "muc": [*muc_da_ro, *[
                {"duong_dan": p, "dan_chung": [], "ghi_chu": ly_do} for p in sorted(muc_chua_ro)
            ]],
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

    def test_ma_bo_suy_luan_can_can_cu_va_quan_tri_xac_nhan(self):
        khoa = "ma_phuong_thuc_cua_bo"
        duong_dan = f"/quy_tac_xet_tuyen/cong_thuc/0/{khoa}"
        trich_dan = "Diện TSA xét kết quả kỳ thi đánh giá tư duy do chính trường tổ chức."
        ly_do = "Điểm kỳ thi do trường tổ chức là căn cứ độc lập để xét nên thuộc nhóm 401."
        nguon = {"id": 1, "url": _URL, "chinh_thuc": True, "phu_hop": True, "nam_ap_dung": 2026, "lua_chon": "su_dung"}
        tai_lieu = {1: ai._TaiLieu(_URL, "Đề án 2026", [(_MUC, trich_dan)], [])}
        for phan_loai, ghi_chu, cau_trich, ma, mong_doi in (
            ("suy_luan", ly_do, trich_dan, "401", "401"),
            ("cong_bo", ly_do, trich_dan, "401", None),
            ("suy_luan", None, trich_dan, "401", None),
            ("suy_luan", ly_do, "Không có đoạn này trong nguồn.", "401", None),
            ("suy_luan", ly_do, trich_dan, "PT401", None),
        ):
            with self.subTest(phan_loai=phan_loai, ghi_chu=ghi_chu, cau_trich=cau_trich, ma=ma):
                du_lieu = {"quy_tac_xet_tuyen": {"cong_thuc": [{khoa: ma}]}}
                data = {
                    "du_lieu": du_lieu,
                    "muc": [{
                        "duong_dan": duong_dan,
                        "phan_loai_ma_bo": phan_loai,
                        "ghi_chu": ghi_chu,
                        "dan_chung": [{"nguon_id": 1, "vi_tri": _MUC, "trich_dan": cau_trich, "gia_tri": ma}],
                    }],
                }

                ai._chuan_hoa_ma_phuong_thuc(data, 2026, {2026: {"401"}}, tai_lieu, {})
                muc_ai = ai._chuan_hoa_dan_chung(data["muc"], tai_lieu, [])
                muc = lap_muc_ban_nhap(du_lieu, muc_ai, [nguon], 2026)
                self.assertEqual(du_lieu["quy_tac_xet_tuyen"]["cong_thuc"][0][khoa], "401" if ma == "401" else None)
                self.assertFalse(muc[0]["dan_chung_ids"])
                if mong_doi is None:
                    self.assertTrue(muc[0]["ghi_chu"])
                    continue

                self.assertIn("Mã Bộ suy luận (401).", muc[0]["ghi_chu"])
                self.assertIn(ly_do, muc[0]["ghi_chu"])
                self.assertEqual(muc[0]["dan_chung"][0]["trich_dan"], trich_dan)
                self.assertTrue(any(loi.startswith(duong_dan) for loi in canh_bao_dan_chung(du_lieu, muc)))
                da_xac_nhan, muc_da_xac_nhan, _ = sua_muc_ban_nhap(du_lieu, muc, [
                    SuaMucBanNhap(duong_dan=duong_dan, dan_chung_ids=["1"], ghi_chu=ly_do, da_kiem_tra=True),
                ], [nguon])
                self.assertFalse(
                    any(loi.startswith(duong_dan) for loi in canh_bao_dan_chung(da_xac_nhan, muc_da_xac_nhan))
                )

    def test_ban_nhap_giu_ket_luan_ai_ve_ma_500_va_gia_tri_chua_ro(self):
        danh_muc = [{"ma_phuong_thuc": "500", "ten_phuong_thuc": "Phương thức khác"}]
        khoa = "ma_phuong_thuc_cua_bo"
        muc_phuong_thuc = f"/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_phuong_thuc/0/{khoa}"
        muc_cong_thuc = f"/quy_tac_xet_tuyen/cong_thuc/0/{khoa}"
        truong_hop = [
            ({khoa: "500"}, "Mã phương thức của Bộ GD&ĐT: 500", "500"),
            ({khoa: "500"}, "Mã tham chiếu cổng đăng ký chung: 500", "500"),
            ({khoa: None}, "Mã phương thức: 500 (mã riêng của trường).", None),
            ({khoa: None}, "500 - Phương thức khác (mã nội bộ).", None),
            ({khoa: None}, "500 chỉ tiêu", None),
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
                        {"duong_dan": duong_dan, "phan_loai_ma_bo": "cong_bo" if bo.get(khoa) else None,
                         "ghi_chu": None if bo.get(khoa) else "AI chưa xác định được mã Bộ từ nguồn này.", "dan_chung": [{
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
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {"chi_tieu": 80}, "quy_tac_xet_tuyen": {}},
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
            patch.object(ai, "_openai", side_effect=[
                (data, []),
                ({"ket_luan": [{"duong_dan": _PATH, "gia_tri": 95, "dan_chung_ids": [2],
                                "ly_do": "Thông báo điều chỉnh chỉ tiêu của kỳ tuyển sinh này."}]}, []),
            ]) as openai,
        ):
            ket_qua = ai.extract_draft(_TRUONG, 2026, sources)
        self.assertEqual({call.args[0] for call in tai.call_args_list}, {_URL, _URL_SUA})
        self.assertFalse(openai.call_args.kwargs.get("tim_kiem", False))
        self.assertEqual({s["url"] for s in openai.call_args_list[0].args[1]["nguon_da_chon"]}, {_URL, _URL_SUA})
        self.assertEqual(openai.call_args.args[1]["cac_muc"][0]["duong_dan"], _PATH)
        self.assertEqual(ket_qua["du_lieu"]["dats_tuyen_sinh"]["chi_tieu"], 95)
        self.assertEqual(ket_qua["muc"][0]["phan_tich_mau_thuan_ai"]["dan_chung_ids"], [2])
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

        def tra_loi_chon_doan(_, payload, __, **_tuy_chon):
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

    def test_doi_chieu_chuong_trinh_giu_cach_doc_pham_vi_va_don_vi_cua_ai(self):
        url = "https://tuyensinh.huce.edu.vn/du-kien-cap-nhat"
        noi_dung = "Theo quyết định chính thức, cả khóa mở hai hướng.\nIT10 | Tin học"
        doc = ai._TaiLieu(url, "Phụ lục điều chỉnh", [(_MUC, noi_dung)], [])
        source = dict(_thong_tin(url), id=10, phu_hop=True, loai="dieu_chinh")
        tong = {"nguon_id": 10, "vi_tri": _MUC, "trich_dan": noi_dung.splitlines()[0], "cac_ma": [],
                "tong_cong_bo": 2, "don_vi_tong": "chương trình", "pham_vi": "toan_truong"}
        dong = {**tong, "trich_dan": "IT10 | Tin học", "cac_ma": ["IT1", "IT10"], "tong_cong_bo": None,
                "pham_vi": "phan_pham_vi"}
        ds = ai._doi_chieu_chuong_trinh([tong, dong, {**tong, "trich_dan": "không có trong tài liệu"}],
                                        [source], {10: doc}, 2026)
        self.assertEqual([(d["cac_ma"], d["tong_cong_bo"], d["pham_vi"]) for d in ds],
                         [([], 2, "toan_truong"), (["IT10"], None, "phan_pham_vi")])
        self.assertEqual(ds[0]["don_vi_tong"], "chương trình")

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

    def test_bo_sung_dan_chung_qua_160_muc_va_tiep_tuc_sau_lo_loi(self):
        cau = "Các công thức trong bảng đều dùng thang điểm 30."
        doc = ai._TaiLieu(_URL, "Thông tin tuyển sinh", [(_MUC, cau)], [])
        cong_thuc = [{"thang_diem": 30} for _ in range(205)]
        du_lieu = {"quy_tac_xet_tuyen": {"cong_thuc": cong_thuc}}
        cac_lo, tien_do, ghi_chu = [], [], []
        def path(i):
            return f"/quy_tac_xet_tuyen/cong_thuc/{i}/thang_diem"

        def xu_ly(_prompt, data, _tokens):
            lo = data["gia_tri_can_kiem"]
            cac_lo.append(list(lo))
            if len(cac_lo) == 1:
                raise ai._LoiDungLuongModel("Phản hồi dài.")
            if path(70) in lo:
                raise ai.AdmissionAIError("Dịch vụ tạm thời gián đoạn.")
            return {"dan_chung": [{"duong_dan": p, "nguon_id": 1, "vi_tri": _MUC, "trich_dan": cau} for p in lo]}, []

        da_co = [{"duong_dan": path(13), "dan_chung": [{"nguon_id": 1, "gia_tri": 30}]}]
        with patch.object(ai, "_openai", side_effect=xu_ly):
            muc = ai._bo_sung_dan_chung_cong_thuc(du_lieu, da_co, {1: doc}, ghi_chu, lambda *p: tien_do.append(p))
        self.assertEqual(set(cac_lo[0]), set(cac_lo[1]) | set(cac_lo[2]))
        self.assertFalse(set(cac_lo[1]) & set(cac_lo[2]))
        self.assertEqual(set().union(*cac_lo), {path(i) for i in range(205)} - {path(13)})
        loi = next(lo for lo in cac_lo if path(70) in lo)
        self.assertEqual({m["duong_dan"] for m in muc if m["dan_chung"]}, {path(i) for i in range(205)} - {path(13), *loi})
        self.assertTrue(any("tạm thời gián đoạn" in g for g in ghi_chu))
        self.assertEqual(tien_do[-1], ("doi_chieu_cong_thuc", 204, 204))

    def test_dung_doi_chieu_cong_thuc_truoc_khi_goi_lo_ke_tiep(self):
        cong_thuc = [{"thang_diem": 30} for _ in range(90)]
        doc = ai._TaiLieu(_URL, "Thông tin tuyển sinh", [(_MUC, "Điểm theo thang điểm 30.")], [])
        def dung(_buoc, da_xu_ly, _tong):
            if da_xu_ly:
                raise RuntimeError("Đã dừng lượt thu thập")
        with patch.object(ai, "_openai", return_value=({"dan_chung": []}, [])) as model:
            with self.assertRaisesRegex(RuntimeError, "Đã dừng"):
                ai._bo_sung_dan_chung_cong_thuc({"quy_tac_xet_tuyen": {"cong_thuc": cong_thuc}}, [], {1: doc}, [], dung)
        self.assertEqual(model.call_count, 1)

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

    def test_luot_tu_dong_chan_pdf_qua_url_chuyen_huong_mime_va_noi_dung(self):
        client = httpx.Client
        redirect = httpx.Response(302, headers={"location": _URL_SUA})
        pdf = b"%PDF-1.7 test"
        for response in (
            redirect,
            httpx.Response(200, headers={"content-type": "application/pdf; charset=binary"}),
            httpx.Response(200, headers={"content-type": "application/octet-stream"}, stream=httpx.ByteStream(pdf)),
        ):
            with (
                self.subTest(status=response.status_code, mime=response.headers.get("content-type")),
                patch.object(ai, "_dia_chi_cong_khai", return_value=["9.9.9.9"]) as dns,
                patch.object(ai.httpx, "Client", lambda **kw: client(transport=httpx.MockTransport(lambda _: response), **kw)),
                patch.object(ai, "_doc_pdf") as doc_pdf,
                self.assertRaisesRegex(ai.AdmissionAIError, "Tạm bỏ PDF"),
            ):
                ai._doc_tai_lieu(_URL, chi_html=True)
            self.assertEqual(dns.call_count, 1)
            doc_pdf.assert_not_called()

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

    def test_ai_xem_duoc_ngu_canh_lien_ket_khong_nhan_o_cuoi_trang_dai(self):
        raw = ("<title>Đề án</title><p>Tài liệu công bố theo từng diện.</p>"
               + "".join(f'<a href="/tl/{i}">Xem</a>' for i in range(83))
               + '<p>Biểu điểm theo từng mã</p><a href="/bo-sung"></a>')
        with patch.object(ai, "_tai_tai_lieu", return_value=(httpx.URL(_URL), raw.encode(), "text/html")):
            trang = ai._doc_tai_lieu(_URL)
        phu_luc = ai._TaiLieu("https://tuyensinh.huce.edu.vn/bo-sung", "Biểu điểm", [], [])

        def chon(prompt, du_lieu, ngan_sach):
            muc = du_lieu["tai_nguyen"]
            for u in muc:
                if u["url"].endswith("/bo-sung"):
                    self.assertEqual(u["nhan"], "")
                    self.assertIn("Biểu điểm theo từng mã", u["ngu_canh"])
                    return {"ids": [u["id"]]}, []
            return {"ids": [muc[0]["id"]]}, []

        with (patch.object(ai, "_openai", side_effect=chon) as mo_hinh,
              patch.object(ai, "_doc_tai_lieu", return_value=phu_luc) as tai):
            ket_qua, _ = ai._doc_phu_luc({"chinh_thuc": True, "phu_hop": True}, trang, toi_da=1)
        self.assertEqual(mo_hinh.call_count, 3)
        tai.assert_called_once_with(phu_luc.url, chi_html=True)
        self.assertEqual(ket_qua[0].url_goc, phu_luc.url)

    def test_doc_phu_luc_chi_doc_html_va_bo_qua_pdf_drive(self):
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
                ("/phu-luc1", "Quyển xanh"),
                ("/phu-luc2.pdf", "Phụ lục 2: Bảng quy đổi"),
                (drive, "Phụ lục 2: Bảng quy đổi điểm"),
                (drive_download, "Phụ lục 2: Bảng quy đổi"),
            ],
        )
        trang = "https://tuyensinh.huce.edu.vn/phu-luc1"
        doc = ai._TaiLieu(trang, "", [("Quy đổi", "IELTS 6.5: 9.5 điểm")], [])
        da_doc = set()
        with (patch.object(ai, "_doc_tai_lieu", return_value=doc) as doc_file,
              patch.object(ai, "_openai", return_value=({"ids": [2]}, [])) as chon):
            ket_qua, ghi_chu = ai._doc_phu_luc(
                {"chinh_thuc": True, "phu_hop": True},
                tai_lieu,
                toi_da=1,
                bo_qua=da_doc,
            )
        self.assertEqual([r["nhan"] for r in chon.call_args.args[1]["tai_nguyen"]], ["Xem thêm", "Quyển xanh"])
        doc_file.assert_called_once_with(trang, chi_html=True)
        self.assertEqual(len(ket_qua), 1)
        self.assertEqual(ket_qua[0].url_goc, trang)
        self.assertTrue(ket_qua[0].tai_lieu.doi_chieu("Quy đổi", "IELTS 6.5: 9.5 điểm"))
        self.assertEqual(da_doc, {trang})
        self.assertEqual(ghi_chu, [])

    def test_doc_phu_luc_bao_loi_tai_va_chuyen_huong_khac_ten_mien(self):
        tai_lieu = ai._TaiLieu(
            _URL,
            "Đề án 2026",
            [(_MUC, _XAC_MINH)],
            [],
            lien_ket_co_nhan=[("/phu-luc1", "Phụ lục 1"), ("/phu-luc2", "Phụ lục 2")],
        )

        def tai(url, *, chi_html):
            self.assertTrue(chi_html)
            if url.endswith("phu-luc1"):
                raise ai.AdmissionAIError("Không tải được.")
            return ai._TaiLieu("https://tam.example.com/phu-luc.pdf", "", [("Trang PDF 2", "Sai nguồn")], [])

        with (patch.object(ai, "_doc_tai_lieu", side_effect=tai) as doc_file,
              patch.object(ai, "_openai", return_value=({"ids": [1, 2]}, []))):
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
