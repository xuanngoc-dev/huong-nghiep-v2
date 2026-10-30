import unittest
from decimal import Decimal

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_tru_so import DatsTruSo
from app.services.dats_detail import DeAnRows, DetailLookups, assemble_bang, code_name


class DatsDetailTests(unittest.TestCase):
    def test_code_name_joins_code_and_name(self):
        self.assertEqual(code_name("BF1", "Sinh học", 1), "BF1 — Sinh học")
        self.assertEqual(code_name(None, None, 4), "#4")
        self.assertEqual(code_name("  ", "Cơ sở 1", 3), "Cơ sở 1")

    def test_assemble_replaces_foreign_keys_with_labels(self):
        program = DatsChuongTrinhDaoTao(
            id=10,
            de_an_id=1,
            nganh_dao_tao_id=5,
            ma_xet_tuyen="BF1",
            ten_chuong_trinh="Kỹ thuật Sinh học",
            trinh_do_dao_tao="dai_hoc",
            hinh_thuc_dao_tao="chinh_quy",
            co_so_id=3,
            thoi_gian_dao_tao_nam=Decimal("4.50"),
            chi_tieu_tuyen_sinh=160,
        )
        method = DatsPhuongThuc(
            id=20,
            de_an_chuong_trinh_id=10,
            ma_phuong_thuc_cua_bo="100",
            ma_phuong_thuc_cua_truong="THPT",
            ten_phuong_thuc_cua_truong="Xét THPT",
            to_hop_mon_hoc=["A00"],
            diem_san=Decimal("22.50"),
        )
        campus = DatsTruSo(id=3, de_an_id=1, ten_co_so="Cơ sở 1", vai_tro="chinh")
        condition = DatsDieuKienDuTuyen(
            id=30,
            de_an_id=1,
            doi_tuong_du_tuyen_id=8,
            de_an_chuong_trinh_id=10,
            de_an_phuong_thuc_id=20,
            ma_dieu_kien="DK_THPT",
            ten_dieu_kien="Tốt nghiệp THPT",
            bat_buoc=True,
        )
        known_combo = DatsPhuongThucToHop(de_an_phuong_thuc_id=20, to_hop_id=7, thu_tu_hien_thi=1)
        missing_combo = DatsPhuongThucToHop(de_an_phuong_thuc_id=99, to_hop_id=98, thu_tu_hien_thi=2)
        lookups = DetailLookups(
            programs={10: "BF1 — Kỹ thuật Sinh học"},
            methods={20: "BF1 — Kỹ thuật Sinh học / THPT — Xét THPT"},
            campuses={3: "Cơ sở 1"},
            audiences={8: "THPT — Thí sinh THPT"},
            majors={5: "7420201 — Sinh học"},
            subjects={7: "A00 — Toán, Lý, Hóa"},
        )

        bang = assemble_bang(
            DeAnRows(
                campuses=[campus],
                programs=[program],
                methods=[method],
                combos=[known_combo, missing_combo],
                conditions=[condition],
            ),
            lookups,
        )

        stored_program = bang["dats_chuong_trinh_dao_tao"][0]
        self.assertEqual(stored_program["row_key"], "10")
        self.assertEqual(stored_program["nganh"], "7420201 — Sinh học")
        self.assertEqual(stored_program["ten_co_so"], "Cơ sở 1")
        self.assertEqual(stored_program["thoi_gian_dao_tao_nam"], "4.5")
        self.assertNotIn("de_an_id", stored_program)
        self.assertNotIn("nganh_dao_tao_id", stored_program)
        self.assertNotIn("co_so_id", stored_program)

        stored_method = bang["dats_phuong_thuc"][0]
        self.assertEqual(stored_method["chuong_trinh"], "BF1 — Kỹ thuật Sinh học")
        self.assertEqual(stored_method["diem_san"], "22.5")
        self.assertEqual(stored_method["to_hop_mon_hoc"], ["A00"])
        self.assertNotIn("de_an_chuong_trinh_id", stored_method)

        self.assertEqual(bang["dats_tru_so"][0]["ten_co_so"], "Cơ sở 1")
        self.assertEqual(bang["dats_phuong_thuc_to_hop"][0]["row_key"], "20-7")
        self.assertEqual(bang["dats_phuong_thuc_to_hop"][0]["to_hop"], "A00 — Toán, Lý, Hóa")
        self.assertEqual(bang["dats_phuong_thuc_to_hop"][1]["phuong_thuc"], "#99")
        self.assertEqual(bang["dats_phuong_thuc_to_hop"][1]["to_hop"], "#98")

        stored_condition = bang["dats_dieu_kien_du_tuyen"][0]
        self.assertEqual(stored_condition["doi_tuong"], "THPT — Thí sinh THPT")
        self.assertEqual(stored_condition["chuong_trinh"], "BF1 — Kỹ thuật Sinh học")
        self.assertEqual(stored_condition["phuong_thuc"], "BF1 — Kỹ thuật Sinh học / THPT — Xét THPT")
        self.assertIs(stored_condition["bat_buoc"], True)
        self.assertNotIn("doi_tuong_du_tuyen_id", stored_condition)
        self.assertEqual(bang["dats_website"], [])


if __name__ == "__main__":
    unittest.main()
