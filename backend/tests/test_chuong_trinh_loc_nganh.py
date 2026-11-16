"""Danh sách chương trình: lọc theo ngành, đề án và trả kèm phương thức (trang Chương trình & phương thức)."""

import unittest

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.api.v1.endpoints.dats_chuong_trinh_dao_tao import list_chuong_trinh
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_truong import DmTruong


@compiles(BIGINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


class LocNganhTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in (DmTruong, DmNganhDaoTao, DatsTuyenSinh, DatsTruSo, DatsChuongTrinhDaoTao, DatsTrinhDoNganh, DatsPhuongThuc):
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add_all(
            [
                DmTruong(ma_truong="SPH", ten_truong="Sư phạm"),
                DmTruong(ma_truong="XDA", ten_truong="Xây dựng"),
                DmNganhDaoTao(id=1, ma_nhom_nganh="71401", ma_nganh="7140103", ten_nganh="Công nghệ giáo dục",
                              ten_tieng_anh="", trinh_do="ĐH"),
                DatsTuyenSinh(id=10, ma_truong="SPH", nam_tuyen_sinh=2026),
                DatsTuyenSinh(id=11, ma_truong="XDA", nam_tuyen_sinh=2026),
                # Gắn ngành chuẩn.
                DatsChuongTrinhDaoTao(id=1, de_an_id=10, ma_xet_tuyen="SP01", ten_chuong_trinh="CNGD", nganh_dao_tao_id=1),
                # Chưa gắn ngành, chỉ khai mã ngành ở trình độ ngành.
                DatsChuongTrinhDaoTao(id=2, de_an_id=11, ma_xet_tuyen="XD01", ten_chuong_trinh="CNGD XD"),
                DatsChuongTrinhDaoTao(id=3, de_an_id=11, ma_xet_tuyen="XD02", ten_chuong_trinh="Kỹ thuật xây dựng"),
                DatsTrinhDoNganh(de_an_chuong_trinh_id=2, ma_nganh_chuan="7140103"),
                DatsTrinhDoNganh(de_an_chuong_trinh_id=3, ma_nganh_chuan="7580201"),
                DatsPhuongThuc(de_an_chuong_trinh_id=2, ma_phuong_thuc_cua_bo="100", to_hop_mon_hoc=["A00", "D01"],
                               thu_tu_uu_tien=1),
                DatsPhuongThuc(de_an_chuong_trinh_id=2, ma_phuong_thuc_cua_bo="402", ma_phuong_thuc_cua_truong="TSA",
                               thu_tu_uu_tien=2),
            ]
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _list(self, **kw):
        args = dict(q=None, nam_tuyen_sinh=None, ma_truong=None, ma_nganh=None, de_an_id=None, kem_phuong_thuc=False,
                    page=1, page_size=50, db=self.db, _=None)
        args.update(kw)
        return list_chuong_trinh(**args)

    def test_loc_nganh_theo_nganh_gan_hoac_trinh_do_nganh(self):
        self.assertEqual(sorted(i.id for i in self._list(ma_nganh="7140103").items), [1, 2])
        self.assertEqual(self._list(ma_nganh="7140103").total, 2)
        # Đầu mã (nhóm ngành) cũng khớp.
        self.assertEqual(sorted(i.id for i in self._list(ma_nganh="71401").items), [1, 2])
        self.assertEqual([i.id for i in self._list(ma_nganh="7140103", ma_truong="XDA").items], [2])
        self.assertEqual(self._list(ma_nganh="9999").items, [])

    def test_loc_de_an_va_kem_phuong_thuc(self):
        kq = self._list(de_an_id=11, kem_phuong_thuc=True)
        theo_id = {i.id: i for i in kq.items}
        self.assertEqual(set(theo_id), {2, 3})
        self.assertEqual(
            [(p.ma_phuong_thuc_cua_bo, p.to_hop_mon_hoc) for p in theo_id[2].phuong_thuc], [("100", ["A00", "D01"]), ("402", None)]
        )
        self.assertEqual((theo_id[2].ma_nganh_chuan, theo_id[3].phuong_thuc), (["7140103"], []))
        # Không yêu cầu thì không trả kèm.
        self.assertIsNone(self._list(de_an_id=11).items[0].phuong_thuc)


if __name__ == "__main__":
    unittest.main()
