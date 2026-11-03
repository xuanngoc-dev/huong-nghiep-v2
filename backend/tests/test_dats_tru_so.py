import unittest

from pydantic import ValidationError

from app.schemas.dats_tru_so import DatsTruSoFields, DatsTruSoImportRequest


class DatsTruSoSchemaTests(unittest.TestCase):
    def test_import_keeps_selected_proposal_and_drops_source_ids(self):
        request = DatsTruSoImportRequest.model_validate(
            {
                "de_an_id": 42,
                "du_lieu": [
                    {
                        "id": 1,
                        "de_an_id": 7,
                        "vai_tro": "chinh",
                        "ten_co_so": "Cơ sở 1",
                        "loai_co_so": "tru_so",
                        "dia_chi": "Số 1 Đại Cồ Việt, Hà Nội",
                        "so_dien_thoai": "02438692222",
                        "ghi_chu": None,
                    }
                ],
            }
        )
        self.assertEqual(request.de_an_id, 42)
        stored = request.du_lieu[0].model_dump()
        self.assertNotIn("id", stored)
        self.assertNotIn("de_an_id", stored)
        self.assertEqual(stored["ten_co_so"], "Cơ sở 1")
        self.assertEqual(stored["vai_tro"], "chinh")

    def test_blank_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            DatsTruSoFields.model_validate({"ten_co_so": "   "})


if __name__ == "__main__":
    unittest.main()
