import unittest

from pydantic import ValidationError

from app.schemas.dats_website import DatsWebsiteFields, DatsWebsiteImportRequest


class DatsWebsiteSchemaTests(unittest.TestCase):
    def test_import_keeps_selected_proposal_and_drops_source_ids(self):
        request = DatsWebsiteImportRequest.model_validate(
            {
                "de_an_id": 42,
                "du_lieu": [
                    {
                        "id": 1,
                        "de_an_id": 7,
                        "loai_website": "tuyen_sinh",
                        "ten_trang": "Cổng tuyển sinh",
                        "url": "https://ts.hust.edu.vn",
                        "ghi_chu": None,
                    }
                ],
            }
        )
        self.assertEqual(request.de_an_id, 42)
        stored = request.du_lieu[0].model_dump()
        self.assertNotIn("id", stored)
        self.assertNotIn("de_an_id", stored)
        self.assertEqual(stored["ten_trang"], "Cổng tuyển sinh")
        self.assertEqual(stored["url"], "https://ts.hust.edu.vn")

    def test_blank_name_is_rejected(self):
        with self.assertRaises(ValidationError):
            DatsWebsiteFields.model_validate({"ten_trang": "   "})


if __name__ == "__main__":
    unittest.main()
