"""Phiên khảo sát lưu định hướng người dùng chọn khi làm bài (cột dinh_huong)."""

import unittest
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.api.v1.endpoints import tn_phien_khao_sat as phien_api
from app.constants.doi_tuong_ap_dung import DOI_TUONG_DI_LAM
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_chi_tiet_tra_loi import TnChiTietTraLoi
from app.models.tn_phien_khao_sat import TnPhienKhaoSat


class TestPhienDinhHuong(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (TnPhienKhaoSat, TnChiTietTraLoi, DmLoaiCauHoi, TnCauHoiTracNghiem, DmNhomTinhCachHolland):
            model.__table__.create(engine)
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _tao_phien(self, doi_tuong_ap_dung):
        # Bỏ qua bước chọn câu hỏi (cần dữ liệu câu hỏi và JSON_CONTAINS của MySQL).
        with patch.object(phien_api, "_chon_cau_hoi", return_value=[(1, 10), (1, 11)]) as chon:
            ket_qua = phien_api.bat_dau_holland(doi_tuong_ap_dung=doi_tuong_ap_dung, db=self.db, current_user=None)
        chon.assert_called_once_with(self.db, doi_tuong_ap_dung)
        return ket_qua

    def test_luu_dinh_huong_khi_tao_phien(self):
        ket_qua = self._tao_phien(DOI_TUONG_DI_LAM)
        self.assertEqual(ket_qua.dinh_huong, DOI_TUONG_DI_LAM)
        self.assertEqual(self.db.get(TnPhienKhaoSat, ket_qua.id).dinh_huong, DOI_TUONG_DI_LAM)

    def test_khong_truyen_dinh_huong_thi_null(self):
        self.assertIsNone(self._tao_phien(None).dinh_huong)

    def test_tom_tat_phien_tra_dinh_huong(self):
        phien = TnPhienKhaoSat(ssid="abc", dinh_huong=1)
        self.db.add(phien)
        self.db.commit()
        tom_tat = phien_api._tom_tat_phien(self.db, [phien])
        self.assertEqual(tom_tat["abc"]["dinh_huong"], 1)


if __name__ == "__main__":
    unittest.main()
