"""CORS: mặc định mọi domain gọi được API từ trình duyệt; lỗi 500 vẫn có header CORS."""

import os
import unittest
from unittest.mock import patch

from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from app import main
from app.core.config import Settings


class CorsTests(unittest.TestCase):
    def setUp(self):
        # Thêm tạm một route lỗi vào app thật (không chạy lifespan nên không kết nối CSDL).
        @main.app.get("/__thu_loi_500")
        def loi():
            raise RuntimeError("lỗi thử")
        self.addCleanup(lambda: main.app.router.routes.pop())
        # Dựng lại middleware với CORS_ORIGINS="*" như mặc định, không phụ thuộc .env của máy chạy test.
        cors = next(m for m in main.app.user_middleware if m.cls is CORSMiddleware)
        cu = cors.kwargs["allow_origins"]
        cors.kwargs["allow_origins"] = ["*"]
        main.app.middleware_stack = None

        def tra_lai():
            cors.kwargs["allow_origins"] = cu
            main.app.middleware_stack = None
        self.addCleanup(tra_lai)
        self.client = TestClient(main.app, raise_server_exceptions=False)

    def test_mac_dinh_cho_phep_moi_domain(self):
        with patch.dict(os.environ):
            os.environ.pop("CORS_ORIGINS", None)
            self.assertEqual(Settings(_env_file=None).cors_origins, ["*"])
        self.assertEqual(Settings(_env_file=None, cors_origins="").cors_origins, ["*"])
        self.assertEqual(Settings(_env_file=None, cors_origins="https://a.vn/, https://b.vn").cors_origins,
                         ["https://a.vn", "https://b.vn"])

    def test_preflight_va_request_tu_domain_bat_ky(self):
        origin = {"Origin": "https://mot-domain-bat-ky.example"}
        preflight = self.client.options(
            "/api/v1/health",
            headers={**origin, "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"},
        )
        self.assertEqual(preflight.status_code, 200)
        self.assertEqual(preflight.headers["access-control-allow-origin"], origin["Origin"])

    def test_loi_500_van_co_header_cors(self):
        # Lớp bắt lỗi nằm trong CORS: trình duyệt thấy lỗi 500 thật thay vì "bị chặn CORS".
        response = self.client.get("/__thu_loi_500", headers={"Origin": "https://mot-domain-bat-ky.example"})
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Lỗi hệ thống. Vui lòng thử lại sau.")
        self.assertEqual(response.headers["access-control-allow-origin"], "https://mot-domain-bat-ky.example")


if __name__ == "__main__":
    unittest.main()
