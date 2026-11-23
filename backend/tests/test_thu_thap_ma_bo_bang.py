import unittest

from app.services import thu_thap_tuyen_sinh_ai as ai


class TestMaBoTrongBang(unittest.TestCase):
    def setUp(self):
        html = ai._TrangWeb()
        html.feed(
            "<h2>Đối chiếu phương thức</h2><table>"
            "<tr><th colspan='3'>Tuyển sinh năm 2026</th></tr>"
            "<tr><th>Mã xét tuyển</th><th>Mã diện</th><th>Mã phương thức <br>của Bộ GD&amp;ĐT</th></tr>"
            "<tr><td>IT1</td><td>D1</td><td>100</td></tr>"
            "<tr><td>IT1</td><td>D2</td><td><span>500</span></td></tr>"
            "<tr><td>IT2</td><td>D1</td><td>500</td></tr>"
            "</table><table><tr><th>Mã xét tuyển</th><th>Mã diện</th><th>Mã nội bộ</th></tr>"
            "<tr><td>IT1</td><td>D1</td><td>500</td></tr></table>"
        )
        html.close()
        self.doc = ai._TaiLieu("https://truong.edu.vn/2026", "", html.doan, [])
        self.vi_tri = "Mục: Đối chiếu phương thức · Bảng 1"

    def doi_chieu(self, trich_dan, ma="500", dien="D2", phan_loai="cong_bo", vi_tri=None):
        khoa = "ma_phuong_thuc_cua_bo"
        dong = {"ma_phuong_thuc_cua_truong": dien, khoa: ma}
        chuong_trinh = {"ma_xet_tuyen": "IT1", "dats_phuong_thuc": [dong]}
        muc = {
            "duong_dan": f"/dats_tuyen_sinh/dats_chuong_trinh_dao_tao/0/dats_phuong_thuc/0/{khoa}",
            "dan_chung": [{"nguon_id": 1, "vi_tri": vi_tri or self.vi_tri, "trich_dan": trich_dan, "gia_tri": ma}],
            "phan_loai_ma_bo": phan_loai, "ghi_chu": "Mô tả của diện xét.",
        }
        data = {"du_lieu": {"dats_tuyen_sinh": {"dats_chuong_trinh_dao_tao": [chuong_trinh]}}, "muc": [muc]}
        ai._chuan_hoa_ma_phuong_thuc(data, 2026, {2026: {"100", "500"}}, {1: self.doc}, {})
        return dong[khoa], muc["dan_chung"]

    def test_nhan_phan_loai_ma_cua_ai_voi_cach_ghi_bang_cua_truong(self):
        hang = "| IT1 | D2 | 500 |"
        self.assertEqual(self.doi_chieu(hang)[0], "500")
        ma, dan_chung = self.doi_chieu("| IT1 | D1 | 100 |", ma="100", dien="D1", phan_loai="suy_luan")
        self.assertEqual(ma, "100")
        self.assertEqual(dan_chung[0]["phan_loai_ma_bo"], "suy_luan")

    def test_ma_cong_bo_can_trich_duoc_gia_tri_tai_dung_vi_tri(self):
        self.assertEqual(self.doi_chieu("| IT1 | D1 | 100 |", ma="500"), ("500", []))
        self.assertEqual(self.doi_chieu("| IT1 | D2 | 500 |", vi_tri="Không tồn tại"), ("500", []))

    def test_hai_ma_cong_bo_mau_thuan_giu_de_xuat_cho_ai_va_nguoi_duyet(self):
        khoa = "ma_phuong_thuc_cua_bo"
        cong_thuc = {khoa: "100"}
        muc = {"duong_dan": f"/quy_tac_xet_tuyen/cong_thuc/0/{khoa}", "phan_loai_ma_bo": "cong_bo", "dan_chung": []}
        docs = {}
        for i, ma in enumerate(("100", "500"), 1):
            noi_dung = f"D1, mã phương thức của Bộ GD&ĐT: {ma}."
            docs[i] = ai._TaiLieu("", "", [("D1", noi_dung)], [])
            muc["dan_chung"].append({"nguon_id": i, "vi_tri": "D1", "trich_dan": noi_dung, "gia_tri": ma})
        data = {"du_lieu": {"quy_tac_xet_tuyen": {"cong_thuc": [cong_thuc]}}, "muc": [muc]}
        ai._chuan_hoa_ma_phuong_thuc(data, 2026, {2026: {"100", "500"}}, docs, {})
        self.assertEqual(cong_thuc[khoa], "100")
        self.assertIn("100, 500", muc["ghi_chu"])
