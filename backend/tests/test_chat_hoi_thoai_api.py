"""API quản trị phiên hội thoại: danh sách (tìm, lọc, xem trước tin nhắn cuối) và chi tiết tin nhắn."""

import unittest

from fastapi import HTTPException

from app.api.v1.endpoints.chat_hoi_thoai import (
    chi_tiet_hoi_thoai_cua_toi,
    chi_tiet_phien,
    doi_tieu_de_hoi_thoai_cua_toi,
    doi_tieu_de_phien,
    ket_thuc_hoi_thoai_cua_toi,
    danh_sach_hoi_thoai_cua_toi,
    danh_sach_phien,
    doi_trang_thai_phien,
    xoa_phien,
)
from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.nguoi_dung import NguoiDung
from app.schemas.chat_hoi_thoai import ChatPhienDoiTieuDe, ChatPhienTrangThai
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
        kq = chi_tiet_phien(p.ma_dinh_danh, self.db)
        self.assertEqual(chi_tiet_phien(str(p.id), self.db).phien.id, p.id)
        self.assertEqual([m.loai_nguoi_gui for m in kq.tin_nhan], ["user", "bot"])
        self.assertEqual((kq.tin_nhan[1].trang_thai, kq.phien.tin_nhan_cuoi), ("loi", "Hết giờ"))

    def test_ket_thuc_va_mo_lai_phien(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Hỏi", "m")
        self.db.commit()
        kq = doi_trang_thai_phien(p.ma_dinh_danh, ChatPhienTrangThai(trang_thai="da_dong"), self.db)
        self.assertEqual((kq.trang_thai, kq.tin_nhan_cuoi), ("da_dong", "Hỏi"))
        self.assertEqual([x.id for x in self._ds(trang_thai="da_dong").items], [p.id])
        with self.assertRaises(luu_chat.PhienDaKetThuc):
            luu_chat.luu_cau_hoi(self.db, p.ma_dinh_danh, None, "tb1", "Tiếp", "m")
        self.db.rollback()
        doi_trang_thai_phien(str(p.id), ChatPhienTrangThai(trang_thai="dang_hoat_dong"), self.db)
        self.assertEqual(luu_chat.luu_cau_hoi(self.db, p.ma_dinh_danh, None, "tb1", "Tiếp", "m").id, p.id)

    def test_quan_tri_doi_tieu_de_phien(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Hỏi", "m")
        self.db.commit()
        kq = doi_tieu_de_phien(str(p.id), ChatPhienDoiTieuDe(tieu_de=" Khách hỏi  điểm chuẩn "), self.db)
        self.assertEqual((kq.tieu_de, kq.tin_nhan_cuoi), ("Khách hỏi điểm chuẩn", "Hỏi"))
        with self.assertRaises(HTTPException) as caught:
            doi_tieu_de_phien("999", ChatPhienDoiTieuDe(tieu_de="x"), self.db)
        self.assertEqual(caught.exception.status_code, 400)

    def test_xoa_phien_xoa_ca_tin_nhan(self):
        p = luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Hỏi", "m")
        con_lai = luu_chat.luu_cau_hoi(self.db, None, None, "tb2", "Khác", "m")
        self.db.commit()
        self.assertEqual(xoa_phien(p.ma_dinh_danh, self.db).status_code, 204)
        self.assertEqual([x.id for x in self.db.query(ChatConversation)], [con_lai.id])
        self.assertEqual({m.phien_chat_id for m in self.db.query(ChatMessage)}, {con_lai.id})
        with self.assertRaises(HTTPException) as caught:
            xoa_phien(p.ma_dinh_danh, self.db)
        self.assertEqual(caught.exception.status_code, 400)

    def test_thanh_vien_chi_thay_hoi_thoai_cua_minh(self):
        a1 = luu_chat.luu_cau_hoi(self.db, None, 1, None, "Ngành CNTT", "m")
        a2 = luu_chat.luu_cau_hoi(self.db, None, 1, None, "Điểm chuẩn BKA", "m")
        b = luu_chat.luu_cau_hoi(self.db, None, 2, None, "Của B", "m")
        luu_chat.luu_cau_hoi(self.db, None, None, "tb1", "Của khách", "m")
        a2.trang_thai = "da_dong"
        self.db.commit()
        nguoi_a = self.db.get(NguoiDung, 1)

        def ds(**loc):
            params = {"q": None, "trang_thai": None, "page": 1, "page_size": 20, **loc}
            return danh_sach_hoi_thoai_cua_toi(nguoi_dung=nguoi_a, db=self.db, **params)

        self.assertEqual({x.id for x in ds().items}, {a1.id, a2.id})
        self.assertEqual([x.id for x in ds(trang_thai="da-ket-thuc").items], [a2.id])
        self.assertEqual([x.id for x in ds(trang_thai="dang-hoat-dong").items], [a1.id])
        self.assertEqual([x.id for x in ds(q="cntt").items], [a1.id])
        kq = chi_tiet_hoi_thoai_cua_toi(a1.ma_dinh_danh, nguoi_a, self.db)
        self.assertEqual([m.noi_dung_tin_nhan for m in kq.tin_nhan], ["Ngành CNTT"])
        with self.assertRaises(HTTPException) as caught:
            chi_tiet_hoi_thoai_cua_toi(b.ma_dinh_danh, nguoi_a, self.db)
        self.assertEqual(caught.exception.status_code, 400)

    def test_thanh_vien_doi_tieu_de_va_ket_thuc_hoi_thoai_cua_minh(self):
        a = luu_chat.luu_cau_hoi(self.db, None, 1, None, "Ngành CNTT", "m")
        b = luu_chat.luu_cau_hoi(self.db, None, 2, None, "Của B", "m")
        self.db.commit()
        nguoi_a = self.db.get(NguoiDung, 1)
        kq = doi_tieu_de_hoi_thoai_cua_toi(a.ma_dinh_danh, ChatPhienDoiTieuDe(tieu_de="  Tìm hiểu   CNTT "), nguoi_a, self.db)
        self.assertEqual(kq.tieu_de, "Tìm hiểu CNTT")
        with self.assertRaises(ValueError):
            ChatPhienDoiTieuDe(tieu_de="   ")
        with self.assertRaises(HTTPException) as caught:
            doi_tieu_de_hoi_thoai_cua_toi(b.ma_dinh_danh, ChatPhienDoiTieuDe(tieu_de="x"), nguoi_a, self.db)
        self.assertEqual(caught.exception.status_code, 400)

        self.assertEqual(ket_thuc_hoi_thoai_cua_toi(a.ma_dinh_danh, nguoi_a, self.db).trang_thai, "da_dong")
        with self.assertRaises(luu_chat.PhienDaKetThuc):
            luu_chat.luu_cau_hoi(self.db, a.ma_dinh_danh, 1, None, "Tiếp", "m")
        self.db.rollback()
        with self.assertRaises(HTTPException):
            ket_thuc_hoi_thoai_cua_toi(b.ma_dinh_danh, nguoi_a, self.db)

    def test_phien_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as caught:
            chi_tiet_phien("999", self.db)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn("999", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
