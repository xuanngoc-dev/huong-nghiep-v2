"""API quản trị phiên hội thoại: danh sách (tìm, lọc, xem trước tin nhắn cuối) và chi tiết tin nhắn."""

import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.chat_hoi_thoai import chi_tiet_phien, danh_sach_phien
from app.services import luu_chat
from tests import test_luu_chat as mau


class ChatHoiThoaiApiTests(unittest.TestCase):
    # Dữ liệu mẫu: người dùng id 1 (A), 2 (B) trên SQLite.
    setUp = mau.LuuChatTests.setUp
    tearDown = mau.LuuChatTests.tearDown

    def _ds(self, **loc):
        params = {"q": None, "trang_thai": None, "doi_tuong": None, "page": 1, "page_size": 20, **loc}
        return danh_sach_phien(db=self.db, **params)

    def test_danh_sach_rong(self):
        self.assertEqual(self._ds().model_dump(), {"items": [], "total": 0, "page": 1, "page_size": 20})

    def test_danh_sach_loc_tim_va_xem_truoc(self):
        p1 = luu_chat.luu_cau_hoi(self.db, None, 1, None, "Ngành CNTT", "m")
        luu_chat.luu_tra_loi(
            self.db, p1.id, tra_loi="CNTT học lập trình", model_ai="m", nguon=None, usage=None, thoi_gian_ms=5
        )
        luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Điểm chuẩn BKA", "m")
        self.db.commit()

        trang = self._ds()
        self.assertEqual(trang.total, 2)
        thanh_vien = self._ds(doi_tuong="thanh-vien").items
        self.assertEqual(
            [(x.ho_ten, x.tin_nhan_cuoi, x.so_tin_nhan) for x in thanh_vien], [("A", "CNTT học lập trình", 2)]
        )
        self.assertEqual([x.ma_khach_vang_lai for x in self._ds(doi_tuong="khach").items], ["tb1"])
        self.assertEqual([x.tieu_de for x in self._ds(q="bka").items], ["Điểm chuẩn BKA"])
        self.assertEqual(self._ds(q="a@vd").total, 1)

    def test_chi_tiet_tin_nhan_theo_thu_tu(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Hỏi", "m")
        luu_chat.luu_tra_loi(
            self.db, p.id, tra_loi="", model_ai="m", nguon=None, usage=None, thoi_gian_ms=5, loi="Hết giờ"
        )
        self.db.commit()
        kq = chi_tiet_phien(p.id, self.db)
        self.assertEqual([m.loai_nguoi_gui for m in kq.tin_nhan], ["user", "bot"])
        self.assertEqual((kq.tin_nhan[1].trang_thai, kq.phien.tin_nhan_cuoi), ("loi", "Hết giờ"))

    def test_phien_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as caught:
            chi_tiet_phien(999, self.db)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("999", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
