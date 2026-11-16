import unittest
from types import SimpleNamespace

from app.api.v1.endpoints.ho_so import get_ho_so, update_thong_tin_ca_nhan
from app.schemas.ho_so import ThongTinCaNhanWrite


def _ho_so(**kwargs):
    """Bản ghi nguoi_dung_thong_tin giả, mặc định trống."""
    data = dict(
        gioi_tinh=None,
        ngay_sinh=None,
        dan_toc=None,
        ton_giao=None,
        tinh_thanh_id=None,
        khu_vuc_uu_tien_id=None,
        doi_tuong_uu_tien_id=None,
        trinh_do_hoc_van=None,
        suc_khoe_the_chat=None,
        kha_nang_tai_chinh=None,
        edu_coin=0,
        xu_he_thong=0,
        luot_tra_cuu=0,
        luot_hoi_dap=0,
        luot_khao_sat=0,
        mat_khau_thanh_toan=None,
        created_at=None,
        updated_at=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _tai_khoan():
    return SimpleNamespace(id=1, ho_ten="Nguyễn Văn An", email="a@example.com", so_dien_thoai=None)


class _DbGia:
    """Session giả: đã có sẵn hồ sơ, không trùng số điện thoại."""

    def __init__(self, profile):
        self.profile = profile
        self.committed = False

    def scalar(self, *_args, **_kwargs):
        return self.profile

    def get(self, *_args, **_kwargs):
        return object()

    def add(self, *_args):
        pass

    def commit(self):
        self.committed = True

    def refresh(self, *_args):
        pass


class TestThongTinCaNhan(unittest.TestCase):
    def test_chi_cap_nhat_thong_tin_ca_nhan_giu_nguyen_ho_so_nang_luc(self):
        nang_luc = {"hoc_luc_trung_binh": {"12": 8.5}}
        suc_khoe = {"chieu_cao": 165}
        profile = _ho_so(trinh_do_hoc_van=nang_luc, suc_khoe_the_chat=suc_khoe)
        user = SimpleNamespace(id=1, ho_ten="Cũ", email="a@example.com", so_dien_thoai=None)
        db = _DbGia(profile)

        result = update_thong_tin_ca_nhan(
            ThongTinCaNhanWrite(ho_ten="  Nguyễn Văn An ", gioi_tinh=1, tinh_thanh_id=5), db, user
        )

        self.assertTrue(db.committed)
        self.assertEqual(user.ho_ten, "Nguyễn Văn An")
        self.assertEqual(profile.gioi_tinh, 1)
        self.assertEqual(profile.tinh_thanh_id, 5)
        self.assertIs(profile.trinh_do_hoc_van, nang_luc)
        self.assertIs(profile.suc_khoe_the_chat, suc_khoe)
        self.assertEqual(result.ho_ten, "Nguyễn Văn An")

    def test_schema_thong_tin_ca_nhan_khong_nhan_ho_so_nang_luc(self):
        self.assertNotIn("trinh_do_hoc_van", ThongTinCaNhanWrite.model_fields)


class TestLayHoSo(unittest.TestCase):
    def test_chua_co_ho_so_van_tra_du_cau_truc(self):
        result = get_ho_so(_DbGia(None), _tai_khoan())
        self.assertEqual(result.nguoi_dung_id, 1)
        self.assertEqual(result.email, "a@example.com")
        self.assertIsNone(result.gioi_tinh)
        self.assertEqual(
            (result.edu_coin, result.luot_tra_cuu, result.luot_hoi_dap, result.luot_khao_sat), (0, 0, 0, 0)
        )
        self.assertFalse(result.co_mat_khau_thanh_toan)

    def test_tra_ve_so_du_va_khong_lo_mat_khau_thanh_toan(self):
        profile = _ho_so(
            gioi_tinh=2, edu_coin=120, luot_tra_cuu=5, luot_khao_sat=2, mat_khau_thanh_toan="hash-bi-mat"
        )
        result = get_ho_so(_DbGia(profile), _tai_khoan())
        self.assertEqual(result.gioi_tinh, 2)
        self.assertEqual((result.edu_coin, result.luot_tra_cuu, result.luot_khao_sat), (120, 5, 2))
        self.assertTrue(result.co_mat_khau_thanh_toan)
        self.assertNotIn("hash-bi-mat", result.model_dump_json())


if __name__ == "__main__":
    unittest.main()


class _DbCommit:
    def __init__(self):
        self.da_commit = False

    def commit(self):
        self.da_commit = True


class TestDoiMatKhau(unittest.TestCase):
    def setUp(self):
        from app.core.security import hash_password

        self.user = SimpleNamespace(id=1, mat_khau=hash_password("matkhaucu"))

    def _doi(self, cu, moi, db=None):
        from app.api.v1.endpoints.ho_so import doi_mat_khau
        from app.schemas.auth import DoiMatKhauRequest

        return doi_mat_khau(DoiMatKhauRequest(mat_khau_cu=cu, mat_khau_moi=moi), db or _DbCommit(), self.user)

    def test_dung_mat_khau_cu_thi_doi_duoc(self):
        from app.core.security import verify_password

        db = _DbCommit()
        self.assertTrue(self._doi("matkhaucu", "matkhaumoi", db).thanh_cong)
        self.assertTrue(db.da_commit)
        self.assertTrue(verify_password("matkhaumoi", self.user.mat_khau))

    def test_sai_mat_khau_cu_tra_400(self):
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as ctx:
            self._doi("sai", "matkhaumoi")
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.detail, "Mật khẩu hiện tại không đúng")

    def test_mat_khau_moi_trung_cu_tra_400(self):
        from fastapi import HTTPException

        with self.assertRaises(HTTPException) as ctx:
            self._doi("matkhaucu", "matkhaucu")
        self.assertEqual(ctx.exception.status_code, 400)
