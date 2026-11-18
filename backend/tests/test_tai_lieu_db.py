"""Chat đọc dữ liệu tuyển sinh từ CSDL (CHAT_NGUON_DU_LIEU=database): dựng đề án thành cấu trúc file JSON."""

import unittest
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import chat as chat_api
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_diem_cong import DatsDiemCong
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_hoc_phi import DatsHocPhi
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_quy_doi_diem_trung_tuyen import DatsQuyDoiDiemTrungTuyen
from app.models.dats_quy_doi_nguong_dau_vao import DatsQuyDoiNguongDauVao
from app.models.dats_tieu_chi_xet_tuyen import DatsTieuChiXetTuyen
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_bai_thi_danh_gia import DmBaiThiDanhGia
from app.models.dm_bang_cap_chung_chi import DmBangCapChungChi
from app.models.dm_mon_hoc import DmMonHoc
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong
from app.models.xt_bang_quy_doi import XtBangQuyDoi, XtBangQuyDoiChiTiet
from app.models.xt_cong_thuc import XtCongThuc, XtCongThucThanhPhan
from app.models.xt_diem_chuan import XtDiemChuan
from app.schemas.chat import KeHoachTraCuu
from app.services import tra_cuu_tuyen_sinh
from app.services.tai_lieu_db import tai_lieu_tu_csdl
from tests import hoi_quy_xet_tuyen  # noqa: F401  (khai báo BIGINT → INTEGER trên SQLite)

BANG = (
    DmTruong, DatsTuyenSinh, DatsTruSo, DmNganhDaoTao, DmPhuongThucTuyenSinh, DmToHopMonHoc, DatsChuongTrinhDaoTao,
    DatsPhuongThuc, DatsPhuongThucToHop, DatsDieuKienDuTuyen, DatsTieuChiXetTuyen, DatsDiemCong, DatsHocPhi, XtDiemChuan,
    DmBaiThiDanhGia, DmBangCapChungChi, DmMonHoc, XtBangQuyDoi, XtBangQuyDoiChiTiet, XtCongThuc, XtCongThucThanhPhan,
    DatsQuyDoiDiemTrungTuyen, DatsQuyDoiNguongDauVao,
)


class TaiLieuDbTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        for model in BANG:
            model.__table__.create(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        db = self.db = self.Session()
        db.add_all([
            DmTruong(id=1, ma_truong="BKA", ten_truong="Đại học Bách khoa Hà Nội", ten_viet_tat="HUST",
                     ten_tinh_thanh="Hà Nội"),
            DatsTuyenSinh(id=9, ma_truong="BKA", nam_tuyen_sinh=2027, trang_thai="da_cong_bo",
                          nguon_du_lieu_url="https://ts.hust.edu.vn/de-an"),
            # Đề án nháp không được đưa vào chat.
            DatsTuyenSinh(id=10, ma_truong="BKA", nam_tuyen_sinh=2028, trang_thai="nhap"),
            DatsTruSo(id=6, de_an_id=9, vai_tro="chinh", ten_co_so="Trụ sở Hà Nội", dia_chi="Số 1 Đại Cồ Việt"),
            DmNganhDaoTao(id=5, ma_nhom_nganh="74801", ma_nganh="7480101", ten_nganh="Khoa học máy tính",
                          ten_tieng_anh="Computer Science", trinh_do="dai_hoc"),
            DmPhuongThucTuyenSinh(id=1, ma_phuong_thuc="100", ten_phuong_thuc="Xét điểm thi THPT", loai_phuong_thuc="THPT"),
            DmToHopMonHoc(id=2, ma_to_hop="A00", ten_to_hop="Toán, Lý, Hóa", ds_mon_hoc=["TOAN", "LY", "HOA"]),
            DatsChuongTrinhDaoTao(id=20, de_an_id=9, nganh_dao_tao_id=5, ma_xet_tuyen="IT1", ten_chuong_trinh="Khoa học Máy tính",
                                  co_so_id=6, chi_tieu_tuyen_sinh=300),
            DatsPhuongThuc(id=30, de_an_chuong_trinh_id=20, ma_phuong_thuc_cua_bo="100", ma_phuong_thuc_cua_truong="THPT",
                           diem_san=Decimal("20.00"), thang_diem=Decimal("30.00"), cong_thuc_tinh_diem="M1 + M2 + M3",
                           dieu_kien_can={"tot_nghiep_thpt": True}),
            DatsPhuongThucToHop(de_an_phuong_thuc_id=30, to_hop_id=2, thu_tu_hien_thi=1),
            DatsDieuKienDuTuyen(id=40, de_an_id=9, de_an_chuong_trinh_id=20, de_an_phuong_thuc_id=30, ma_dieu_kien="IELTS",
                                ten_dieu_kien="IELTS tối thiểu", loai_dieu_kien="chung_chi_ngoai_ngu", toan_tu_so_sanh=">=",
                                gia_tri_dieu_kien={"diem": 5.5}, bat_buoc=True),
            DatsTieuChiXetTuyen(id=50, de_an_id=9, de_an_phuong_thuc_id=30, ma_tieu_chi="TOAN", ten_tieu_chi="Điểm Toán",
                                noi_dung_tieu_chi="Dùng khi bằng điểm"),
            DatsDiemCong(id=60, de_an_id=9, loai_diem_cong="diem_thuong", doi_tuong_duoc_cong="IELTS từ 6.5",
                         diem_cong=Decimal("1.000")),
            DatsHocPhi(id=70, de_an_id=9, de_an_chuong_trinh_id=20, nam_hoc="2027-2028", hoc_phi_tu=Decimal("32000000")),
            XtDiemChuan(id=80, ma_truong="BKA", nam_tuyen_sinh=2026, ma_xet_tuyen="IT1", ma_phuong_thuc_cua_bo="100",
                        diem_chuan=Decimal("28.50"), thang_diem=Decimal("30.00"), tieu_chi_phu="Toán >= 9"),
            XtDiemChuan(id=81, ma_truong="BKA", nam_tuyen_sinh=2027, ma_xet_tuyen="IT1", ma_phuong_thuc_cua_bo="100",
                        to_hop_id=2, diem_chuan=Decimal("28.75"), thang_diem=Decimal("30.00")),
            # Quy đổi: bảng HSA (thang 150) → thang 30 dùng cho phương thức 402; mốc ngưỡng THPT → học bạ.
            DmPhuongThucTuyenSinh(id=2, ma_phuong_thuc="200", ten_phuong_thuc="Xét học bạ"),
            DmBaiThiDanhGia(id=16, ma_bai_thi="HSA", ten_bai_thi="Đánh giá năng lực HSA"),
            XtBangQuyDoi(id=90, de_an_id=9, ma_bang="QD_HSA", ten_bang="HSA sang thang 30", thang_diem_dich=Decimal("30.00")),
            XtBangQuyDoiChiTiet(bang_quy_doi_id=90, bai_thi_id=16, diem_tu=Decimal("75"), diem_den=Decimal("75"),
                                diem_quy_doi=Decimal("20.480")),
            XtBangQuyDoiChiTiet(bang_quy_doi_id=90, bai_thi_id=16, diem_tu=Decimal("76"), diem_den=Decimal("80"),
                                diem_quy_doi=Decimal("20.500"), he_so_noi_suy=Decimal("0.25"), dat_nguong=True),
            XtCongThuc(id=95, de_an_id=9, ma_cong_thuc="PT_HSA", ten_cong_thuc="Xét HSA", ma_phuong_thuc_cua_bo="402",
                       kieu_tinh="THANH_PHAN"),
            XtCongThucThanhPhan(cong_thuc_id=95, vi_tri=1, loai_nguon="BAI_THI", bang_quy_doi_id=90),
            DatsQuyDoiNguongDauVao(id=97, de_an_id=9, de_an_chuong_trinh_id=20, nam_tuyen_sinh=2027, phuong_thuc_nguon_id=1,
                                   to_hop_nguon_id=2, phuong_thuc_dich_id=2, to_hop_dich_id=2,
                                   diem_moc_nguon=Decimal("20.000"), diem_moc_dich=Decimal("24.000"),
                                   cong_thuc_noi_suy="Nội suy tuyến tính giữa hai mốc liền kề"),
        ])
        db.commit()
        tra_cuu_tuyen_sinh._db_cache.update(docs=None, het_han=0.0)

    def tearDown(self):
        self.db.close()
        tra_cuu_tuyen_sinh._db_cache.update(docs=None, het_han=0.0)

    def test_dung_de_an_dung_cau_truc_file_json(self):
        ds = tai_lieu_tu_csdl(self.db)
        self.assertEqual([t.ten for t in ds], ["BKA_2027_de_an_9.json"])
        du_lieu = ds[0].du_lieu
        self.assertTrue(tra_cuu_tuyen_sinh.valid_admission_data(du_lieu))
        truong = du_lieu["truong"]
        self.assertEqual((truong["ma_truong"], truong["nam_tuyen_sinh"], truong["aliases"]), ("BKA", 2027, ["HUST"]))
        self.assertEqual(truong["url_nguon"], "https://ts.hust.edu.vn/de-an")
        nganh = du_lieu["danh_sach_nganh"][0]
        self.assertEqual((nganh["ma_nganh"], nganh["ten_nganh"], nganh["co_so_dao_tao"]), ("7480101", "Khoa học máy tính", "Trụ sở Hà Nội"))
        self.assertEqual(nganh["hoc_phi"], [{"nam_hoc": "2027-2028", "hoc_phi_tu": 32000000}])
        # Điểm chuẩn mọi năm có ghi năm; điểm cùng năm đề án gắn vào tổ hợp của phương thức.
        self.assertEqual([(d["nam"], d["diem_chuan"]) for d in nganh["diem_chuan_cac_nam"]], [(2027, 28.75), (2026, 28.5)])
        pt = nganh["phuong_thuc_tuyen_sinh"][0]
        self.assertEqual((pt["ma_phuong_thuc"], pt["loai_phuong_thuc"], pt["diem_san"], pt["thang_diem"]), ("100", "THPT", 20, 30))
        self.assertNotIn("diem_chuan", pt)
        self.assertEqual(pt["to_hop_mon"], [{"ma_to_hop": "A00", "ten_to_hop": "Toán, Lý, Hóa",
                                             "danh_sach_mon": ["TOAN", "LY", "HOA"], "diem_chuan": 28.75}])
        self.assertEqual([d["loai"] for d in pt["dieu_kien_phu"]], ["CHUNG_CHI_NGOAI_NGU", "DIEU_KIEN_CAN"])
        self.assertEqual(pt["tieu_chi_dong_diem"], ["Điểm Toán: Dùng khi bằng điểm"])
        # Điểm cộng của cả đề án áp dụng cho phương thức chưa có điểm cộng riêng.
        self.assertEqual(pt["diem_cong_uu_tien"][0]["diem_cong"], 1)

    def test_quy_doi_diem_cua_de_an(self):
        quy_doi = tai_lieu_tu_csdl(self.db)[0].du_lieu["truong"]["quy_doi_diem"]
        bang = quy_doi["bang_quy_doi"][0]
        self.assertEqual((bang["ma_bang"], bang["thang_diem_quy_doi"], bang["dung_cho_phuong_thuc"]), ("QD_HSA", 30, ["402"]))
        self.assertEqual(bang["muc"], [["HSA (Đánh giá năng lực HSA)", None, 75, 75, 20.48, 0, True],
                                       ["HSA (Đánh giá năng lực HSA)", None, 76, 80, 20.5, 0.25, True]])
        self.assertEqual(quy_doi["moc_quy_doi_nguong_dau_vao"], [{
            "nam": 2027, "chuong_trinh": "IT1", "tu_phuong_thuc": "100", "tu_to_hop": "A00", "sang_phuong_thuc": "200",
            "sang_to_hop": "A00", "diem_moc_nguon": 20, "diem_moc_dich": 24, "cach_quy_doi": "Nội suy tuyến tính giữa hai mốc liền kề",
        }])
        self.assertNotIn("moc_quy_doi_diem_trung_tuyen", quy_doi)

    def test_chat_doc_tu_csdl_khi_bat_che_do_database(self):
        plan = KeHoachTraCuu(ma_truong=["BKA"], nganh=["Khoa học máy tính"], thong_tin=["diem", "hoc_phi"], che_do="chi_tiet")
        with (
            patch.object(tra_cuu_tuyen_sinh.settings, "chat_nguon_du_lieu", "database"),
            patch("app.db.session.SessionLocal", self.Session),
        ):
            ket_qua = tra_cuu_tuyen_sinh.search("điểm chuẩn khoa học máy tính", [], None, plan)
            self.assertEqual(ket_qua.files, ["BKA_2027_de_an_9.json"])
            self.assertIn("28.75", ket_qua.context)
            self.assertIn("32000000", ket_qua.context)
            # Câu hỏi quy đổi (điều kiện) gửi kèm bảng quy đổi của trường cho AI.
            self.assertIn('"quy_doi_diem"', ket_qua.context)
            hoi_diem = tra_cuu_tuyen_sinh.search(
                "điểm chuẩn", [], None, KeHoachTraCuu(ma_truong=["BKA"], thong_tin=["diem"], che_do="tong_quan")
            )
            self.assertNotIn('"quy_doi_diem"', hoi_diem.context)
            nguon = ket_qua.sources[0]
            self.assertEqual((nguon.duong_dan, nguon.url_goc), ("/api/v1/chat/nguon/BKA_2027_de_an_9.json", "https://ts.hust.edu.vn/de-an"))
            # Link nguồn trả đúng dữ liệu đề án đã dựng.
            self.assertIn('"ma_xet_tuyen": "IT1"', chat_api.get_nguon("BKA_2027_de_an_9.json").body.decode())
            with self.assertRaises(HTTPException) as caught:
                chat_api.get_nguon("khong_co.json")
            self.assertEqual(caught.exception.status_code, 400)

    def test_loi_csdl_dung_lai_du_lieu_cu_hoac_bao_503(self):
        with patch.object(tra_cuu_tuyen_sinh.settings, "chat_nguon_du_lieu", "database"):
            with patch("app.db.session.SessionLocal", self.Session):
                docs = tra_cuu_tuyen_sinh.documents()
            tra_cuu_tuyen_sinh._db_cache["het_han"] = 0.0
            with patch("app.services.tai_lieu_db.tai_lieu_tu_csdl", side_effect=RuntimeError("mất kết nối")), \
                    patch("app.db.session.SessionLocal", self.Session):
                self.assertIs(tra_cuu_tuyen_sinh.documents(), docs)
                tra_cuu_tuyen_sinh._db_cache.update(docs=None, het_han=0.0)
                with self.assertRaises(HTTPException) as caught:
                    tra_cuu_tuyen_sinh.documents()
        self.assertEqual(caught.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
