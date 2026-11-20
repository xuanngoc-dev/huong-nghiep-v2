import asyncio
import json
import unittest
from unittest.mock import patch

import httpx

from app.core.config import settings
from app.schemas.chat import HoiChatRequest, HoSoChat, KeHoachTraCuu, ModelChat, NguCanhChat, TinNhan
from app.services import chat_stream, tra_cuu_tuyen_sinh as lookup
from test_chat import CorpusFixture, program


def scored(name, score, scale=30, method="100"):
    record = program(name, score)
    record["phuong_thuc_tuyen_sinh"][0].update(thang_diem=scale, ma_phuong_thuc=method)
    return record


class DynamicLookupTests(CorpusFixture, unittest.TestCase):
    def setUp(self):
        self.setup_corpus()
        self.write("alpha.json", "AAA", "Đại học Alpha Hà Nội", [
            scored("Thấp", 22), scored("Gần", 27.8), scored("Cao", 29.5),
            scored("Khác thang", 28, scale=40), scored("Học bạ", 28, method="200")])

    def plan(self, **changes):
        return KeHoachTraCuu(ma_truong=["AAA"], to_hop=["A00"], phuong_thuc=["100"], thang_diem=30,
                            diem_muc_tieu=28, sap_xep="gan_diem", **changes)

    def records(self, result):
        return sorted([r for s in json.loads(result.context)["ket_qua"] for r in s["chuong_trinh"]],
                      key=lambda r: r["thu_tu_tra_cuu"])

    def test_target_score_shows_only_cutoffs_within_the_configured_margin(self):
        # Khoảng điểm đặt rõ trong test, không phụ thuộc CHAT_SCORE_MARGIN của máy chạy test.
        with patch.object(settings, "chat_score_margin", 1.0):
            rows = self.records(lookup.search("Tư vấn", plan=self.plan()))
        # 28 ± 1: chỉ "Gần" (27.8); "Cao" (29.5) và "Thấp" (22) nằm ngoài khoảng.
        self.assertEqual([r["ten_nganh"] for r in rows], ["Gần"])
        self.assertEqual(rows[0]["phuong_thuc_tom_tat"][0][3], 27.8)
        with patch.object(settings, "chat_score_margin", 2.0):
            rows = self.records(lookup.search("Tư vấn", plan=self.plan()))
        # 28 ± 2: thêm "Cao" (29.5), gần mục tiêu hơn thì đứng trước.
        self.assertEqual([r["ten_nganh"] for r in rows], ["Gần", "Cao"])

    def test_filters_follow_the_plan_instead_of_a_default_score_window(self):
        result = lookup.search("Ưu tiên chắc chắn", plan=self.plan(diem_tu=20, diem_den=25))
        self.assertEqual([r["ten_nganh"] for r in self.records(result)], ["Thấp"])

    def test_combination_cutoff_overrides_method_cutoff_and_floor_is_not_cutoff(self):
        record = scored("Theo tổ hợp", 29)
        record["phuong_thuc_tuyen_sinh"][0]["to_hop_mon"] = [
            {"ma_to_hap": "A00", "diem_chuan": 22}, {"ma_to_hap": "A01", "diem_chuan": 28}]
        floor_only = scored("Chỉ có sàn", None)
        floor_only["phuong_thuc_tuyen_sinh"][0]["diem_san"] = 28
        self.write("alpha.json", "AAA", "Alpha", [record, floor_only])
        self.assertFalse(lookup.search("A00", plan=self.plan(diem_tu=27)).context)

    def test_overview_retains_scores_when_the_followup_asks_for_best_major(self):
        scope = NguCanhChat(diem=28, to_hop=["A00"], khu_vuc="miền Bắc", tom_tat="Thích lập trình")
        result = lookup.search("ngành nào tốt nhất", plan=self.plan(ngu_canh=scope))
        self.assertEqual(result.scope, scope)
        self.assertTrue(all(r["phuong_thuc_tom_tat"][0][3] is not None for r in self.records(result)))

    def test_unselected_notes_do_not_consume_the_context_or_leave_unused_sources(self):
        huge = scored("Quá dài", 28)
        huge["phuong_thuc_tuyen_sinh"][0]["ghi_chu"] = "Nội dung điều kiện dài " * 1000
        self.write("alpha.json", "AAA", "Alpha", [huge, scored("Gọn", 27)])
        with patch.object(settings, "chat_detail_context_max_chars", 4000):
            result = lookup.search("Chi tiết", plan=self.plan(che_do="chi_tiet"))
        self.assertLessEqual(len(result.context), 4000)
        data = json.loads(result.context)
        self.assertEqual(data["so_chuong_trinh_gui"], 1)
        self.assertEqual(data["ket_qua"][0]["chuong_trinh"][0]["ten_nganh"], "Gọn")
        self.assertEqual(data["chu_thich"], {})
        self.assertEqual(len(result.sources), 1)

    def test_planning_keeps_uploaded_prose_searchable(self):
        (self.root / "guide.txt").write_text("Thông tin học bổng dành cho vận động viên thể thao.", encoding="utf-8")
        result = lookup.search("học bổng vận động viên", plan=KeHoachTraCuu(khong_can_tra_cuu=True))
        self.assertEqual(result.files, ["guide.txt"])

    def test_international_certificate_and_sat_matching(self):
        cert_method = {
            "ma_phuong_thuc": "415",
            "ten_phuong_thuc": "Xét tuyển tài năng theo chứng chỉ quốc tế SAT/ACT/A-Level/AP/IB",
            "loai_phuong_thuc": "ChungChiQuocTe",
            "diem_chuan": 85.0,
            "thang_diem": 100,
            "cong_thuc_tinh_diem": {"SAT": "(SAT+thuong)/16", "ACT": "(ACT+thuong)/36"},
            "dieu_kien_phu": [
                {"loai": "CHUNG_CHI_QUOC_TE", "gia_tri": ["SAT", "ACT", "A-Level", "AP", "IB"]}
            ]
        }
        prog = program("Khoa học Máy tính", score=85)
        prog["phuong_thuc_tuyen_sinh"] = [cert_method]
        self.write("alpha.json", "AAA", "Đại học Alpha Hà Nội", [prog])

        # Match by SAT
        sat_result = lookup.search("SAT", plan=KeHoachTraCuu(ma_truong=["AAA"], phuong_thuc=["SAT"]))
        self.assertTrue(sat_result.context)
        sat_data = json.loads(sat_result.context)
        self.assertEqual(sat_data["tong_chuong_trinh"], 1)
        self.assertIn("cong_thuc_tinh_diem", sat_data["ket_qua"][0]["chuong_trinh"][0]["phuong_thuc_tuyen_sinh"][0])

        # Match by Vietnamese method name
        vn_result = lookup.search("Chứng chỉ quốc tế", plan=KeHoachTraCuu(ma_truong=["AAA"], phuong_thuc=["Chứng chỉ quốc tế"]))
        self.assertTrue(vn_result.context)
        vn_data = json.loads(vn_result.context)
        self.assertEqual(vn_data["tong_chuong_trinh"], 1)

        # Match by PascalCase
        pascal_result = lookup.search("ChungChiQuocTe", plan=KeHoachTraCuu(ma_truong=["AAA"], phuong_thuc=["ChungChiQuocTe"]))
        self.assertTrue(pascal_result.context)



class PlannerFlowTests(CorpusFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.setup_corpus()
        self.write("alpha.json", "AAA", "Đại học Alpha Hà Nội", [scored("Marketing", 28)])
        self.model = ModelChat(id="test", ten="Test", nha_cung_cap="OpenAI", phi=True,
                               mo_ta="", san_sang=True, provider="openai")
        models = patch.object(chat_stream, "danh_sach_model", return_value=[self.model])
        models.start(); self.addCleanup(models.stop)
        self.original_client = httpx.AsyncClient

    async def test_two_stage_flow_uses_conversation_then_retrieved_evidence(self):
        requests = []
        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            if len(requests) == 1:
                self.assertIn("ngành nào tốt nhất", body["messages"][-1]["content"])
                self.assertIn("28 điểm A00 miền Bắc", body["messages"][-2]["content"])
                plan = KeHoachTraCuu(ma_truong=["AAA"], to_hop=["A00"], phuong_thuc=["100"], thang_diem=30,
                                    diem_muc_tieu=28, sap_xep="gan_diem", ngu_canh=NguCanhChat(tom_tat="Cần hỏi sở thích"))
                answer = plan.model_dump_json(exclude_unset=True)
            else:
                system = body["messages"][0]["content"]
                self.assertIn("phuong_thuc_tom_tat", system)
                self.assertIn('"diem": 28', system)
                self.assertIn("Marketing", system)
                answer = "Bạn thích công việc nào hơn?"
            payload = {"choices": [{"delta": {"content": answer}, "finish_reason": "stop"}]}
            return httpx.Response(200, text="data: " + json.dumps(payload) + "\n\ndata: [DONE]\n\n")
        transport = httpx.MockTransport(handler)
        with patch.object(chat_stream.httpx, "AsyncClient", side_effect=lambda **kwargs: self.original_client(transport=transport, **kwargs)):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="ngành nào tốt nhất", model_id="test",
                ngu_canh=NguCanhChat(diem=28, to_hop=["A00"], khu_vuc="miền Bắc"),
                lich_su=[TinNhan(vai_tro="user", noi_dung="28 điểm A00 miền Bắc")]))
            events = [event async for event in chat_stream.events(prepared)]
        self.assertEqual(len(requests), 2)
        self.assertEqual(prepared.result.scope.diem, 28)
        self.assertEqual(events[-1][0], "done")
        self.assertEqual(events[-1][1]["tra_loi"], "Bạn thích công việc nào hơn?")

    async def test_planner_sees_profile_when_scoring_needs_certificate_bonus(self):
        requests = []
        def handler(request):
            body = json.loads(request.content)
            requests.append(body)
            if len(requests) == 1:
                self.assertIn("HỒ SƠ THÍ SINH:", body["messages"][0]["content"])
                self.assertIn("IELTS", body["messages"][0]["content"])
                self.assertIn("7.5", body["messages"][0]["content"])
                answer = KeHoachTraCuu(ma_truong=["AAA"], che_do="chi_tiet", thong_tin=["diem", "dieu_kien"]).model_dump_json()
            else:
                self.assertIn("HỒ SƠ THÍ SINH:", body["messages"][0]["content"])
                self.assertIn("7.5", body["messages"][0]["content"])
                answer = "IELTS 7.5 được cộng theo công thức của chương trình."
            payload = {"choices": [{"delta": {"content": answer}, "finish_reason": "stop"}]}
            return httpx.Response(200, text="data: " + json.dumps(payload) + "\n\ndata: [DONE]\n\n")
        transport = httpx.MockTransport(handler)
        profile = {"trinh_do_hoc_van": {"chung_chi_ngoai_ngu": [
            {"ma": "IELTS", "thanh_tich": "7.5", "thoi_gian_cap": "2025-06-15"}]}}
        with patch.object(chat_stream.httpx, "AsyncClient", side_effect=lambda **kwargs: self.original_client(transport=transport, **kwargs)):
            response = await chat_stream.answer(HoiChatRequest(cau_hoi="Điểm SAT trường BKA", model_id="test", ho_so=profile))
        self.assertEqual(len(requests), 2)
        self.assertIn("IELTS", response.tra_loi)

    async def test_invalid_plan_does_not_invent_restrictive_filters(self):
        async def invalid(_):
            yield "delta", {"text": '{"ma_truong":["AAA"], "diem_den": "khong phai so"'}
        scope = NguCanhChat(diem=28, to_hop=["A00"])
        with patch.object(chat_stream, "_provider", invalid):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Hỏi tiếp", model_id="test", ngu_canh=scope))
        data = json.loads(prepared.result.context)
        self.assertEqual(data["ke_hoach_tra_cuu"]["bo_loc"]["ma_truong"], [])
        self.assertIsNone(data["ke_hoach_tra_cuu"]["bo_loc"]["diem_den"])
        self.assertEqual(prepared.result.scope, scope)

    async def test_school_without_data_answers_fixed_message_without_ai(self):
        calls = []

        async def planner(_):
            calls.append(1)
            # Mã ngoài danh mục cũng được coi là trường chưa có dữ liệu (không bỏ kế hoạch rồi tra cứu mọi trường).
            yield "delta", {"text": '{"ma_truong":["ZZZ"], "truong_chua_co_du_lieu":["Đại học Zeta"]}'}
        with patch.object(chat_stream, "_provider", planner):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Điểm chuẩn Đại học Zeta?", model_id="test"))
            events = [event async for event in chat_stream.events(prepared)]
        self.assertEqual(len(calls), 1)
        self.assertEqual(prepared.result.missing_schools, ["Đại học Zeta", "ZZZ"])
        answer = events[-1][1]["tra_loi"]
        self.assertIn("chưa có dữ liệu tuyển sinh", answer)
        self.assertIn("Đại học Zeta", answer)
        self.assertIn("Đại học Alpha Hà Nội (AAA)", answer)

    async def test_school_in_catalog_without_data_is_caught_even_if_planner_misses_it(self):
        calls = []

        async def planner(_):
            calls.append(1)
            # AI lập kế hoạch bỏ sót trường chưa có dữ liệu: kiểm tra cứng theo danh mục trường vẫn chặn.
            yield "delta", {"text": '{"khong_can_tra_cuu": true, "can_lam_ro": "Bạn hỏi trường nào?"}'}
        with patch.object(chat_stream, "_provider", planner):
            prepared = await chat_stream.prepare(
                HoiChatRequest(cau_hoi="Trường Đại học Thương mại tuyển sinh những ngành nào?", model_id="test"))
            events = [event async for event in chat_stream.events(prepared)]
        self.assertEqual(len(calls), 1)
        self.assertEqual(prepared.result.missing_schools, ["Trường Đại học Thương mại"])
        self.assertIn("chưa có dữ liệu tuyển sinh", events[-1][1]["tra_loi"])

    def test_missing_school_detection_uses_longest_name_and_ignores_schools_with_data(self):
        docs = [d for d in lookup.documents() if d.data]
        self.assertEqual(lookup.missing_schools_in_question("Đại học Kiến trúc Hà Nội tuyển ngành nào?", docs),
                         ["Đại học Kiến trúc Hà Nội"])
        self.assertEqual(lookup.missing_schools_in_question("Đại học Alpha Hà Nội tuyển ngành nào?", docs), [])
        self.assertEqual(lookup.missing_schools_in_question("Ngành CNTT học gì, ra làm gì?", docs), [])

    async def test_known_and_missing_school_tells_ai_not_to_use_outside_knowledge(self):
        async def planner(_):
            yield "delta", {"text": '{"ma_truong":["AAA"], "truong_chua_co_du_lieu":["Đại học Zeta"]}'}
        with patch.object(chat_stream, "_provider", planner):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="So sánh Alpha và Zeta", model_id="test"))
        system = prepared.messages[0]["content"]
        self.assertIn("TRƯỜNG CHƯA CÓ DỮ LIỆU TRÊN HỆ THỐNG: Đại học Zeta", system)
        self.assertIn("Không lấy các thông tin này từ kiến thức sẵn có, Internet", system)
        self.assertIn("Marketing", system)
        self.assertIn("Hệ thống chưa có dữ liệu tuyển sinh của Đại học Zeta.", prepared.result.notes)

    async def test_planner_and_answer_see_the_conversation_audience(self):
        instructions = []
        async def planner(request):
            instructions.append(request.messages[0]["content"])
            yield "delta", {"text": '{"khong_can_tra_cuu": true}'}
        with patch.object(chat_stream, "_provider", planner):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Con tôi nên học gì?", model_id="test",
                                                                doi_tuong_huong_den="phu-huynh"))
            default = await chat_stream.prepare(HoiChatRequest(cau_hoi="Chọn ngành gì?", model_id="test"))
        self.assertIn("ĐỐI TƯỢNG NGƯỜI HỎI: Phụ huynh.", instructions[0])
        self.assertIn("ĐỐI TƯỢNG NGƯỜI HỎI: Phụ huynh.", prepared.messages[0]["content"])
        self.assertIn("ĐỐI TƯỢNG NGƯỜI HỎI: Học sinh THPT thi đại học & cao đẳng.", default.messages[0]["content"])

    async def test_only_thpt_audience_uses_profile_and_is_told_to_ask_for_missing_info(self):
        async def planner(_):
            yield "delta", {"text": '{"khong_can_tra_cuu": true}'}
        ho_so = HoSoChat(tinh_thanh_id=7)
        with patch.object(chat_stream, "_provider", planner):
            thpt = await chat_stream.prepare(HoiChatRequest(cau_hoi="Em nên học ngành gì?", model_id="test", ho_so=ho_so,
                                                            doi_tuong_huong_den="thpt-du-hoc"))
            khach = await chat_stream.prepare(HoiChatRequest(cau_hoi="Em nên học ngành gì?", model_id="test"))
            phu_huynh = await chat_stream.prepare(HoiChatRequest(cau_hoi="Con tôi nên học gì?", model_id="test",
                                                                 ho_so=ho_so, doi_tuong_huong_den="phu-huynh"))
        system = thpt.messages[0]["content"]
        self.assertIn('HỒ SƠ THÍ SINH:\n{"tinh_thanh_id": 7}', system)
        self.assertIn("CÁ NHÂN HÓA THEO HỒ SƠ (học sinh THPT)", system)
        self.assertIn("HỒ SƠ THÍ SINH: chưa có", khach.messages[0]["content"])
        self.assertNotIn("HỒ SƠ THÍ SINH", phu_huynh.messages[0]["content"])
        self.assertNotIn("CÁ NHÂN HÓA THEO HỒ SƠ", phu_huynh.messages[0]["content"])

    async def test_gemini_planning_and_answer_use_the_same_stream_protocol(self):
        self.model.provider = "gemini"
        calls = []
        def handler(request):
            body = json.loads(request.content)
            calls.append(body)
            self.assertIn("systemInstruction", body)
            if len(calls) == 1:
                answer = KeHoachTraCuu(ma_truong=["AAA"], to_hop=["A00"], phuong_thuc=["100"], thang_diem=30).model_dump_json()
            else:
                self.assertIn("Marketing", body["systemInstruction"]["parts"][0]["text"])
                answer = "Mình có thể cùng bạn so sánh các ngành."
            data = {"candidates": [{"content": {"parts": [{"text": answer}]}, "finishReason": "STOP"}]}
            return httpx.Response(200, text="data: " + json.dumps(data) + "\n\n")
        transport = httpx.MockTransport(handler)
        with patch.object(chat_stream.httpx, "AsyncClient", side_effect=lambda **kwargs: self.original_client(transport=transport, **kwargs)):
            response = await chat_stream.answer(HoiChatRequest(cau_hoi="28 điểm A00", model_id="test"))
        self.assertEqual(len(calls), 2)
        self.assertEqual(response.tra_loi, "Mình có thể cùng bạn so sánh các ngành.")

    async def test_planner_timeout_closes_stream_and_preserves_memory(self):
        closed = []
        async def slow(_):
            try:
                await asyncio.sleep(1)
                yield "delta", {"text": "{}"}
            finally:
                closed.append(True)
        with patch.object(chat_stream, "_provider", slow), patch.object(settings, "chat_planning_timeout_seconds", 0.01):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Hỏi tiếp", model_id="test"))
        self.assertEqual(closed, [True])
        self.assertTrue(prepared.result.context)


if __name__ == "__main__":
    unittest.main()
