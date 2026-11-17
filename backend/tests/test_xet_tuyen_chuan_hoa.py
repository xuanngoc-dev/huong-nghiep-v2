"""Chuẩn hóa linh hoạt file quy tắc xét tuyển: mã gần đúng đổi về chuẩn, phần chưa tính được thành cảnh báo."""

import unittest

from app.services.xet_tuyen_chuan_hoa import chuan_hoa, doi_dieu_kien, tim_ma
from app.services.xet_tuyen_import import chuan_bi_nhap
from tests.test_xet_tuyen_import import DANH_MUC, _mau


def _dk(ma_chi_so, khoa="", toan_tu=">=", gia_tri=1):
    return {"ma_chi_so": ma_chi_so, "khoa": khoa, "toan_tu": toan_tu, "gia_tri": gia_tri}


class DoiDieuKienTests(unittest.TestCase):
    def test_tim_ma_bo_dau_gach(self):
        self.assertEqual(tim_ma("VACT", DANH_MUC.bai_thi), "V-ACT")
        self.assertEqual(tim_ma("hsg_qg", DANH_MUC.thanh_tich), "HSG-QG")
        self.assertIsNone(tim_ma("SPT", DANH_MUC.bai_thi))

    def test_bi_danh_va_ten_chung_chi(self):
        self.assertEqual(doi_dieu_kien(_dk("TOT_NGHIEP_HOP_LE"), DANH_MUC)["ma_chi_so"], "DA_TOT_NGHIEP_THPT")
        moi = doi_dieu_kien(_dk("IELTS", "IELTS_7", gia_tri=7.0), DANH_MUC)
        self.assertEqual((moi["ma_chi_so"], moi["khoa"], moi["gia_tri"]), ("DIEM_CHUNG_CHI", "IELTS", 7.0))
        moi = doi_dieu_kien(_dk("TOEFL_IBT", "TOEFL_IBT_94", gia_tri=94), DANH_MUC)
        self.assertEqual(moi["khoa"], "TOEFL_IBT_120")

    def test_diem_mon_theo_ten_chi_so(self):
        moi = doi_dieu_kien(_dk("DIEM_THI_TOAN_2026", gia_tri=7.5), DANH_MUC)
        self.assertEqual((moi["ma_chi_so"], moi["khoa"]), ("DIEM_THI_THPT", "TOAN"))
        moi = doi_dieu_kien(_dk("DIEM_HOC_BA_TOAN"), DANH_MUC)
        self.assertEqual((moi["ma_chi_so"], moi["khoa"]), ("DIEM_HOC_BA_TB", "TOAN"))

    def test_thanh_tich_kem_muc_giai(self):
        moi = doi_dieu_kien(_dk("THANH_TICH", "HSGTINH_KK", "=", 1), DANH_MUC)
        self.assertEqual((moi["khoa"], moi["toan_tu"], moi["gia_tri"]), ("HSG-TINH", "=", 4))
        # Điều kiện không theo dạng "có giải" (= 1) thì không đoán.
        self.assertIsNone(doi_dieu_kien(_dk("THANH_TICH", "HSGQG_NHI", "<=", 3), DANH_MUC))

    def test_chi_so_la_khong_doan(self):
        self.assertIsNone(doi_dieu_kien(_dk("DIEM_THPT_TO_HOP_2026", gia_tri=23.5), DANH_MUC))
        self.assertIsNone(doi_dieu_kien(_dk("DIEM_CHUNG_CHI", "KHONG_CO"), DANH_MUC))


class ChuanHoaFileTests(unittest.TestCase):
    def test_khong_sua_du_lieu_goc_va_file_chuan_khong_doi(self):
        du_lieu = _mau("mau_BKA_2026.json")
        moi, canh_bao, chua = chuan_hoa(du_lieu, DANH_MUC)
        self.assertEqual(moi, du_lieu)
        self.assertEqual((canh_bao, chua), ([], []))

    def test_file_ma_gan_dung_van_nhap_duoc_kem_canh_bao(self):
        du_lieu = _mau("mau_BKA_2026.json")
        tsa = next(c for c in du_lieu["cong_thuc"] if c["ma_cong_thuc"] == "BKA_TSA")
        tsa["thanh_phan"][0]["ma_bai_thi"] = "tsa"
        du_lieu["dieu_kien_chung"][0]["mot_trong"][0]["ma_chi_so"] = "TOT_NGHIEP_HOP_LE"
        du_lieu["diem_cong"] = [
            {
                "loai_diem_cong": "DIEM_KHUYEN_KHICH",
                "nhom_cong": "ANH",
                "ma_chi_so": "IELTS",
                "khoa": "IELTS_7",
                "toan_tu": ">=",
                "gia_tri": 7.0,
                "diem_cong": 1.5,
            },
            {
                "loai_diem_cong": "DIEM_THUONG",
                "nhom_cong": "KHAC",
                "ma_chi_so": "CHI_SO_LA",
                "toan_tu": "=",
                "gia_tri": 1,
                "diem_cong": 1,
            },
        ]
        du_lieu["chuong_trinh"][0]["hoc_phi"] = {"nam_hoc": "2026-2027", "hoc_phi_tu": None}
        du_lieu["chuong_trinh"][0]["dieu_kien_rieng"] = [
            {"ma_nhom": "TONG_TO_HOP", "ten_nhom": "Tổng tổ hợp", "mot_trong": [_dk("DIEM_THPT_TO_HOP", gia_tri=23.5)]}
        ]
        ke_hoach = chuan_bi_nhap(du_lieu, DANH_MUC)

        self.assertEqual(len(ke_hoach.diem_cong), 1)
        self.assertEqual(
            (ke_hoach.diem_cong[0]["ma_chi_so"], ke_hoach.diem_cong[0]["khoa"]), ("DIEM_CHUNG_CHI", "IELTS")
        )
        loai = {x["loai"] for x in ke_hoach.quy_dinh_chua_mo_hinh_hoa}
        self.assertTrue({"DIEM_CONG_CHUA_MO_HINH_HOA", "DIEU_KIEN_CHUA_MO_HINH_HOA"} <= loai)
        self.assertTrue(any("bỏ khối học phí" in x for x in ke_hoach.canh_bao))
        self.assertTrue(any('"tsa"' in x and "V-ACT" not in x for x in ke_hoach.canh_bao))

    def test_thanh_phan_khong_tinh_duoc_chuyen_thu_cong(self):
        du_lieu = _mau("mau_BKA_2026.json")
        tsa = next(c for c in du_lieu["cong_thuc"] if c["ma_cong_thuc"] == "BKA_TSA")
        tsa["thanh_phan"] = [{"vi_tri": 1, "loai_nguon": "HOC_BA_VA_THANH_TICH"}]
        sat = {
            **tsa,
            "ma_cong_thuc": "SAT",
            "ten_cong_thuc": "SAT",
            "thang_diem": 1600,
            "thanh_phan": [{"vi_tri": 1, "loai_nguon": "CHUNG_CHI", "ma_bai_thi": "SAT"}],
        }
        du_lieu["cong_thuc"].append(sat)
        du_lieu["chuong_trinh"][0]["phuong_an"].append({"ma_cong_thuc": "SAT"})
        ke_hoach = chuan_bi_nhap(du_lieu, DANH_MUC)

        theo_ma = {c["ma_cong_thuc"]: c for c in ke_hoach.cong_thuc}
        self.assertEqual(theo_ma["BKA_TSA"]["kieu_tinh"], "THU_CONG")
        self.assertEqual(theo_ma["SAT"]["kieu_tinh"], "THANH_PHAN")
        self.assertTrue(
            any(x["loai"] == "CONG_THUC_THU_CONG" and x["ma"] == "BKA_TSA" for x in ke_hoach.quy_dinh_chua_mo_hinh_hoa)
        )

    def test_nguon_diem_mon_gan_dung(self):
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["cong_thuc"][0]["nguon_diem_mon"] = "HOC_BA_THPT_VA_CHUNG_CHI"
        moi, canh_bao, chua = chuan_hoa(du_lieu, DANH_MUC)
        self.assertEqual(moi["cong_thuc"][0]["nguon_diem_mon"], "HOC_BA")
        self.assertEqual(chua[0]["loai"], "NGUON_DIEM_CHUA_MO_HINH_HOA")

    def test_chi_dieu_kien_chua_co_nhom_chi_canh_bao(self):
        du_lieu = _mau("mau_BKA_2026.json")
        xtt = next(c for c in du_lieu["cong_thuc"] if c["kieu_tinh"] == "CHI_DIEU_KIEN")
        xtt["dieu_kien"] = []
        ke_hoach = chuan_bi_nhap(du_lieu, DANH_MUC)
        self.assertTrue(any("chưa có nhóm dieu_kien" in x for x in ke_hoach.canh_bao))


if __name__ == "__main__":
    unittest.main()
