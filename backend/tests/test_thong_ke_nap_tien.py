import unittest
from datetime import date, datetime

from app.services.thong_ke_nap_tien import SO_NGAY_GAN_DAY, tong_hop

# Thứ Tư 18/11/2026, 10 giờ sáng.
NOW = datetime(2026, 11, 18, 10, 0)


def _ky(ket_qua, ma):
    return next(k for k in ket_qua["ky"] if k["ma"] == ma)


class TestTongHop(unittest.TestCase):
    def test_rong_van_du_cau_truc(self):
        kq = tong_hop([], NOW)
        self.assertEqual([k["ma"] for k in kq["ky"]], ["hom_nay", "tuan_nay", "thang_nay", "nam_nay"])
        self.assertTrue(all(k["so_tien"] == 0 for k in kq["ky"]))
        self.assertEqual(len(kq["theo_ngay"]), SO_NGAY_GAN_DAY)
        self.assertEqual(kq["theo_ngay"][-1]["ngay"], date(2026, 11, 18))
        self.assertEqual([t["thang"] for t in kq["theo_thang"]], list(range(1, 13)))
        self.assertEqual(kq["theo_loai"], [])

    def test_cong_theo_ky(self):
        kq = tong_hop(
            [
                (datetime(2026, 11, 18, 8, 0), 50_000, "tra_cuu"),  # hôm nay
                (datetime(2026, 11, 16, 9, 0), 20_000, "khao_sat"),  # thứ Hai tuần này
                (datetime(2026, 11, 2, 9, 0), 10_000, "tra_cuu"),  # đầu tháng
                (datetime(2026, 3, 5, 9, 0), 5_000, "hoi_dap"),  # đầu năm
            ],
            NOW,
        )
        self.assertEqual(_ky(kq, "hom_nay")["so_tien"], 50_000)
        self.assertEqual(_ky(kq, "tuan_nay")["so_tien"], 70_000)
        self.assertEqual(_ky(kq, "thang_nay")["so_tien"], 80_000)
        self.assertEqual(_ky(kq, "nam_nay")["so_tien"], 85_000)
        self.assertEqual(_ky(kq, "nam_nay")["so_giao_dich"], 4)

    def test_so_sanh_cung_ky_truoc(self):
        kq = tong_hop(
            [
                (datetime(2026, 11, 17, 9, 0), 30_000, "tra_cuu"),  # hôm qua, trước 10 giờ: tính
                (datetime(2026, 11, 17, 15, 0), 99_000, "tra_cuu"),  # hôm qua, sau 10 giờ: không tính
                (datetime(2026, 11, 10, 9, 0), 40_000, "tra_cuu"),  # thứ Ba tuần trước: tính
                (datetime(2026, 11, 13, 9, 0), 99_000, "tra_cuu"),  # thứ Sáu tuần trước: không tính
            ],
            NOW,
        )
        self.assertEqual(_ky(kq, "hom_nay")["so_tien_ky_truoc"], 30_000)
        # Tuần trước tính đến thứ Tư 11/11 10 giờ.
        self.assertEqual(_ky(kq, "tuan_nay")["so_tien_ky_truoc"], 40_000)
        self.assertEqual(_ky(kq, "tuan_nay")["so_giao_dich_ky_truoc"], 1)

    def test_theo_ngay_thang_loai(self):
        kq = tong_hop(
            [
                (datetime(2026, 11, 18, 8, 0), 50_000, "tra_cuu"),
                (datetime(2026, 11, 18, 9, 0), 10_000, "khao_sat"),
                (datetime(2026, 2, 1, 9, 0), 15_000, "tra_cuu"),
                (datetime(2025, 12, 31, 9, 0), 99_000, "tra_cuu"),  # năm ngoái: chỉ dùng để so sánh
            ],
            NOW,
        )
        self.assertEqual(kq["theo_ngay"][-1], {"ngay": date(2026, 11, 18), "so_tien": 60_000, "so_giao_dich": 2})
        self.assertEqual(kq["theo_thang"][1]["so_tien"], 15_000)
        self.assertEqual(kq["theo_thang"][10]["so_tien"], 60_000)
        self.assertEqual(
            kq["theo_loai"],
            [
                {"loai_ap_dung": "tra_cuu", "so_tien": 65_000, "so_giao_dich": 2},
                {"loai_ap_dung": "khao_sat", "so_tien": 10_000, "so_giao_dich": 1},
            ],
        )


if __name__ == "__main__":
    unittest.main()
