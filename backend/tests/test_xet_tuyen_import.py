import copy
import json
import unittest
from decimal import Decimal
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_thanh_tich_hoc_tap_nghien_cuu import DmThanhTichHocTapNghienCuu
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_to_hop_mon_hoc_chi_tiet import DmToHopMonHocChiTiet
from app.models.dm_truong import DmTruong
from app.services.xet_tuyen_import import DanhMucXetTuyen, XetTuyenImportError, chuan_bi_nhap


@compiles(BIGINT, "sqlite")
@compiles(SMALLINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


# Bản sao của docs/de-an-tuyen-sinh/chuan_du_lieu để test không phụ thuộc thư mục tài liệu.
DU_LIEU = Path(__file__).resolve().parent / "du_lieu" / "xet_tuyen"
DANH_MUC = DanhMucXetTuyen.tu_file(DU_LIEU / "danh_muc_ma.json")


def _mau(ten: str) -> dict:
    return json.loads((DU_LIEU / ten).read_text(encoding="utf-8"))


def _loi(du_lieu) -> list[str]:
    with unittest.TestCase().assertRaises(XetTuyenImportError) as caught:
        chuan_bi_nhap(du_lieu, DANH_MUC)
    return caught.exception.loi


class NghiemThuFileMauTests(unittest.TestCase):
    """Tiêu chí nghiệm thu bước 2.3: hai file mẫu ra đúng số dòng như file SQL 04 của tài liệu."""

    def test_ftu(self):
        so_dong = chuan_bi_nhap(_mau("mau_NTH_2026.json"), DANH_MUC).so_dong()
        self.assertEqual(so_dong["xt_cong_thuc"], 26)
        self.assertEqual(so_dong["xt_phuong_an"], 770)
        self.assertEqual(so_dong["xt_nhom_dieu_kien"], 51)
        self.assertEqual(so_dong["xt_diem_cong"], 10)
        self.assertEqual(so_dong["dats_chuong_trinh_dao_tao"], 51)
        self.assertEqual(so_dong["dats_tru_so"], 3)

    def test_bka(self):
        so_dong = chuan_bi_nhap(_mau("mau_BKA_2026.json"), DANH_MUC).so_dong()
        self.assertEqual(so_dong["xt_cong_thuc"], 7)
        self.assertEqual(so_dong["xt_phuong_an"], 501)
        self.assertEqual(so_dong["xt_nhom_dieu_kien"], 32)
        self.assertEqual(so_dong["dm_to_hop_mon_hoc"], 1)


class ChuanBiNhapTests(unittest.TestCase):
    def test_to_hop_rieng_gan_tien_to_ma_truong(self):
        ke_hoach = chuan_bi_nhap(_mau("mau_BKA_2026.json"), DANH_MUC)
        to_hop = ke_hoach.to_hop_rieng[0]
        self.assertEqual((to_hop["ma_to_hop"], to_hop["ma_goc"]), ("BKA-K01", "K01"))
        # Toán, Văn, rồi 4 môn cùng vị trí 3.
        self.assertEqual([thu_tu for _mon, thu_tu in to_hop["chi_tiet"]], [1, 2, 3, 3, 3, 3])
        dung_k01 = {p["ma_to_hop"] for p in ke_hoach.phuong_an if p["ma_cong_thuc"] == "BKA_THPT_K01"}
        self.assertEqual(dung_k01, {"BKA-K01"})
        # Tổ hợp chuẩn vẫn giữ mã và có id danh mục.
        a00 = next(p for p in ke_hoach.phuong_an if p["ma_to_hop"] == "A00")
        self.assertEqual(a00["to_hop_id"], DANH_MUC.to_hop["A00"])

    def test_tien_to_qua_dai_bi_tu_choi(self):
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["to_hop_rieng"][0]["ma_to_hop"] = "K" * 18
        for ct in du_lieu["chuong_trinh"]:
            for pa in ct["phuong_an"]:
                pa["to_hop"] = ["K" * 18 if th == "K01" else th for th in pa.get("to_hop", [])]
        self.assertTrue(any("dài quá 20" in x for x in _loi(du_lieu)))

    def test_quy_dinh_chua_mo_hinh_hoa(self):
        ke_hoach = chuan_bi_nhap(_mau("mau_BKA_2026.json"), DANH_MUC)
        theo_loai = {(x["loai"], x["ma"]) for x in ke_hoach.quy_dinh_chua_mo_hinh_hoa}
        self.assertIn(("GHI_CHU_DE_AN", None), theo_loai)
        self.assertIn(("CONG_THUC_CHUA_DUNG", "BKA_THPT_TOAN_X2"), theo_loai)
        self.assertIn(("CONG_THUC_THU_CONG", "BKA_XTTN_12"), theo_loai)
        # Phương án THU_CONG vẫn được nạp (chuẩn hóa từng phần), không có tổ hợp.
        thu_cong = [p for p in ke_hoach.phuong_an if p["ma_cong_thuc"] == "BKA_XTTN_12"]
        self.assertTrue(thu_cong)
        self.assertTrue(all(p["ma_to_hop"] is None for p in thu_cong))

    def test_he_so_phan_so_giu_du_chu_so(self):
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["cong_thuc"][0]["he_so_nhan"] = 1.33333333
        ke_hoach = chuan_bi_nhap(du_lieu, DANH_MUC)
        self.assertEqual(ke_hoach.cong_thuc[0]["he_so_nhan"], Decimal("1.33333333"))

    def test_loi_cau_truc_neu_duong_dan(self):
        du_lieu = _mau("mau_BKA_2026.json")
        du_lieu["khoa_la"] = 1
        du_lieu["cong_thuc"][0]["nguon_diem_mon"] = 5
        loi = _loi(du_lieu)
        self.assertTrue(any(x.startswith("khoa_la:") for x in loi))
        self.assertTrue(any(x.startswith("cong_thuc/0/nguon_diem_mon") for x in loi))

    def test_gom_moi_loi_tham_chieu_va_danh_muc(self):
        du_lieu = _mau("mau_BKA_2026.json")
        ct = du_lieu["chuong_trinh"][0]
        ct["phuong_an"].append({"ma_cong_thuc": "KHONG_CO"})
        ct["phuong_an"][0]["to_hop"].append("Z99")
        ct["ma_nganh"] = "0000000"
        du_lieu["dieu_kien_chung"][0]["mot_trong"][0] = {"ma_chi_so": "DIEM_THI_THPT", "toan_tu": ">=", "gia_tri": 5}
        loi = _loi(du_lieu)
        self.assertTrue(any('công thức "KHONG_CO" không tồn tại' in x for x in loi))
        self.assertTrue(any('tổ hợp "Z99"' in x for x in loi))
        self.assertTrue(any('"0000000" không có trong danh mục ngành' in x for x in loi))
        self.assertTrue(any("DIEM_THI_THPT phải có khoa" in x for x in loi))

    def test_khong_sua_du_lieu_dau_vao(self):
        du_lieu = _mau("mau_BKA_2026.json")
        ban_dau = copy.deepcopy(du_lieu)
        chuan_bi_nhap(du_lieu, DANH_MUC)
        self.assertEqual(du_lieu, ban_dau)


class DanhMucTuCsdlTests(unittest.TestCase):
    def test_vi_tri_to_hop_lay_tu_bang_chi_tiet(self):
        engine = create_engine("sqlite://")
        for model in (
            DmMonHoc,
            DmToHopMonHoc,
            DmToHopMonHocChiTiet,
            DmTruong,
            DmTinhThanh,
            DmBaiThiDanhGia,
            DmBangCapChungChi,
            DmThanhTichHocTapNghienCuu,
            DmPhuongThucTuyenSinh,
            DmNganhDaoTao,
        ):
            model.__table__.create(engine)
        with Session(engine) as db:
            db.add_all(
                [
                    DmMonHoc(id=1, ma_mon_hoc="TOAN", ten_mon_hoc="Toán", nhom_mon="Tự nhiên"),
                    DmMonHoc(id=2, ma_mon_hoc="LY", ten_mon_hoc="Lý", nhom_mon="Tự nhiên"),
                    DmMonHoc(id=3, ma_mon_hoc="HOA", ten_mon_hoc="Hóa", nhom_mon="Tự nhiên"),
                    DmToHopMonHoc(id=9, ma_to_hop="X01", ten_to_hop="X01", ds_mon_hoc=["TOAN", "LY", "HOA"]),
                    DmToHopMonHocChiTiet(to_hop_id=9, mon_hoc_id=1, thu_tu_mon=1),
                    DmToHopMonHocChiTiet(to_hop_id=9, mon_hoc_id=2, thu_tu_mon=2),
                    DmToHopMonHocChiTiet(to_hop_id=9, mon_hoc_id=3, thu_tu_mon=2),
                ]
            )
            db.commit()
            dm = DanhMucXetTuyen.tu_csdl(db)
        self.assertEqual(dm.to_hop, {"X01": 9})
        # Lý và Hóa cùng thu_tu_mon 2 = chọn một trong hai.
        self.assertEqual(dm.vi_tri_to_hop["X01"], [["TOAN"], ["LY", "HOA"]])
        self.assertEqual(dm.mon["HOA"], 3)
        self.assertEqual(dm.nhom_mon["LY"], "Tự nhiên")


if __name__ == "__main__":
    unittest.main()
