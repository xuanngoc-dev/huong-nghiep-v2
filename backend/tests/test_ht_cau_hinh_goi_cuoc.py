import unittest

from pydantic import ValidationError

from app.schemas.ht_cau_hinh_goi_cuoc import HtCauHinhGoiCuocWrite


class TestHtCauHinhGoiCuocWrite(unittest.TestCase):
    def test_chuan_hoa_ma_va_ghi_chu(self):
        item = HtCauHinhGoiCuocWrite(
            ma_goi_cuoc="  goi_10 ",
            ten_goi_cuoc=" Gói 10 lượt ",
            loai_ap_dung="tra_cuu",
            gia_goc=50000,
            ghi_chu="   ",
        )
        self.assertEqual(item.ma_goi_cuoc, "GOI_10")
        self.assertEqual(item.ten_goi_cuoc, "Gói 10 lượt")
        self.assertIsNone(item.ghi_chu)

    def test_tu_choi_gia_khuyen_mai_lon_hon_gia_goc(self):
        with self.assertRaises(ValidationError):
            HtCauHinhGoiCuocWrite(
                ma_goi_cuoc="G1", ten_goi_cuoc="G1", loai_ap_dung="hoi_dap", gia_goc=10000, gia_khuyen_mai=20000
            )

    def test_nhan_loai_edu_coin(self):
        item = HtCauHinhGoiCuocWrite(ma_goi_cuoc="COIN_100", ten_goi_cuoc="100 Edu coin", loai_ap_dung="edu_coin")
        self.assertEqual(item.loai_ap_dung, "edu_coin")

    def test_nhan_loai_token(self):
        item = HtCauHinhGoiCuocWrite(ma_goi_cuoc="TOKEN_50K", ten_goi_cuoc="50.000 token", loai_ap_dung="token")
        self.assertEqual(item.loai_ap_dung, "token")

    def test_tu_choi_loai_ap_dung_khong_hop_le(self):
        with self.assertRaises(ValidationError):
            HtCauHinhGoiCuocWrite(ma_goi_cuoc="G1", ten_goi_cuoc="G1", loai_ap_dung="khac")


if __name__ == "__main__":
    unittest.main()
