"""Nghiệm thu luồng nguồn, bản nháp và nhập đề án bằng CSDL SQLite cô lập."""

import json
import unittest
from datetime import timedelta
from unittest.mock import patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models as M
from app.api.deps import get_current_user
from app.api.v1.endpoints import dats_thu_thap as api
from app.db.session import get_db
from app.schemas.dats_thu_thap import (
    BoSungBanNhap, ChonNguon, DungTaoBanNhap, PhienBanRequest, PhienThuThapCreate, SuaBanNhap, ThemNguon,
)
from app.services.dats_ban_nhap_thu_thap import _muc_du_lieu
from tests.hoi_quy_xet_tuyen import DANH_MUC_MA, tao_csdl

NAM = 2027
GOC = "https://example.edu.vn/de-an-2027.pdf"
PHU_LUC = "https://example.edu.vn/dieu-chinh-2027.pdf"
CU = "https://example.edu.vn/de-an-2026.pdf"
CHI_TIEU = "/dats_tuyen_sinh/chi_tieu"


def tai_lieu(url: str, **thuoc_tinh) -> dict:
    return {
        "url": url, "tieu_de": "Đề án tuyển sinh", "loai": "de_an", "co_quan": "Trường BKA",
        "nam_ap_dung": NAM, "phu_hop": True, "chinh_thuc": True, **thuoc_tinh,
    }


def trich_xuat(*, ma_nganh="7480101", chi_tieu=95, mau_thuan=False):
    du_lieu = {
        "dats_tuyen_sinh": {"ten_de_an": "Tuyển sinh đại học", "nguon_du_lieu_url": GOC,
                           "chi_tieu": chi_tieu, "dats_chuong_trinh_dao_tao": [
            {"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "Công nghệ thông tin", "ma_nganh": ma_nganh,
             "chi_tieu_tuyen_sinh": chi_tieu,
             "dats_phuong_thuc": [{"ma_phuong_thuc_cua_bo": "100", "cong_thuc_tinh_diem": "THPT",
                                   "to_hop_mon_hoc": ["A00"]}]},
        ]},
        "quy_tac_xet_tuyen": {"de_an": {"ten_de_an": "Tuyển sinh đại học", "nguon_du_lieu_url": GOC},
                              "cong_thuc": [{"ma_cong_thuc": "THPT", "ten_cong_thuc": "Điểm thi THPT",
                                            "kieu_tinh": "TO_HOP_MON", "nguon_diem_mon": "THI_THPT",
                                            "ma_phuong_thuc_cua_bo": "100", "thang_diem": 30}],
                              "chuong_trinh": [{"ma_chuong_trinh": "IT1", "ma_xet_tuyen": "IT1",
                                                "ten_chuong_trinh": "Công nghệ thông tin", "hoc_phi": None,
                                                "chi_tieu": chi_tieu,
                                               "phuong_an": [{"ma_cong_thuc": "THPT", "to_hop": ["A00"]}]}]},
    }
    muc = [{"duong_dan": p, "dan_chung": [{"nguon_id": 1, "vi_tri": "Trang 2", "trich_dan": str(v), "gia_tri": v}]}
           for p, v in _muc_du_lieu(du_lieu, set()).items() if v is not None]
    if mau_thuan:
        item = next(i for i in muc if i["duong_dan"] == CHI_TIEU)
        item["dan_chung"].append({"nguon_id": 2, "vi_tri": "Trang 1", "trich_dan": "Điều chỉnh lên 95", "gia_tri": 95})
    return {"du_lieu": du_lieu, "muc": muc, "ghi_chu": [], "doi_chieu_chuong_trinh": [
        {"nguon_id": 1, "vi_tri": "Trang 2", "trich_dan": "1 mã xét tuyển: IT1", "cac_ma": ["IT1"],
         "tong_cong_bo": 1, "pham_vi": "toan_truong"},
    ]}


class ThuThapTuyenSinhTests(unittest.TestCase):
    def setUp(self):
        self.db, _ = tao_csdl("BKA")
        for model in (M.NguoiDung, M.DatsPhienThuThap, M.DatsBanNhapThuThap, M.DatsNhatKyThuThap,
                      M.DmPhuongThucTuyenSinh, M.DmThanhTichHocTapNghienCuu):
            model.__table__.create(self.db.get_bind())
        dm = json.loads(DANH_MUC_MA.read_text(encoding="utf-8"))
        self.db.add_all(M.DmPhuongThucTuyenSinh(ma_phuong_thuc=x["ma"], ten_phuong_thuc=x["ten"]) for x in dm["phuong_thuc_cua_bo"])
        self.db.add(M.DmNganhDaoTao(ma_nhom_nganh="74801", ma_nganh="7480101", ten_nganh="Công nghệ thông tin",
                                    ten_tieng_anh="", trinh_do="ĐH"))
        self.user = M.NguoiDung(ho_ten="Quản trị", email="admin@example.edu.vn", mat_khau="test", vai_tro=1)
        self.db.add(self.user)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _dem(self, model):
        return self.db.scalar(select(func.count()).select_from(model))

    def _tao_phien(self, mau_thuan=False):
        phien = api.tao_phien(PhienThuThapCreate(ma_truong="bka", nam_tuyen_sinh=NAM), self.db, self.user)
        with patch.object(api.ai, "search_sources", return_value=(
            [tai_lieu(GOC), tai_lieu(PHU_LUC, loai="dieu_chinh", thay_the_url=GOC, pham_vi_dieu_chinh="Chỉ tiêu"),
             tai_lieu(CU, nam_ap_dung=NAM - 1, phu_hop=False, ly_do="Sai năm")], ["Có một nguồn sai năm"]
        )):
            phien = api.tim_nguon(phien.id, self.db, self.user)
        self.assertEqual(len(phien.nguon), 3)
        self.assertEqual(phien.nguon[1].thay_the_url, GOC)
        for nguon_id in ([1, 2] if mau_thuan else [1]):
            api.chon_nguon(phien.id, nguon_id, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        return phien.id

    def _tao_ban_nhap(self, phien_id, ket_qua):
        with patch.object(api.ai, "extract_draft", return_value=ket_qua) as mock:
            phien = api.tao_ban_nhap(phien_id, self.db, self.user)
            self.assertTrue(all(n["lua_chon"] == "su_dung" and n["url"] != CU for n in mock.call_args.args[2]))
        return phien

    def test_gui_danh_muc_phuong_thuc_dang_ap_dung_cho_nam_cua_phien(self):
        phien_id = self._tao_phien()
        thpt = self.db.scalar(select(M.DmPhuongThucTuyenSinh).where(M.DmPhuongThucTuyenSinh.ma_phuong_thuc == "100"))
        thpt.nam_ap_dung_tu = thpt.nam_ap_dung_den = NAM
        thpt.giai_thich = "Dùng kết quả thi tốt nghiệp THPT."
        self.db.add_all([
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="990", ten_phuong_thuc="Đã hết hiệu lực", nam_ap_dung_den=NAM - 1),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="991", ten_phuong_thuc="Chưa áp dụng", nam_ap_dung_tu=NAM + 1),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="992", ten_phuong_thuc="Ngừng sử dụng", trang_thai=0),
        ])
        self.db.commit()

        with patch.object(api.ai, "extract_draft", return_value=trich_xuat()) as mock:
            api.tao_ban_nhap(phien_id, self.db, self.user)

        danh_muc = mock.call_args.kwargs["danh_muc_phuong_thuc"]
        self.assertEqual(len(danh_muc), 19)
        self.assertEqual(danh_muc[0]["ma_phuong_thuc"], "100")
        self.assertEqual(danh_muc[0]["giai_thich"], "Dùng kết quả thi tốt nghiệp THPT.")
        self.assertTrue({"990", "991", "992"}.isdisjoint(dong["ma_phuong_thuc"] for dong in danh_muc))

    def test_tinh_trang_nguon_tu_luc_tao_den_khi_chon_nguon_nam_hien_tai(self):
        phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user)
        self.assertEqual(phien.tinh_trang_nguon, "chua_tim_nguon")

        with patch.object(api.ai, "search_sources", return_value=([], [])):
            phien = api.tim_nguon(phien.id, self.db, self.user)
        self.assertEqual(phien.tinh_trang_nguon, "chua_co_nguon_phu_hop")
        danh_sach = api.danh_sach_phien(q=None, ma_truong=None, nam_tuyen_sinh=None, trang_thai=None,
                                       page=1, page_size=20, db=self.db)
        self.assertEqual(danh_sach.items[0].tinh_trang_nguon, "chua_co_nguon_phu_hop")

        diem_cu = tai_lieu(CU, nam_ap_dung=NAM - 1, loai="diem_lich_su", chi_diem_lich_su=True)
        with patch.object(api.ai, "inspect_source", return_value=diem_cu):
            phien = api.them_nguon(phien.id, ThemNguon(url=CU), self.db, self.user)
        phien = api.chon_nguon(phien.id, 1, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        self.assertEqual(phien.tinh_trang_nguon, "chua_co_nguon_phu_hop")

        with patch.object(api.ai, "inspect_source", return_value=tai_lieu(GOC)):
            phien = api.them_nguon(phien.id, ThemNguon(url=GOC), self.db, self.user)
        self.assertEqual(phien.tinh_trang_nguon, "cho_chon_nguon")
        phien = api.chon_nguon(phien.id, 2, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        self.assertEqual(phien.tinh_trang_nguon, "san_sang_tao_nhap")

    def test_chon_nhieu_nguon_giu_lua_chon_cu_va_khong_ghi_lai_khi_goi_lap(self):
        phien_id = self._tao_phien()
        ly_do = "Không áp dụng cho chương trình đang xét."
        api.chon_nguon(phien_id, 2, ChonNguon(lua_chon="loai", ly_do=ly_do), self.db, self.user)
        goc_moi = "https://example.edu.vn/thong-bao-2027.pdf"
        diem_cu = "https://example.edu.vn/diem-chuan-2026.pdf"
        with patch.object(api.ai, "search_sources", return_value=([
            tai_lieu(goc_moi),
            tai_lieu(diem_cu, nam_ap_dung=NAM - 1, loai="diem_lich_su", chi_diem_lich_su=True),
        ], [])):
            api.tim_nguon(phien_id, self.db, self.user)

        yeu_cau = api.ChonTatCaNguon(lua_chon="su_dung")
        phien = api.chon_nhieu_nguon(phien_id, yeu_cau, self.db, self.user)
        self.assertEqual([n.lua_chon for n in phien.nguon], ["su_dung", "loai", "chua_chon", "su_dung", "su_dung"])
        self.assertEqual(phien.nguon[1].ly_do_loai, ly_do)
        self.assertEqual(phien.lich_su[0].hanh_dong, "chon_nhieu_nguon")
        self.assertEqual(phien.lich_su[0].chi_tiet["nguon_ids"], [4, 5])
        self.assertEqual(phien.tinh_trang_nguon, "san_sang_tao_nhap")

        sua_lan = self.db.get(M.DatsPhienThuThap, phien_id).sua_lan
        goi_lai = api.chon_nhieu_nguon(phien_id, yeu_cau, self.db, self.user)
        self.assertEqual(goi_lai.lich_su, phien.lich_su)
        self.assertEqual(goi_lai.cap_nhat_luc, phien.cap_nhat_luc)
        self.assertEqual(self.db.get(M.DatsPhienThuThap, phien_id).sua_lan, sua_lan)

    def test_loi_dich_vu_ai_duoc_ghi_nhat_ky_va_co_the_thu_lai(self):
        phien_id = self._tao_phien()
        truoc = api.chi_tiet_phien(phien_id, None, self.db)
        loi_ai = api.ai.AdmissionAIError("Dịch vụ AI chưa trả về bản nháp.")
        with patch.object(api.ai, "extract_draft", side_effect=loi_ai), self.assertRaises(HTTPException) as loi:
            api.tao_ban_nhap(phien_id, self.db, self.user)

        self.assertEqual(loi.exception.status_code, 502)
        sau = api.chi_tiet_phien(phien_id, None, self.db)
        self.assertFalse(sau.dang_tao_ban_nhap)
        self.assertEqual(sau.trang_thai, truoc.trang_thai)
        self.assertEqual(sau.nguon, truoc.nguon)
        self.assertEqual(sau.lich_su[1:], truoc.lich_su)
        self.assertEqual(sau.lich_su[0].hanh_dong, "tao_ban_nhap_that_bai")
        self.assertEqual(sau.loi_tao_ban_nhap.message, str(loi_ai))
        self.assertEqual(sau.loi_tao_ban_nhap.xay_ra_luc, sau.cap_nhat_luc)
        with Session(self.db.get_bind()) as db_khac:
            ds = api.danh_sach_phien(None, None, None, api.THU_THAP, 1, 20, db_khac)
            self.assertEqual(ds.items[0].loi_tao_ban_nhap, sau.loi_tao_ban_nhap)
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 0)

        def trich_xuat_lai(*args, **kwargs):
            with Session(self.db.get_bind()) as db_khac:
                dang_tao = api.chi_tiet_phien(phien_id, None, db_khac)
                self.assertTrue(dang_tao.dang_tao_ban_nhap)
                self.assertIsNone(dang_tao.loi_tao_ban_nhap)
            return trich_xuat()

        with patch.object(api.ai, "extract_draft", side_effect=trich_xuat_lai):
            tao_lai = api.tao_ban_nhap(phien_id, self.db, self.user)
        self.assertEqual((tao_lai.trang_thai, tao_lai.phien_ban), (api.CHO_DUYET, 1))
        self.assertIsNone(tao_lai.loi_tao_ban_nhap)

    def test_luu_ban_nhap_va_canh_bao_khi_mot_nguon_bi_bo_qua(self):
        phien_id = self._tao_phien(mau_thuan=True)
        canh_bao = "Nguồn #2 không đọc được."
        ket_qua = {**trich_xuat(), "nguon_ids": [1], "loi_nguon": {2: canh_bao}, "ghi_chu": [canh_bao]}
        phien = self._tao_ban_nhap(phien_id, ket_qua)

        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))
        self.assertIsNone(phien.loi_tao_ban_nhap)
        self.assertIn(canh_bao, phien.ban_nhap.ghi_chu)
        self.assertEqual(phien.lich_su[0].chi_tiet["nguon_ids"], [1])
        self.assertEqual(phien.lich_su[0].chi_tiet["loi_nguon"], {"2": canh_bao})
        self.assertEqual(phien.nguon[1].lua_chon, "su_dung")
        self.assertEqual(phien.ban_nhap.nguon[1].lua_chon, "loai")

    def test_luu_nhap_trong_khi_khong_con_nguon_doc_duoc(self):
        phien_id = self._tao_phien()
        canh_bao = "Nguồn #1 không đọc được."
        phien = self._tao_ban_nhap(phien_id, {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {}},
            "nguon_ids": [], "loi_nguon": {1: canh_bao}, "ghi_chu": [canh_bao], "muc": [],
        })
        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))
        self.assertEqual(phien.ban_nhap.du_lieu["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"], [])
        self.assertIn(canh_bao, phien.ban_nhap.ghi_chu)
        self.assertTrue(phien.ban_nhap.loi)

    def test_da_dat_trang_thai_dang_tao_truoc_khi_goi_ai_va_chan_luot_trung(self):
        phien_id, user_id = self._tao_phien(), self.user.id

        def trich_xuat_trong_luc_dang_tao(*args, bao_tien_do, danh_muc_phuong_thuc):
            self.assertFalse(self.db.in_transaction())
            bao_tien_do("doc_nguon", 1, 3)
            with Session(self.db.get_bind()) as db_khac:
                phien = api.chi_tiet_phien(phien_id, None, db_khac)
                self.assertTrue(phien.dang_tao_ban_nhap)
                self.assertEqual(phien.trang_thai, api.THU_THAP)
                self.assertIsNotNone(phien.bat_dau_tao_ban_nhap_luc)
                self.assertIsNotNone(phien.luot_tao_ban_nhap)
                self.assertEqual(phien.tien_do_tao_ban_nhap.model_dump(), {"buoc": "doc_nguon", "da_xu_ly": 1, "tong": 3})
                ds = api.danh_sach_phien(None, None, None, api.THU_THAP, 1, 20, db_khac)
                self.assertTrue(ds.items[0].dang_tao_ban_nhap)
                user = db_khac.get(M.NguoiDung, user_id)
                for thao_tac in (
                    lambda: api.tao_ban_nhap(phien_id, db_khac, user),
                    lambda: api.chon_nguon(phien_id, 1, ChonNguon(lua_chon="chua_chon"), db_khac, user),
                    lambda: api.xoa_phien(phien_id, db_khac),
                ):
                    with self.assertRaises(HTTPException) as bi_chan:
                        thao_tac()
                    self.assertEqual(bi_chan.exception.status_code, 409)
                    self.assertTrue(bi_chan.exception.detail["dang_tao_ban_nhap"])
                    db_khac.rollback()
            return trich_xuat()

        with patch.object(api.ai, "extract_draft", side_effect=trich_xuat_trong_luc_dang_tao) as ai:
            phien = api.tao_ban_nhap(phien_id, self.db, self.user)
        ai.assert_called_once()
        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))
        self.assertFalse(phien.dang_tao_ban_nhap)
        self.assertIsNone(phien.tien_do_tao_ban_nhap)

    def test_luot_tao_qua_30_phut_van_co_the_luu(self):
        phien_id = self._tao_phien()
        luc_bat_dau = api._bay_gio()
        thoi_gian = luc_bat_dau

        def trich_xuat_lau(*args, bao_tien_do, danh_muc_phuong_thuc):
            nonlocal thoi_gian
            thoi_gian += timedelta(hours=1)
            bao_tien_do("trich_xuat", 1, 2)
            with Session(self.db.get_bind()) as db_khac:
                phien = api.chi_tiet_phien(phien_id, None, db_khac)
                self.assertTrue(phien.dang_tao_ban_nhap)
                self.assertEqual(phien.bat_dau_tao_ban_nhap_luc.replace(tzinfo=None), luc_bat_dau)
            return trich_xuat()

        with (
            patch.object(api, "_bay_gio", side_effect=lambda: thoi_gian),
            patch.object(api.ai, "extract_draft", side_effect=trich_xuat_lau),
        ):
            phien = api.tao_ban_nhap(phien_id, self.db, self.user)
        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))

    def test_dung_luot_tao_va_chan_ket_qua_cu_sau_khi_tao_lai(self):
        phien_id, user_id = self._tao_phien(), self.user.id

        def trich_xuat_luot_cu(*args, **kwargs):
            with Session(self.db.get_bind()) as db_moi:
                user = db_moi.get(M.NguoiDung, user_id)
                dang_tao = api.chi_tiet_phien(phien_id, None, db_moi)
                yeu_cau = DungTaoBanNhap(luot_tao_ban_nhap=dang_tao.luot_tao_ban_nhap)
                da_dung = api.dung_tao_ban_nhap(phien_id, yeu_cau, db_moi, user)
                self.assertFalse(da_dung.dang_tao_ban_nhap)
                self.assertEqual(da_dung.trang_thai, api.THU_THAP)
                self.assertIsNone(da_dung.loi_tao_ban_nhap)
                self.assertEqual(da_dung.lich_su[0].hanh_dong, "dung_tao_ban_nhap")

                def trich_xuat_luot_moi(*args, **kwargs):
                    with Session(self.db.get_bind()) as db_khac:
                        with self.assertRaises(HTTPException) as yeu_cau_cu:
                            api.dung_tao_ban_nhap(phien_id, yeu_cau, db_khac, db_khac.get(M.NguoiDung, user_id))
                        self.assertEqual(yeu_cau_cu.exception.status_code, 409)
                    return trich_xuat(chi_tieu=95)

                with patch.object(api.ai, "extract_draft", side_effect=trich_xuat_luot_moi):
                    self.assertEqual(api.tao_ban_nhap(phien_id, db_moi, user).phien_ban, 1)
            return trich_xuat(chi_tieu=80)

        with patch.object(api.ai, "extract_draft", side_effect=trich_xuat_luot_cu), self.assertRaises(HTTPException) as cu:
            api.tao_ban_nhap(phien_id, self.db, self.user)
        self.assertEqual(cu.exception.status_code, 409)
        phien = api.chi_tiet_phien(phien_id, None, self.db)
        self.assertEqual(phien.trang_thai, api.CHO_DUYET)
        self.assertEqual(phien.ban_nhap.du_lieu["dats_tuyen_sinh"]["chi_tieu"], 95)
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 1)

    def test_mau_thuan_sua_duyet_goi_lai_va_tai_dung_ban_chot(self):
        phien_id = self._tao_phien(mau_thuan=True)
        phien = self._tao_ban_nhap(phien_id, trich_xuat(chi_tieu=80, mau_thuan=True))
        self.assertEqual(phien.trang_thai, api.CHO_DUYET)
        self.assertEqual(self._dem(M.DatsTuyenSinh), 0)
        with self.assertRaises(HTTPException) as tai_truoc:
            api.tai_json(phien_id, self.db)
        self.assertEqual(tai_truoc.exception.status_code, 409)
        with self.assertRaises(HTTPException) as mau_thuan:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(mau_thuan.exception.status_code, 422)
        self.assertIn("mâu thuẫn", str(mau_thuan.exception.detail))
        self.db.rollback()

        da_sua = api.sua_ban_nhap(phien_id, SuaBanNhap(phien_ban=1, thay_doi=[{
            "duong_dan": CHI_TIEU, "gia_tri": 95, "dan_chung_ids": ["2"], "da_kiem_tra": True,
            "ghi_chu": "Phụ lục điều chỉnh từ 80 thành 95.",
        }], xac_nhan_doi_chieu={"chi_tieu": {
            "nguon_id": 2, "ly_do": "Phụ lục ghi tổng mới; chỉ tiêu chương trình vẫn theo bảng đã công bố.",
        }}),
            self.db, self.user)
        self.assertEqual(da_sua.phien_ban, 2)
        self.assertEqual(da_sua.lich_su[0].chi_tiet["thay_doi"][0]["truoc"], 80)
        self.assertEqual(da_sua.lich_su[0].chi_tiet["thay_doi"][0]["sau"], 95)
        self.assertEqual(api.chi_tiet_phien(phien_id, 1, self.db).ban_nhap.du_lieu["dats_tuyen_sinh"]["chi_tieu"], 80)
        with self.assertRaises(HTTPException) as cu:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(cu.exception.status_code, 409)
        self.db.rollback()

        duyet = api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=2), self.db, self.user)
        goi_lai = api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=2), self.db, self.user)
        de_an = self.db.get(M.DatsTuyenSinh, duyet.de_an_id)
        self.assertEqual((de_an.chi_tieu, de_an.trang_thai, de_an.trang_thai_xet_tuyen), (95, "nhap", 1))
        self.assertEqual(self._dem(M.XtLichSuImport), 1)
        self.assertEqual(self._dem(M.DatsTuyenSinh), 1)
        self.assertEqual(goi_lai.de_an_id, duyet.de_an_id)
        tep = api.tai_json(phien_id, self.db)
        self.assertIn("BKA_2027_tuyen_sinh.json", tep.headers["content-disposition"])
        self.assertEqual(json.loads(tep.body.decode("utf-8")), da_sua.ban_nhap.du_lieu)
        with self.assertRaises(HTTPException) as loi_xoa:
            api.xoa_phien(phien_id, self.db)
        self.assertEqual(loi_xoa.exception.status_code, 409)
        self.assertEqual(api.chi_tiet_phien(phien_id, None, self.db).de_an_id, duyet.de_an_id)
        self.assertEqual(self._dem(M.DatsTuyenSinh), 1)

    def test_hai_nhanh_khop_nhung_thieu_ma_trong_bang_cong_bo(self):
        phien_id = self._tao_phien()
        ket_qua = trich_xuat()
        ket_qua["doi_chieu_chuong_trinh"][0].update(cac_ma=["IT1", "IT2"], tong_cong_bo=2)
        phien = self._tao_ban_nhap(phien_id, ket_qua)
        ban_nhap = api.chi_tiet_phien(phien_id, phien.phien_ban, self.db).ban_nhap
        dats, quy_tac = ban_nhap.du_lieu["dats_tuyen_sinh"], ban_nhap.du_lieu["quy_tac_xet_tuyen"]
        self.assertEqual([ct["ma_xet_tuyen"] for ct in dats["dats_chuong_trinh_dao_tao"]], ["IT1"])
        self.assertEqual([ct["ma_xet_tuyen"] for ct in quy_tac["chuong_trinh"]], ["IT1"])
        self.assertEqual([ct["ma_cong_thuc"] for ct in quy_tac["cong_thuc"]], ["THPT"])
        self.assertTrue(any("thiếu mã công bố" in loi and "IT2" in loi for loi in phien.ban_nhap.loi))
        with self.assertRaises(HTTPException) as loi:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(loi.exception.status_code, 422)
        self.assertEqual(self._dem(M.DatsTuyenSinh), 0)

    def test_xac_nhan_pham_vi_khi_bang_ma_va_chi_tieu_chua_du(self):
        phien_id = self._tao_phien()
        ket_qua = trich_xuat()
        ket_qua["doi_chieu_chuong_trinh"] = []
        ket_qua["du_lieu"]["dats_tuyen_sinh"]["chi_tieu"] = 120
        muc_chi_tieu = next(muc for muc in ket_qua["muc"] if muc["duong_dan"] == CHI_TIEU)
        muc_chi_tieu["dan_chung"][0]["gia_tri"] = 120
        phien = self._tao_ban_nhap(phien_id, ket_qua)
        self.assertEqual(set(phien.ban_nhap.doi_chieu.can_xac_nhan), {"chuong_trinh", "chi_tieu"})
        with self.assertRaises(HTTPException) as loi:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(loi.exception.status_code, 422)
        self.db.rollback()
        with self.assertRaises(HTTPException) as sai_nguon:
            api.sua_ban_nhap(phien_id, SuaBanNhap(phien_ban=1, xac_nhan_doi_chieu={
                "chi_tieu": {"nguon_id": 3, "ly_do": "Nguồn của năm trước."},
            }), self.db, self.user)
        self.assertEqual(sai_nguon.exception.status_code, 422)
        self.db.rollback()
        phien = api.sua_ban_nhap(phien_id, SuaBanNhap(phien_ban=1, xac_nhan_doi_chieu={
            "chuong_trinh": {"nguon_id": 1, "ly_do": "Đã đối chiếu nhóm mã trong phụ lục đang áp dụng."},
            "chi_tieu": {"nguon_id": 1, "ly_do": "Chỉ tiêu tổng cho hai đợt; chương trình chỉ công bố đợt 1."},
        }), self.db, self.user)
        self.assertEqual(phien.phien_ban, 2)
        self.assertEqual(phien.ban_nhap.loi, [])
        duyet = api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=2), self.db, self.user)
        self.assertEqual(duyet.trang_thai, api.DA_DUYET)
        self.assertNotIn("doi_chieu", json.loads(api.tai_json(phien_id, self.db).body))

    def test_chan_chi_tieu_lech_khi_phan_bo_rieng_cung_pham_vi(self):
        phien_id = self._tao_phien()
        ket_qua = trich_xuat()
        du_lieu = ket_qua["du_lieu"]
        de_an = du_lieu["dats_tuyen_sinh"]
        quy_tac = du_lieu["quy_tac_xet_tuyen"]
        de_an["dats_chuong_trinh_dao_tao"][0].update(
            chi_tieu_tuyen_sinh=80, kieu_phan_bo_chi_tieu="theo_chuong_trinh",
            dats_ke_hoach_tuyen_sinh=[{"dot_tuyen_sinh": "Đợt 1", "pham_vi_tuyen_sinh": "Cả nước",
                                     "don_vi_chi_tieu": "sinh_vien"}],
        )
        quy_tac["chuong_trinh"][0]["chi_tieu"] = 80
        de_an["dats_chuong_trinh_dao_tao"].append({
            **de_an["dats_chuong_trinh_dao_tao"][0], "ma_xet_tuyen": "IT2", "ten_chuong_trinh": "Khoa học máy tính",
        })
        quy_tac["chuong_trinh"].append({
            **quy_tac["chuong_trinh"][0], "ma_chuong_trinh": "IT2", "ma_xet_tuyen": "IT2",
            "ten_chuong_trinh": "Khoa học máy tính",
        })
        ket_qua["doi_chieu_chuong_trinh"][0].update(cac_ma=["IT1", "IT2"], tong_cong_bo=2)
        ket_qua["muc"] = [{
            "duong_dan": p, "dan_chung": [{"nguon_id": 1, "vi_tri": "Trang 2", "trich_dan": str(v), "gia_tri": v}],
        } for p, v in _muc_du_lieu(du_lieu, set()).items() if v is not None]
        phien = self._tao_ban_nhap(phien_id, ket_qua)
        self.assertNotIn("chi_tieu", phien.ban_nhap.doi_chieu.can_xac_nhan)
        with self.assertRaises(HTTPException) as loi:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(loi.exception.status_code, 422)
        self.assertIn("tổng chỉ tiêu chương trình cùng phạm vi là 160", str(loi.exception.detail))

    def test_xoa_phien_chua_nhap_co_the_tao_lai_cung_truong_nam(self):
        phien_id = self._tao_phien()
        self._tao_ban_nhap(phien_id, trich_xuat())
        self.db.rollback()
        self.db.execute(text("PRAGMA foreign_keys = ON"))
        self.assertEqual(api.xoa_phien(phien_id, self.db).deleted, 1)
        self.assertEqual(self._dem(M.DatsPhienThuThap), 0)
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 0)
        self.assertEqual(self._dem(M.DatsNhatKyThuThap), 0)
        with self.assertRaises(HTTPException) as loi:
            api.chi_tiet_phien(phien_id, None, self.db)
        self.assertEqual(loi.exception.status_code, 400)

        phien_moi = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user)
        self.assertEqual(phien_moi.trang_thai, api.THU_THAP)
        self.assertIsNone(phien_moi.phien_ban)
        self.assertEqual(phien_moi.nguon, [])

    def test_trung_truong_nam_tra_link_de_an_va_giu_cho_duyet(self):
        phien_id = self._tao_phien()
        self._tao_ban_nhap(phien_id, trich_xuat())
        de_an = M.DatsTuyenSinh(ma_truong="BKA", nam_tuyen_sinh=NAM)
        self.db.add(de_an)
        self.db.commit()
        with self.assertRaises(HTTPException) as loi:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(loi.exception.status_code, 409)
        self.assertEqual(loi.exception.detail["de_an_id"], de_an.id)
        self.assertEqual(api.chi_tiet_phien(phien_id, None, self.db).trang_thai, api.CHO_DUYET)

    def test_duyet_hang_loat_giu_cac_phien_loi_va_lap_lai_khong_nhap_trung(self):
        mau_thuan = self._tao_phien(mau_thuan=True)
        self._tao_ban_nhap(mau_thuan, trich_xuat(chi_tieu=80, mau_thuan=True))
        hop_le, trung, sai_phien_ban = [self._tao_phien() for _ in range(3)]
        for phien_id in (hop_le, trung, sai_phien_ban):
            self._tao_ban_nhap(phien_id, trich_xuat())

        yeu_cau = api.DuyetHangLoatRequest(phien=[
            {"id": mau_thuan, "phien_ban": 1}, {"id": hop_le, "phien_ban": 1},
            {"id": trung, "phien_ban": 1}, {"id": sai_phien_ban, "phien_ban": 2},
        ])
        ket_qua = api.duyet_hang_loat(yeu_cau, self.db, self.user)
        self.assertEqual([(r.id, r.phien_ban) for r in ket_qua.da_duyet], [(hop_le, 1)])
        de_an_id = ket_qua.da_duyet[0].de_an_id
        self.assertEqual([(r.id, r.status) for r in ket_qua.that_bai], [(mau_thuan, 422), (trung, 409), (sai_phien_ban, 409)])
        self.assertEqual(ket_qua.that_bai[1].detail["de_an_id"], de_an_id)
        for phien_id in (mau_thuan, trung, sai_phien_ban):
            self.assertEqual(api.chi_tiet_phien(phien_id, None, self.db).trang_thai, api.CHO_DUYET)

        lap_lai = api.duyet_hang_loat(yeu_cau, self.db, self.user)
        self.assertEqual(lap_lai.da_duyet, ket_qua.da_duyet)
        self.assertEqual(self._dem(M.DatsTuyenSinh), 1)
        self.assertEqual(self._dem(M.XtLichSuImport), 1)

    def test_loi_danh_muc_hoan_tac_ca_de_an_va_quy_tac(self):
        phien_id = self._tao_phien()
        ket_qua = trich_xuat(ma_nganh=None)
        # Khối DATS hợp lệ, quy tắc lỗi mã ngành sau khi DATS đã được ghi trong transaction.
        ket_qua["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["ma_nganh"] = "9999999"
        ket_qua["muc"].append({"duong_dan": "/quy_tac_xet_tuyen/chuong_trinh/0/ma_nganh", "dan_chung": [
            {"nguon_id": 1, "vi_tri": "Trang 3", "trich_dan": "9999999", "gia_tri": "9999999"},
        ]})
        phien = self._tao_ban_nhap(phien_id, ket_qua)
        self.assertEqual(phien.ban_nhap.loi, [])
        with self.assertRaises(HTTPException) as loi:
            api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(loi.exception.status_code, 422)
        self.assertIn("9999999", str(loi.exception.detail))
        self.assertEqual(self._dem(M.DatsTuyenSinh), 0)
        self.assertEqual(self._dem(M.DatsChuongTrinhDaoTao), 0)
        self.assertEqual(self._dem(M.XtCongThuc), 0)
        self.assertEqual(api.chi_tiet_phien(phien_id, None, self.db).trang_thai, api.CHO_DUYET)

    def test_bo_sung_luu_phien_ban_va_nguon_cu(self):
        phien_id = self._tao_phien()
        self._tao_ban_nhap(phien_id, trich_xuat(chi_tieu=80))
        api.yeu_cau_bo_sung(phien_id, BoSungBanNhap(phien_ban=1, duong_dan=[CHI_TIEU], ly_do="Cần kiểm tra chỉ tiêu."), self.db, self.user)
        with patch.object(api.ai, "inspect_source", return_value=tai_lieu(
            "https://example.edu.vn/bo-sung.pdf", loai="phu_luc"
        )):
            api.them_nguon(phien_id, ThemNguon(url="https://example.edu.vn/bo-sung.pdf"), self.db, self.user)
        with self.assertRaises(HTTPException) as sai_nam:
            api.chon_nguon(phien_id, 3, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        self.assertEqual(sai_nam.exception.status_code, 422)
        self.db.rollback()
        with patch.object(api.ai, "extract_draft", return_value={"du_lieu": {}}), self.assertRaises(HTTPException) as loi:
            api.tao_ban_nhap(phien_id, self.db, self.user)
        self.assertEqual(loi.exception.status_code, 502)
        cho_bo_sung = api.chi_tiet_phien(phien_id, None, self.db)
        self.assertEqual(cho_bo_sung.trang_thai, api.BO_SUNG)
        self.assertFalse(cho_bo_sung.dang_tao_ban_nhap)
        self.assertEqual(cho_bo_sung.yeu_cau_bo_sung.ly_do, "Cần kiểm tra chỉ tiêu.")
        moi = self._tao_ban_nhap(phien_id, trich_xuat())
        self.assertEqual(moi.trang_thai, api.CHO_DUYET)
        self.assertEqual(moi.phien_ban, 2)
        self.assertEqual(len(moi.ban_nhap.nguon), 4)
        self.assertEqual(len(api.chi_tiet_phien(phien_id, 1, self.db).ban_nhap.nguon), 3)


class ThuThapPhanQuyenTests(unittest.TestCase):
    def test_nguoi_dung_thuong_khong_duoc_duyet_hoac_tai(self):
        app = FastAPI()
        app.include_router(api.router)
        app.dependency_overrides[get_db] = lambda: None
        client = TestClient(app)
        goc = "/de-an-tuyen-sinh/thu-thap/phien/1"
        duyet_hang_loat = "/de-an-tuyen-sinh/thu-thap/phien/duyet-hang-loat"
        phien = {"id": 1, "phien_ban": 1}
        self.assertEqual(client.get(goc + "/json").status_code, 401)
        self.assertEqual(client.delete(goc).status_code, 401)
        self.assertEqual(client.post(goc + "/dung-tao-ban-nhap", json={"luot_tao_ban_nhap": 1}).status_code, 401)
        self.assertEqual(client.post(duyet_hang_loat, json={"phien": [phien]}).status_code, 401)
        app.dependency_overrides[get_current_user] = lambda: M.NguoiDung(vai_tro=0)
        self.assertEqual(client.get(goc + "/json").status_code, 403)
        self.assertEqual(client.post(goc + "/duyet", json={"phien_ban": 1}).status_code, 403)
        self.assertEqual(client.delete(goc).status_code, 403)
        self.assertEqual(client.post(goc + "/dung-tao-ban-nhap", json={"luot_tao_ban_nhap": 1}).status_code, 403)
        self.assertEqual(client.post(duyet_hang_loat, json={"phien": [phien]}).status_code, 403)

        app.dependency_overrides[get_current_user] = lambda: M.NguoiDung(vai_tro=1)
        loi = client.post(duyet_hang_loat, json={"phien": [phien, {**phien, "phien_ban": 2}]})
        self.assertEqual(loi.status_code, 422)
        self.assertIn("Mỗi phiên chỉ được xuất hiện một lần", loi.json()["detail"][0]["msg"])


class TimNguonHttpTests(unittest.TestCase):
    def test_tim_nguon_khong_ap_tran_so_luong_tu_yeu_cau_cu(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        self.addCleanup(engine.dispose)
        for model in (M.DmTruong, M.NguoiDung, M.DatsPhienThuThap, M.DatsBanNhapThuThap, M.DatsNhatKyThuThap):
            model.__table__.create(engine)
        with Session(engine) as db:
            db.add(M.DmTruong(ma_truong="BKA", ten_truong="Trường BKA"))
            db.commit()

        def get_test_db():
            with Session(engine) as db:
                yield db

        app = FastAPI()
        app.include_router(api.router)
        app.dependency_overrides[get_db] = get_test_db
        app.dependency_overrides[get_current_user] = lambda: M.NguoiDung(id=1, ho_ten="Quản trị", vai_tro=1)

        urls = [GOC, PHU_LUC, "https://example.edu.vn/thong-bao-2027.pdf"]
        data = {"nguon": [tai_lieu(url, dung_truong_co_so=True) for url in urls]}
        output = [{"type": "web_search_call", "action": {"sources": [{"url": url} for url in urls]}}]

        with (
            TestClient(app) as client,
            patch.object(api.ai, "_openai", return_value=(data, output)) as openai,
        ):
            goc = "/de-an-tuyen-sinh/thu-thap/phien"
            phien = client.post(goc, json={"ma_truong": "BKA", "nam_tuyen_sinh": NAM})
            self.assertEqual(phien.status_code, 201, phien.text)
            tim_nguon = f"{goc}/{phien.json()['id']}/tim-nguon"

            for tham_so in ({}, {"json": {"so_nguon_toi_da": 1}}):
                with self.subTest(tham_so=tham_so):
                    ket_qua = client.post(tim_nguon, **tham_so)
                    self.assertEqual(ket_qua.status_code, 200, ket_qua.text)
                    luot_tim = ket_qua.json()["lich_su"][0]
                    self.assertEqual(luot_tim["chi_tiet"]["urls"], urls)
            self.assertEqual(openai.call_count, 2)
