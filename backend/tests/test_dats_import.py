import json
import unittest
from collections import Counter
from pathlib import Path

from app.services.dats_import import CatalogIndex, DatsImportError, conflict_policy, prepare_import

# File mẫu đặt trong tests/du_lieu để test không phụ thuộc tài liệu trong docs/.
# Bản lồng nhau rút gọn từ file BKA 2026 gốc: giữ 4 chương trình (BF1, BF2, FL1, BF-E12) và toàn bộ bảng cấp đề án.
DU_LIEU = Path(__file__).resolve().parent / "du_lieu"
SAMPLE = DU_LIEU / "BKA_2026_import_mot_truong_mot_nam.json"
NESTED = DU_LIEU / "BKA_2026_import_long_nhau_rut_gon.json"
CODES = {
    "phuong_thuc": {
        "XTTN": 11,
        "DGTD": 12,
        "THPT": 13,
        "100": 14,
        "301": 15,
        "401": 16,
        "415": 17,
        "500": 18,
    },
    "to_hop": {"K01": 21, "A00": 22, "A01": 23, "D07": 24, "D01": 25, "B00": 26, "D04": 27, "DD2": 28},
}


def catalogs() -> CatalogIndex:
    return CatalogIndex(
        phuong_thuc_by_code=CODES["phuong_thuc"],
        phuong_thuc_ids=set(CODES["phuong_thuc"].values()),
        to_hop_by_code=CODES["to_hop"],
        to_hop_ids=set(CODES["to_hop"].values()),
    )


class DatsImportTests(unittest.TestCase):
    def test_ten_bang_viet_tat_uu_tien_xt_duoc_hieu_la_bang_day_du(self):
        chinh_sach = [{"id": 5, "ten_chinh_sach": "Ưu tiên học sinh giỏi"}]
        # JSON phẳng: bảng viết tắt cùng cấp với đề án, nối bằng de_an_id.
        flat = {
            "dats_tuyen_sinh": {"id": 1, "ten_de_an": "Đề án"},
            "dats_chinh_sach_uu_tien_xt": [dict(chinh_sach[0], de_an_id=1)],
        }
        rows = prepare_import(flat, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertEqual([row.table for row in rows], ["dats_tuyen_sinh", "dats_chinh_sach_uu_tien_xet_tuyen"])
        self.assertEqual(rows[1].values["ten_chinh_sach"], "Ưu tiên học sinh giỏi")
        # JSON lồng nhau: bảng viết tắt nằm trong dats_tuyen_sinh.
        nested = {"dats_tuyen_sinh": {"id": 1, "ten_de_an": "Đề án", "dats_chinh_sach_uu_tien_xt": chinh_sach}}
        self.assertEqual(conflict_policy(nested), "tu_choi")
        rows = prepare_import(nested, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertEqual(Counter(row.table for row in rows)["dats_chinh_sach_uu_tien_xet_tuyen"], 1)
        # Dữ liệu gốc không bị sửa.
        self.assertIn("dats_chinh_sach_uu_tien_xt", nested["dats_tuyen_sinh"])

    def test_khong_cho_vua_viet_tat_vua_day_du(self):
        document = {
            "dats_tuyen_sinh": {"id": 1, "ten_de_an": "Đề án"},
            "dats_chinh_sach_uu_tien_xt": [],
            "dats_chinh_sach_uu_tien_xet_tuyen": [],
        }
        with self.assertRaises(DatsImportError) as caught:
            prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertIn("dats_chinh_sach_uu_tien_xt", str(caught.exception))

    def test_sample_file_contains_only_the_proposal(self):
        document = json.loads(SAMPLE.read_text())
        self.assertEqual(
            [key for key in document if key.startswith("dats_")],
            ["dats_tuyen_sinh"],
        )
        rows = prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2027, catalogs=catalogs())
        self.assertEqual([row.table for row in rows], ["dats_tuyen_sinh"])
        proposal = rows[0]
        self.assertEqual(proposal.values["ma_truong"], "BKA")
        self.assertEqual(proposal.values["nam_tuyen_sinh"], 2027)
        self.assertEqual(proposal.values["chi_tieu"], 9880)
        self.assertEqual(proposal.values["ten_de_an"], document["dats_tuyen_sinh"]["ten_de_an"])

    def test_missing_subject_combo_is_rejected(self):
        document = {
            "dats_tuyen_sinh": {"id": 1, "ten_de_an": "Đề án"},
            "dats_chuong_trinh_dao_tao": [
                {"id": 2, "de_an_id": 1, "ten_chuong_trinh": "Kỹ thuật"},
            ],
            "dats_phuong_thuc": [
                {
                    "id": 3,
                    "de_an_chuong_trinh_id": 2,
                    "ma_phuong_thuc_cua_truong": "XTTN",
                    "ten_phuong_thuc_cua_truong": "Xét tuyển tài năng",
                },
            ],
            "dats_phuong_thuc_to_hop": [
                {"de_an_phuong_thuc_id": 3, "ghi_chu": "ma_to_hop=K01"},
            ],
        }
        limited = catalogs()
        limited_without_combo = CatalogIndex(
            phuong_thuc_by_code=limited.phuong_thuc_by_code,
            phuong_thuc_ids=limited.phuong_thuc_ids,
            to_hop_by_code={},
            to_hop_ids=set(),
        )
        with self.assertRaises(DatsImportError) as caught:
            prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=limited_without_combo)
        self.assertIn("tổ hợp", str(caught.exception))

    def test_nested_sample_links_children_from_parent_position(self):
        document = json.loads(NESTED.read_text())
        self.assertEqual(conflict_policy(document), "tu_choi")
        rows = prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        counts = Counter(row.table for row in rows)
        self.assertEqual(counts["dats_tuyen_sinh"], 1)
        self.assertEqual(counts["dats_chuong_trinh_dao_tao"], 4)
        self.assertEqual(counts["dats_phuong_thuc"], 20)
        self.assertEqual(counts["dats_phuong_thuc_to_hop"], 14)
        self.assertEqual(counts["dats_doi_tuong_du_tuyen"], 5)
        self.assertEqual(counts["dats_dieu_kien_du_tuyen"], 8)
        self.assertEqual(counts["dats_trinh_do_nganh"], 4)
        self.assertEqual(counts["dats_lien_he_tuyen_sinh"], 1)

        proposal = rows[0]
        self.assertEqual(proposal.values["ma_truong"], "BKA")
        self.assertEqual(proposal.values["nam_tuyen_sinh"], 2026)
        program = next(
            row
            for row in rows
            if row.table == "dats_chuong_trinh_dao_tao" and row.values["ma_xet_tuyen"] == "BF1"
        )
        self.assertEqual(program.values["de_an_id"], proposal.source_id)
        methods = [
            row
            for row in rows
            if row.table == "dats_phuong_thuc" and row.values["de_an_chuong_trinh_id"] == program.source_id
        ]
        self.assertEqual(
            [row.values["ma_phuong_thuc_cua_bo"] for row in methods],
            ["301", "415", "500", "401", "100"],
        )
        combos = [
            row
            for row in rows
            if row.table == "dats_phuong_thuc_to_hop"
            and row.values["de_an_phuong_thuc_id"] == methods[-1].source_id
        ]
        self.assertEqual([row.values["to_hop_id"] for row in combos], [21, 22, 26, 24])
        self.assertEqual(methods[-1].values["to_hop_mon_hoc"], ["K01", "A00", "B00", "D07"])
        self.assertIsNone(methods[0].values["to_hop_mon_hoc"])
        subject = next(
            row
            for row in rows
            if row.table == "dats_doi_tuong_du_tuyen" and row.values["ma_doi_tuong"] == "XTTN_11"
        )
        condition = next(
            row
            for row in rows
            if row.table == "dats_dieu_kien_du_tuyen" and row.values["ma_dieu_kien"] == "DK_XTTN_11"
        )
        self.assertEqual(condition.values["doi_tuong_du_tuyen_id"], subject.source_id)
        self.assertEqual(condition.values["de_an_id"], proposal.source_id)
        scoped = [
            row
            for row in rows
            if row.table == "dats_dieu_kien_du_tuyen" and row.values["de_an_chuong_trinh_id"] is not None
        ]
        self.assertEqual(len(scoped), 2)
        self.assertTrue(all(row.values["de_an_id"] == proposal.source_id for row in scoped))

    def test_method_combo_ids_accept_null_and_codes(self):
        document = {
            "dats_tuyen_sinh": {
                "ten_de_an": "Đề án",
                "dats_chuong_trinh_dao_tao": [
                    {
                        "ten_chuong_trinh": "Kỹ thuật",
                        "dats_phuong_thuc": [
                            {
                                "ma_phuong_thuc_cua_bo": "100",
                                "ten_phuong_thuc_cua_truong": "Mọi tổ hợp",
                                "to_hop_mon_hoc": None,
                            },
                            {
                                "ma_phuong_thuc_cua_bo": "301",
                                "ten_phuong_thuc_cua_truong": "Một số tổ hợp",
                                "to_hop_mon_hoc": ["K01", "A00", "K01"],
                            },
                        ],
                    }
                ],
            }
        }
        rows = prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        methods = [row for row in rows if row.table == "dats_phuong_thuc"]
        self.assertIsNone(methods[0].values["to_hop_mon_hoc"])
        self.assertEqual(methods[1].values["to_hop_mon_hoc"], ["K01", "A00"])

    def test_unknown_combo_code_is_named_in_the_response(self):
        document = {
            "dats_tuyen_sinh": {
                "ten_de_an": "Đề án",
                "dats_chuong_trinh_dao_tao": [
                    {
                        "ten_chuong_trinh": "Kỹ thuật",
                        "dats_phuong_thuc": [
                            {
                                "ma_phuong_thuc_cua_bo": "100",
                                "ten_phuong_thuc_cua_truong": "THPT",
                                "to_hop_mon_hoc": ["A01", "ZZ9"],
                            }
                        ],
                    }
                ],
            }
        }
        with self.assertLogs("app.services.dats_import", level="WARNING") as logs:
            with self.assertRaises(DatsImportError) as caught:
                prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertEqual(
            str(caught.exception),
            "dats_phuong_thuc dòng 1 có mã tổ hợp ZZ9 không có trong danh mục",
        )
        self.assertTrue(any("ma_to_hop=ZZ9" in line for line in logs.output))

    def test_unknown_subject_code_is_rejected(self):
        document = {
            "dats_tuyen_sinh": {
                "ten_de_an": "Đề án",
                "dats_dieu_kien_du_tuyen": [
                    {"ten_dieu_kien": "Tốt nghiệp", "ma_doi_tuong_du_tuyen": "NOPE"},
                ],
            }
        }
        with self.assertRaises(DatsImportError) as caught:
            prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertIn("NOPE", str(caught.exception))

    def test_method_outside_program_is_rejected(self):
        document = {
            "dats_tuyen_sinh": {
                "ten_de_an": "Đề án",
                "dats_phuong_thuc": [
                    {"ma_phuong_thuc_cua_bo": "100", "ten_phuong_thuc_cua_truong": "THPT"},
                ],
            }
        }
        with self.assertRaises(DatsImportError) as caught:
            prepare_import(document, ma_truong="BKA", nam_tuyen_sinh=2026, catalogs=catalogs())
        self.assertIn("dats_chuong_trinh_dao_tao", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
