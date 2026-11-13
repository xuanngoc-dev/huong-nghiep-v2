import importlib
import logging
import pkgutil
import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

import app.api.v1.endpoints as endpoints
from app.api import deps
from app.core.config import settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.main import app


def _token(value: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=value)


class _FakeDb:
    def __init__(self, users: dict[int, SimpleNamespace]):
        self.users = users

    def get(self, _model, user_id: int):
        return self.users.get(user_id)


def _dependency_calls(dependant) -> set:
    calls = {dependant.call}
    for sub in dependant.dependencies:
        calls |= _dependency_calls(sub)
    return calls


def _dm_routes():
    """Mọi route của các module dm_* (cả `router` và `public_router`)."""
    for info in pkgutil.iter_modules(endpoints.__path__):
        if not info.name.startswith("dm_"):
            continue
        module = importlib.import_module(f"{endpoints.__name__}.{info.name}")
        for router_name in ("router", "public_router"):
            router = getattr(module, router_name, None)
            if router is None:
                continue
            for route in router.routes:
                if isinstance(route, APIRoute):
                    yield info.name, route


class DepsTests(unittest.TestCase):
    def setUp(self):
        self.db = _FakeDb(
            {
                1: SimpleNamespace(id=1, vai_tro=1, trang_thai=1),
                2: SimpleNamespace(id=2, vai_tro=2, trang_thai=1),
                3: SimpleNamespace(id=3, vai_tro=2, trang_thai=0),
            }
        )

    def assert_status(self, status_code: int, func, *args):
        with self.assertRaises(HTTPException) as ctx:
            func(*args)
        self.assertEqual(ctx.exception.status_code, status_code)

    def test_thieu_token_tra_401(self):
        self.assert_status(401, deps.get_current_user, None, self.db)

    def test_token_sai_tra_401(self):
        self.assert_status(401, deps.get_current_user, _token("khong-hop-le"), self.db)

    def test_nguoi_dung_khong_ton_tai_tra_401(self):
        self.assert_status(401, deps.get_current_user, _token(create_access_token(999)), self.db)

    def test_tai_khoan_bi_khoa_tra_403(self):
        self.assert_status(403, deps.get_current_user, _token(create_access_token(3)), self.db)

    def test_token_hop_le_tra_nguoi_dung(self):
        user = deps.get_current_user(_token(create_access_token(2)), self.db)
        self.assertEqual(user.id, 2)

    def test_khong_phai_admin_tra_403(self):
        self.assert_status(403, deps.get_admin_user, self.db.users[2])

    def test_admin_duoc_qua(self):
        self.assertIs(deps.get_admin_user(self.db.users[1]), self.db.users[1])

    def test_optional_khong_token_tra_none(self):
        self.assertIsNone(deps.get_optional_user(None, self.db))

    def test_optional_token_hop_le_tra_nguoi_dung(self):
        user = deps.get_optional_user(_token(create_access_token(1)), self.db)
        self.assertEqual(user.id, 1)


class DanhMucPhanQuyenTests(unittest.TestCase):
    """GET danh sách: không cần đăng nhập. GET chi tiết: cần đăng nhập. Ghi: chỉ admin."""

    def test_quy_tac_phan_quyen_danh_muc(self):
        vi_pham = []
        for module_name, route in _dm_routes():
            calls = _dependency_calls(route.dependant)
            can_dang_nhap = deps.get_current_user in calls
            la_admin = deps.get_admin_user in calls
            co_tham_so_path = "{" in route.path
            for method in route.methods:
                if method == "GET" and not co_tham_so_path and can_dang_nhap:
                    vi_pham.append(f"{module_name}: GET {route.path} danh sách không được bắt đăng nhập")
                elif method == "GET" and co_tham_so_path and not can_dang_nhap:
                    vi_pham.append(f"{module_name}: GET {route.path} chi tiết phải bắt đăng nhập")
                elif method != "GET" and not la_admin:
                    vi_pham.append(f"{module_name}: {method} {route.path} phải dùng get_admin_user")
        self.assertEqual(vi_pham, [], "\n".join(vi_pham))


class PublicRouterThuTuTests(unittest.TestCase):
    """`public_router` phải include trước admin router, nếu không `/{item_id}` sẽ bắt mất path public."""

    def setUp(self):
        def _db_loi():
            raise RuntimeError("không dùng DB trong test")
            yield  # pragma: no cover

        app.dependency_overrides[get_db] = _db_loi
        self.client = TestClient(app, raise_server_exceptions=False)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)
        app.dependency_overrides.pop(get_db, None)

    def test_path_public_khong_bi_router_admin_chan(self):
        for info in pkgutil.iter_modules(endpoints.__path__):
            module = importlib.import_module(f"{endpoints.__name__}.{info.name}")
            public_router = getattr(module, "public_router", None)
            if public_router is None:
                continue
            for route in public_router.routes:
                if not isinstance(route, APIRoute) or "GET" not in route.methods or "{" in route.path:
                    continue
                if _dependency_calls(route.dependant) & {deps.get_current_user, deps.get_admin_user}:
                    continue
                with self.subTest(module=info.name, path=route.path):
                    response = self.client.get(settings.api_v1_prefix + route.path)
                    # Qua được tầng xác thực/định tuyến; lỗi 500 do DB giả là chấp nhận được.
                    self.assertNotIn(response.status_code, (401, 403, 404, 405, 422))


if __name__ == "__main__":
    unittest.main()
