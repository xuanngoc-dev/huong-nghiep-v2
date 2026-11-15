import importlib
import pkgutil
import unittest

from fastapi import HTTPException

from app.api.v1 import endpoints


class _DbRong:
    """Session giả: không tìm thấy bản ghi nào."""

    def get(self, *_args, **_kwargs):
        return None


def _cac_module():
    for info in pkgutil.iter_modules(endpoints.__path__):
        yield info.name, importlib.import_module(f"{endpoints.__name__}.{info.name}")


class TestKhongTra404(unittest.TestCase):
    """404 chỉ dành cho sai đường dẫn API; không tìm thấy id trả 400 kèm thông báo cụ thể."""

    def test_khong_con_helper_get_or_404(self):
        for name, module in _cac_module():
            with self.subTest(module=name):
                self.assertFalse(hasattr(module, "_get_or_404"))

    def test_get_or_400_bao_ro_id(self):
        for name, module in _cac_module():
            helper = getattr(module, "_get_or_400", None)
            if helper is None:
                continue
            with self.subTest(module=name):
                with self.assertRaises(HTTPException) as ctx:
                    helper(_DbRong(), 987654)
                self.assertEqual(ctx.exception.status_code, 400)
                self.assertIn("987654", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
