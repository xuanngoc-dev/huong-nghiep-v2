"""Bước 4.4: script chuyển hồ sơ năng lực cũ sang hs_*."""

import unittest

from sqlalchemy import func, select

import app.models as M
from app.scripts.chuyen_ho_so_xet_tuyen import bao_cao, chuyen
from tests import test_hs_ho_so as hs_test


class ChuyenHoSoTests(unittest.TestCase):
    # Dùng lại CSDL SQLite của test hồ sơ xét tuyển (không kế thừa để các test đó không chạy lại ở đây).
    setUp = hs_test.HoSoXetTuyenTests.setUp
    tearDown = hs_test.HoSoXetTuyenTests.tearDown

    def _them(self, nguoi_dung_id: int, trinh_do: dict, co_hs: bool = False) -> None:
        self.db.add(M.NguoiDung(id=nguoi_dung_id, ho_ten=f"N{nguoi_dung_id}", email=f"n{nguoi_dung_id}@vd.vn", mat_khau="x"))
        self.db.add(M.NguoiDungThongTin(nguoi_dung_id=nguoi_dung_id, trinh_do_hoc_van=trinh_do))
        if co_hs:
            self.db.add(M.HsHoSo(nguoi_dung_id=nguoi_dung_id, ten_ho_so="Đã có"))
        self.db.commit()

    def _so_hs(self) -> int:
        return self.db.scalar(select(func.count()).select_from(M.HsHoSo))

    def test_chay_thu_roi_ghi_that(self):
        json_cu = {
            "diem_thi_thpt_quoc_gia": {"du_kien": {"TOAN": 8.5, "NN1": 7, "CN": 9}},
            "diem_trung_binh_hoc_ba": {"12": {"TOAN": 8, "GDDP": 9}},
            "hoc_luc_trung_binh": {"12": 8.2},
            "chung_chi_ngoai_ngu": [{"ma": "IELTS", "thanh_tich": "6.5"}, {"ma": "XYZ", "thanh_tich": "1"}],
        }
        self._them(10, json_cu)
        self._them(11, {"hoc_luc_trung_binh": {"10": 7}}, co_hs=True)

        thu = chuyen(self.db, ghi=False, nam=2026)
        self.assertEqual(self._so_hs(), 1)  # chạy thử không ghi gì
        theo_nguoi = {k.nguoi_dung_id: k for k in thu}
        self.assertEqual((theo_nguoi[10].trang_thai, theo_nguoi[11].trang_thai), ("chuyen", "bo_qua"))
        self.assertEqual(
            theo_nguoi[10].khong_chuyen, ["điểm thi môn CN", "học bạ lớp 12 môn GDDP", "chứng chỉ XYZ"]
        )
        self.assertIn("điểm thi môn CN", bao_cao(thu, ghi=False))

        chuyen(self.db, ghi=True, nam=2026)
        self.db.commit()
        self.assertEqual(self._so_hs(), 2)
        hs = self.db.scalars(select(M.HsHoSo).where(M.HsHoSo.nguoi_dung_id == 10)).one()
        mon = dict(self.db.execute(select(M.DmMonHoc.id, M.DmMonHoc.ma_mon_hoc)).all())
        diem = {
            (d.nguon_diem, mon[d.mon_hoc_id]): float(d.diem)
            for d in self.db.scalars(select(M.HsDiemMon).where(M.HsDiemMon.ho_so_id == hs.id))
        }
        self.assertEqual(diem, {("THI_THPT", "TOAN"): 8.5, ("THI_THPT", "ANH"): 7.0, ("HOC_BA", "TOAN"): 8.0})
        ket_qua_nam = self.db.scalars(select(M.HsKetQuaNamHoc).where(M.HsKetQuaNamHoc.ho_so_id == hs.id)).one()
        self.assertEqual((ket_qua_nam.lop, ket_qua_nam.hoc_luc), (12, 4))
        # JSON cũ giữ nguyên.
        profile = self.db.scalars(select(M.NguoiDungThongTin).where(M.NguoiDungThongTin.nguoi_dung_id == 10)).one()
        self.assertEqual(profile.trinh_do_hoc_van, json_cu)
        # Chạy lại không tạo thêm.
        chuyen(self.db, ghi=True, nam=2026)
        self.assertEqual(self._so_hs(), 2)


if __name__ == "__main__":
    unittest.main()
