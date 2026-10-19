import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import kiem_tra_du_lieu
from app.core.config import settings
from app.services import kiem_tra_du_lieu as service


def _school(code, name, programs):
    return {"truong": {"ma_truong": code, "ten_truong": name, "loai_hinh": "DaiHoc", "nam_tuyen_sinh": 2026}, "danh_sach_nganh": programs}


class KiemTraDuLieuTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        setting = patch.object(settings, "tai_lieu_dir", str(self.root))
        setting.start()
        self.addCleanup(setting.stop)
        self.addCleanup(service._corpus.cache_clear)
        program = {
            "ma_nganh": "7340115",
            "ma_xet_tuyen": "EP19",
            "ten_nganh": "Marketing",
            "phuong_thuc_tuyen_sinh": [
                {"ma_phuong_thuc": "100", "ten_phuong_thuc": "Thi THPT", "loai_phuong_thuc": "DiemThiTHPT"},
                {"ma_phuong_thuc": "200", "ten_phuong_thuc": "Học bạ", "loai_phuong_thuc": "HocBa"},
            ],
        }
        (self.root / "beta.json").write_text(json.dumps(_school("BBB", "Đại học Beta", [program])), encoding="utf-8")
        (self.root / "alpha (1).json").write_text(json.dumps(_school("AAA", "Đại học Alpha", [program, program])), encoding="utf-8")
        (self.root / "hong.json").write_text("{", encoding="utf-8")
        app = FastAPI()
        app.include_router(kiem_tra_du_lieu.router, prefix="/api/v1")
        self.client = TestClient(app)

    def test_danh_sach_va_noi_dung(self):
        response = self.client.get("/api/v1/kiem-tra-du-lieu/truong")
        self.assertEqual(response.status_code, 200)
        rows = {item["ten_tep"]: item for item in response.json()}
        self.assertEqual(set(rows), {"alpha (1).json", "beta.json", "hong.json"})
        self.assertEqual(rows["alpha (1).json"]["ma_truong"], "AAA")
        self.assertEqual(rows["alpha (1).json"]["so_nganh"], 2)
        self.assertEqual(rows["alpha (1).json"]["so_phuong_thuc"], 2)
        self.assertEqual(rows["alpha (1).json"]["so_ban_ghi_phuong_thuc"], 4)
        self.assertTrue(rows["beta.json"]["hop_le"])
        self.assertFalse(rows["hong.json"]["hop_le"])

        detail = self.client.get("/api/v1/kiem-tra-du-lieu/noi-dung", params={"ten_tep": "alpha (1).json"})
        self.assertEqual(detail.status_code, 200)
        body = detail.json()
        self.assertTrue(body["hop_le"])
        self.assertEqual(body["du_lieu"]["truong"]["ma_truong"], "AAA")
        self.assertEqual(len(body["du_lieu"]["danh_sach_nganh"]), 2)

    def test_tu_choi_ten_tep_va_file_hong(self):
        self.assertEqual(self.client.get("/api/v1/kiem-tra-du-lieu/noi-dung", params={"ten_tep": "../beta.json"}).status_code, 400)
        self.assertEqual(self.client.get("/api/v1/kiem-tra-du-lieu/noi-dung", params={"ten_tep": "khong-co.json"}).status_code, 404)
        broken = self.client.get("/api/v1/kiem-tra-du-lieu/noi-dung", params={"ten_tep": "hong.json"})
        self.assertEqual(broken.status_code, 400)
