import unittest
from types import SimpleNamespace

from app.api.v1.endpoints.ho_so import update_thong_tin_ca_nhan
from app.schemas.ho_so import ThongTinCaNhanWrite


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
        profile = SimpleNamespace(
            gioi_tinh=None,
            ngay_sinh=None,
            dan_toc=None,
            ton_giao=None,
            tinh_thanh_id=None,
            khu_vuc_uu_tien_id=None,
            doi_tuong_uu_tien_id=None,
            trinh_do_hoc_van=nang_luc,
            suc_khoe_the_chat=suc_khoe,
            kha_nang_tai_chinh=None,
        )
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


if __name__ == "__main__":
    unittest.main()
