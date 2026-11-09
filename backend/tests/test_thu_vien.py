import io
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app.core.config import settings
from app.services import thu_vien


PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


class ThuVienTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old_dir = settings.thu_vien_dir
        settings.thu_vien_dir = self.tmp.name
        self.addCleanup(setattr, settings, "thu_vien_dir", self.old_dir)

    def test_save_png_stays_inside_library_and_returns_path(self):
        item = thu_vien.save_thu_vien("anh minh hoa.png", io.BytesIO(PNG))

        stored = Path(self.tmp.name) / item.ten
        self.assertTrue(stored.is_file())
        self.assertEqual(stored.read_bytes(), PNG)
        self.assertEqual(item.loai, "hinh_anh")
        self.assertTrue(item.duong_dan.startswith("/api/v1/thu-vien/tep/"))
        self.assertEqual(thu_vien.list_thu_vien()[0].ten, item.ten)

    def test_rejects_text_and_mismatched_bytes(self):
        with self.assertRaises(HTTPException):
            thu_vien.save_thu_vien("ghi-chu.txt", io.BytesIO(b"xin chao"))
        with self.assertRaises(HTTPException):
            thu_vien.save_thu_vien("gia.png", io.BytesIO(b"khong phai anh"))
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])

    def test_delete_does_not_escape_library(self):
        outside = Path(self.tmp.name).parent / "ngoai.png"
        outside.write_bytes(PNG)
        self.addCleanup(outside.unlink, missing_ok=True)

        with self.assertRaises(HTTPException):
            thu_vien.delete_thu_vien("../ngoai.png")
        self.assertTrue(outside.is_file())

    def test_folder_rename_and_zip_roundtrip(self):
        folder = thu_vien.tao_thu_muc("", "Ảnh")
        saved = thu_vien.save_thu_vien("a.png", io.BytesIO(PNG), folder.duong_dan_tuong_doi)
        renamed = thu_vien.doi_ten(saved.duong_dan_tuong_doi, "b.png")

        self.assertEqual(renamed.ten, "b.png")
        self.assertEqual(thu_vien.list_thu_vien(folder.duong_dan_tuong_doi)[0].ten, "b.png")

        archive = thu_vien.nen_muc("", [folder.duong_dan_tuong_doi], "bo-suu-tap")
        self.assertEqual(archive.loai, "nen")
        with zipfile.ZipFile(Path(self.tmp.name) / archive.ten) as packed:
            self.assertIn("Ảnh/b.png", packed.namelist())

        extracted = thu_vien.giai_nen(archive.duong_dan_tuong_doi)
        restored = Path(self.tmp.name) / extracted.ten / "Ảnh" / "b.png"
        self.assertEqual(restored.read_bytes(), PNG)

    def test_zip_slip_is_rejected(self):
        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as archive:
            archive.writestr("../evil.txt", b"no")
        payload.seek(0)
        item = thu_vien.save_thu_vien("bad.zip", payload)

        with self.assertRaises(HTTPException):
            thu_vien.giai_nen(item.duong_dan_tuong_doi)
        self.assertFalse((Path(self.tmp.name) / "evil.txt").exists())
        self.assertFalse((Path(self.tmp.name).parent / "evil.txt").exists())

    def test_copy_move_and_delete_many(self):
        dest = thu_vien.tao_thu_muc("", "dich")
        saved = thu_vien.save_thu_vien("a.png", io.BytesIO(PNG))

        copied = thu_vien.sao_chep([saved.duong_dan_tuong_doi], dest.duong_dan_tuong_doi)
        self.assertEqual(copied, 1)
        self.assertTrue((Path(self.tmp.name) / "a.png").is_file())
        self.assertTrue((Path(self.tmp.name) / "dich" / "a.png").is_file())

        moved = thu_vien.di_chuyen([saved.duong_dan_tuong_doi], dest.duong_dan_tuong_doi)
        self.assertEqual(moved, 1)
        self.assertFalse((Path(self.tmp.name) / "a.png").exists())
        self.assertTrue((Path(self.tmp.name) / "dich" / "a-2.png").is_file())

        removed = thu_vien.xoa_nhieu([dest.duong_dan_tuong_doi])
        self.assertEqual(removed, 1)
        self.assertFalse((Path(self.tmp.name) / "dich").exists())

    def test_download_url_saves_like_upload_and_blocks_internal_hosts(self):
        with self.assertRaises(HTTPException):
            thu_vien.tai_tu_url("file:///etc/passwd")
        with self.assertRaises(HTTPException):
            thu_vien.tai_tu_url("http://127.0.0.1/a.png")

        class FakeResponse:
            status_code = 200
            headers = {"content-type": "image/png"}

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def iter_bytes(self, chunk_size=None):
                yield PNG

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def stream(self, method, url, headers=None):
                return FakeResponse()

        def public_dns(host, port, *args, **kwargs):
            return [(2, 1, 6, "", ("93.184.216.34", port or 0))]

        with patch("app.services.thu_vien.socket.getaddrinfo", public_dns), patch(
            "app.services.thu_vien.httpx.Client", FakeClient
        ):
            item = thu_vien.tai_tu_url("https://example.com/anh-mau.png")

        stored = Path(self.tmp.name) / item.ten
        self.assertEqual(stored.read_bytes(), PNG)
        self.assertTrue(item.duong_dan.startswith("/api/v1/thu-vien/tep/"))

    def test_cannot_move_folder_into_itself(self):
        folder = thu_vien.tao_thu_muc("", "goc")
        child = thu_vien.tao_thu_muc(folder.duong_dan_tuong_doi, "con")
        with self.assertRaises(HTTPException):
            thu_vien.di_chuyen([folder.duong_dan_tuong_doi], child.duong_dan_tuong_doi)


if __name__ == "__main__":
    unittest.main()
