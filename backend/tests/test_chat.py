import asyncio
import json
import logging
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import StreamingResponse

from app.api.deps import get_current_user
from app.api.v1.endpoints import chat, tai_lieu
from app.core.config import settings
from app.core.logging import register_request_logging
from app.schemas.chat import HoiChatRequest, ModelChat, TinNhan
from app.services import chat_stream, tra_cuu_tuyen_sinh as lookup


def program(name, score=20, code="7340115", condition="Điều kiện riêng"):
    return {"ten_nganh": name, "ten_chuong_trinh": name, "ma_nganh": code, "ma_xet_tuyen": name,
            "chi_tieu_nganh": 0, "dieu_kien_nganh": [condition], "phuong_thuc_tuyen_sinh": [
                {"ma_phuong_thuc": "100", "ten_phuong_thuc": "Thi THPT", "diem_chuan": score,
                 "dieu_kien_phu": [condition], "to_hop_mon": [{"ma_to_hap": "A00", "ten_to_hap": "Toán, Lý, Hóa"}]}]}


class CorpusFixture:
    def setup_corpus(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.addCleanup(lookup._load_documents.cache_clear)
        setting = patch.object(settings, "tai_lieu_dir", str(self.root))
        setting.start()
        self.addCleanup(setting.stop)
        self.write("alpha.json", "AAA", "Đại học Alpha Hà Nội", [program("Marketing", 20, condition="Điều kiện A"), program("Marketing số", 28, condition="Điều kiện B"), program("Logistics", 25)])
        self.write("beta.json", "BBB", "Đại học Beta Đà Nẵng", [program("Logistics", 22)])

    def write(self, filename, code, name, programs):
        data = {"truong": {"ma_truong": code, "ten_truong": name, "nam_tuyen_sinh": 2026}, "danh_sach_nganh": programs}
        (self.root / filename).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


class LookupTests(CorpusFixture, unittest.TestCase):
    def setUp(self):
        self.setup_corpus()

    def test_followup_and_switch_school(self):
        history = [TinNhan(vai_tro="user", noi_dung="Marketing AAA")]
        result = lookup.search("còn điều kiện thì sao?", history)
        self.assertEqual([s.ma_truong for s in result.sources], ["AAA"])
        self.assertEqual(json.loads(result.context)["tong_chuong_trinh"], 2)
        result = lookup.search("Logistics BBB", history)
        self.assertEqual([s.ma_truong for s in result.sources], ["BBB"])
        self.assertEqual(json.loads(result.context)["tong_chuong_trinh"], 1)

    def test_structured_scope_survives_history_window(self):
        result = lookup.search("Marketing AAA năm 2026")
        recent = [TinNhan(vai_tro="user", noi_dung="còn điểm thì sao?")] * 30
        following = lookup.search("còn điều kiện thì sao?", recent, result.scope)
        self.assertEqual([s.ma_truong for s in following.sources], ["AAA"])
        self.assertEqual(json.loads(following.context)["tong_chuong_trinh"], 2)
        self.assertEqual(following.scope.nam, 2026)

    def test_school_filter_and_complete_programs(self):
        result = lookup.search("Phương thức Marketing AAA")
        data = json.loads(result.context)
        records = data["ket_qua"][0]["chuong_trinh"]
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["chi_tieu_nganh"], 0)
        self.assertNotEqual(records[0]["phuong_thuc_tuyen_sinh"][0]["dieu_kien_phu"], records[1]["phuong_thuc_tuyen_sinh"][0]["dieu_kien_phu"])

    def test_points_and_combinations_retained(self):
        result = lookup.search("Điểm chuẩn AAA")
        methods = [m for n in json.loads(result.context)["ket_qua"][0]["chuong_trinh"] for m in n["phuong_thuc_tuyen_sinh"]]
        self.assertEqual({m["diem_chuan"] for m in methods}, {20, 28, 25})
        result = lookup.search("AAA ngành nào xét A00?")
        self.assertIn('"ma_to_hap":"A00"', result.context)
        self.assertFalse(lookup.search("AAA ngành nào xét D01?").context)

    def test_cross_school_query_has_all_matches(self):
        result = lookup.search("Những trường nào có Logistics?")
        self.assertEqual({s.ma_truong for s in result.sources}, {"AAA", "BBB"})
        self.assertTrue(json.loads(result.context)["chi_tiet_day_du"])

    def test_unrelated_and_unknown_year_do_not_send_files(self):
        self.assertFalse(lookup.search("zzzzqqqqxxxx").context)
        self.assertFalse(lookup.search("AAA năm 2027").sources)

    def test_unknown_school_and_cross_school_scope_do_not_reuse_old_school(self):
        history = [TinNhan(vai_tro="user", noi_dung="Marketing AAA")]
        self.assertFalse(lookup.search("Điểm ngành Marketing trường Không Tồn Tại", history).context)
        self.assertFalse(lookup.search("Điều kiện ngành Xyz AAA", history).context)
        history.append(TinNhan(vai_tro="user", noi_dung="Những trường nào có Logistics?"))
        result = lookup.search("còn học phí thì sao?", history)
        self.assertEqual({s.ma_truong for s in result.sources}, {"AAA", "BBB"})

    def test_cache_changes_after_upload_and_delete(self):
        self.assertEqual(len(lookup.search("Những trường nào có Logistics?").sources), 2)
        self.write("gamma.json", "CCC", "Đại học Gamma", [program("Logistics")])
        self.assertEqual(len(lookup.search("Những trường nào có Logistics?").sources), 3)
        (self.root / "gamma.json").unlink()
        self.assertEqual(len(lookup.search("Những trường nào có Logistics?").sources), 2)

    def test_malformed_structured_upload_is_rejected(self):
        from app.services.tai_lieu import save_tai_lieu
        bad = {"truong": {"ten_truong": "Bad"}, "danh_sach_nganh": [{"ten_nganh": ["bad"]}]}
        with self.assertRaises(HTTPException):
            save_tai_lieu("bad.json", json.dumps(bad).encode())
        self.assertFalse((self.root / "bad.json").exists())

    def test_budget_keeps_whole_records_and_discloses_missing(self):
        with patch.object(lookup, "CONTEXT_BUDGET", 1300):
            result = lookup.search("Marketing AAA")
        data = json.loads(result.context)
        self.assertLessEqual(len(result.context), 1300)
        self.assertTrue(result.notes or data["chi_tiet_day_du"])

    def test_plain_text_documents_are_searchable(self):
        (self.root / "guide.txt").write_text("Thông tin học bổng dành cho vận động viên thể thao.", encoding="utf-8")
        result = lookup.search("học bổng vận động viên")
        self.assertEqual(result.files, ["guide.txt"])


class RealCorpusRegressionTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2] / "data_dh_json"
        if not root.exists():
            self.skipTest("Không có bộ dữ liệu tuyển sinh mẫu")
        setting = patch.object(settings, "tai_lieu_dir", str(root))
        setting.start()
        self.addCleanup(setting.stop)

    def test_neu_marketing_preserves_all_five_programs(self):
        result = lookup.search("Phương thức xét tuyển ngành Marketing trường NEU 2026?")
        self.assertEqual([s.ma_truong for s in result.sources], ["NEU"])
        data = json.loads(result.context)
        self.assertEqual(len(data["ket_qua"][0]["chuong_trinh"]), 5)
        self.assertTrue(data["chi_tiet_day_du"])

    def test_all_it_logistics_sources(self):
        docs = [d for d in lookup.documents() if d.data]
        expected = {d.name for d in docs if any("cong nghe thong tin" in lookup.normalize(n.get("ten_nganh", "") + ' ' + n.get("ten_chuong_trinh", "")) or "logistics" in lookup.normalize(n.get("ten_nganh", "") + ' ' + n.get("ten_chuong_trinh", "")) for n in d.data["danh_sach_nganh"])}
        result = lookup.search("Những trường nào có ngành Công nghệ thông tin hoặc Logistics?")
        self.assertEqual(set(result.files), expected)

    def test_accentless_school_and_ambiguous_school(self):
        self.assertEqual([s.ma_truong for s in lookup.search("hoc phi bach khoa ha noi").sources], ["BKA"])
        result = lookup.search("Bách khoa tuyển sinh thế nào?")
        self.assertFalse(result.context)
        self.assertEqual(len(result.suggestions), 3)

    def test_full_school_name_is_not_treated_as_major(self):
        result = lookup.search("Đại học Kinh tế Quốc dân có những ngành nào?")
        self.assertEqual(json.loads(result.context)["tong_chuong_trinh"], 104)

    def test_short_major_name_in_comparison_filters_programs(self):
        result = lookup.search("So sánh Logistics NEU và HUST")
        data = json.loads(result.context)
        self.assertEqual({s.ma_truong for s in result.sources}, {"NEU", "BKA"})
        for school in data["ket_qua"]:
            self.assertTrue(school["chuong_trinh"])
            for record in school["chuong_trinh"]:
                self.assertIn("logistics", lookup.normalize(record["ten_nganh"] + ' ' + record.get("ten_chuong_trinh", "")))


class SchemaTests(unittest.TestCase):

    def test_history_allows_long_answer_and_caps_total(self):
        HoiChatRequest(cau_hoi="Hỏi tiếp", model_id="x", lich_su=[TinNhan(vai_tro="bot", noi_dung="a" * 16000)])
        with self.assertRaises(ValidationError):
            HoiChatRequest(cau_hoi="Hỏi tiếp", model_id="x", lich_su=[TinNhan(vai_tro="bot", noi_dung="a" * 16000)] * 5)
        with self.assertRaises(ValidationError):
            HoiChatRequest(cau_hoi="   ", model_id="x")


class StreamTests(CorpusFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.setup_corpus()
        self.models = [ModelChat(id="openai-test", ten="OpenAI Test", nha_cung_cap="OpenAI", phi=True, mo_ta="", san_sang=True, provider="openai"),
                       ModelChat(id="gemini-test", ten="Gemini Test", nha_cung_cap="Google", phi=False, mo_ta="", san_sang=True, provider="gemini")]
        patcher = patch.object(chat_stream, "danh_sach_model", return_value=self.models)
        patcher.start(); self.addCleanup(patcher.stop)
        planner = patch.object(chat_stream, "_plan_lookup", return_value=(None, {}))
        planner.start(); self.addCleanup(planner.stop)
        self.original_client = httpx.AsyncClient

    async def collect(self, model="openai-test"):
        prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Marketing AAA", model_id=model))
        return [item async for item in chat_stream.events(prepared)]

    def transport(self, handler):
        return patch.object(chat_stream.httpx, "AsyncClient", side_effect=lambda **kwargs: self.original_client(transport=httpx.MockTransport(handler), **kwargs))

    async def test_stream_delta_and_done(self):
        def handler(request):
            body = json.loads(request.content)
            self.assertTrue(body["stream"])
            return httpx.Response(200, text='data: {"choices":[{"delta":{"content":"Xin chào"},"finish_reason":null}]}\n\ndata: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n\ndata: {"choices":[],"usage":{"total_tokens":9}}\n\ndata: [DONE]\n\n')
        with self.transport(handler):
            result = await self.collect()
        self.assertEqual(result[-1][0], "done")
        self.assertEqual(result[-1][1]["tra_loi"], "Xin chào")
        self.assertEqual(result[-1][1]["nguon"][0]["ma_truong"], "AAA")

    async def test_gemini_fallback_reports_actual_model(self):
        def handler(request):
            if "gemini-test:" in str(request.url):
                return httpx.Response(503)
            return httpx.Response(200, text='data: {"candidates":[{"content":{"parts":[{"text":"Ẩn","thought":true},{"text":"Kết quả"}]},"finishReason":"STOP"}]}\n\n')
        with self.transport(handler):
            result = await self.collect("gemini-test")
        self.assertEqual(result[-1][1]["model_id"], "gemini-3.5-flash-lite")
        self.assertEqual(result[-1][1]["tra_loi"], "Kết quả")

    async def test_disconnect_is_error_not_success(self):
        with self.transport(lambda _: httpx.Response(200, text='data: {"choices":[{"delta":{"content":"Một phần"}}]}\n\n')):
            result = await self.collect()
        self.assertEqual(result[-1][0], "error")
        self.assertNotIn("done", [e for e, _ in result])

    async def test_upstream_error_does_not_expose_key(self):
        with self.transport(lambda _: httpx.Response(401, text='{"error":"sk-sensitive-secret"}')):
            result = await self.collect()
        self.assertEqual(result[-1][0], "error")
        self.assertNotIn("sensitive", json.dumps(result))

    async def test_unknown_model_rejected_and_history_used(self):
        with self.assertRaises(HTTPException):
            await chat_stream.prepare(HoiChatRequest(cau_hoi="Marketing AAA", model_id="expensive-unapproved"))
        prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="còn điều kiện thì sao?", model_id="openai-test", lich_su=[TinNhan(vai_tro="user", noi_dung="Marketing AAA")]))
        self.assertEqual(prepared.result.files, ["alpha.json"])

    async def test_unavailable_model_can_return_local_no_data_reply(self):
        self.models[0].san_sang = False
        with patch.object(chat_stream, "_provider", side_effect=AssertionError("must not call provider")):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="zzzzxxxxx", model_id="openai-test"))
            result = [e async for e in chat_stream.events(prepared)]
        self.assertEqual(result[-1][0], "done")

    async def test_timeout_and_cancel_close_provider(self):
        closed = []
        async def slow_provider(_):
            try:
                yield "delta", {"text": "Một phần"}
                await asyncio.sleep(1)
            finally:
                closed.append(True)
        with patch.object(chat_stream, "_provider", slow_provider), patch.object(settings, "chat_timeout_seconds", 0.01):
            result = await self.collect()
        self.assertEqual(result[-1][0], "error")
        self.assertEqual(len(closed), 1)
        with patch.object(chat_stream, "_provider", slow_provider):
            prepared = await chat_stream.prepare(HoiChatRequest(cau_hoi="Marketing AAA", model_id="openai-test"))
            stream = chat_stream.events(prepared)
            await stream.__anext__()  # metadata
            await stream.__anext__()  # partial answer
            await stream.aclose()
        self.assertEqual(len(closed), 2)

    async def test_logging_does_not_buffer_stream_or_log_chat(self):
        app = FastAPI()
        register_request_logging(app)
        consumed = False
        async def content():
            nonlocal consumed
            consumed = True
            yield b"secret-answer"
        async def next_response(_):
            return StreamingResponse(content(), media_type="text/event-stream")
        dispatch = app.user_middleware[0].kwargs["dispatch"]
        request = Request({"type": "http", "method": "POST", "path": f"{settings.api_v1_prefix}/chat/hoi/stream", "query_string": b"", "headers": [], "client": ("127.0.0.1", 1)})
        with self.assertLogs("app.api", level=logging.INFO) as logs:
            response = await dispatch(request, next_response)
        self.assertFalse(consumed)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        self.assertNotIn("secret-answer", " ".join(logs.output))


class EndpointTests(CorpusFixture, unittest.TestCase):
    def setUp(self):
        self.setup_corpus()
        self.app = FastAPI()
        self.app.include_router(chat.router)
        self.app.include_router(tai_lieu.router)

    def test_stream_route_contract(self):
        model = ModelChat(id="test", ten="Test", nha_cung_cap="OpenAI", phi=True, mo_ta="", san_sang=True, provider="openai")
        async def provider(_):
            yield "model", {"model_id": "test", "model_ten": "Test"}
            yield "delta", {"text": "Kết quả [1]"}
        with patch.object(chat_stream, "danh_sach_model", return_value=[model]), patch.object(chat_stream, "_provider", provider), patch.object(chat_stream, "_plan_lookup", return_value=(None, {})):
            with TestClient(self.app) as client:
                response = client.post("/chat/hoi/stream", json={"model_id": "test", "cau_hoi": "Marketing AAA"})
                self.assertEqual(response.status_code, 200)
                self.assertIn("text/event-stream", response.headers["content-type"])
                self.assertIn("event: meta", response.text)
                self.assertIn("event: delta", response.text)
                self.assertIn("event: done", response.text)
                response = client.post("/chat/hoi", json={"model_id": "test", "cau_hoi": "Marketing AAA"})
                self.assertEqual(response.json()["tra_loi"], "Kết quả [1]")

    def test_document_permissions_and_public_sources(self):
        with TestClient(self.app) as client:
            self.assertEqual(client.get("/tai-lieu").status_code, 401)
            self.assertEqual(client.delete("/tai-lieu/alpha.json").status_code, 401)
            self.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(vai_tro=0)
            self.assertEqual(client.delete("/tai-lieu/alpha.json").status_code, 403)
            self.app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(vai_tro=1)
            self.assertEqual(client.get("/tai-lieu").status_code, 200)
            self.assertEqual(client.get("/chat/nguon/alpha.json").status_code, 200)
            self.assertEqual(client.get("/chat/nguon/unknown.json").status_code, 404)
            self.assertEqual(client.get("/chat/nguon/.env").status_code, 400)
        self.assertTrue((self.root / "alpha.json").exists())


if __name__ == "__main__":
    unittest.main()
