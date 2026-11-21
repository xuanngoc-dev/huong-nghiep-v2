import unittest
from contextlib import nullcontext
from unittest.mock import patch
from types import SimpleNamespace

from app.api.v1.endpoints.ho_so import get_ho_so, update_doi_tuong, update_thong_tin_ca_nhan
from app.schemas.ho_so import DoiTuongTaiKhoan, ThongTinCaNhanWrite


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
        so_luong_token_kha_dung=0,
        so_luong_token_da_dung=0,
        mat_khau_thanh_toan=None,
        created_at=None,
        updated_at=None,
    )
    data.update(kwargs)
    return SimpleNamespace(**data)


def _tai_khoan():
    return SimpleNamespace(id=1, ho_ten="Nguyễn Văn An", email="a@example.com", so_dien_thoai=None, doi_tuong=None)


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

    def flush(self):
        pass

    def begin_nested(self):
        return nullcontext()

    def commit(self):
        self.committed = True

    def refresh(self, *_args):
        pass


# Đồng bộ sang hồ sơ hs_* được kiểm ở tests/test_hs_ho_so.py; Session giả ở đây không chạy truy vấn thật.
@patch("app.api.v1.endpoints.ho_so.dong_bo_tu_json", return_value=None)
class TestThongTinCaNhan(unittest.TestCase):
    def test_chi_cap_nhat_thong_tin_ca_nhan_giu_nguyen_ho_so_nang_luc(self, _dong_bo):
        nang_luc = {"hoc_luc_trung_binh": {"12": 8.5}}
        suc_khoe = {"chieu_cao": 165}
        profile = _ho_so(trinh_do_hoc_van=nang_luc, suc_khoe_the_chat=suc_khoe)
        user = SimpleNamespace(id=1, ho_ten="Cũ", email="a@example.com", so_dien_thoai=None, doi_tuong=None)
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

    def _cap_nhat_doi_tuong(self, user, **kw):
        return update_thong_tin_ca_nhan(ThongTinCaNhanWrite(ho_ten="Nguyễn Văn An", **kw), _DbGia(_ho_so()), user)

    def test_cap_nhat_doi_tuong(self, _dong_bo):
        user = _tai_khoan()
        result = self._cap_nhat_doi_tuong(user, doi_tuong="sinh-vien")
        self.assertEqual(user.doi_tuong, "sinh-vien")
        self.assertEqual(result.doi_tuong, "sinh-vien")

    def test_khong_gui_doi_tuong_thi_giu_nguyen(self, _dong_bo):
        # Trang Hồ sơ năng lực lưu thông tin cá nhân nhưng không gửi doi_tuong: không được xóa đối tượng đã chọn.
        user = _tai_khoan()
        user.doi_tuong = "phu-huynh"
        self._cap_nhat_doi_tuong(user)
        self.assertEqual(user.doi_tuong, "phu-huynh")

    def test_gui_null_thi_bo_doi_tuong(self, _dong_bo):
        user = _tai_khoan()
        user.doi_tuong = "phu-huynh"
        self._cap_nhat_doi_tuong(user, doi_tuong=None)
        self.assertIsNone(user.doi_tuong)

    def test_doi_tuong_khong_hop_le(self, _dong_bo):
        with self.assertRaises(ValueError):
            ThongTinCaNhanWrite(ho_ten="Nguyễn Văn An", doi_tuong="ca-si")

    def test_schema_thong_tin_ca_nhan_khong_nhan_ho_so_nang_luc(self, _dong_bo):
        self.assertNotIn("trinh_do_hoc_van", ThongTinCaNhanWrite.model_fields)


class TestDoiTuongTaiKhoan(unittest.TestCase):
    def test_doi_doi_tuong_tu_khung_chat(self):
        user = _tai_khoan()
        user.doi_tuong = "phu-huynh"
        db = _DbGia(None)
        result = update_doi_tuong(DoiTuongTaiKhoan(doi_tuong="sinh-vien"), db, user)
        self.assertTrue(db.committed)
        self.assertEqual(user.doi_tuong, "sinh-vien")
        self.assertEqual(result.doi_tuong, "sinh-vien")

    def test_bo_chon_doi_tuong(self):
        user = _tai_khoan()
        user.doi_tuong = "phu-huynh"
        update_doi_tuong(DoiTuongTaiKhoan(doi_tuong=None), _DbGia(None), user)
        self.assertIsNone(user.doi_tuong)

    def test_ma_khong_hop_le(self):
        with self.assertRaises(ValueError):
            DoiTuongTaiKhoan(doi_tuong="ca-si")


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
            gioi_tinh=2, edu_coin=120, luot_tra_cuu=5, luot_khao_sat=2, mat_khau_thanh_toan="hash-bi-mat",
            so_luong_token_kha_dung=5000, so_luong_token_da_dung=1200,
        )
        result = get_ho_so(_DbGia(profile), _tai_khoan())
        self.assertEqual(result.gioi_tinh, 2)
        self.assertEqual((result.edu_coin, result.luot_tra_cuu, result.luot_khao_sat), (120, 5, 2))
        self.assertEqual((result.so_luong_token_kha_dung, result.so_luong_token_da_dung), (5000, 1200))
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


class _DbThongKe:
    """Session giả: execute() trả lần lượt kết quả nhóm theo ngày của tìm trường rồi khảo sát."""

    def __init__(self, *ket_qua):
        self.ket_qua = list(ket_qua)

    def execute(self, *_args, **_kwargs):
        rows = self.ket_qua.pop(0)
        return SimpleNamespace(all=lambda: rows)


class TestThongKeSuDung(unittest.TestCase):
    def test_du_tung_ngay_va_cong_theo_loai_luot(self):
        from datetime import date, timedelta

        from app.api.v1.endpoints.ho_so import thong_ke_su_dung

        hom_nay = date.today()
        hom_qua = hom_nay - timedelta(days=1)
        db = _DbThongKe(
            [(hom_nay, "mien_phi", 2), (hom_nay, "tra_phi", 1), (hom_qua, "mien_phi", 1)],
            [(hom_qua, 3)],
        )
        kq = thong_ke_su_dung(so_ngay=7, db=db, current_user=SimpleNamespace(id=1))
        self.assertEqual(len(kq.theo_ngay), 7)
        self.assertEqual(kq.theo_ngay[-1].ngay, hom_nay)
        self.assertEqual(kq.theo_ngay[-1].tim_truong, 3)
        self.assertEqual(kq.theo_ngay[-2].khao_sat, 3)
        self.assertEqual(kq.theo_ngay[0].tim_truong, 0)
        self.assertEqual((kq.tong_tim_truong, kq.tim_truong_mien_phi, kq.tim_truong_tra_phi), (4, 3, 1))
        self.assertEqual(kq.tong_khao_sat, 3)

    def test_chua_dung_thi_tra_du_ngay_gia_tri_0(self):
        from app.api.v1.endpoints.ho_so import thong_ke_su_dung

        kq = thong_ke_su_dung(so_ngay=30, db=_DbThongKe([], []), current_user=SimpleNamespace(id=1))
        self.assertEqual(len(kq.theo_ngay), 30)
        self.assertEqual(kq.tong_tim_truong + kq.tong_khao_sat, 0)
