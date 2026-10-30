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
    def test_sample_file_contains_only_the_proposal(self):
        document = json.loads(SAMPLE.read_text())
        self.assertEqual(
            [key for key in document if key.startswith("dats_")],
            ["dats_tuyen_sinh"],
        )
        rows = prepare_import(document, truong_id=9, nam_tuyen_sinh=2027, catalogs=catalogs())
        self.assertEqual([row.table for row in rows], ["dats_tuyen_sinh"])
        proposal = rows[0]
        self.assertEqual(proposal.values["truong_id"], 9)
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
            prepare_import(document, truong_id=9, nam_tuyen_sinh=2026, catalogs=limited_without_combo)
        self.assertIn("tổ hợp", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
