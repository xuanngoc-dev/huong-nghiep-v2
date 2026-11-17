import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import func, select

from app.api.v1.endpoints.xt_quy_tac import doi_trang_thai_quy_tac, get_quy_tac, import_quy_tac
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.nguoi_dung import NguoiDung
from app.models.xt_cong_thuc import XtCongThuc
from app.schemas.xt_quy_tac import XtImportRequest, XtTrangThaiWrite
from tests import test_xet_tuyen_ghi as ghi
from tests.test_xet_tuyen_import import DANH_MUC, _mau


class XtQuyTacApiTests(unittest.TestCase):
    """Bước 2.5: API xem và import quy tắc xét tuyển của một đề án."""

    # Dùng lại CSDL SQLite của test phần ghi (không kế thừa để không chạy lại các test đó).
    setUp = ghi.XetTuyenGhiTests.setUp
    tearDown = ghi.XetTuyenGhiTests.tearDown

    def _chuan_bi(self):
        for model in (NguoiDung, DmMonHoc, DmBaiThiDanhGia):
            model.__table__.create(self.db.get_bind())
        self.admin = NguoiDung(ho_ten="Quản trị", email="admin@vd.vn", mat_khau="x", vai_tro=1)
        self.de_an = DatsTuyenSinh(ma_truong="BKA", nam_tuyen_sinh=2026, ten_de_an="BKA 2026")
        self.db.add_all([self.admin, self.de_an])
        # Bảng tổ hợp mang đúng id của danh mục giả để API ra được mã tổ hợp của phương án.
        self.db.add_all(
            DmToHopMonHoc(id=to_hop_id, ma_to_hop=ma, ten_to_hop=ma, ds_mon_hoc=[]) for ma, to_hop_id in DANH_MUC.to_hop.items()
        )
        self.db.commit()
        patcher = patch("app.services.xet_tuyen_ghi.DanhMucXetTuyen.tu_csdl", return_value=DANH_MUC)
        patcher.start()
        self.addCleanup(patcher.stop)
        # File import lưu vào thư mục tạm, không ghi vào logs/ thật.
        thu_muc = tempfile.TemporaryDirectory()
        self.addCleanup(thu_muc.cleanup)
        self.log_dir = Path(thu_muc.name)
        log_patcher = patch("app.core.logging.IMPORT_LOG_DIR", self.log_dir)
        log_patcher.start()
        self.addCleanup(log_patcher.stop)

    def _import(self, du_lieu, de_an_id=None):
        payload = XtImportRequest(du_lieu=du_lieu, ten_file="mau_BKA_2026.json")
        return import_quy_tac(de_an_id or self.de_an.id, payload, self.db, self.admin)

    def _loi_400(self, ham, *args):
        with self.assertRaises(HTTPException) as caught:
            ham(*args)
        self.assertEqual(caught.exception.status_code, 400)
        return caught.exception.detail

    def test_chua_import_tra_danh_sach_rong(self):
        self._chuan_bi()
        quy_tac = get_quy_tac(self.de_an.id, self.db)
        self.assertEqual((quy_tac.cong_thuc, quy_tac.nhom_dieu_kien, quy_tac.lich_su), ([], [], []))
        self.assertEqual(quy_tac.trang_thai_xet_tuyen, 0)

    def test_de_an_khong_ton_tai_tra_400(self):
        self._chuan_bi()
        self.assertIn("id = 999", self._loi_400(get_quy_tac, 999, self.db))
        self.assertIn("id = 999", self._loi_400(self._import, _mau("mau_BKA_2026.json"), 999))

    def test_file_khac_truong_bi_tu_choi(self):
        self._chuan_bi()
        detail = self._loi_400(self._import, _mau("mau_NTH_2026.json"))
        self.assertIn("trường NTH năm 2026", detail)
        self.assertIn("trường BKA năm 2026", detail)

    def test_file_loi_tra_danh_sach_loi_va_khong_ghi(self):
        self._chuan_bi()
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["chuong_trinh"][0]["phuong_an"].append({"ma_cong_thuc": "KHONG_CO"})
        detail = self._loi_400(self._import, du_lieu)
        self.assertTrue(any("KHONG_CO" in x for x in detail["loi"]))
        self.assertIn("thong_bao", detail)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(XtCongThuc)), 0)

    def test_file_loi_luu_vao_log_kem_du_loi_va_gia_tri_sai(self):
        self._chuan_bi()
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["cong_thuc"][0]["kieu_tinh"] = "KHONG_HOP_LE"
        detail = self._loi_400(self._import, du_lieu)
        self.assertTrue(any('(nhận: "KHONG_HOP_LE")' in x for x in detail["loi"]))
        files = list(self.log_dir.glob("*/*_quy_tac_BKA_2026_loi.json"))
        self.assertEqual(len(files), 1)
        noi_dung = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(noi_dung["loi"], detail["loi"])
        self.assertEqual(noi_dung["du_lieu"]["cong_thuc"][0]["kieu_tinh"], "KHONG_HOP_LE")

    def test_import_roi_xem_quy_tac(self):
        self._chuan_bi()
        ket_qua = self._import(_mau("mau_BKA_2026.json"))
        self.assertEqual((ket_qua.de_an_id, ket_qua.so_dong["xt_phuong_an"]), (self.de_an.id, 501))
        quy_tac = get_quy_tac(self.de_an.id, self.db)
        self.assertEqual(quy_tac.trang_thai_xet_tuyen, 1)
        self.assertEqual(len(quy_tac.cong_thuc), 7)
        self.assertEqual(sum(ct.so_phuong_an for ct in quy_tac.cong_thuc), 501)
        bf1 = next(ct for ct in quy_tac.chuong_trinh if ct.ma_xet_tuyen == "BF1")
        theo_cong_thuc = {pa.ma_cong_thuc: pa.to_hop for pa in bf1.phuong_an}
        self.assertEqual(theo_cong_thuc["BKA_THPT_30"], ["A00", "B00", "D07"])
        self.assertEqual(theo_cong_thuc["BKA_THPT_K01"], ["BKA-K01"])
        self.assertEqual(theo_cong_thuc["BKA_TSA"], [])
        self.assertEqual(len(quy_tac.nhom_dieu_kien), 32)
        self.assertTrue(all(n.dieu_kien for n in quy_tac.nhom_dieu_kien))
        self.assertEqual(quy_tac.lich_su[0].nguoi_import, "Quản trị")
        self.assertEqual(quy_tac.lich_su[0].so_dong["xt_cong_thuc"], 7)

    def test_doi_trang_thai(self):
        self._chuan_bi()
        detail = self._loi_400(doi_trang_thai_quy_tac, self.de_an.id, XtTrangThaiWrite(trang_thai_xet_tuyen=2), self.db)
        self.assertIn("chưa có quy tắc", detail)
        self._import(_mau("mau_BKA_2026.json"))
        kq = doi_trang_thai_quy_tac(self.de_an.id, XtTrangThaiWrite(trang_thai_xet_tuyen=2), self.db)
        self.assertEqual(kq.trang_thai_xet_tuyen, 2)
        self.assertEqual(get_quy_tac(self.de_an.id, self.db).trang_thai_xet_tuyen, 2)
        self.assertEqual(doi_trang_thai_quy_tac(self.de_an.id, XtTrangThaiWrite(trang_thai_xet_tuyen=0), self.db).trang_thai_xet_tuyen, 0)
        self.assertIn("id = 999", self._loi_400(doi_trang_thai_quy_tac, 999, XtTrangThaiWrite(trang_thai_xet_tuyen=1), self.db))



if __name__ == "__main__":
    unittest.main()
