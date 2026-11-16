import unittest
from decimal import Decimal

from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.xt_diem_chuan import (
    create_diem_chuan,
    create_diem_chuan_bulk,
    delete_diem_chuan,
    delete_diem_chuan_many,
    get_diem_chuan,
    list_diem_chuan,
    update_diem_chuan,
)
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong
from app.models.xt_diem_chuan import XtDiemChuan
from app.schemas.xt_diem_chuan import XtDiemChuanDeleteMany, XtDiemChuanWrite


@compiles(BIGINT, "sqlite")
def _bigint_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


def _dc(ma_xet_tuyen="IT1", phuong_thuc="100", **kwargs) -> XtDiemChuanWrite:
    data = {
        "ma_truong": "BKA",
        "nam_tuyen_sinh": 2025,
        "ma_xet_tuyen": ma_xet_tuyen,
        "ma_phuong_thuc_cua_bo": phuong_thuc,
        "diem_chuan": "28.5",
    }
    data.update(kwargs)
    return XtDiemChuanWrite(**data)


class XtDiemChuanTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (DmTruong, DmPhuongThucTuyenSinh, DmToHopMonHoc, XtDiemChuan):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add_all(
            [
                DmTruong(ma_truong="BKA", ten_truong="Bách khoa"),
                DmPhuongThucTuyenSinh(ma_phuong_thuc="100", ten_phuong_thuc="Điểm thi THPT"),
                DmPhuongThucTuyenSinh(ma_phuong_thuc="401", ten_phuong_thuc="Đánh giá tư duy"),
                DmToHopMonHoc(id=22, ma_to_hop="A00", ten_to_hop="Toán, Lý, Hóa", ds_mon_hoc=["TOAN", "LY", "HOA"]),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _ds(self, **kwargs):
        params = {"q": None, "ma_truong": None, "nam_tuyen_sinh": None, "ma_phuong_thuc_cua_bo": None}
        params.update(kwargs)
        return list_diem_chuan(
            params["q"], params["ma_truong"], params["nam_tuyen_sinh"], params["ma_phuong_thuc_cua_bo"], 1, 20, self.db
        )

    def _loi_400(self, ham, *args) -> str:
        with self.assertRaises(HTTPException) as caught:
            ham(*args, self.db)
        self.assertEqual(caught.exception.status_code, 400)
        return caught.exception.detail

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        trang = self._ds()
        self.assertEqual((trang.items, trang.total, trang.page, trang.page_size), ([], 0, 1, 20))

    def test_them_va_tra_ten_lien_ket(self):
        moi = create_diem_chuan(_dc(to_hop_id=22), self.db)
        self.assertEqual((moi.ten_truong, moi.ten_phuong_thuc, moi.ma_to_hop), ("Bách khoa", "Điểm thi THPT", "A00"))
        self.assertEqual((moi.diem_chuan, moi.thang_diem), (28.5, 30.0))
        self.assertEqual(get_diem_chuan(moi.id, self.db).ma_xet_tuyen, "IT1")
        self.assertEqual(self._ds(q="it1", nam_tuyen_sinh=2025).total, 1)
        self.assertEqual(self._ds(ma_phuong_thuc_cua_bo="401").total, 0)

    def test_id_khong_ton_tai_tra_400(self):
        for ham, args in ((get_diem_chuan, (99,)), (update_diem_chuan, (99, _dc())), (delete_diem_chuan, (99,))):
            with self.subTest(ham=ham.__name__):
                self.assertIn("id = 99", self._loi_400(ham, *args))
        self.assertEqual(delete_diem_chuan_many(XtDiemChuanDeleteMany(ids=[99]), self.db).deleted, 0)

    def test_tu_choi_trung_khoa_nhung_cho_khac_phuong_thuc(self):
        create_diem_chuan(_dc(), self.db)
        self.assertIn("Đã có điểm chuẩn", self._loi_400(create_diem_chuan, _dc()))
        # Khác phương thức hoặc chung mọi phương thức (NULL) là dòng khác.
        create_diem_chuan(_dc(phuong_thuc="401", diem_chuan="76", thang_diem="100"), self.db)
        create_diem_chuan(_dc(phuong_thuc=None), self.db)
        self.assertIn("Đã có điểm chuẩn", self._loi_400(create_diem_chuan, _dc(phuong_thuc=None)))

    def test_sua_giu_khoa_cua_chinh_no(self):
        moi = create_diem_chuan(_dc(), self.db)
        self.assertEqual(update_diem_chuan(moi.id, _dc(diem_chuan="27"), self.db).diem_chuan, 27.0)
        khac = create_diem_chuan(_dc("ME1"), self.db)
        self.assertIn("Đã có điểm chuẩn", self._loi_400(update_diem_chuan, khac.id, _dc()))

    def test_danh_muc_khong_ton_tai(self):
        self.assertIn("XYZ", self._loi_400(create_diem_chuan, _dc(ma_truong="XYZ")))
        self.assertIn("999", self._loi_400(create_diem_chuan, _dc(phuong_thuc="999")))
        self.assertIn("77", self._loi_400(create_diem_chuan, _dc(to_hop_id=77)))

    def test_nhap_nhieu_mot_dong_loi_thi_khong_luu(self):
        self.assertEqual(create_diem_chuan_bulk([_dc("IT1"), _dc("ME1")], self.db).created, 2)
        self.assertIn("trùng", self._loi_400(create_diem_chuan_bulk, [_dc("BF1"), _dc("BF1")]))
        self.assertIn("Đã có", self._loi_400(create_diem_chuan_bulk, [_dc("FL1"), _dc("IT1")]))
        self.assertEqual(self._ds().total, 2)

    def test_diem_chuan_khong_vuot_thang_diem(self):
        with self.assertRaises(ValidationError):
            _dc(diem_chuan="31", thang_diem="30")
        self.assertEqual(_dc(diem_chuan="76", thang_diem="100").thang_diem, Decimal("100"))


if __name__ == "__main__":
    unittest.main()
