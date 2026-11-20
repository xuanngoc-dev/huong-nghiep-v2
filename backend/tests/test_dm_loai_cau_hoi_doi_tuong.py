"""Đối tượng áp dụng của loại câu hỏi: chỉ nhận mã trong bộ định nghĩa, bỏ trùng, rỗng lưu null."""

import unittest

from fastapi import HTTPException
from pydantic import ValidationError

from app.constants.doi_tuong_ap_dung import DOI_TUONG_AP_DUNG
from app.api.v1.endpoints.tn_phien_khao_sat import bat_dau_holland
from app.schemas.dm_loai_cau_hoi import DmLoaiCauHoiWrite


def _loai(**kw):
    return DmLoaiCauHoiWrite(ten_loai_cau_hoi="Sở thích", thu_tu_uu_tien=1, **kw)


class TestDoiTuongApDung(unittest.TestCase):
    def test_bo_trung_va_sap_xep(self):
        self.assertEqual(_loai(doi_tuong_ap_dung=[2, 1, 2]).doi_tuong_ap_dung, [1, 2])

    def test_rong_hoac_khong_gui_thi_null(self):
        self.assertIsNone(_loai(doi_tuong_ap_dung=[]).doi_tuong_ap_dung)
        self.assertIsNone(_loai().doi_tuong_ap_dung)

    def test_ma_ngoai_bo_dinh_nghia_bi_tu_choi(self):
        with self.assertRaises(ValidationError) as ctx:
            _loai(doi_tuong_ap_dung=[1, 99])
        self.assertIn("99", str(ctx.exception))

    def test_nhan_du_moi_ma(self):
        self.assertEqual(_loai(doi_tuong_ap_dung=list(DOI_TUONG_AP_DUNG)).doi_tuong_ap_dung, sorted(DOI_TUONG_AP_DUNG))


class TestTaoPhienTheoDoiTuong(unittest.TestCase):
    def test_ma_doi_tuong_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as ctx:
            bat_dau_holland(doi_tuong_ap_dung=99, db=None, current_user=None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("99", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
