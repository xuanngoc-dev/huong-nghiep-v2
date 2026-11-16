"""Bước 4.3: hồ sơ xét tuyển hs_*, API GET / PUT và ghi song song với hồ sơ năng lực cũ (JSON)."""

import unittest
from datetime import date

from fastapi import HTTPException
from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints.ho_so import _dong_bo_ho_so_xet_tuyen
from app.api.v1.endpoints.hs_ho_so import get_ho_so_xet_tuyen, put_ho_so_xet_tuyen
from app.schemas.hs_ho_so import HoSoXetTuyenWrite
from app.services.ho_so_xet_tuyen import dong_bo_tu_json


@compiles(BIGINT, "sqlite")
@compiles(SMALLINT, "sqlite")
@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


_BANG = [
    M.NguoiDung,
    M.NguoiDungThongTin,
    M.DmMonHoc,
    M.DmToHopMonHoc,
    M.DmBaiThiDanhGia,
    M.DmBangCapChungChi,
    M.DmThanhTichHocTapNghienCuu,
    M.DmTinhThanh,
    M.DmKhuVucUuTien,
    M.DmDoiTuongUuTien,
    M.HsHoSo,
    M.HsKetQuaNamHoc,
    M.HsDiemMon,
    M.HsDiemBaiThi,
    M.HsChungChi,
    M.HsThanhTich,
    M.HsTieuChiMongMuon,
]

HO_SO = {
    "ten_ho_so": "Hồ sơ chính",
    "nam_tot_nghiep": 2026,
    "he_chuyen": True,
    "ma_mon_chuyen": "toan",
    "ma_tinh": "01",
    "ma_khu_vuc_uu_tien": "KV2-NT",
    "ngan_sach_hoc_phi_nam": 60000000,
    "ket_qua_nam_hoc": [{"lop": 10, "diem_tb_chung": 8.9, "hoc_luc": 4, "ren_luyen": 4}],
    "diem_mon": [
        {"ma_mon": "TOAN", "nguon_diem": "THI_THPT", "diem": 9, "nam": 2026, "la_du_kien": True},
        {"ma_mon": "ANH", "nguon_diem": "THI_THPT", "diem": 8},
        {"ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 10, "diem": 9.2},
        {"ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 10, "hoc_ky": 1, "diem": 9.0},
    ],
    "diem_bai_thi": [{"ma_bai_thi": "HSA", "nam_thi": 2026, "diem": 112, "phan_tu_chon": "KHOA_HOC"}],
    "chung_chi": [{"ma_chung_chi": "IELTS", "diem": 7, "ngay_cap": "2025-12-01", "ngay_het_han": "2027-12-01"}],
    "thanh_tich": [{"ma_thanh_tich": "HSG-TINH", "ma_mon": "TOAN", "muc_giai": 2, "nam_dat_giai": 2026, "lop": 12}],
    "mong_muon": [{"loai": "TINH_THANH", "gia_tri": "01"}, {"loai": "NGANH", "gia_tri": "7480101"}],
}


class HoSoXetTuyenTests(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite://")
        for model in _BANG:
            model.__table__.create(engine)
        self.db = Session(engine)
        db = self.db
        self.user = M.NguoiDung(id=5, ho_ten="Học sinh", email="hs@vd.vn", mat_khau="x")
        db.add(self.user)
        db.add_all(
            M.DmMonHoc(ma_mon_hoc=ma, ten_mon_hoc=ma, nhom_mon=nhom)
            for ma, nhom in (("TOAN", "Tự nhiên"), ("LY", "Tự nhiên"), ("ANH", "Ngoại ngữ"), ("PHAP", "Ngoại ngữ"))
        )
        db.add(M.DmBaiThiDanhGia(ma_bai_thi="HSA", ten_bai_thi="HSA"))
        db.add(M.DmBangCapChungChi(ma_chung_chi="IELTS", ten_chung_chi="IELTS"))
        db.add(M.DmThanhTichHocTapNghienCuu(ma_thanh_tich="HSG-TINH", ten_thanh_tich="HSG tỉnh"))
        db.add(M.DmTinhThanh(ma_tinh="01", ten_tinh="Hà Nội", khu_vuc="Bắc"))
        db.add_all(M.DmKhuVucUuTien(ma_khu_vuc=ma, ten_khu_vuc=ma) for ma in ("KV1", "KV2-NT", "KV3"))
        db.commit()

    def tearDown(self):
        self.db.close()

    def _profile(self):
        return self.db.scalar(select(M.NguoiDungThongTin).where(M.NguoiDungThongTin.nguoi_dung_id == self.user.id))

    def test_luu_roi_doc_lai_y_nguyen(self):
        luu = put_ho_so_xet_tuyen(HoSoXetTuyenWrite(**HO_SO), self.db, self.user)
        doc = get_ho_so_xet_tuyen(self.db, self.user)
        self.assertFalse(doc.tu_du_lieu_cu)
        self.assertEqual(doc.id, luu.id)
        bo_qua = {"id", "la_ho_so_chinh", "tu_du_lieu_cu", "cap_nhat_luc"}
        self.assertEqual(doc.model_dump(exclude=bo_qua), HoSoXetTuyenWrite(**HO_SO).model_dump())
        self.assertEqual(doc.ma_mon_chuyen, "TOAN")
        self.assertEqual(doc.chung_chi[0].ngay_het_han, date(2027, 12, 1))

    def test_luu_mot_lan_hai_noi_khop_nhau(self):
        put_ho_so_xet_tuyen(HoSoXetTuyenWrite(**HO_SO), self.db, self.user)
        p = self._profile()
        hv = p.trinh_do_hoc_van
        self.assertEqual(hv["diem_thi_thpt_quoc_gia"]["du_kien"], {"TOAN": 9.0, "ANH": 8.0})
        # Điểm học kỳ chỉ ở hs_*; JSON cũ chỉ có điểm cả năm.
        self.assertEqual(hv["diem_trung_binh_hoc_ba"], {"10": {"TOAN": 9.2}})
        self.assertEqual((hv["hoc_luc_trung_binh"], hv["hanh_kiem"]), ({"10": 8.9}, {"10": "Tốt"}))
        self.assertEqual(hv["chung_chi_ngoai_ngu"], [{"ma": "IELTS", "thanh_tich": "7", "thoi_gian_cap": "2025-12-01"}])
        self.assertEqual(hv["thanh_tich_hoc_tap_nghien_cuu"], [{"ma": "HSG-TINH", "thanh_tich": "Giải Nhì"}])
        kv = self.db.scalar(select(M.DmKhuVucUuTien.id).where(M.DmKhuVucUuTien.ma_khu_vuc == "KV2-NT"))
        self.assertEqual(p.khu_vuc_uu_tien_id, kv)

    def test_chua_co_ho_so_dung_tu_du_lieu_cu(self):
        self.db.add(
            M.NguoiDungThongTin(
                nguoi_dung_id=self.user.id,
                trinh_do_hoc_van={
                    "diem_thi_thpt_quoc_gia": {"du_kien": {"TOAN": 8.5, "NN1": 7.5, "CN": 8}},
                    "hoc_luc_trung_binh": {"12": 7.0},
                    "chung_chi_ngoai_ngu": [{"ma": "IELTS", "thanh_tich": "6.5"}],
                },
            )
        )
        self.db.commit()
        hs = get_ho_so_xet_tuyen(self.db, self.user)
        self.assertTrue(hs.tu_du_lieu_cu)
        self.assertIsNone(hs.id)
        # NN1 → ANH; mã ngoài danh mục (CN) bị bỏ; học lực suy từ điểm trung bình.
        self.assertEqual({d.ma_mon: d.diem for d in hs.diem_mon}, {"TOAN": 8.5, "ANH": 7.5})
        self.assertEqual((hs.ket_qua_nam_hoc[0].lop, hs.ket_qua_nam_hoc[0].hoc_luc), (12, 3))
        self.assertEqual(self.db.scalar(select(func.count()).select_from(M.HsHoSo)), 0)
        # Lưu lại ngay được.
        put_ho_so_xet_tuyen(HoSoXetTuyenWrite(**hs.model_dump(include=set(HoSoXetTuyenWrite.model_fields))), self.db, self.user)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(M.HsHoSo)), 1)

    def test_luu_ho_so_nang_luc_cu_cap_nhat_hs_va_giu_thong_tin_rieng(self):
        put_ho_so_xet_tuyen(HoSoXetTuyenWrite(**HO_SO), self.db, self.user)
        p = self._profile()
        hv = dict(p.trinh_do_hoc_van)
        hv["diem_thi_thpt_quoc_gia"] = {"du_kien": {"TOAN": 9.5, "LY": 8.0}}
        hv["chung_chi_ngoai_ngu"] = [{"ma": "IELTS", "thanh_tich": "7.5"}]
        p.trinh_do_hoc_van = hv
        dong_bo_tu_json(self.db, p, nam_tuyen_sinh=2026)
        self.db.commit()
        hs = get_ho_so_xet_tuyen(self.db, self.user)
        thpt = {d.ma_mon: d.diem for d in hs.diem_mon if d.nguon_diem == "THI_THPT"}
        self.assertEqual(thpt, {"TOAN": 9.5, "LY": 8.0})
        # Thông tin chỉ hs_* có được giữ: hạn chứng chỉ, điểm học kỳ, môn đạt giải, nguyện vọng, ngân sách, môn chuyên.
        self.assertEqual((hs.chung_chi[0].diem, hs.chung_chi[0].ngay_het_han), (7.5, date(2027, 12, 1)))
        self.assertTrue(any(d.hoc_ky == 1 for d in hs.diem_mon))
        self.assertEqual(hs.thanh_tich[0].ma_mon, "TOAN")
        self.assertEqual(len(hs.mong_muon), 2)
        self.assertEqual((hs.ngan_sach_hoc_phi_nam, hs.ma_mon_chuyen), (60000000, "TOAN"))

    def test_ma_khong_co_trong_danh_muc_tra_400(self):
        du_lieu = dict(HO_SO, diem_bai_thi=[{"ma_bai_thi": "XYZ", "nam_thi": 2026, "diem": 1}])
        with self.assertRaises(HTTPException) as caught:
            put_ho_so_xet_tuyen(HoSoXetTuyenWrite(**du_lieu), self.db, self.user)
        self.assertEqual(caught.exception.status_code, 400)
        self.assertIn('bài thi "XYZ"', caught.exception.detail)
        self.assertEqual(self.db.scalar(select(func.count()).select_from(M.HsHoSo)), 0)

    def test_kiem_tra_du_lieu_dau_vao(self):
        for loi in (
            {"ket_qua_nam_hoc": [{"lop": 10}, {"lop": 10}]},
            {"diem_mon": [{"ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 0, "diem": 9}]},
            {"diem_mon": [{"ma_mon": "TOAN", "nguon_diem": "THI_THPT", "diem": 11}]},
            {"thanh_tich": [{"ma_thanh_tich": "HSG-TINH", "muc_giai": 5}]},
            {"chung_chi": [{"ma_chung_chi": "IELTS"}]},
        ):
            with self.subTest(loi=loi), self.assertRaises(ValueError):
                HoSoXetTuyenWrite(**loi)


class ChuaChayMigrationTests(unittest.TestCase):
    def test_csdl_chua_co_bang_hs_thi_luu_ho_so_cu_van_duoc(self):
        engine = create_engine("sqlite://")
        for model in (M.NguoiDung, M.NguoiDungThongTin):
            model.__table__.create(engine)
        with Session(engine) as db:
            db.add(M.NguoiDung(id=7, ho_ten="A", email="a@vd.vn", mat_khau="x"))
            profile = M.NguoiDungThongTin(nguoi_dung_id=7, trinh_do_hoc_van={"hoc_luc_trung_binh": {"12": 8}})
            db.add(profile)
            db.flush()
            with self.assertLogs("app.api.v1.endpoints.ho_so", level="ERROR"):
                _dong_bo_ho_so_xet_tuyen(db, profile)
            db.commit()  # giao dịch chính vẫn dùng được sau khi savepoint lỗi
            self.assertEqual(db.get(M.NguoiDungThongTin, profile.id).trinh_do_hoc_van, {"hoc_luc_trung_binh": {"12": 8}})


if __name__ == "__main__":
    unittest.main()
