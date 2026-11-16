import unittest

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dats_chuong_trinh_dao_tao import gan_nganh_co_so, list_gan_nganh_co_so
from app.api.v1.endpoints.dats_tru_so import create_tru_so, update_tru_so
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_truong import DmTruong
from app.schemas.dats_chuong_trinh_dao_tao import ChuongTrinhGanNganhWrite
from app.schemas.dats_tru_so import DatsTruSoWrite
from app.services.goi_y_nganh import NGUONG_AP_DUNG, Nganh, chuan_hoa_ten, goi_y_nganh, ten_cot_loi


@compiles(BIGINT, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


DS_NGANH = [
    Nganh(1, "7480201", "Công nghệ thông tin"),
    Nganh(2, "7310101", "Kinh tế"),
    Nganh(3, "7310106", "Kinh tế quốc tế"),
    Nganh(4, "7340101", "Quản trị kinh doanh"),
    Nganh(5, "7340120", "Kinh doanh quốc tế"),
    Nganh(6, "7480101", "Khoa học máy tính"),
]


class GoiYNganhTests(unittest.TestCase):
    def test_chuan_hoa_bo_dau_ngoac_va_tien_to(self):
        self.assertEqual(chuan_hoa_ten("Kỹ thuật Điều khiển & Tự động hóa"), "ky thuat dieu khien va tu dong hoa")
        self.assertEqual(ten_cot_loi("CT CLC Kinh doanh quốc tế (học bằng tiếng Anh)"), "kinh doanh quoc te")
        self.assertEqual(ten_cot_loi("CT TT i-Hons Kinh doanh quốc tế"), "kinh doanh quoc te")

    def test_ma_nganh_chuan_va_ma_xet_tuyen_duoc_tin_nhat(self):
        goi_y = goi_y_nganh("Tên bất kỳ", "NTH01", DS_NGANH, ma_nganh_chuan="7480201")
        self.assertEqual((goi_y[0].nganh_dao_tao_id, goi_y[0].diem), (1, 1.0))
        goi_y = goi_y_nganh("Quản trị – Tiếng Anh toàn phần", "73401011F", DS_NGANH)
        self.assertEqual(goi_y[0].nganh_dao_tao_id, 4)
        self.assertGreaterEqual(goi_y[0].diem, NGUONG_AP_DUNG)

    def test_ten_trung_hoac_bat_dau_bang_ten_nganh_dai(self):
        self.assertEqual(goi_y_nganh("CT TC Kinh doanh quốc tế", "NTH05", DS_NGANH)[0].diem, 1.0)
        goi_y = goi_y_nganh("Công nghệ Thông tin Việt - Pháp (tăng cường tiếng Pháp)", "IT-EP", DS_NGANH)
        self.assertEqual(goi_y[0].nganh_dao_tao_id, 1)
        self.assertGreaterEqual(goi_y[0].diem, NGUONG_AP_DUNG)

    def test_ten_nganh_ngan_o_dau_khong_tu_ap_dung(self):
        # "Kinh tế đối ngoại" không phải ngành "Kinh tế": vẫn gợi ý nhưng dưới ngưỡng để người duyệt chọn.
        goi_y = goi_y_nganh("CT TT Kinh tế đối ngoại", "NTH01", DS_NGANH)
        self.assertTrue(goi_y)
        self.assertLess(goi_y[0].diem, NGUONG_AP_DUNG)

    def test_khong_giong_thi_khong_goi_y(self):
        self.assertEqual(goi_y_nganh("Hóa học Mỹ phẩm", "CH3", DS_NGANH), [])


class GanNganhCoSoTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (
            DmTinhThanh,
            DmTruong,
            DmNganhDaoTao,
            DatsTuyenSinh,
            DatsTruSo,
            DatsChuongTrinhDaoTao,
            DatsTrinhDoNganh,
        ):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add_all(
            [
                DmTinhThanh(id=1, ma_tinh="01", ten_tinh="Hà Nội"),
                DmTruong(ma_truong="NTH", ten_truong="Ngoại thương"),
                DmNganhDaoTao(
                    id=5, ma_nhom_nganh="73401", ma_nganh="7340120", ten_nganh="Kinh doanh quốc tế",
                    ten_tieng_anh="", trinh_do="ĐH",
                ),
                DatsTuyenSinh(id=10, ma_truong="NTH", nam_tuyen_sinh=2026),
                DatsTuyenSinh(id=11, ma_truong="NTH", nam_tuyen_sinh=2025),
                DatsTruSo(id=20, de_an_id=10, ten_co_so="Trụ sở chính"),
                DatsTruSo(id=21, de_an_id=11, ten_co_so="Trụ sở chính 2025"),
                DatsChuongTrinhDaoTao(id=30, de_an_id=10, ma_xet_tuyen="NTH05", ten_chuong_trinh="CT TC Kinh doanh quốc tế"),
                DatsChuongTrinhDaoTao(id=31, de_an_id=10, ma_xet_tuyen="NTH09", ten_chuong_trinh="Ngành lạ",
                                      nganh_dao_tao_id=5, co_so_id=20),
                DatsChuongTrinhDaoTao(id=32, de_an_id=11, ma_xet_tuyen="NTH05", ten_chuong_trinh="Kinh doanh quốc tế"),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _ds(self, **kwargs):
        params = {"q": None, "chi_thieu": False, "page": 1, "page_size": 500}
        params.update(kwargs)
        return list_gan_nganh_co_so(10, params["q"], params["chi_thieu"], params["page"], params["page_size"], self.db, None)

    def _loi_400(self, ham, *args) -> str:
        with self.assertRaises(HTTPException) as caught:
            ham(*args, self.db, None)
        self.assertEqual(caught.exception.status_code, 400)
        return caught.exception.detail

    def test_danh_sach_co_dem_thieu_va_goi_y(self):
        trang = self._ds()
        self.assertEqual((trang.total, trang.so_thieu_nganh, trang.so_thieu_co_so), (2, 1, 1))
        dong = {item.id: item for item in trang.items}
        self.assertEqual(dong[30].goi_y[0].nganh_dao_tao_id, 5)
        self.assertEqual(dong[31].ten_nganh, "Kinh doanh quốc tế")
        self.assertEqual([item.id for item in self._ds(chi_thieu=True).items], [30])

    def test_de_an_khong_ton_tai_tra_400(self):
        detail = self._loi_400(list_gan_nganh_co_so, 999, None, False, 1, 500)
        self.assertIn("Đề án", detail)

    def test_luu_hang_loat_chi_doi_ba_cot(self):
        payload = ChuongTrinhGanNganhWrite(
            de_an_id=10,
            items=[{"id": 30, "nganh_dao_tao_id": 5, "co_so_id": 20, "ma_xet_tuyen_nam_truoc": " NTH05 "}],
        )
        self.assertEqual(gan_nganh_co_so(payload, self.db, None).updated, 1)
        item = self.db.get(DatsChuongTrinhDaoTao, 30)
        self.assertEqual((item.nganh_dao_tao_id, item.co_so_id, item.ma_xet_tuyen_nam_truoc), (5, 20, "NTH05"))
        self.assertEqual(item.ten_chuong_trinh, "CT TC Kinh doanh quốc tế")

    def test_tu_choi_chuong_trinh_hoac_co_so_cua_de_an_khac(self):
        detail = self._loi_400(gan_nganh_co_so, ChuongTrinhGanNganhWrite(de_an_id=10, items=[{"id": 32}]))
        self.assertIn("không thuộc đề án", detail)
        detail = self._loi_400(gan_nganh_co_so, ChuongTrinhGanNganhWrite(de_an_id=10, items=[{"id": 30, "co_so_id": 21}]))
        self.assertIn("Cơ sở không thuộc đề án", detail)
        detail = self._loi_400(gan_nganh_co_so, ChuongTrinhGanNganhWrite(de_an_id=10, items=[{"id": 99}]))
        self.assertIn("99", detail)

    def test_khong_cho_lap_chuong_trinh(self):
        with self.assertRaises(ValidationError):
            ChuongTrinhGanNganhWrite(de_an_id=10, items=[{"id": 30}, {"id": 30}])

    def test_co_so_luu_va_tra_tinh_thanh(self):
        moi = create_tru_so(DatsTruSoWrite(de_an_id=10, ten_co_so="Cơ sở 2", tinh_thanh_id=1), self.db, None)
        self.assertEqual((moi.tinh_thanh_id, moi.ten_tinh), (1, "Hà Nội"))
        detail = self._loi_400(update_tru_so, moi.id, DatsTruSoWrite(de_an_id=10, ten_co_so="Cơ sở 2", tinh_thanh_id=7))
        self.assertIn("Tỉnh/thành không tồn tại", detail)


if __name__ == "__main__":
    unittest.main()
