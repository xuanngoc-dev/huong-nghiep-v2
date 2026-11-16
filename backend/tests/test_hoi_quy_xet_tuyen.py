"""Bộ test hồi quy nhiều trường (bước 3.8): mỗi thư mục trong tests/du_lieu/hoi_quy_xet_tuyen là một trường.

Trường nào cũng phải có bộ test này xanh trước khi chuyển đề án sang "đang áp dụng".
"""

import json
import unittest

from tests.hoi_quy_xet_tuyen import _khoa, cac_truong, chay_truong


def _theo_khoa(ds: list[dict]) -> dict[tuple, dict]:
    return {_khoa(x["ma_xet_tuyen"], x["ten_chuong_trinh"], x["ma_cong_thuc"], x["ma_to_hop"]): x for x in ds}


class HoiQuyNhieuTruongTests(unittest.TestCase):
    def test_co_it_nhat_ftu_va_bka(self):
        self.assertTrue({"NTH_2026", "BKA_2026"} <= {p.name for p in cac_truong()})

    def test_moi_truong_khop_ket_qua_mong_doi(self):
        for thu_muc in cac_truong():
            thuc_te = chay_truong(thu_muc)
            mong_doi_files = sorted((thu_muc / "ket_qua").glob("*.json"))
            with self.subTest(truong=thu_muc.name):
                self.assertTrue(mong_doi_files, "chưa có kết quả mong đợi")
                self.assertEqual({f.stem for f in mong_doi_files}, set(thuc_te), "hồ sơ và kết quả mong đợi không khớp nhau")
            for file in mong_doi_files:
                mong_doi = json.loads(file.read_text(encoding="utf-8"))
                thuc = thuc_te[file.stem]
                vi_tri = f"{thu_muc.name} / hồ sơ {file.stem}"
                with self.subTest(truong=thu_muc.name, ho_so=file.stem):
                    self.assertEqual(
                        (thuc["so_phuong_an"], thuc["so_chuong_trinh"]),
                        (mong_doi["so_phuong_an"], mong_doi["so_chuong_trinh"]),
                        vi_tri,
                    )
                    mong_doi_pa, thuc_pa = _theo_khoa(mong_doi["phuong_an"]), _theo_khoa(thuc["phuong_an"])
                    self.assertEqual(set(thuc_pa), set(mong_doi_pa), f"{vi_tri}: tập phương án khác")
                    for khoa, x in mong_doi_pa.items():
                        self.assertEqual(thuc_pa[khoa], x, f"{vi_tri}: phương án {khoa}")
                    self.assertEqual(thuc["xep_hang"], mong_doi["xep_hang"], f"{vi_tri}: thứ tự xếp hạng")


if __name__ == "__main__":
    unittest.main()
