import unittest

from pydantic import ValidationError

from app.schemas.dats_chuong_trinh_dao_tao import (
    DatsChuongTrinhDaoTaoFields,
    DatsChuongTrinhDaoTaoImportRequest,
)


class DatsChuongTrinhDaoTaoSchemaTests(unittest.TestCase):
    def test_import_keeps_selected_proposal_and_drops_source_ids(self):
        request = DatsChuongTrinhDaoTaoImportRequest.model_validate(
            {
                "de_an_id": 42,
                "du_lieu": [
                    {
                        "id": 2610001,
                        "de_an_id": 2600001,
                        "nganh_dao_tao_id": None,
                        "ma_xet_tuyen": "BF1",
                        "ten_chuong_trinh": "Kỹ thuật Sinh học",
                        "trinh_do_dao_tao": "dai_hoc",
                        "hinh_thuc_dao_tao": "chinh_quy",
                        "co_so_id": None,
                        "thoi_gian_dao_tao_nam": None,
                        "ngon_ngu_dao_tao": None,
                        "chi_tieu_tuyen_sinh": 160,
                        "kieu_phan_bo_chi_tieu": None,
                        "ghi_chu": "Nhóm: chuong_trinh_chuan",
                    }
                ],
            }
        )
        self.assertEqual(request.de_an_id, 42)
        stored = request.du_lieu[0].model_dump()
        self.assertNotIn("id", stored)
        self.assertNotIn("de_an_id", stored)
        self.assertEqual(stored["ten_chuong_trinh"], "Kỹ thuật Sinh học")
        self.assertEqual(stored["chi_tieu_tuyen_sinh"], 160)

    def test_blank_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            DatsChuongTrinhDaoTaoFields.model_validate({"ten_chuong_trinh": "   "})


if __name__ == "__main__":
    unittest.main()
