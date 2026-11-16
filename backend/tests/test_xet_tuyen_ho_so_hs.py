"""Bước 4.6: bộ tính đọc hồ sơ từ hs_* (đủ thông tin hơn JSON cũ)."""

import unittest
from types import SimpleNamespace

from sqlalchemy import select

import app.models as M
from app.api.v1.endpoints.tn_tim_truong_phu_hop import _danh_gia_xet_tuyen
from app.schemas.hs_ho_so import HoSoXetTuyenWrite
from app.schemas.tn_lich_su_tim_truong_phu_hop import TimTruongPhuHopRequest
from app.services.ho_so_xet_tuyen import DanhMucMa, ghi_ho_so
from app.services.xet_tuyen.chuyen_ho_so import tu_ho_so_hs
from tests import test_xet_tuyen_danh_gia as danh_gia
from tests.test_xet_tuyen_bo_tinh import KET_QUA_JS, ho_so_tu_preset

# Hồ sơ mẫu A của trang test_xet_tuyen.html, ở dạng hồ sơ xét tuyển hs_*.
HO_SO_A = HoSoXetTuyenWrite(
    nam_tot_nghiep=2026,
    da_tot_nghiep=True,
    he_chuyen=True,
    ma_mon_chuyen="TOAN",
    ma_tinh="01",
    ma_khu_vuc_uu_tien="KV2-NT",
    ngan_sach_hoc_phi_nam=60000000,
    ket_qua_nam_hoc=[
        {"lop": 10, "diem_tb_chung": 8.9, "hoc_luc": 4, "ren_luyen": 4},
        {"lop": 11, "diem_tb_chung": 9.0, "hoc_luc": 4, "ren_luyen": 4},
        {"lop": 12, "diem_tb_chung": 9.2, "hoc_luc": 4, "ren_luyen": 4},
    ],
    diem_mon=[
        *(
            {"ma_mon": ma, "nguon_diem": "THI_THPT", "diem": d}
            for ma, d in (("TOAN", 9.0), ("LY", 8.5), ("HOA", 8.75), ("ANH", 8.0), ("VAN", 8.0))
        ),
        *(
            {"ma_mon": ma, "nguon_diem": "HOC_BA", "lop": lop, "diem": d}
            for ma, theo_lop in (
                ("TOAN", (9.2, 9.4, 9.6)),
                ("LY", (9.0, 9.1, 9.2)),
                ("HOA", (8.8, 9.0, 9.2)),
                ("VAN", (8.0, 8.2, 8.4)),
                ("ANH", (9.0, 9.2, 9.4)),
            )
            for lop, d in zip((10, 11, 12), theo_lop, strict=True)
        ),
    ],
    diem_bai_thi=[
        {"ma_bai_thi": "HSA", "nam_thi": 2026, "diem": 112, "phan_tu_chon": "KHOA_HOC"},
        {"ma_bai_thi": "TSA", "nam_thi": 2026, "diem": 72.5},
    ],
    chung_chi=[{"ma_chung_chi": "IELTS", "diem": 7.0, "ngay_het_han": "2027-12-01"}],
    thanh_tich=[{"ma_thanh_tich": "HSG-TINH", "muc_giai": 2}],
    mong_muon=[{"loai": "TINH_THANH", "gia_tri": "01"}],
)


class TuHoSoHsTests(unittest.TestCase):
    def test_ho_so_hs_tuong_duong_ho_so_mau_a(self):
        kq = tu_ho_so_hs(HO_SO_A, nam_tuyen_sinh=2026)
        self.assertEqual(kq.ho_so, ho_so_tu_preset(KET_QUA_JS["ho_so"]["A"]["ho_so"]))
        # Đủ dữ liệu nên không phải giả định gì.
        self.assertEqual(kq.gia_dinh, [])

    def test_gia_dinh_khi_thieu_du_lieu(self):
        kq = tu_ho_so_hs(
            HoSoXetTuyenWrite(
                ma_tinh="79",
                ket_qua_nam_hoc=[{"lop": 12, "diem_tb_chung": 7.0}],
                diem_mon=[
                    {"ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 12, "hoc_ky": 1, "diem": 7.5},
                    {"ma_mon": "TOAN", "nguon_diem": "HOC_BA", "lop": 12, "hoc_ky": 2, "diem": 9.0},
                ],
            ),
            nam_tuyen_sinh=2026,
        )
        hs = kq.ho_so
        self.assertEqual((hs.nam_tot_nghiep, hs.nam_hoc[12].hoc_luc, hs.mong_muon_tinh), (2026, 3, ["79"]))
        # Lớp chỉ có hai học kỳ: (HK1 + 2 x HK2) / 3.
        self.assertEqual(hs.hoc_ba["TOAN"][12], 8.5)
        self.assertEqual(len(kq.gia_dinh), 3)


class DungHoSoHsKhiTimTruongTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        danh_gia.DanhGiaTuCsdlTests.setUpClass.__func__(cls)
        bind = cls.db.get_bind()
        for model in (
            M.NguoiDung,
            M.NguoiDungThongTin,
            M.DmThanhTichHocTapNghienCuu,
            M.HsHoSo,
            M.HsKetQuaNamHoc,
            M.HsDiemMon,
            M.HsDiemBaiThi,
            M.HsChungChi,
            M.HsThanhTich,
            M.HsTieuChiMongMuon,
        ):
            model.__table__.create(bind)
        cls.db.add(M.DmThanhTichHocTapNghienCuu(ma_thanh_tich="HSG-TINH", ten_thanh_tich="HSG tỉnh"))
        cls.user = M.NguoiDung(id=21, ho_ten="HS", email="hs21@vd.vn", mat_khau="x")
        cls.db.add(cls.user)
        cls.db.flush()
        # Gắn một ngành cho mọi chương trình BKA để lượt tìm theo ngành có chương trình để tính.
        nganh = M.DmNganhDaoTao(ma_nhom_nganh="74802", ma_nganh="7480201", ten_nganh="CNTT", ten_tieng_anh="", trinh_do="ĐH")
        cls.db.add(nganh)
        cls.db.flush()
        bka = cls.db.scalars(select(M.DatsTuyenSinh.id).where(M.DatsTuyenSinh.ma_truong == "BKA")).one()
        for ct in cls.db.scalars(select(M.DatsChuongTrinhDaoTao).where(M.DatsChuongTrinhDaoTao.de_an_id == bka)):
            ct.nganh_dao_tao_id = nganh.id
        danh_gia._CACHE.clear()
        cls.hs = M.HsHoSo(nguoi_dung_id=21)
        cls.db.add(cls.hs)
        ghi_ho_so(cls.db, cls.hs, HO_SO_A, DanhMucMa.tu_csdl(cls.db))
        cls.db.commit()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_thanh_vien_co_hs_dung_ho_so_hs(self):
        payload = TimTruongPhuHopRequest(ma_yeu_cau="yeu-cau-hs-0001", ma_nganh="7480201", nam_tuyen_sinh=2026)
        item = SimpleNamespace(id=1, phien_ban_thuat_toan="loc-co-ban-v1", du_lieu_ket_qua={})
        _danh_gia_xet_tuyen(self.db, item, payload, self.user)
        self.db.commit()
        lan = self.db.get(M.XtLanDanhGia, item.du_lieu_ket_qua["xet_tuyen"]["lan_danh_gia_id"])
        self.assertEqual((lan.ho_so_id, lan.nguoi_dung_id, lan.gia_dinh), (self.hs.id, 21, []))
        self.assertEqual(lan.ho_so_xet_tuyen["mon_chuyen"], "TOAN")
        # Như hồ sơ A với BKA trong bộ test hồi quy (tests/du_lieu/hoi_quy_xet_tuyen/BKA_2026/ket_qua/A.json).
        self.assertEqual(lan.so_chuong_trinh, 68)

    def test_thanh_vien_chua_co_hs_dung_json_cu(self):
        nguoi = M.NguoiDung(id=22, ho_ten="HS2", email="hs22@vd.vn", mat_khau="x")
        self.db.add(nguoi)
        self.db.add(M.NguoiDungThongTin(nguoi_dung_id=22, trinh_do_hoc_van={"hoc_luc_trung_binh": {"12": 8}}))
        self.db.commit()
        payload = TimTruongPhuHopRequest(ma_yeu_cau="yeu-cau-hs-0002", ma_nganh="7480201", nam_tuyen_sinh=2026)
        item = SimpleNamespace(id=2, phien_ban_thuat_toan="loc-co-ban-v1", du_lieu_ket_qua={})
        _danh_gia_xet_tuyen(self.db, item, payload, nguoi)
        lan = self.db.scalars(select(M.XtLanDanhGia).where(M.XtLanDanhGia.nguoi_dung_id == 22)).one()
        self.assertIsNone(lan.ho_so_id)
        self.assertIn("Học lực suy ra từ điểm trung bình cả năm", lan.gia_dinh)


if __name__ == "__main__":
    unittest.main()
