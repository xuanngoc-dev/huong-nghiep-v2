import json
import unicodedata
import unittest

from app.core.json_utf8 import Utf8JSONResponse, chuan_hoa_utf8


class JsonUtf8Tests(unittest.TestCase):
    def test_strings_are_composed_and_encoded_as_utf8(self):
        tach = unicodedata.normalize("NFD", "Đại học Hà Nội")
        body = Utf8JSONResponse({"ten": tach, "tags": [tach]}).body

        self.assertEqual(body, body.decode("utf-8").encode("utf-8"))
        self.assertNotIn("\\u", body.decode("utf-8"))
        data = json.loads(body)
        self.assertEqual(data["ten"], "Đại học Hà Nội")
        self.assertTrue(unicodedata.is_normalized("NFC", data["ten"]))
        self.assertEqual(data["tags"], ["Đại học Hà Nội"])

    def test_content_type_declares_utf8(self):
        response = Utf8JSONResponse({"ten": "Học viện"})
        self.assertEqual(response.headers["content-type"], "application/json; charset=utf-8")

    def test_nested_keys_are_normalized(self):
        key = unicodedata.normalize("NFD", "mô tả")
        self.assertEqual(chuan_hoa_utf8({key: "ệ"})[unicodedata.normalize("NFC", key)], "ệ")


if __name__ == "__main__":
    unittest.main()
