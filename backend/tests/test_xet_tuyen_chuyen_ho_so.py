import unittest

from app.services.xet_tuyen.bo_tinh import tinh_phuong_an
from app.services.xet_tuyen.chuyen_ho_so import (
    DanhMucHoSo,
    hoc_luc_tu_diem_tb,
    tu_du_lieu_khach,
    tu_ho_so_thanh_vien,
)
from tests.test_xet_tuyen_bo_tinh import DIEM_CHUAN, HOM_NAY, NAM, QUY_TAC, TEN_CONG_THUC

DANH_MUC = DanhMucHoSo(
    khu_vuc={1: "KV1", 3: "KV2-NT"},
    doi_tuong={7: "01"},
    tinh={71: ("01", "Bắc"), 99: ("79", "Nam")},
    to_hop_ba_mon={
        "A00": ["TOAN", "LY", "HOA"],
        "A01": ["TOAN", "LY", "ANH"],
        "D01": ["TOAN", "VAN", "ANH"],
    },
)

# Hồ sơ năng lực tương đương hồ sơ mẫu A của trang test_xet_tuyen.html, ở dạng JSON trinh_do_hoc_van hiện có.
TRINH_DO_A = {
    "diem_thi_thpt_quoc_gia": {"du_kien": {"TOAN": 9.0, "LY": 8.5, "HOA": 8.75, "NN1": 8.0, "VAN": 8.0}},
    "diem_trung_binh_hoc_ba": {
        "10": {"TOAN": 9.2, "LY": 9.0, "HOA": 8.8, "VAN": 8.0, "NN1": 9.0},
        "11": {"TOAN": 9.4, "LY": 9.1, "HOA": 9.0, "VAN": 8.2, "NN1": 9.2},
        "12": {"TOAN": 9.6, "LY": 9.2, "HOA": 9.2, "VAN": 8.4, "NN1": 9.4},
    },
    "hoc_luc_trung_binh": {"10": 8.9, "11": 9.0, "12": 9.2},
    "hanh_kiem": {"10": "Tốt", "11": "Tốt", "12": "Tốt"},
    "chung_chi_ngoai_ngu": [{"ma": "IELTS", "thanh_tich": "7.0", "thoi_gian_cap": "2025-12-01"}],
    "bai_thi_danh_gia_nang_luc": [{"ma": "TSA", "thanh_tich": "72.5", "thoi_gian_cap": "2026-03-01"}],
    "thanh_tich_hoc_tap_nghien_cuu": [{"ma": "HSG-TINH", "thanh_tich": "Giải Nhì"}],
}


class ChuyenHoSoThanhVienTests(unittest.TestCase):
    def setUp(self):
        self.kq = tu_ho_so_thanh_vien(
            TRINH_DO_A,
            nam_tuyen_sinh=2026,
            danh_muc=DANH_MUC,
            khu_vuc_uu_tien_id=3,
            tinh_thanh_id=71,
            kha_nang_tai_chinh={"muc": "Khá"},
        )
        self.hs = self.kq.ho_so

    def test_cac_quy_tac_chuyen_da_chot(self):
        hs = self.hs
        self.assertEqual((hs.nam_tot_nghiep, hs.da_tot_nghiep), (2026, True))
        # NN1 → ANH ở cả điểm thi và học bạ.
        self.assertEqual(hs.diem_thpt["ANH"], 8.0)
        self.assertEqual(hs.hoc_ba["ANH"], {10: 9.0, 11: 9.2, 12: 9.4})
        self.assertEqual((hs.nam_hoc[12].tbc, hs.nam_hoc[12].hoc_luc, hs.nam_hoc[12].ren_luyen), (9.2, 4, 4))
        self.assertEqual((hs.khu_vuc, hs.mong_muon_tinh, hs.ngan_sach), ("KV2-NT", ["01"], 50_000_000))
        self.assertEqual((hs.thanh_tich[0].ma, hs.thanh_tich[0].muc_giai), ("HSG-TINH", 2))
        self.assertEqual((hs.bai_thi[0].diem, hs.bai_thi[0].nam), (72.5, 2026))
        self.assertTrue(any("Tiếng Anh" in x for x in self.kq.gia_dinh))

    def test_bo_tinh_ra_dung_diem_cua_ho_so_mau_a(self):
        kq = tinh_phuong_an(QUY_TAC, self.hs, NAM, HOM_NAY, DIEM_CHUAN)

        def pa(ma, to_hop=None):
            return next(
                p for p in kq.phuong_an if TEN_CONG_THUC[p.cong_thuc_id] == ma and (to_hop is None or p.ma_to_hop == to_hop)
            )

        self.assertEqual(pa("FTU_THPT_30", "A00").diem_xet, 26.5)
        self.assertEqual(pa("FTU_HB_30", "A00").diem_xet, 27.67)
        self.assertEqual(pa("BKA_TSA").diem_xet, 74.17)

    def test_ho_so_rong_khong_loi(self):
        hs = tu_ho_so_thanh_vien(None, nam_tuyen_sinh=2026, danh_muc=DANH_MUC).ho_so
        self.assertEqual((hs.diem_thpt, hs.hoc_ba, hs.nam_hoc, hs.khu_vuc), ({}, {}, {}, None))
        self.assertEqual(tinh_phuong_an(QUY_TAC, hs, NAM, HOM_NAY).phuong_an, [])


class ChuyenDuLieuKhachTests(unittest.TestCase):
    def test_uoc_tinh_diem_mon_tu_tong_theo_khoi(self):
        kq = tu_du_lieu_khach(
            {"tinh_thanh_id": 99, "diem_trung_binh": {"10": 7.0, "11": 7.2}, "diem_thi_thu": {"A00": 27, "A01": 24}},
            {"muc_hoc_phi": "30_50"},
            nam_tuyen_sinh=2026,
            danh_muc=DANH_MUC,
        )
        hs = kq.ho_so
        self.assertTrue(kq.uoc_tinh)
        # Toán, Lý có trong cả hai khối: trung bình (9 + 8) = 8.5; Hóa chỉ A00 = 9; Anh chỉ A01 = 8.
        self.assertEqual(hs.diem_thpt, {"TOAN": 8.5, "LY": 8.5, "HOA": 9.0, "ANH": 8.0})
        self.assertEqual((hs.ngan_sach, hs.mong_muon_tinh), (50_000_000, ["79"]))
        self.assertEqual((hs.nam_hoc[10].hoc_luc, hs.nam_hoc[11].hoc_luc), (3, 3))

    def test_tren_100_trieu_khong_gioi_han_hoc_phi(self):
        kq = tu_du_lieu_khach({}, {"muc_hoc_phi": "tren_100"}, nam_tuyen_sinh=2026, danh_muc=DANH_MUC)
        self.assertIsNone(kq.ho_so.ngan_sach)
        self.assertFalse(kq.uoc_tinh)


class HocLucTests(unittest.TestCase):
    def test_nguong_hoc_luc(self):
        self.assertEqual([hoc_luc_tu_diem_tb(x) for x in (8.0, 7.99, 6.5, 5.0, 4.9, None)], [4, 3, 3, 2, 1, None])


if __name__ == "__main__":
    unittest.main()
