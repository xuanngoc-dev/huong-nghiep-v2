import json
import unittest
from pathlib import Path

from app.services.dats_import import CatalogIndex, DatsImportError, prepare_import

SAMPLE = Path(__file__).resolve().parents[2] / "docs" / "BKA_2026_import_mot_truong_mot_nam.json"
CODES = {
    "phuong_thuc": {"XTTN": 11, "DGTD": 12, "THPT": 13},
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
    def test_sample_file_keeps_every_dats_table_and_resolves_catalogs(self):
        document = json.loads(SAMPLE.read_text())
        rows = prepare_import(document, truong_id=9, nam_tuyen_sinh=2027, catalogs=catalogs())
        counts = {}
        for row in rows:
            counts[row.table] = counts.get(row.table, 0) + 1

        self.assertEqual(counts["dats_tuyen_sinh"], 1)
        self.assertEqual(counts["dats_chuong_trinh_dao_tao"], 68)
        self.assertEqual(counts["dats_phuong_thuc"], 204)
        self.assertEqual(counts["dats_phuong_thuc_to_hop"], 229)
        self.assertEqual(counts["dats_lien_he_tuyen_sinh"], 1)
        self.assertEqual(counts["dats_trinh_do_nganh"], 68)
        self.assertEqual(counts["dats_doi_tuong_du_tuyen"], 5)
        self.assertEqual(counts["dats_dieu_kien_du_tuyen"], 30)
        self.assertEqual(counts["dats_tieu_chi_xet_tuyen"], 13)
        self.assertEqual(counts["dats_diem_cong"], 2)
        self.assertEqual(counts["dats_ho_so_du_tuyen"], 5)
        self.assertEqual(counts["dats_chinh_sach_xet_tuyen_thang"], 2)

        proposal = next(row for row in rows if row.table == "dats_tuyen_sinh")
        self.assertEqual(proposal.values["truong_id"], 9)
        self.assertEqual(proposal.values["nam_tuyen_sinh"], 2027)
        self.assertEqual(proposal.source_id, 2600001)

        methods = [row for row in rows if row.table == "dats_phuong_thuc"]
        self.assertEqual(
            {row.values["ma_phuong_thuc_cua_bo"] for row in methods},
            set(CODES["phuong_thuc"]),
        )
        self.assertTrue(all(row.values["de_an_chuong_trinh_id"] for row in methods))

        combos = [row for row in rows if row.table == "dats_phuong_thuc_to_hop"]
        self.assertEqual({row.values["to_hop_id"] for row in combos}, set(CODES["to_hop"].values()))
        self.assertTrue(all(row.values["de_an_phuong_thuc_id"] for row in combos))

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
            prepare_import(document, truong_id=9, nam_tuyen_sinh=2026, catalogs=limited_without_combo)
        self.assertIn("tổ hợp", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
