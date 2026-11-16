import unittest

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dm_truong import DmTruong
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucHeSoMon, XtCongThucThanhPhan
from app.models.xt_diem_chuan import XtDiemChuan
from app.models.xt_dieu_kien import XtDiemCong, XtDieuKien, XtNhomDieuKien
from app.models.xt_lich_su_import import XtLichSuImport
from app.models.xt_phuong_an import XtPhuongAn
from app.services.dats_import import _TABLES
from app.services.xet_tuyen_ghi import THU_NGHIEM, nhap_quy_tac
from app.services.xet_tuyen_import import XetTuyenImportError
from tests.test_xet_tuyen_import import DANH_MUC, _mau


@compiles(BIGINT, "sqlite")
@compiles(TINYINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    # SQLite chỉ tự tăng khóa chính kiểu INTEGER.
    return "INTEGER"


_BANG = [
    DmTruong,
    DmToHopMonHoc,
    DmToHopMonHocChiTiet,
    *(model for _ten, model, _kind in _TABLES),
    XtBangQuyDoi,
    XtBangQuyDoiChiTiet,
    XtCongThuc,
    XtCongThucHeSoMon,
    XtCongThucThanhPhan,
    XtPhuongAn,
    XtNhomDieuKien,
    XtDieuKien,
    XtDiemCong,
    DatsHocPhi,
    XtDiemChuan,
    XtLichSuImport,
]


class XetTuyenGhiTests(unittest.TestCase):
    """Bước 2.4: ghi quy tắc vào CSDL trong một transaction, thay toàn bộ quy tắc cũ của đề án."""

    def setUp(self):
        engine = create_engine("sqlite://")
        for model in _BANG:
            model.__table__.create(engine)
        self.db = Session(engine)
        self.db.add_all([DmTruong(ma_truong="BKA", ten_truong="Bách khoa"), DmTruong(ma_truong="NTH", ten_truong="FTU")])
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def _nhap(self, du_lieu, **kwargs):
        ket_qua = nhap_quy_tac(self.db, du_lieu, danh_muc=DANH_MUC, **kwargs)
        self.db.commit()
        return ket_qua

    def _dem(self, model, *dieu_kien) -> int:
        return self.db.scalar(select(func.count()).select_from(model).where(*dieu_kien))

    def test_nap_bka_vao_csdl_trong(self):
        ket_qua = self._nhap(_mau("mau_BKA_2026.json"), ten_file="mau_BKA_2026.json", ma_bam="abc")
        self.assertTrue(ket_qua.tao_de_an)
        de_an = self.db.get(DatsTuyenSinh, ket_qua.de_an_id)
        self.assertEqual((de_an.ma_truong, de_an.nam_tuyen_sinh, de_an.trang_thai_xet_tuyen), ("BKA", 2026, THU_NGHIEM))
        self.assertEqual(self._dem(XtCongThuc), 7)
        self.assertEqual(self._dem(XtPhuongAn), 501)
        self.assertEqual(self._dem(XtNhomDieuKien), 32)
        self.assertEqual(self._dem(DatsChuongTrinhDaoTao), 68)
        self.assertEqual(ket_qua.so_dong["xt_phuong_an"], 501)
        # Tổ hợp riêng K01 lưu thành BKA-K01, phương án trỏ đúng tổ hợp mới.
        k01 = self.db.scalar(select(DmToHopMonHoc).where(DmToHopMonHoc.ma_to_hop == "BKA-K01"))
        self.assertEqual(self._dem(DmToHopMonHocChiTiet, DmToHopMonHocChiTiet.to_hop_id == k01.id), 6)
        dung_k01 = sum("K01" in pa.get("to_hop", []) for ct in _mau("mau_BKA_2026.json")["chuong_trinh"] for pa in ct["phuong_an"])
        self.assertEqual(self._dem(XtPhuongAn, XtPhuongAn.to_hop_id == k01.id), dung_k01)
        lich_su = self.db.scalars(select(XtLichSuImport)).one()
        self.assertEqual((lich_su.ten_file, lich_su.ma_bam, lich_su.so_dong["xt_cong_thuc"]), ("mau_BKA_2026.json", "abc", 7))
        self.assertTrue(any(x["ma"] == "BKA_XTTN_12" for x in lich_su.quy_dinh_chua_mo_hinh_hoa))

    def test_nap_ftu_du_bang(self):
        self._nhap(_mau("mau_NTH_2026.json"))
        self.assertEqual(self._dem(XtCongThuc), 26)
        self.assertEqual(self._dem(XtPhuongAn), 770)
        self.assertEqual(self._dem(XtNhomDieuKien), 51)
        self.assertEqual(self._dem(XtDiemCong), 10)
        self.assertEqual(self._dem(XtBangQuyDoi), 3)
        self.assertEqual(self._dem(DatsHocPhi), 51)
        self.assertEqual(self._dem(DatsTruSo), 3)
        # Chương trình không khai cơ sở thuộc trụ sở chính.
        chinh = self.db.scalar(select(DatsTruSo.id).where(DatsTruSo.vai_tro == "chinh"))
        self.assertEqual(self._dem(DatsChuongTrinhDaoTao, DatsChuongTrinhDaoTao.co_so_id.is_(None)), 0)
        self.assertGreater(self._dem(DatsChuongTrinhDaoTao, DatsChuongTrinhDaoTao.co_so_id == chinh), 0)

    def test_nap_lai_thay_toan_bo_va_giu_lich_su(self):
        self._nhap(_mau("mau_BKA_2026.json"))
        self._nhap(_mau("mau_BKA_2026.json"))
        self.assertEqual(self._dem(XtCongThuc), 7)
        self.assertEqual(self._dem(XtPhuongAn), 501)
        self.assertEqual(self._dem(XtDieuKien), 89)
        self.assertEqual(self._dem(DatsChuongTrinhDaoTao), 68)
        self.assertEqual(self._dem(DmToHopMonHoc, DmToHopMonHoc.ma_to_hop == "BKA-K01"), 1)
        self.assertEqual(self._dem(DmToHopMonHocChiTiet), 6)
        self.assertEqual(self._dem(XtLichSuImport), 2)

    def test_khop_de_an_va_chuong_trinh_san_co(self):
        de_an = DatsTuyenSinh(ma_truong="BKA", nam_tuyen_sinh=2026, ten_de_an="Đề án đã nhập tay", trang_thai_xet_tuyen=2)
        self.db.add(de_an)
        self.db.flush()
        bf1 = DatsChuongTrinhDaoTao(
            de_an_id=de_an.id, ma_xet_tuyen="BF1", ten_chuong_trinh="Kỹ thuật Sinh học", nganh_dao_tao_id=99
        )
        cu = DatsChuongTrinhDaoTao(de_an_id=de_an.id, ma_xet_tuyen="CU1", ten_chuong_trinh="Chương trình đã dừng")
        self.db.add_all([bf1, cu])
        self.db.flush()
        pt = DatsPhuongThuc(de_an_chuong_trinh_id=bf1.id, ma_phuong_thuc_cua_bo="100", ma_phuong_thuc_cua_truong="THPT")
        self.db.add(pt)
        self.db.commit()

        ket_qua = self._nhap(_mau("mau_BKA_2026.json"))
        self.assertFalse(ket_qua.tao_de_an)
        self.assertEqual(ket_qua.de_an_id, de_an.id)
        self.db.refresh(de_an)
        # Không ghi đè mô tả; đang áp dụng thì giữ nguyên trạng thái.
        self.assertEqual((de_an.ten_de_an, de_an.trang_thai_xet_tuyen), ("Đề án đã nhập tay", 2))
        self.assertEqual(self._dem(DatsChuongTrinhDaoTao), 68 + 1)
        self.db.refresh(bf1)
        self.assertEqual((bf1.nganh_dao_tao_id, bf1.chi_tieu_tuyen_sinh), (99, 160))
        # Phương án của BF1 theo phương thức 100 nối với dòng mô tả phương thức sẵn có.
        self.assertGreater(self._dem(XtPhuongAn, XtPhuongAn.de_an_phuong_thuc_id == pt.id), 0)
        self.assertTrue(any("CU1" in x for x in ket_qua.canh_bao))

    def test_file_loi_khong_ghi_gi(self):
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["chuong_trinh"][0]["phuong_an"].append({"ma_cong_thuc": "KHONG_CO"})
        with self.assertRaises(XetTuyenImportError):
            nhap_quy_tac(self.db, du_lieu, danh_muc=DANH_MUC)
        self.db.rollback()
        for model in (DatsTuyenSinh, DatsChuongTrinhDaoTao, XtCongThuc, XtPhuongAn, XtLichSuImport, DmToHopMonHoc):
            with self.subTest(table=model.__tablename__):
                self.assertEqual(self._dem(model), 0)

    def test_diem_chuan_thay_theo_nam_trong_file(self):
        self.db.add(XtDiemChuan(ma_truong="BKA", nam_tuyen_sinh=2024, ma_xet_tuyen="BF1", diem_chuan=22, thang_diem=30))
        self.db.add(XtDiemChuan(ma_truong="BKA", nam_tuyen_sinh=2025, ma_xet_tuyen="BF1", diem_chuan=20, thang_diem=30))
        self.db.commit()
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["diem_chuan"] = [
            {"nam_tuyen_sinh": 2025, "ma_xet_tuyen": "BF1", "ma_phuong_thuc_cua_bo": "100", "diem_chuan": 23, "thang_diem": 30},
            {"nam_tuyen_sinh": 2025, "ma_xet_tuyen": "BF1", "ma_to_hop": "K01", "diem_chuan": 24, "thang_diem": 30},
        ]
        self._nhap(du_lieu)
        nam_2025 = self.db.scalars(select(XtDiemChuan).where(XtDiemChuan.nam_tuyen_sinh == 2025)).all()
        self.assertEqual(sorted(float(d.diem_chuan) for d in nam_2025), [23.0, 24.0])
        k01 = self.db.scalar(select(DmToHopMonHoc.id).where(DmToHopMonHoc.ma_to_hop == "BKA-K01"))
        self.assertIn(k01, {d.to_hop_id for d in nam_2025})
        # Năm không có trong file giữ nguyên.
        self.assertEqual(self._dem(XtDiemChuan, XtDiemChuan.nam_tuyen_sinh == 2024), 1)


if __name__ == "__main__":
    unittest.main()
