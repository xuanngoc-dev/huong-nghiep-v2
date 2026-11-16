import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from app.api.v1.endpoints import tn_tim_truong_phu_hop as ep
from app.schemas.tn_lich_su_tim_truong_phu_hop import TimTruongPhuHopRequest


class _DbGia:
    """Session giả: không có yêu cầu trùng mã, giữ bản ghi lịch sử vừa thêm."""

    def __init__(self):
        self.item = None

    def scalar(self, *_args, **_kwargs):
        return None

    def add(self, obj):
        obj.id = 1
        self.item = obj

    def get(self, _model, _id):
        return self.item

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, _obj):
        pass


def _payload(**kwargs):
    data = dict(ma_yeu_cau="YEUCAU0001", ma_nganh="7480201", nam_tuyen_sinh=2026)
    data.update(kwargs)
    return TimTruongPhuHopRequest(**data)


class TestLuotTimTruong(unittest.TestCase):
    """Dùng lượt miễn phí trước, hết thì trừ lượt tra cứu đã mua, hết cả hai thì 429."""

    def setUp(self):
        self.user = SimpleNamespace(id=3)
        self.ho_so = SimpleNamespace(luot_tra_cuu=3)
        cau_hinh = SimpleNamespace(so_luot_tra_cuu_thanh_vien_ngay=5, so_luot_tra_cuu_khach_ngay=1)
        ket_qua_dem = SimpleNamespace(total=2, items=[])
        self.patches = [
            patch.object(ep, "cau_hinh_dang_ap_dung", return_value=cau_hinh),
            patch.object(ep, "_ho_so", side_effect=lambda *_a, **_k: self.ho_so),
            patch.object(ep, "_dem_truong", return_value=ket_qua_dem),
            patch.object(ep, "_ket_qua", side_effect=lambda _db, item, *_a: item),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def _tim(self, da_dung, user="thanh_vien", **kwargs):
        user = self.user if user == "thanh_vien" else None
        with patch.object(ep, "_da_dung_hom_nay", return_value=da_dung):
            return ep.tim_truong_phu_hop(_payload(**kwargs), _DbGia(), user)

    def test_con_luot_mien_phi_thi_khong_tru_luot_tra_cuu(self):
        item = self._tim(da_dung=4)
        self.assertEqual(item.loai_luot, "mien_phi")
        self.assertEqual(self.ho_so.luot_tra_cuu, 3)

    def test_het_mien_phi_thi_tru_luot_tra_cuu(self):
        item = self._tim(da_dung=5)
        self.assertEqual(item.loai_luot, "tra_phi")
        self.assertEqual(item.trang_thai_xu_ly, "thanh_cong")
        self.assertEqual(self.ho_so.luot_tra_cuu, 2)

    def test_het_ca_hai_thi_429(self):
        self.ho_so.luot_tra_cuu = 0
        with self.assertRaises(HTTPException) as ctx:
            self._tim(da_dung=5)
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertIn("nạp thêm lượt tra cứu", ctx.exception.detail)

    def test_khach_het_mien_phi_thi_429(self):
        with self.assertRaises(HTTPException) as ctx:
            self._tim(da_dung=1, user=None, ma_thiet_bi="thietbi-0001")
        self.assertEqual(ctx.exception.status_code, 429)

    def test_tim_loi_thi_hoan_luot_tra_cuu(self):
        with patch.object(ep, "_dem_truong", side_effect=RuntimeError("lỗi")):
            with self.assertRaises(HTTPException) as ctx:
                self._tim(da_dung=5)
        self.assertEqual(ctx.exception.status_code, 500)
        self.assertEqual(self.ho_so.luot_tra_cuu, 3)


if __name__ == "__main__":
    unittest.main()
