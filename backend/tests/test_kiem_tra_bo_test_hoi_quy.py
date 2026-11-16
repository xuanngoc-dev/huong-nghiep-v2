"""Bước 5.4: đối chiếu đề án trong CSDL với bộ test hồi quy."""

import json
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import select

import app.models as M
from app.scripts.kiem_tra_bo_test_hoi_quy import kiem_tra, ma_bam_file
from tests import test_xet_tuyen_danh_gia as danh_gia


class KiemTraBoTestTests(unittest.TestCase):
    setUpClass = classmethod(danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__)
    tearDownClass = classmethod(danh_gia.DanhGiaTuCsdlTests.tearDownClass.__func__)

    def test_thieu_lech_du(self):
        de_an = {d.ma_truong: d for d in self.db.scalars(select(M.DatsTuyenSinh))}
        du_lieu = {"ma_truong": "BKA", "nam_tuyen_sinh": 2026, "x": 1}
        self.db.add(M.XtLichSuImport(de_an_id=de_an["BKA"].id, ma_bam=ma_bam_file(du_lieu), ten_file="bka.json"))
        self.db.commit()
        with tempfile.TemporaryDirectory() as tam:
            thu_muc = Path(tam)
            (thu_muc / "BKA_2026").mkdir()
            (thu_muc / "BKA_2026" / "de_an.json").write_text(json.dumps(du_lieu), encoding="utf-8")
            ket_qua = {d.ma_truong: d.ket_luan for d in kiem_tra(self.db, thu_muc)}
            self.assertEqual(ket_qua, {"BKA": "DU", "NTH": "THIEU"})
            (thu_muc / "BKA_2026" / "de_an.json").write_text(json.dumps({**du_lieu, "x": 2}), encoding="utf-8")
            self.assertEqual({d.ma_truong: d.ket_luan for d in kiem_tra(self.db, thu_muc)}["BKA"], "LECH")


if __name__ == "__main__":
    unittest.main()
