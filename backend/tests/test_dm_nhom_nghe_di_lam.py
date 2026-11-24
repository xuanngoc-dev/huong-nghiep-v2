"""Danh mục nhóm nghề đi làm, nghề cụ thể, tiêu chí gợi ý và liên kết nhóm nghề - tiêu chí."""

import unittest

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints import (
    dm_nghe_cu_the_di_lam as nghe,
    dm_nhom_nghe_di_lam as nhom,
    dm_nhom_nghe_tieu_chi as lien_ket,
    dm_tieu_chi_goi_y as tieu_chi,
)
from app.db.base import Base
from app.schemas.dm_nhom_nghe_di_lam import (
    DmNgheCuTheDiLamWrite,
    DmNhomNgheDiLamDeleteMany,
    DmNhomNgheDiLamWrite,
    DmNhomNgheTieuChiDeleteMany,
    DmNhomNgheTieuChiUpdate,
    DmNhomNgheTieuChiWrite,
    DmTieuChiGoiYWrite,
)


@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


_BANG = [M.DmNhomNgheDiLam, M.DmNgheCuTheDiLam, M.DmTieuChiGoiY, M.DmNhomNgheTieuChi]


def _ds_nhom(db, **kw):
    params = {"q": None, "trang_thai": None, "loai_hinh_dau_vao": None, "nhom_muc_tieu": None, "page": 1,
              "page_size": 10}
    return nhom.list_nhom_nghe_di_lam(**{**params, **kw}, db=db)


def _ds_nghe(db, **kw):
    params = {"q": None, "nhom_nghe_di_lam_id": None, "co_bang_cap": None, "chinh_quy": None, "page": 1,
              "page_size": 10}
    return nghe.list_nghe_cu_the_di_lam(**{**params, **kw}, db=db)


def _ds_lien_ket(db, **kw):
    params = {"q": None, "nhom_nghe_di_lam_id": None, "tieu_chi_goi_y_id": None, "page": 1, "page_size": 10}
    return lien_ket.list_nhom_nghe_tieu_chi(**{**params, **kw}, db=db)


class TestDmNhomNgheDiLam(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        event.listen(engine, "connect", lambda conn, _: conn.execute("PRAGMA foreign_keys=ON"))
        Base.metadata.create_all(engine, tables=[m.__table__ for m in _BANG])
        self.db = Session(engine)

    def tearDown(self):
        self.db.close()

    def _tao_du_lieu(self):
        n = nhom.create_nhom_nghe_di_lam(
            DmNhomNgheDiLamWrite(ma_nhom=" lam_dep ", ten_nhom="Làm đẹp", mo_ta_dac_diem="Tóc, nail",
                                 loai_hinh_dau_vao="hoc_nghe_ngan_han", luong_khoi_diem_min=6,
                                 luong_khoi_diem_max=10),
            db=self.db, _=None,
        )
        t = tieu_chi.create_tieu_chi_goi_y(
            DmTieuChiGoiYWrite(ma_tieu_chi="kheo_tay", ten_tieu_chi="Khéo tay", nhom_tieu_chi="Năng lực"),
            db=self.db, _=None,
        )
        return n, t

    def test_danh_sach_rong_tra_dung_cau_truc(self):
        for page in (_ds_nhom(self.db), _ds_nghe(self.db), _ds_lien_ket(self.db),
                     tieu_chi.list_tieu_chi_goi_y(q=None, nhom_tieu_chi=None, page=1, page_size=10, db=self.db)):
            self.assertEqual((page.items, page.total, page.page), ([], 0, 1))

    def test_id_khong_ton_tai_tra_400(self):
        with self.assertRaises(HTTPException) as ctx:
            lien_ket.get_nhom_nghe_tieu_chi(5, 7, db=self.db, _=None)
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("nhom_nghe_di_lam_id = 5", ctx.exception.detail)
        with self.assertRaises(HTTPException) as ctx:
            nghe.create_nghe_cu_the_di_lam(
                DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=99, ten_nghe="Thợ"), db=self.db, _=None
            )
        self.assertEqual(ctx.exception.status_code, 400)
        self.assertIn("99", ctx.exception.detail)

    def test_chuan_hoa_ma_va_tu_choi_trung(self):
        n, t = self._tao_du_lieu()
        self.assertEqual((n.ma_nhom, t.ma_tieu_chi), ("LAM_DEP", "KHEO_TAY"))
        with self.assertRaises(HTTPException) as ctx:
            nhom.create_nhom_nghe_di_lam_bulk(
                [DmNhomNgheDiLamWrite(ma_nhom="LAM_DEP", ten_nhom="X", mo_ta_dac_diem="Y")], db=self.db, _=None
            )
        self.assertIn("LAM_DEP", ctx.exception.detail)

    def test_khoang_luong_nguoc_bi_tu_choi(self):
        with self.assertRaises(ValueError):
            DmNhomNgheDiLamWrite(ma_nhom="A", ten_nhom="A", mo_ta_dac_diem="A", luong_khoi_diem_min=10,
                                 luong_khoi_diem_max=5)

    def test_lien_ket_va_xoa_nhom_xoa_theo(self):
        n, t = self._tao_du_lieu()
        nghe.create_nghe_cu_the_di_lam(DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=n.id, ten_nghe="Thợ nail"),
                                       db=self.db, _=None)
        lk = lien_ket.create_nhom_nghe_tieu_chi(
            DmNhomNgheTieuChiWrite(nhom_nghe_di_lam_id=n.id, tieu_chi_goi_y_id=t.id, diem_phu_hop=5),
            db=self.db, _=None,
        )
        self.assertEqual((lk.ma_nhom, lk.ma_tieu_chi, lk.diem_phu_hop), ("LAM_DEP", "KHEO_TAY", 5))
        with self.assertRaises(HTTPException):
            lien_ket.create_nhom_nghe_tieu_chi(
                DmNhomNgheTieuChiWrite(nhom_nghe_di_lam_id=n.id, tieu_chi_goi_y_id=t.id, diem_phu_hop=3),
                db=self.db, _=None,
            )
        sua = lien_ket.update_nhom_nghe_tieu_chi(n.id, t.id, DmNhomNgheTieuChiUpdate(diem_phu_hop=4, ghi_chu=" "),
                                                 db=self.db, _=None)
        self.assertEqual((sua.diem_phu_hop, sua.ghi_chu), (4, None))
        self.assertEqual(_ds_nghe(self.db, q="nail").items[0].ten_nhom, "Làm đẹp")

        nhom.delete_nhom_nghe_di_lam_many(DmNhomNgheDiLamDeleteMany(ids=[n.id, 999]), db=self.db, _=None)
        self.assertEqual((_ds_nghe(self.db).total, _ds_lien_ket(self.db).total), (0, 0))

    def test_loc_theo_bang_cap_va_chinh_quy(self):
        n, _ = self._tao_du_lieu()
        for ten, bang_cap, chinh_quy in [
            ("Hộ lý", None, None),
            ("Lái xe tải", "Giấy phép lái xe hạng C", None),
            ("Bác sĩ", "Bằng bác sĩ", 1),
            ("Thợ phụ", "  ", 0),  # Chuỗi rỗng / 0 được lưu thành null: coi như không yêu cầu.
        ]:
            nghe.create_nghe_cu_the_di_lam(
                DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=n.id, ten_nghe=ten, yeu_cau_bang_cap=bang_cap,
                                      bat_buoc_dao_tao_chinh_quy=chinh_quy),
                db=self.db, _=None,
            )

        def ten(**kw):
            return sorted(item.ten_nghe for item in _ds_nghe(self.db, **kw).items)

        self.assertEqual(ten(co_bang_cap=1), ["Bác sĩ", "Lái xe tải"])
        self.assertEqual(ten(co_bang_cap=0), ["Hộ lý", "Thợ phụ"])
        self.assertEqual(ten(chinh_quy=1), ["Bác sĩ"])
        self.assertEqual(ten(chinh_quy=0), ["Hộ lý", "Lái xe tải", "Thợ phụ"])
        self.assertEqual(ten(co_bang_cap=1, chinh_quy=0), ["Lái xe tải"])

    def test_thong_tin_chi_tiet_nghe(self):
        n, _ = self._tao_du_lieu()
        tao = nghe.create_nghe_cu_the_di_lam(
            DmNgheCuTheDiLamWrite(
                nhom_nghe_di_lam_id=n.id, ten_nghe="Thợ hàn", ky_nang_mem="  ", don_vi_tien_te="vnd",
                nhom_holland="rc", muc_do_ap_luc="cao", luong_khoi_diem_min=8_000_000, luong_khoi_diem_max=10_000_000,
                tu_khoa_tim_kiem="hàn TIG; cơ khí",
            ),
            db=self.db, _=None,
        )
        self.assertEqual(
            (tao.ky_nang_mem, tao.don_vi_tien_te, tao.chu_ky_luong, tao.nhom_holland, tao.muc_do_ap_luc),
            (None, "VND", "thang", "RC", "cao"),
        )
        self.assertEqual(int(tao.luong_khoi_diem_max), 10_000_000)
        # Tìm theo từ khóa tìm kiếm của nghề.
        self.assertEqual([item.ten_nghe for item in _ds_nghe(self.db, q="TIG").items], ["Thợ hàn"])
        with self.assertRaises(ValueError):
            DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=n.id, ten_nghe="X", luong_cao_min=30, luong_cao_max=20)
        with self.assertRaises(ValueError):
            DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=n.id, ten_nghe="X", chu_ky_luong="tuan")

    def test_lo_trinh_phat_trien_theo_giai_doan(self):
        n, _ = self._tao_du_lieu()
        tao = nghe.create_nghe_cu_the_di_lam(
            DmNgheCuTheDiLamWrite(
                nhom_nghe_di_lam_id=n.id, ten_nghe="Thợ hàn",
                lo_trinh_phat_trien=[
                    {"giai_doan": " Thợ phụ ", "mo_ta_cong_viec": "Phụ việc, chuẩn bị phôi",
                     "luong_trung_binh_min": 7_000_000, "luong_trung_binh_max": 9_000_000, "ghi_chu": "  "},
                    {"giai_doan": "Thợ hàn 6G", "luong_trung_binh_min": 20_000_000},
                ],
            ),
            db=self.db, _=None,
        )
        buoc = [b.model_dump() for b in tao.lo_trinh_phat_trien]
        self.assertEqual(buoc[0], {"giai_doan": "Thợ phụ", "mo_ta_cong_viec": "Phụ việc, chuẩn bị phôi",
                                   "luong_trung_binh_min": 7_000_000, "luong_trung_binh_max": 9_000_000,
                                   "ghi_chu": None})
        self.assertEqual((buoc[1]["giai_doan"], buoc[1]["luong_trung_binh_max"]), ("Thợ hàn 6G", None))
        # Đọc lại từ danh sách (qua cột JSON) giữ nguyên thứ tự giai đoạn.
        doc_lai = _ds_nghe(self.db).items[0].lo_trinh_phat_trien
        self.assertEqual([b.giai_doan for b in doc_lai], ["Thợ phụ", "Thợ hàn 6G"])

    def test_lo_trinh_nhan_chuoi_cu_va_kiem_tra_luong(self):
        cu = DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=1, ten_nghe="X",
                                   lo_trinh_phat_trien="Thợ phụ → Thợ hàn bậc 3G -> Tổ trưởng.")
        self.assertEqual([b.giai_doan for b in cu.lo_trinh_phat_trien], ["Thợ phụ", "Thợ hàn bậc 3G", "Tổ trưởng"])
        for rong in ("", "  ", []):
            self.assertIsNone(
                DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=1, ten_nghe="X", lo_trinh_phat_trien=rong).lo_trinh_phat_trien
            )
        with self.assertRaises(ValueError):
            DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=1, ten_nghe="X", lo_trinh_phat_trien=[
                {"giai_doan": "A", "luong_trung_binh_min": 10, "luong_trung_binh_max": 5}])
        with self.assertRaises(ValueError):
            DmNgheCuTheDiLamWrite(nhom_nghe_di_lam_id=1, ten_nghe="X", lo_trinh_phat_trien=[{"giai_doan": "  "}])

    def test_xoa_nhieu_lien_ket_khong_ton_tai_tra_0(self):
        kq = lien_ket.delete_nhom_nghe_tieu_chi_many(
            DmNhomNgheTieuChiDeleteMany(items=[{"nhom_nghe_di_lam_id": 1, "tieu_chi_goi_y_id": 1}]),
            db=self.db, _=None,
        )
        self.assertEqual(kq.deleted, 0)


if __name__ == "__main__":
    unittest.main()
