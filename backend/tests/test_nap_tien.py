import logging
import unittest
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import get_db
from app.main import app
from app.models.ht_lich_su_giao_dich_ngan_hang import HtLichSuGiaoDichNganHang
from app.services import nap_tien

WEBHOOK = settings.api_v1_prefix + "/webhook/giao-dich-ngan-hang"
PAYLOAD = {
    "id": 92704,
    "gateway": "Vietcombank",
    "transactionDate": "2024-07-02 11:08:33",
    "accountNumber": "1017588888",
    "subAccount": "",
    "code": "SEVN63DC8E5C",
    "content": "SEVN63DC8E5C chuyen tien",
    "transferType": "in",
    "description": "NGUYEN VAN A chuyen tien",
    "transferAmount": 5000000,
    "accumulated": 105000000,
    "referenceCode": "FT24012345678",
}


class _DbGia:
    """Session giả: scalar() trả lần lượt các giá trị trong hàng đợi, hết thì None."""

    def __init__(self, *ket_qua):
        self.ket_qua = list(ket_qua)
        self.da_them = []

    def scalar(self, *_args, **_kwargs):
        return self.ket_qua.pop(0) if self.ket_qua else None

    def add(self, obj):
        self.da_them.append(obj)

    def flush(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            obj.id = 1


def _giao_dich(**kwargs):
    data = dict(
        id=7,
        ma_giao_dich="DH4K9F7Q",
        nguoi_dung_id=3,
        loai_ap_dung="tra_cuu",
        so_luot_nhan_duoc=10,
        so_tien_nap=Decimal(15000),
        so_tien_thuc_nhan=None,
        ma_tham_chieu_ngan_hang=None,
        trang_thai=nap_tien.CHO_THANH_TOAN,
        thoi_gian_thanh_toan=None,
        thoi_gian_xac_nhan=None,
        nguoi_xac_nhan_id=None,
        ghi_chu=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _tien_vao(noi_dung, so_tien=15000, loai="in"):
    return HtLichSuGiaoDichNganHang(
        ma_giao_dich_cong="1",
        loai_giao_dich=loai,
        noi_dung=noi_dung,
        so_tien=Decimal(so_tien),
        ma_tham_chieu="FT1",
    )


class TestTimMaGiaoDich(unittest.TestCase):
    def test_tim_duoc_ma_ke_ca_khi_ngan_hang_chen_khoang_trang(self):
        self.assertEqual(nap_tien.tim_ma_giao_dich("dh 4k9f 7q chuyen tien"), ["DH4K9F7Q"])

    def test_khong_bi_chuoi_dh_trong_ten_nguoi_chuyen_nuot_mat_ma(self):
        # "...DHANG" ngay trước mã: tìm chồng lấn vẫn ra mã thật.
        self.assertIn("DH4K9F7Q", nap_tien.tim_ma_giao_dich("TRAN DHANG DH4K9F7Q"))

    def test_sinh_ma_8_ky_tu_theo_thoi_gian(self):
        from datetime import datetime

        ma = nap_tien.tao_ma_giao_dich(_DbGia(), datetime(2026, 11, 15, 10, 30))
        self.assertEqual(len(ma), 8)
        self.assertTrue(ma.startswith("DH"))
        self.assertEqual(nap_tien.tim_ma_giao_dich(f"{ma} chuyen tien"), [ma])
        # Cùng phút thì chung phần thời gian, khác phút thì khác.
        cung_phut = nap_tien.tao_ma_giao_dich(_DbGia(), datetime(2026, 11, 15, 10, 30, 59))
        phut_sau = nap_tien.tao_ma_giao_dich(_DbGia(), datetime(2026, 11, 15, 10, 31))
        self.assertEqual(ma[2:6], cung_phut[2:6])
        self.assertNotEqual(ma[2:6], phut_sau[2:6])

    def test_khong_co_ma(self):
        self.assertEqual(nap_tien.tim_ma_giao_dich("SEVN63DC8E5C chuyen tien", None), [])


class TestDoiSoat(unittest.TestCase):
    def test_du_tien_thi_xac_nhan_va_cong_so_du(self):
        gd = _giao_dich()
        ho_so = SimpleNamespace(luot_tra_cuu=2)
        tien = _tien_vao("DH4K9F7Q chuyen tien", 15000)
        nap_tien.doi_soat(_DbGia(gd, ho_so), tien)
        self.assertEqual(tien.trang_thai_doi_soat, nap_tien.DA_KHOP)
        self.assertEqual(tien.lich_su_nap_tien_id, 7)
        self.assertEqual(gd.trang_thai, nap_tien.THANH_CONG)
        self.assertEqual(gd.ma_tham_chieu_ngan_hang, "FT1")
        self.assertEqual(ho_so.luot_tra_cuu, 12)

    def test_thieu_tien_thi_khong_cong(self):
        gd = _giao_dich()
        tien = _tien_vao("DH4K9F7Q", 10000)
        nap_tien.doi_soat(_DbGia(gd), tien)
        self.assertEqual(tien.trang_thai_doi_soat, nap_tien.THIEU_TIEN)
        self.assertEqual(gd.trang_thai, nap_tien.CHO_THANH_TOAN)
        self.assertEqual(gd.so_tien_thuc_nhan, Decimal(10000))

    def test_tien_ra_khong_doi_soat(self):
        tien = _tien_vao("DH4K9F7Q", loai="out")
        nap_tien.doi_soat(_DbGia(), tien)
        self.assertEqual(tien.trang_thai_doi_soat, nap_tien.TIEN_RA)

    def test_giao_dich_da_xu_ly_thi_khong_cong_lai(self):
        gd = _giao_dich(trang_thai=nap_tien.THANH_CONG)
        tien = _tien_vao("DH4K9F7Q")
        nap_tien.doi_soat(_DbGia(gd), tien)
        self.assertEqual(tien.trang_thai_doi_soat, nap_tien.CHUA_KHOP)
        self.assertEqual(gd.trang_thai, nap_tien.THANH_CONG)


class TestWebhook(unittest.TestCase):
    def setUp(self):
        self.db = _DbGia()
        app.dependency_overrides[get_db] = lambda: self.db
        self.client = TestClient(app, raise_server_exceptions=False)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        app.dependency_overrides.pop(get_db, None)

    def test_chua_cau_hinh_khoa_thi_bo_qua_xac_thuc(self):
        with patch.object(settings, "webhook_ngan_hang_api_key", ""):
            response = self.client.post(WEBHOOK, json=PAYLOAD)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["success"])

    def test_sai_khoa_tra_401(self):
        with patch.object(settings, "webhook_ngan_hang_api_key", "dung"):
            response = self.client.post(WEBHOOK, json=PAYLOAD, headers={"Authorization": "Apikey sai"})
        self.assertEqual(response.status_code, 401)

    def test_dung_khoa_luu_giao_dich(self):
        with patch.object(settings, "webhook_ngan_hang_api_key", "dung"):
            response = self.client.post(WEBHOOK, json=PAYLOAD, headers={"Authorization": "Apikey dung"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["success"])
        gd = self.db.da_them[0]
        self.assertEqual(gd.ma_giao_dich_cong, "92704")
        self.assertEqual(gd.so_tien, Decimal(5000000))
        self.assertEqual(gd.loai_giao_dich, "in")
        self.assertIsNone(gd.tai_khoan_phu)
        self.assertEqual(str(gd.thoi_gian_giao_dich), "2024-07-02 11:08:33")
        self.assertEqual(gd.trang_thai_doi_soat, nap_tien.CHUA_KHOP)

    def _gui(self, **kwargs):
        with patch.object(settings, "webhook_ngan_hang_api_key", ""):
            return self.client.post(WEBHOOK, **kwargs)

    def _form_sepay(self):
        # SePay gửi dạng form: mọi giá trị là chuỗi, null thành chuỗi rỗng.
        return {key: "" if value is None else str(value) for key, value in {**PAYLOAD, "subAccount": None}.items()}

    def test_nhan_multipart_form_data(self):
        files = {key: (None, value) for key, value in self._form_sepay().items()}
        response = self._gui(files=files)
        self.assertEqual(response.status_code, 200, response.text)
        gd = self.db.da_them[0]
        self.assertEqual(gd.ma_giao_dich_cong, "92704")
        self.assertEqual(gd.so_tien, Decimal(5000000))
        self.assertEqual(gd.so_du_luy_ke, Decimal(105000000))
        self.assertIsNone(gd.tai_khoan_phu)

    def test_nhan_x_www_form_urlencoded(self):
        response = self._gui(data=self._form_sepay())
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.db.da_them[0].ma_tham_chieu, "FT24012345678")

    def test_header_form_nhung_than_la_json(self):
        import json

        response = self._gui(content=json.dumps(PAYLOAD), headers={"Content-Type": "multipart/form-data"})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(self.db.da_them[0].ngan_hang, "Vietcombank")

    def test_thieu_so_tien_tra_422(self):
        response = self._gui(data={**self._form_sepay(), "transferAmount": ""})
        self.assertEqual(response.status_code, 422)

    def test_gui_lai_cung_id_khong_luu_trung(self):
        self.db.ket_qua = [SimpleNamespace(id=5, trang_thai_doi_soat=1)]
        with patch.object(settings, "webhook_ngan_hang_api_key", "dung"):
            response = self.client.post(WEBHOOK, json=PAYLOAD, headers={"Authorization": "Apikey dung"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["trung_lap"])
        self.assertEqual(self.db.da_them, [])


if __name__ == "__main__":
    unittest.main()
