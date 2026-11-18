"""Lưu hội thoại chat: cùng mã phiên thì không tạo phiên mới, mỗi lượt ghi câu hỏi + câu trả lời."""

import asyncio
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import chat as chat_api
from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.nguoi_dung import NguoiDung
from app.schemas.chat import HoiChatRequest, HoiChatResponse
from app.services import luu_chat
from tests import hoi_quy_xet_tuyen  # noqa: F401  (khai báo BIGINT → INTEGER trên SQLite để id tự tăng)


class LuuChatTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        for model in (NguoiDung, ChatConversation, ChatMessage):
            model.__table__.create(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db: Session = self.Session()
        self.db.add_all(
            [
                NguoiDung(id=1, ho_ten="A", email="a@vd.vn", mat_khau="x"),
                NguoiDung(id=2, ho_ten="B", email="b@vd.vn", mat_khau="x"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _dem(self, model):
        return self.db.scalar(select(func.count()).select_from(model))

    def test_cung_ma_phien_khong_tao_phien_moi(self):
        p1 = luu_chat.luu_cau_hoi(self.db, None, 1, None, "Ngành CNTT học gì?", "gpt")
        p2 = luu_chat.luu_cau_hoi(self.db, p1.ma_dinh_danh, 1, None, "Điểm chuẩn?", "gpt")
        self.assertEqual(p1.id, p2.id)
        self.assertEqual(self._dem(ChatConversation), 1)
        self.assertEqual((p1.tieu_de, p1.so_tin_nhan), ("Ngành CNTT học gì?", 2))

    def test_ma_cua_nguoi_khac_hoac_khong_hop_le_thi_tao_phien_moi(self):
        p1 = luu_chat.luu_cau_hoi(self.db, None, 1, None, "a", None)
        p2 = luu_chat.luu_cau_hoi(self.db, p1.ma_dinh_danh, 2, None, "b", None)
        p3 = luu_chat.luu_cau_hoi(self.db, "khong-phai-uuid", None, "tb1", "c", None)
        self.assertEqual(len({p1.id, p2.id, p3.id}), 3)
        uuid.UUID(p3.ma_dinh_danh)

    def test_ma_phien_moi_do_frontend_tao_duoc_giu_lam_ma_phien(self):
        # Trang "Cuộc hội thoại mới" tạo sẵn UUID; câu hỏi đầu tiên tạo phiên đúng mã đó, câu sau nối tiếp.
        ma = str(uuid.uuid4())
        p1 = luu_chat.luu_cau_hoi(self.db, ma, 1, None, "Câu đầu", None)
        self.assertEqual(p1.ma_dinh_danh, ma)
        self.assertEqual(luu_chat.luu_cau_hoi(self.db, ma, 1, None, "Câu sau", None).id, p1.id)

    def test_khach_cung_thiet_bi_noi_tiep_phien(self):
        p1 = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "a", None)
        self.assertEqual(luu_chat.luu_cau_hoi(self.db, p1.ma_dinh_danh, None, "tb1", "b", None).id, p1.id)
        self.assertNotEqual(luu_chat.luu_cau_hoi(self.db, p1.ma_dinh_danh, None, "tb2", "c", None).id, p1.id)

    def test_luu_tra_loi_kem_token_va_loi(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "a", "gemini")
        bot = luu_chat.luu_tra_loi(
            self.db,
            p.id,
            tra_loi="Trả lời",
            model_ai="gemini",
            nguon=[{"id": 1}],
            usage={"promptTokenCount": 10, "candidatesTokenCount": 5},
            thoi_gian_ms=1200,
        )
        self.assertEqual(
            (bot.loai_nguoi_gui, bot.so_token_vao, bot.so_token_ra, bot.trang_thai), ("bot", 10, 5, "thanh_cong")
        )
        self.assertEqual(bot.ma_khach_vang_lai, "tb1")
        loi = luu_chat.luu_tra_loi(
            self.db, p.id, tra_loi="", model_ai="x", nguon=None, usage=None, thoi_gian_ms=1, loi="Hết giờ"
        )
        self.assertEqual((loi.trang_thai, loi.loi_chi_tiet, loi.noi_dung_phan_hoi), ("loi", "Hết giờ", None))
        self.assertEqual(p.so_tin_nhan, 3)

    def test_api_hoi_luu_cau_hoi_va_tra_loi_tra_ma_phien(self):
        tra_loi = HoiChatResponse(tra_loi="Xin chào", model_id="m", model_ten="M", tai_lieu=[])
        payload = HoiChatRequest(cau_hoi="Chào", model_id="m", ma_khach_vang_lai="tb9")
        with (
            patch.object(chat_api, "SessionLocal", self.Session),
            patch.object(chat_api, "hoi", AsyncMock(return_value=tra_loi)),
        ):
            ket_qua = asyncio.run(chat_api.post_hoi(payload, None))
            payload2 = HoiChatRequest(cau_hoi="Tiếp", model_id="m", ma_khach_vang_lai="tb9", ma_phien=ket_qua.ma_phien)
            asyncio.run(chat_api.post_hoi(payload2, None))
        self.assertEqual(self._dem(ChatConversation), 1)
        tin_nhan = self.db.scalars(select(ChatMessage).order_by(ChatMessage.id)).all()
        self.assertEqual([m.loai_nguoi_gui for m in tin_nhan], ["user", "bot", "user", "bot"])
        self.assertEqual(tin_nhan[1].noi_dung_phan_hoi, "Xin chào")

    def test_phien_da_ket_thuc_khong_hoi_tiep_duoc(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "a", None)
        p.trang_thai = "da_dong"
        self.db.commit()
        with self.assertRaises(luu_chat.PhienDaKetThuc):
            luu_chat.luu_cau_hoi(self.db, p.ma_dinh_danh, None, "tb1", "b", None)
        # Thiết bị khác dùng mã đó vẫn chỉ mở phiên mới của mình như trước.
        self.assertNotEqual(luu_chat.luu_cau_hoi(self.db, p.ma_dinh_danh, None, "tb2", "c", None).id, p.id)

    def test_api_hoi_phien_da_ket_thuc_tra_409_khong_goi_ai(self):
        p = luu_chat.luu_cau_hoi(self.db, None, 1, None, "a", None)
        p.trang_thai = "luu_tru"
        self.db.commit()
        hoi = AsyncMock()
        payload = HoiChatRequest(cau_hoi="Tiếp", model_id="m", ma_phien=p.ma_dinh_danh)
        with patch.object(chat_api, "SessionLocal", self.Session), patch.object(chat_api, "hoi", hoi):
            with self.assertRaises(HTTPException) as caught:
                asyncio.run(chat_api.post_hoi(payload, 1))
        self.assertEqual(caught.exception.status_code, 409)
        hoi.assert_not_called()
        self.db.expire_all()
        self.assertEqual(self.db.get(ChatConversation, p.id).so_tin_nhan, 1)

    def test_trang_thai_phien_chi_cho_nguoi_so_huu(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "a", None)
        p.trang_thai = "da_dong"
        self.db.commit()
        cua_minh = chat_api.get_trang_thai_phien(p.ma_dinh_danh, "tb1", None, self.db)
        self.assertEqual((cua_minh.trang_thai, cua_minh.da_ket_thuc), ("da_dong", True))
        nguoi_khac = chat_api.get_trang_thai_phien(p.ma_dinh_danh, "tb2", None, self.db)
        self.assertEqual((nguoi_khac.trang_thai, nguoi_khac.da_ket_thuc), (None, False))

    def _chay_stream(self, su_kien):
        """Gọi /chat/hoi/stream với luồng sự kiện giả; trả các khối SSE đã gửi."""
        prepared = SimpleNamespace(model=SimpleNamespace(id="m"), usage={"prompt_tokens": 7, "completion_tokens": 3})

        async def events(_prepared):
            for event, data in su_kien:
                yield event, data

        async def chay():
            payload = HoiChatRequest(cau_hoi="Hỏi", model_id="m", ma_khach_vang_lai="tb1")
            response = await chat_api.post_hoi_stream(payload, None)
            return [chunk async for chunk in response.body_iterator]

        with (
            patch.object(chat_api, "SessionLocal", self.Session),
            patch.object(chat_api, "prepare", AsyncMock(return_value=prepared)),
            patch.object(chat_api, "events", events),
        ):
            return asyncio.run(chay())

    def test_stream_gui_ma_phien_va_luu_tra_loi(self):
        khoi = self._chay_stream(
            [
                ("meta", {"tra_loi": ""}),
                ("delta", {"text": "Xin "}),
                ("delta", {"text": "chào"}),
                ("done", {"tra_loi": "Xin chào", "model_id": "m", "nguon": []}),
            ]
        )
        ma = self.db.scalar(select(ChatConversation.ma_dinh_danh))
        self.assertIn(f'"ma_phien": "{ma}"', khoi[0])
        bot = self.db.scalar(select(ChatMessage).where(ChatMessage.loai_nguoi_gui == "bot"))
        self.assertEqual((bot.noi_dung_phan_hoi, bot.so_token_vao, bot.trang_thai), ("Xin chào", 7, "thanh_cong"))

    def test_stream_loi_luu_trang_thai_loi_va_phan_da_tra_loi(self):
        self._chay_stream([("meta", {}), ("delta", {"text": "Dở"}), ("error", {"message": "Hết giờ"})])
        bot = self.db.scalar(select(ChatMessage).where(ChatMessage.loai_nguoi_gui == "bot"))
        self.assertEqual((bot.trang_thai, bot.loi_chi_tiet, bot.noi_dung_phan_hoi), ("loi", "Hết giờ", "Dở"))


if __name__ == "__main__":
    unittest.main()
