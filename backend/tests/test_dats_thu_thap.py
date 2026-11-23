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
from app.services.dats_ban_nhap_thu_thap import _muc_du_lieu, dan_chung_diem_dung_nam, dan_chung_diem_sai_nam
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


def test_giu_dan_chung_cho_hoc_phi_theo_tin_chi_trong_ghi_chu():
    ghi_chu = "Học phí IT1 là 800.000 đồng/tín chỉ trong năm học 2026–2027."
    path = "/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/ghi_chu"
    du_lieu = {"dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [
        {"ghi_chu": ghi_chu}, {"ghi_chu": "Chờ tìm nguồn học phí."},
    ]}}
    dc = {"nguon_id": 1, "vi_tri": "Học phí", "trich_dan": ghi_chu, "gia_tri": ghi_chu}
    muc = api.lap_muc_ban_nhap(du_lieu, [{"duong_dan": path, "dan_chung": [dc]}],
                               [tai_lieu(GOC, id=1, lua_chon="su_dung")], NAM)
    assert [(r["duong_dan"], r["dan_chung_ids"]) for r in muc] == [(path, ["1"])]


def test_nam_diem_chuan_can_gan_voi_dong_hoac_muc_diem_tren_trang_nhieu_nam():
    def dung_nam(vi_tri, trich_dan):
        return dan_chung_diem_dung_nam(2026, {"vi_tri": vi_tri, "trich_dan": trich_dan})

    assert dung_nam("Đề án tuyển sinh năm 2027", "Điểm chuẩn năm 2026 của IT1 là 29,27.")
    assert dung_nam("Điểm trúng tuyển năm 2026", "IT1 | 100 | 29,27")
    assert dung_nam("Điểm chuẩn 2025 và 2026", "Năm tuyển sinh: 2026 | IT1 | 29,27")
    assert not dung_nam("Điểm chuẩn 2025 và 2026", "IT1 | 28,0 | 29,27")
    assert not dung_nam("Điểm chuẩn năm 2025", "Điểm chuẩn 2026 | IT1 | 29,27")
    assert not dung_nam("Điểm chuẩn", "Bài đăng ngày 09/08/2026. IT1 | 29,27")
    assert not dung_nam("Tuyển sinh 2027", "Điểm chuẩn IT1 cho thí sinh tốt nghiệp năm 2026.")
    assert not dung_nam("Phương thức tuyển sinh năm 2026", "Mã trường 100. IT1 | 29,27")
    assert dan_chung_diem_sai_nam(2027, {"vi_tri": "Điểm chuẩn", "trich_dan": "Điểm chuẩn 2026 của IT1 là 29,27."})
    assert dan_chung_diem_sai_nam(2026, {"vi_tri": "Điểm chuẩn | 2025 | 2026", "trich_dan": "IT1 | 28,0 | 29,27"})
    assert not dan_chung_diem_sai_nam(2026, {"vi_tri": "Thông báo", "trich_dan": "IT1 | 29,27"})


def test_dan_chung_diem_cu_trong_de_an_hien_tai_can_dung_url_va_dung_nam():
    path = "/quy_tac_xet_tuyen/diem_chuan/0/diem_chuan"
    dong = {"nam_tuyen_sinh": 2026, "nguon_du_lieu_url": GOC, "diem_chuan": 29.27}
    data = {"quy_tac_xet_tuyen": {"diem_chuan": [dong]}}
    dc = {"nguon_id": 1, "trich_dan": "IT1 | 29,27", "vi_tri": "Điểm chuẩn 2026", "gia_tri": 29.27}
    muc = [{"duong_dan": path, "dan_chung": [dc]}]

    def duoc_chon(nguon):
        ket_qua = api.lap_muc_ban_nhap(data, muc, [nguon], NAM)
        return next(i for i in ket_qua if i["duong_dan"] == path)["dan_chung_ids"]

    nguon = tai_lieu(GOC, id=1, lua_chon="su_dung")
    assert duoc_chon(nguon) == ["1"]
    assert not duoc_chon({**nguon, "url": CU})
    assert not duoc_chon({**nguon, "nam_ap_dung": 2025, "chi_diem_lich_su": True})
    dc["vi_tri"] = "Điểm trúng tuyển năm 2027"
    assert not duoc_chon(nguon)
    dong["nam_tuyen_sinh"] = NAM
    assert duoc_chon(nguon) == ["1"]
    dc["vi_tri"] = "Điểm trúng tuyển năm 2026"
    assert not duoc_chon(nguon)
    del dong["nam_tuyen_sinh"]
    assert not duoc_chon(nguon)


class ThuThapTuyenSinhTests(unittest.TestCase):
    def setUp(self):
        chon_lai = patch.object(api.ai, "chon_nguon_doc_lai", return_value=[])
        self.chon_lai = chon_lai.start()
        self.addCleanup(chon_lai.stop)
        noi = patch.object(api, "doi_chieu_lien_ket_ai")
        self.doi_chieu_lien_ket = noi.start()
        self.addCleanup(noi.stop)
        mo_hinh = patch.object(api, "muc_can_tim_bo_sung", return_value=[])
        self.ra_soat_ai = mo_hinh.start()
        self.addCleanup(mo_hinh.stop)
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

    def test_doi_chieu_o_diem_tinh_lai_sau_khi_nguoi_duyet_bo_dan_chung(self):
        phien_id = self._tao_phien()
        data = trich_xuat()
        muc_bang = "Mục: Điểm trúng tuyển · Bảng 1"
        hang = "| IT1 | A00 | 26,5 |"
        data["ra_soat_diem_chuan"] = {"nguon": [{"nguon_id": 1, "da_ra_soat": True}], "can_lam_ro": []}
        data["du_lieu"]["quy_tac_xet_tuyen"]["diem_chuan"] = [{
            "nam_tuyen_sinh": NAM, "nguon_du_lieu_url": GOC, "ma_xet_tuyen": "IT1",
            "diem_chuan": 26.5, "ma_to_hop": "A00", "thang_diem": 30,
        }]
        path = "/quy_tac_xet_tuyen/diem_chuan/0/diem_chuan"
        data["muc"].append({"duong_dan": path, "dan_chung": [
            {"nguon_id": 1, "vi_tri": muc_bang, "trich_dan": hang, "gia_tri": 26.5},
        ]})
        truoc = self._tao_ban_nhap(phien_id, data).ban_nhap.doi_chieu.diem_chuan
        self.assertEqual((truoc.so_o_da_khop, truoc.so_o_nhan_dien, truoc.can_doi_chieu), (1, 1, []))
        moi = api.sua_ban_nhap(phien_id, SuaBanNhap.model_validate({"phien_ban": 1, "thay_doi": [
            {"duong_dan": path, "dan_chung_ids": [], "ghi_chu": "Cần kiểm tra bản công bố."},
        ]}), self.db, self.user)
        self.assertEqual(moi.ban_nhap.doi_chieu.diem_chuan.so_o_da_khop, 0)
        self.assertIn("IT1", moi.ban_nhap.doi_chieu.diem_chuan.can_doi_chieu[0])
        self.assertEqual(self.db.get(M.DatsBanNhapThuThap, (phien_id, 1)).doi_chieu["diem_chuan"]["so_o_da_khop"], 1)

    def test_mot_luot_tu_tim_bo_sung_va_luu_mot_phien_ban_co_dan_chung(self):
        self.ra_soat_ai.side_effect = [["Học phí IT1 theo năm"], ["Hồ sơ diện riêng tại cơ sở 2"]]
        trang = "https://example.edu.vn/tuyen-sinh"
        hoc_phi = "https://example.edu.vn/hoc-phi"
        goc = trich_xuat()
        goc["du_lieu"]["thong_tin_import"] = {}
        quy_tac = goc["du_lieu"]["quy_tac_xet_tuyen"]
        for nhanh in (goc["du_lieu"]["dats_tuyen_sinh"], quy_tac["de_an"]):
            nhanh["nguon_du_lieu_url"] = trang
        for muc in goc["muc"]:
            for dc in muc["dan_chung"]:
                if dc["gia_tri"] == GOC:
                    dc["gia_tri"] = dc["trich_dan"] = trang
        phi = "/quy_tac_xet_tuyen/chuong_trinh/0/hoc_phi/hoc_phi_tu"
        them = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {
                "chuong_trinh": [{"ma_xet_tuyen": "IT1", "hoc_phi": {"hoc_phi_tu": 25000000}}],
            }},
            "muc": [{"duong_dan": phi, "dan_chung": [
                {"nguon_id": 2, "gia_tri": 25000000, "trich_dan": "IT1: 25 triệu đồng/năm", "vi_tri": "Học phí"},
            ]}], "ghi_chu": [], "nguon_ids": [2],
        }
        with (
            patch.object(api.ai, "search_sources", return_value=([tai_lieu(trang)], [])),
            patch.object(api.ai, "search_missing_sources", side_effect=[([tai_lieu(hoc_phi)], []), ([], [])]) as tim_bu,
            patch.object(api.ai, "extract_draft", side_effect=[goc, them]) as doc,
        ):
            phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user, tu_dong=True)

        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))
        self.assertEqual(phien.lich_su[0].chi_tiet["nguon_ids"], [1, 2])
        self.assertEqual([n.url for n in phien.ban_nhap.nguon], [trang, hoc_phi])
        self.assertIn("học phí", " ".join(tim_bu.call_args_list[0].args[2]).casefold())
        self.assertEqual(tim_bu.call_args_list[0].args[3], [trang])
        self.assertEqual(tim_bu.call_args_list[1].args[3], [trang, hoc_phi])
        self.assertEqual([n["url"] for n in doc.call_args_list[1].args[2]], [hoc_phi])
        self.assertTrue(all(c.kwargs["chi_html"] for c in doc.call_args_list))
        du_lieu = phien.ban_nhap.du_lieu
        self.assertEqual(du_lieu["dats_tuyen_sinh"]["chi_tieu"], 95)
        ct = du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"]
        self.assertEqual(len(ct), 1)
        self.assertEqual(ct[0]["hoc_phi"]["hoc_phi_tu"], 25000000)
        muc = next(m for m in phien.ban_nhap.muc if m.duong_dan == phi)
        self.assertEqual((muc.dan_chung[0].nguon_id, muc.dan_chung_ids), (2, ["1"]))
        bao_cao = self.db.get(M.DatsBanNhapThuThap, (phien.id, 1)).doi_chieu["muc_con_thieu"]
        self.assertEqual(bao_cao, ["Hồ sơ diện riêng tại cơ sở 2"])
        self.assertEqual(phien.ban_nhap.doi_chieu.trang_thai_ra_soat_ai, "da_ra_soat")
        self.assertEqual(self.ra_soat_ai.call_args.args[-2], ["Học phí IT1 theo năm"])
        self.assertIn(phi, [m["duong_dan"] for m in self.ra_soat_ai.call_args.args[2]])
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 1)

        # Lưu tay đánh dấu kết luận trước đã cũ. Chỉ AI thay đổi nội dung đánh giá.
        api.sua_ban_nhap(phien.id, SuaBanNhap.model_validate({"phien_ban": 1, "thay_doi": [
            {"duong_dan": phi, "gia_tri": None, "dan_chung_ids": [], "ghi_chu": "Sai mức phí."},
        ]}), self.db, self.user)
        sau = self.db.get(M.DatsBanNhapThuThap, (phien.id, 2)).doi_chieu
        self.assertEqual((sau["trang_thai_ra_soat_ai"], sau["muc_con_thieu"]), ("da_chinh_sua", bao_cao))
        self.assertEqual(self.db.get(M.DatsBanNhapThuThap, (phien.id, 1)).doi_chieu["muc_con_thieu"], bao_cao)

    def test_tu_dong_giu_lua_chon_va_ban_nhap_khi_tim_bu_loi(self):
        self.ra_soat_ai.return_value = ["Tìm chỉ tiêu của chương trình mới"]
        phien_id = self._tao_phien()
        trang = "https://example.edu.vn/hien-tai"
        loai = "https://example.edu.vn/thong-bao-cu"
        bo_chon = "https://example.edu.vn/bo-chon"
        with patch.object(api.ai, "search_sources", return_value=([tai_lieu(loai), tai_lieu(bo_chon)], [])):
            api.tim_nguon(phien_id, self.db, self.user)
        api.chon_nguon(phien_id, 4, ChonNguon(lua_chon="loai", ly_do="Không áp dụng"), self.db, self.user)
        api.chon_nguon(phien_id, 5, ChonNguon(lua_chon="chua_chon"), self.db, self.user)
        goc = {**trich_xuat(), "nguon_ids": [6]}
        with (
            patch.object(api.ai, "search_sources", return_value=([tai_lieu(loai + "?utm_source=x"), tai_lieu(trang)], [])),
            patch.object(api.ai, "search_missing_sources", side_effect=api.ai.AdmissionAIError("Hết thời gian.")),
            patch.object(api.ai, "extract_draft", return_value=goc) as doc,
        ):
            phien = api.tao_ban_nhap(phien_id, self.db, self.user, tu_dong=True)
        self.assertEqual([n["url"] for n in doc.call_args.args[2]], [trang])
        self.assertEqual(phien.nguon[0].lua_chon, "su_dung")
        self.assertEqual(phien.ban_nhap.nguon[0].lua_chon, "loai")  # PDF đã chọn từ trước
        self.assertEqual((phien.nguon[3].lua_chon, phien.nguon[4].lua_chon), ("loai", "chua_chon"))
        self.assertEqual(phien.ban_nhap.du_lieu["dats_tuyen_sinh"]["chi_tieu"], 95)
        self.assertIn("Hết thời gian.", " ".join(phien.canh_bao_nguon))

    def test_doc_lai_nguon_cu_tu_sua_phuong_an_thieu_du_luot_ra_soat_dau_loi(self):
        trang = "https://example.edu.vn/bang-to-hop"
        goc = trich_xuat()
        goc["ghi_chu"] = [f"Nhận xét của phần tài liệu {so}" for so in range(42)]
        goc["du_lieu"]["thong_tin_import"] = {}
        ct = goc["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]
        ct["phuong_an"] = []
        path = "/quy_tac_xet_tuyen/chuong_trinh/0/phuong_an"
        goc["muc"] = [m for m in goc["muc"] if not m["duong_dan"].startswith(path)]
        them = {
            "du_lieu": {"thong_tin_import": {}, "dats_tuyen_sinh": {}, "quy_tac_xet_tuyen": {
                "chuong_trinh": [{"ma_xet_tuyen": "IT1", "phuong_an": [{"ma_cong_thuc": "THPT", "to_hop": ["A00"]}]}]}},
            "nguon_ids": [1], "ghi_chu": [],
            "muc": [{"duong_dan": path + "/0/to_hop", "dan_chung": [
                {"nguon_id": 1, "gia_tri": ["A00"], "trich_dan": "IT1 | A00", "vi_tri": "Bảng tổ hợp"}]}],
        }
        self.ra_soat_ai.side_effect = [api.ai.AdmissionAIError("Phản hồi không hợp lệ"), []]
        self.chon_lai.return_value = [1]
        with (patch.object(api.ai, "search_sources", return_value=([tai_lieu(trang)], [])),
              patch.object(api.ai, "extract_draft", side_effect=[goc, them]) as doc,
              patch.object(api.ai, "search_missing_sources") as tim):
            phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user, tu_dong=True)

        tim.assert_not_called()
        self.assertEqual(self.doi_chieu_lien_ket.call_count, 2)
        self.assertIs(doc.call_args_list[0].kwargs["bo_nho"], doc.call_args_list[1].kwargs["bo_nho"])
        self.assertTrue(any("IT1" in m and "phuong_an" in m for m in doc.call_args.args[3]["muc_can_bo_sung"]))
        self.assertEqual(phien.ban_nhap.doi_chieu.muc_con_thieu, [])
        self.assertIn("Nhận xét của phần tài liệu 41", phien.ban_nhap.ghi_chu)
        self.assertEqual(phien.ban_nhap.doi_chieu.trang_thai_ra_soat_ai, "da_ra_soat")
        self.assertEqual(phien.ban_nhap.du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"][0]["to_hop"], ["A00"])
        self.assertEqual(next(m for m in phien.ban_nhap.muc if m.duong_dan == path + "/0/to_hop").dan_chung[0].nguon_id, 1)
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 1)

    def test_tu_doc_lai_khi_luot_dau_tai_html_that_bai(self):
        trang = "https://example.edu.vn/de-an"
        with (patch.object(api.ai, "search_sources", return_value=([tai_lieu(trang)], [])),
              patch.object(api.ai, "extract_draft", side_effect=[api.ai.LoiDocNguon({1: "Timeout"}), trich_xuat()]) as doc,
              patch.object(api.ai, "search_missing_sources") as tim):
            phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user, tu_dong=True)
        self.assertEqual(doc.call_count, 2)
        self.assertEqual(phien.trang_thai, api.CHO_DUYET)
        self.assertEqual(phien.phien_ban, 1)
        tim.assert_not_called()

    def test_mot_luot_nghien_cuu_truoc_cms_giu_ca_chi_tieu_va_cong_thuc_chua_ro_ma_bo(self):
        from app.services import dats_kiem_ke_cong_thuc, dats_ma_tran_thu_thap, dats_projection_cong_thuc

        url = "https://example.edu.vn/tuyen-sinh-2026"
        tieu_de = "Thông tin tuyển sinh 2026 của Đại học Bách khoa Hà Nội"
        row = "IT1 | Công nghệ thông tin | 300"
        expr = "Điểm hồ sơ = điểm tư duy + điểm thành tích + điểm thưởng"
        doc = api.ai._TaiLieu(url, tieu_de, [("Đầu trang", tieu_de), ("Danh mục", row), ("Diện 1.3", expr)], [])
        thu_tu = []
        def model(hd, data, *args, **kwargs):
            if hd == dats_ma_tran_thu_thap._HUONG_DAN:
                thu_tu.append("ma_tran")
                return {"nguon_xac_minh": [{"nguon_id": 1, "dung_truong_co_so": True, "nam_ap_dung": 2026,
                                            "ma_doan": 1, "da_doc_het_bang": True}],
                        "dong": [{"ma_xet_tuyen": "IT1", "ten_chuong_trinh": "Công nghệ thông tin",
                                  "chi_tieu": 300, "dien": None, "to_hop": None, "pham_vi": None,
                                  "dan_chung": [{"nguon_id": 1, "vi_tri": "Danh mục", "trich_dan": row}]}],
                        "can_lam_ro": []}, []
            if hd == dats_kiem_ke_cong_thuc._HUONG_DAN:
                thu_tu.append("cong_thuc")
                return {"phan": [{"nguon_id": 1, "da_doc_het": True, "can_lam_ro": [], "cong_thuc": [{
                    "ten": "Điểm hồ sơ năng lực", "pham_vi": "Diện 1.3", "ma_xet_tuyen": [], "bieu_thuc": expr,
                    "dan_chung": [{"vi_tri": "Diện 1.3", "trich_dan": expr}]}]}]}, []
            if hd == dats_projection_cong_thuc._CHI_DAN:
                thu_tu.append("chieu")
                return {"ket_qua": [{"stt": 0, "ly_do": "Cách xếp hạng riêng cho diện hồ sơ.",
                                     "cong_thuc_moi": {"ma_cong_thuc": "HSNL", "thang_diem": None}}]}, []
            raise AssertionError(hd[:80])

        def cms(truong, nam, nhom, nghien_cuu, **kwargs):
            thu_tu.append("cms")
            self.assertEqual(nghien_cuu["ma_tran_da_doc"][0]["chi_tieu"], 300)
            self.assertEqual(nghien_cuu["cong_thuc_da_doc_tu_nguon"][0]["bieu_thuc"], expr)
            kq = trich_xuat(chi_tieu=None)
            kq["du_lieu"]["thong_tin_import"] = {}
            kq["muc"] = []
            return kq
        with (patch.object(api.ai, "search_sources", return_value=([tai_lieu(url, nam_ap_dung=2026)], [])),
              patch.object(api.ai, "search_missing_sources", return_value=([], [])),
              patch.object(api.ai, "_doc_cac_nguon", return_value={1: doc}),
              patch.object(api.ai, "_trich_xuat_nhom", side_effect=cms),
              patch.object(api.ai, "_bo_sung_dan_chung_cong_thuc", return_value=[]),
              patch.object(api.ai, "_openai", side_effect=model)):
            phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=2026), self.db, self.user, tu_dong=True)
        self.assertEqual(thu_tu, ["ma_tran", "cong_thuc", "cms", "chieu"])
        self.assertEqual((phien.trang_thai, phien.phien_ban), (api.CHO_DUYET, 1))
        ban = phien.ban_nhap
        self.assertEqual(ban.du_lieu["quy_tac_xet_tuyen"]["chuong_trinh"][0]["chi_tieu"], 300)
        hs = next(r for r in ban.du_lieu["quy_tac_xet_tuyen"]["cong_thuc"] if r["ma_cong_thuc"] == "HSNL")
        self.assertIn(expr, hs["mo_ta_cong_thuc"])
        self.assertIsNone(hs["ma_phuong_thuc_cua_bo"])
        self.assertEqual(ban.doi_chieu.ma_tran.so_ma_da_ghi, 1)
        self.assertEqual(ban.doi_chieu.cong_thuc.cong_thuc[0].trang_thai, "da_ghi_mo_ta")

    def test_chuyen_sang_trang_chinh_thuc_khac_khi_trang_dau_van_loi(self):
        cu, moi = "https://example.edu.vn/de-an", "https://example.edu.vn/phong-dao-tao"
        bai_mat = api.ai.LoiDocNguon({1: "Trang không phản hồi"})
        ket_qua = trich_xuat()
        for muc in ket_qua["muc"]:
            for dc in muc["dan_chung"]:
                dc["nguon_id"] = 2
        with (patch.object(api.ai, "search_sources", return_value=([tai_lieu(cu)], [])),
              patch.object(api.ai, "search_missing_sources", return_value=([tai_lieu(moi)], [])) as tim,
              patch.object(api.ai, "extract_draft", side_effect=[bai_mat, bai_mat, ket_qua]) as doc):
            phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user, tu_dong=True)
        tim.assert_called_once()
        self.assertEqual([n["url"] for n in doc.call_args.args[2]], [moi])
        self.assertEqual(phien.ban_nhap.nguon[0].ly_do_loai, "Trang không phản hồi")
        self.assertEqual(phien.lich_su[0].chi_tiet["nguon_ids"], [2])
        self.assertEqual(self._dem(M.DatsBanNhapThuThap), 1)

    def test_ai_khong_de_nghi_tim_thi_dung_va_phan_biet_loi_ra_soat(self):
        trang = "https://example.edu.vn/tuyen-sinh"
        for ket_qua, trang_thai, muc in (
            ([], "da_ra_soat", []),
            (api.ai.AdmissionAIError("Không nhận được đánh giá"), "chua_hoan_tat", None),
        ):
            with (self.subTest(trang_thai=trang_thai),
                  patch.object(api.ai, "search_sources", return_value=([tai_lieu(trang)], [])),
                  patch.object(api.ai, "extract_draft", return_value=trich_xuat()),
                  patch.object(api.ai, "search_missing_sources") as tim):
                self.ra_soat_ai.side_effect = [ket_qua]
                phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user, tu_dong=True)
                tim.assert_not_called()
                self.assertEqual(phien.ban_nhap.doi_chieu.trang_thai_ra_soat_ai, trang_thai)
                self.assertEqual(phien.ban_nhap.doi_chieu.muc_con_thieu, muc)

    def test_ai_nhan_duoc_ma_chi_co_trong_bang_nguon_de_danh_gia(self):
        from app.services.dats_do_phu_thu_thap import muc_can_tim_bo_sung

        phien_id = self._tao_phien()
        data = trich_xuat()
        bang = {"nguon_id": 1, "vi_tri": "Chương trình tại cơ sở B", "trich_dan": "Hai mã IT1, M2.",
                "cac_ma": ["IT1", "M2"], "tong_cong_bo": 2, "don_vi_tong": "mã xét tuyển", "pham_vi": "phan_pham_vi"}
        data["doi_chieu_chuong_trinh"] = [bang]
        self.ra_soat_ai.side_effect = muc_can_tim_bo_sung
        def doc(chi_dan, payload, gioi_han):
            self.assertEqual(payload["nhan_xet_khi_doc"]["bang_chuong_trinh"], [bang])
            self.assertNotIn("M2", [m["gia_tri"] for m in payload["ban_nhap"]])
            return {"muc_con_thieu": ["Lần theo chương trình M2 tại cơ sở B."]}, []
        with patch.object(api.ai, "_openai", side_effect=doc):
            ban = self._tao_ban_nhap(phien_id, data).ban_nhap
        self.assertEqual(ban.doi_chieu.muc_con_thieu, ["Lần theo chương trình M2 tại cơ sở B."])

    def test_nguoi_duyet_sua_va_bo_dan_chung_khong_can_ghi_ly_do(self):
        phien_id = self._tao_phien()
        self._tao_ban_nhap(phien_id, trich_xuat())
        def luu(so_ban, *cac_muc):
            return api.sua_ban_nhap(phien_id, SuaBanNhap.model_validate({
                "phien_ban": so_ban, "thay_doi": cac_muc,
            }), self.db, self.user)

        ban2 = luu(1, {"duong_dan": CHI_TIEU, "gia_tri": 101},
                   {"duong_dan": "/dats_tuyen_sinh/gioi_thieu", "gia_tri": "Cập nhật bởi người duyệt."})
        muc2 = next(m for m in ban2.ban_nhap.muc if m.duong_dan == CHI_TIEU)
        self.assertEqual(ban2.ban_nhap.du_lieu["dats_tuyen_sinh"]["chi_tieu"], 101)
        self.assertTrue(muc2.dan_chung_ids)
        self.assertFalse(muc2.da_kiem_tra)
        self.assertTrue(any(m["duong_dan"] == CHI_TIEU and m["sau"] == 101 for m in ban2.lich_su[0].chi_tiet["thay_doi"]))

        ban3 = luu(2, {"duong_dan": CHI_TIEU, "dan_chung_ids": []})
        self.assertFalse(next(m.dan_chung_ids for m in ban3.ban_nhap.muc if m.duong_dan == CHI_TIEU))
        self.assertEqual(self.db.get(M.DatsBanNhapThuThap, (phien_id, 1)).du_lieu["dats_tuyen_sinh"]["chi_tieu"], 95)
        for sai in ({"duong_dan": CHI_TIEU, "dan_chung_ids": ["khong-ton-tai"]},
                    {"duong_dan": "/thong_tin_import/ma_truong", "gia_tri": "KHAC"}):
            with self.subTest(sai=sai), self.assertRaises(HTTPException) as loi:
                luu(3, sai)
            self.assertEqual(loi.exception.status_code, 422)

    def test_gui_danh_muc_phuong_thuc_dang_ap_dung_cho_nam_cua_phien(self):
        phien_id = self._tao_phien()
        url_cu = "https://example.edu.vn/diem-chuan-2024"
        with patch.object(api.ai, "inspect_source", return_value=tai_lieu(
            url_cu, nam_ap_dung=2024, loai="diem_lich_su", chi_diem_lich_su=True,
        )):
            api.them_nguon(phien_id, ThemNguon(url=url_cu), self.db, self.user)
        api.chon_nguon(phien_id, 4, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        with patch.object(api.ai, "extract_draft", return_value=trich_xuat()) as mock:
            api.tao_ban_nhap(phien_id, self.db, self.user)

        ky_nay = {d["ma_phuong_thuc"]: d["ten_phuong_thuc"] for d in mock.call_args.kwargs["danh_muc_phuong_thuc"]}
        lich_su = mock.call_args.kwargs["danh_muc_lich_su"]
        self.assertEqual(set(lich_su), {2024, 2025, 2026})
        self.assertEqual(lich_su[2025], [])
        ky_truoc = {d["ma_phuong_thuc"]: d["ten_phuong_thuc"] for d in lich_su[2026]}
        self.assertEqual((len(ky_nay), len(ky_truoc)), (11, 19))
        self.assertIn("cử tuyển", ky_nay["301"])
        self.assertIn("Điều 8", ky_truoc["301"])
        self.assertIn("chứng chỉ quốc tế", ky_nay["500"])
        self.assertIn("phương thức khác", ky_truoc["500"])
        self.assertNotIn("415", ky_nay)
        self.assertNotIn("600", ky_truoc)

    def test_danh_muc_nam_khac_can_ban_ghi_con_hieu_luc_co_nam_ap_dung(self):
        nam_cu = 2025
        self.db.add_all([
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="990", ten_phuong_thuc="Đã hết hiệu lực", nam_ap_dung_den=nam_cu - 1),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="991", ten_phuong_thuc="Chưa áp dụng", nam_ap_dung_tu=nam_cu + 1),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="992", ten_phuong_thuc="Ngừng sử dụng", trang_thai=0, nam_ap_dung_tu=nam_cu),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="993", ten_phuong_thuc="Có hiệu lực", nam_ap_dung_tu=nam_cu),
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc="994", ten_phuong_thuc="Mã nội bộ", nam_ap_dung_tu=nam_cu,
                                    pham_vi_ap_dung="truong"),
        ])
        self.db.commit()
        self.assertEqual([d["ma_phuong_thuc"] for d in api._danh_muc_phuong_thuc(self.db, nam_cu)], ["993"])

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

    def test_tim_lai_giu_nguon_da_xac_minh_va_lua_chon(self):
        phien = api.tao_phien(PhienThuThapCreate(ma_truong="BKA", nam_tuyen_sinh=NAM), self.db, self.user)
        url = "https://example.edu.vn/thong-tin-tuyen-sinh?id=42"
        with patch.object(api.ai, "inspect_source", return_value=tai_lieu(url)):
            phien = api.them_nguon(phien.id, ThemNguon(url=url), self.db, self.user)
        phien = api.chon_nguon(phien.id, phien.nguon[0].id, ChonNguon(lua_chon="su_dung"), self.db, self.user)
        da_chon = phien.nguon[0]
        nguon_tim_lai = tai_lieu(f"{url}&utm_source=search", nam_ap_dung=None, phu_hop=False)
        url_moi = "https://example.edu.vn/thong-tin-tuyen-sinh?id=43"
        with patch.object(api.ai, "search_sources", return_value=([nguon_tim_lai, tai_lieu(url_moi)], [])):
            phien = api.tim_nguon(phien.id, self.db, self.user)

        self.assertEqual(len(phien.nguon), 2)
        self.assertEqual(phien.nguon[0], da_chon)
        self.assertEqual(phien.nguon[1].url, url_moi)
        self.assertEqual(phien.tinh_trang_nguon, "san_sang_tao_nhap")

        nguon_sai_nam = tai_lieu(url, nam_ap_dung=NAM - 1, phu_hop=False)
        with patch.object(api.ai, "inspect_source", return_value=nguon_sai_nam):
            phien = api.them_nguon(phien.id, ThemNguon(url=url), self.db, self.user)

        self.assertEqual(phien.nguon[0].id, da_chon.id)
        self.assertEqual(phien.nguon[0].nam_ap_dung, NAM - 1)
        self.assertEqual(phien.nguon[0].lua_chon, "chua_chon")

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

        def trich_xuat_trong_luc_dang_tao(*args, bao_tien_do, **kwargs):
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
        luc_bat_dau = api.bay_gio()
        thoi_gian = luc_bat_dau

        def trich_xuat_lau(*args, bao_tien_do, **kwargs):
            nonlocal thoi_gian
            thoi_gian += timedelta(hours=1)
            bao_tien_do("trich_xuat", 1, 2)
            with Session(self.db.get_bind()) as db_khac:
                phien = api.chi_tiet_phien(phien_id, None, db_khac)
                self.assertTrue(phien.dang_tao_ban_nhap)
                self.assertEqual(phien.bat_dau_tao_ban_nhap_luc.replace(tzinfo=None), luc_bat_dau)
            return trich_xuat()

        with (
            patch.object(api, "bay_gio", side_effect=lambda: thoi_gian),
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
        self.assertEqual(phien.ban_nhap.loi, [])
        self.assertTrue(any("mâu thuẫn" in x for x in phien.ban_nhap.doi_chieu.canh_bao_dan_chung))

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

    def test_nguoi_duyet_quyet_dinh_khi_ai_bao_thieu_ma_va_thieu_dan_chung(self):
        phien_id = self._tao_phien()
        ket_qua = trich_xuat()
        ket_qua["doi_chieu_chuong_trinh"][0].update(cac_ma=["IT1", "IT2"], tong_cong_bo=2)
        ket_qua["muc"] = []
        phien = self._tao_ban_nhap(phien_id, ket_qua)
        self.assertEqual(phien.ban_nhap.loi, [])
        self.assertTrue(phien.ban_nhap.doi_chieu.canh_bao_dan_chung)
        self.assertEqual(phien.ban_nhap.doi_chieu.nguon[0]["cac_ma"], ["IT1", "IT2"])
        duyet = api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(duyet.trang_thai, api.DA_DUYET)

    def test_nguoi_duyet_tu_danh_gia_phan_bo_chi_tieu(self):
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
        self.assertEqual(phien.ban_nhap.loi, [])
        duyet = api.duyet_va_nhap(phien_id, PhienBanRequest(phien_ban=1), self.db, self.user)
        self.assertEqual(duyet.trang_thai, api.DA_DUYET)

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
        sai_khoa = self._tao_phien()
        sai = trich_xuat()
        sai["du_lieu"]["quy_tac_xet_tuyen"]["chuong_trinh"][0]["phuong_an"][0]["ma_cong_thuc"] = "CHUA_CO"
        self._tao_ban_nhap(sai_khoa, sai)
        hop_le, trung, sai_phien_ban = [self._tao_phien() for _ in range(3)]
        for phien_id in (hop_le, trung, sai_phien_ban):
            self._tao_ban_nhap(phien_id, trich_xuat())

        yeu_cau = api.DuyetHangLoatRequest(phien=[
            {"id": sai_khoa, "phien_ban": 1}, {"id": hop_le, "phien_ban": 1},
            {"id": trung, "phien_ban": 1}, {"id": sai_phien_ban, "phien_ban": 2},
        ])
        ket_qua = api.duyet_hang_loat(yeu_cau, self.db, self.user)
        self.assertEqual([(r.id, r.phien_ban) for r in ket_qua.da_duyet], [(hop_le, 1)])
        de_an_id = ket_qua.da_duyet[0].de_an_id
        self.assertEqual([(r.id, r.status) for r in ket_qua.that_bai], [(sai_khoa, 422), (trung, 409), (sai_phien_ban, 409)])
        self.assertEqual(ket_qua.that_bai[1].detail["de_an_id"], de_an_id)
        for phien_id in (sai_khoa, trung, sai_phien_ban):
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
    def setUp(self):
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        self.addCleanup(engine.dispose)
        for model in (M.DmTruong, M.NguoiDung, M.DatsPhienThuThap, M.DatsBanNhapThuThap, M.DatsNhatKyThuThap,
                      M.DmPhuongThucTuyenSinh):
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
        self.app = app

    def test_tu_tao_phien_chay_nen_va_giu_nguon_khi_doc_that_bai(self):
        trang = "https://example.edu.vn/tuyen-sinh"
        with (
            TestClient(self.app) as client,
            patch.object(api.ai, "search_sources", return_value=([tai_lieu(trang)], ["Chỉ có một trang chính thức."])),
            patch.object(api.ai, "search_missing_sources", return_value=([], [])),
            patch.object(api.ai, "extract_draft", side_effect=api.ai.LoiDocNguon({1: "Không đọc được HTML."})),
        ):
            goc = "/de-an-tuyen-sinh/thu-thap/phien"
            tao = client.post(goc + "?tu_dong=true", json={"ma_truong": "BKA", "nam_tuyen_sinh": NAM})
            self.assertEqual(tao.status_code, 201, tao.text)
            self.assertTrue(tao.json()["dang_tao_ban_nhap"])
            self.assertEqual(tao.json()["tien_do_tao_ban_nhap"]["buoc"], "tim_nguon")
            sau = client.get(f"{goc}/{tao.json()['id']}").json()
            self.assertFalse(sau["dang_tao_ban_nhap"])
            self.assertEqual(sau["loi_tao_ban_nhap"]["nguon_ids"], [sau["nguon"][0]["id"]])
            self.assertEqual(sau["nguon"][0]["url"], trang)
            self.assertEqual(sau["canh_bao_nguon"], ["Chỉ có một trang chính thức."])
            self.assertIsNone(sau["ban_nhap"])

    def test_tim_nguon_khong_ap_tran_so_luong_tu_yeu_cau_cu(self):
        urls = [f"https://example.edu.vn/{trang}" for trang in ("de-an-2027", "dieu-chinh-2027", "thong-bao-2027")]
        data = {"nguon": [tai_lieu(url, dung_truong_co_so=True) for url in urls]}
        output = [{"type": "web_search_call", "action": {"sources": [{"url": url} for url in urls]}}]

        with (
            TestClient(self.app) as client,
            patch.object(api.ai, "_openai", return_value=(data, output)),
        ):
            goc = "/de-an-tuyen-sinh/thu-thap/phien"
            phien = client.post(goc, json={"ma_truong": "BKA", "nam_tuyen_sinh": NAM})
            self.assertEqual(phien.status_code, 201, phien.text)
            tim_nguon = f"{goc}/{phien.json()['id']}/tim-nguon"

            for tham_so in ({}, {"json": {"so_nguon_toi_da": 1}}):
                with self.subTest(tham_so=tham_so):
                    ket_qua = client.post(tim_nguon, **tham_so)
                    self.assertEqual(ket_qua.status_code, 200, ket_qua.text)
                    phien = ket_qua.json()
                    luot_tim = phien["lich_su"][0]
                    self.assertEqual(luot_tim["chi_tiet"]["urls"], urls)
                    self.assertEqual([n["url"] for n in phien["nguon"]], urls)
