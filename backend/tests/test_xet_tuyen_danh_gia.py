"""Bước 3.5: nạp quy tắc từ CSDL (sau khi import 2 file mẫu) cho kết quả giống bản JavaScript, và lưu kết quả đánh giá."""

import json
import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from sqlalchemy import create_engine, func, select
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.api.v1.endpoints.tn_tim_truong_phu_hop import _danh_gia_xet_tuyen
from app.schemas.tn_lich_su_tim_truong_phu_hop import TimTruongPhuHopRequest
from app.services.dats_import import _TABLES
from app.services.xet_tuyen.bo_tinh import tinh_phuong_an, xep_hang
from app.services.xet_tuyen.chuyen_ho_so import KetQuaChuyenHoSo
from app.services.xet_tuyen.danh_gia import _CACHE, chay_danh_gia, tai_quy_tac
from app.services.xet_tuyen_ghi import nhap_quy_tac
from tests.test_xet_tuyen_bo_tinh import DATA, KET_QUA_JS, ho_so_tu_preset
from tests.test_xet_tuyen_import import DANH_MUC, DU_LIEU, _mau


@compiles(BIGINT, "sqlite")
@compiles(INTEGER, "sqlite")
@compiles(SMALLINT, "sqlite")
@compiles(TINYINT, "sqlite")
def _so_nguyen_sqlite(type_, compiler, **kw):
    return "INTEGER"


@compiles(ENUM, "sqlite")
def _enum_sqlite(type_, compiler, **kw):
    return "VARCHAR(50)"


_BANG = [
    M.DmTruong,
    M.DmMonHoc,
    M.DmToHopMonHoc,
    M.DmToHopMonHocChiTiet,
    M.DmBaiThiDanhGia,
    M.DmBangCapChungChi,
    M.DmTinhThanh,
    M.DmKhuVucUuTien,
    M.DmDoiTuongUuTien,
    M.DmMucDiemUuTien,
    M.DmNganhDaoTao,
    *(model for _ten, model, _kind in _TABLES),
    M.XtBangQuyDoi,
    M.XtBangQuyDoiChiTiet,
    M.XtCongThuc,
    M.XtCongThucHeSoMon,
    M.XtCongThucThanhPhan,
    M.XtPhuongAn,
    M.XtNhomDieuKien,
    M.XtDieuKien,
    M.XtDiemCong,
    M.DatsHocPhi,
    M.XtDiemChuan,
    M.XtLichSuImport,
    M.XtBoTieuChi,
    M.XtTieuChiPhuHop,
    M.XtMucPhuHop,
    M.XtLanDanhGia,
    M.XtKetQuaPhuongAn,
    M.XtKetQuaChuongTrinh,
]
HOM_NAY = date(2026, 7, 1)


def _nap_danh_muc(db: Session) -> None:
    """Danh mục với id trùng DANH_MUC (đọc từ danh_muc_ma.json) và điểm ưu tiên, tiêu chí của trang HTML."""
    dm = json.loads((DU_LIEU / "danh_muc_ma.json").read_text(encoding="utf-8"))
    db.add_all(M.DmTruong(ma_truong=ma, ten_truong=ma) for ma in ("BKA", "NTH"))
    db.add_all(
        M.DmMonHoc(id=i, ma_mon_hoc=x["ma"], ten_mon_hoc=x["ten"], nhom_mon=x.get("nhom"))
        for i, x in enumerate(dm["mon_hoc"], start=1)
    )
    for i, x in enumerate(dm["to_hop"], start=1):
        vi_tri = x.get("vi_tri") or []
        db.add(M.DmToHopMonHoc(id=i, ma_to_hop=x["ma"], ten_to_hop=x["ten"], ds_mon_hoc=[m for ds in vi_tri for m in ds]))
        for thu_tu, ds in enumerate(vi_tri, start=1):
            for ma in ds:
                db.add(M.DmToHopMonHocChiTiet(to_hop_id=i, mon_hoc_id=DANH_MUC.mon[ma], thu_tu_mon=thu_tu))
    db.add_all(M.DmBaiThiDanhGia(id=i, ma_bai_thi=x["ma"], ten_bai_thi=x["ten"]) for i, x in enumerate(dm["bai_thi"], 1))
    db.add_all(
        M.DmBangCapChungChi(id=i, ma_chung_chi=x["ma"], ten_chung_chi=x["ten"]) for i, x in enumerate(dm["chung_chi"], 1)
    )
    db.add_all(
        M.DmTinhThanh(id=i, ma_tinh=x["ma"], ten_tinh=x["ten"], khu_vuc=x.get("vung"))
        for i, x in enumerate(dm["tinh_thanh"], 1)
    )
    db.add_all(M.DmKhuVucUuTien(ma_khu_vuc=k["ma"], ten_khu_vuc=k["ten"], diem_cong=k["diem"]) for k in DATA["khuVuc"])
    db.add_all(M.DmDoiTuongUuTien(ma_doi_tuong=k["ma"], ten_doi_tuong=k["ten"], diem_cong=k["diem"]) for k in DATA["doiTuong"])
    bo = M.XtBoTieuChi(ma_bo="MAC_DINH_V1", ten_bo="Mặc định", mac_dinh=True)
    db.add(bo)
    db.flush()
    db.add_all(M.XtTieuChiPhuHop(bo_tieu_chi_id=bo.id, ma_tieu_chi=ma, trong_so=w) for ma, w in DATA["trongSo"].items())
    db.add_all(
        M.XtMucPhuHop(bo_tieu_chi_id=bo.id, loai_muc=m["loai"], gia_tri_tu=m["tu"], gia_tri_den=m["den"], diem=m["diem"], nhan=m["nhan"])
        for m in DATA["mucPhuHop"]
    )
    db.add_all(
        M.XtDiemChuan(
            ma_truong=d["truong"],
            nam_tuyen_sinh=d["nam"],
            ma_xet_tuyen=d["maXt"],
            ma_phuong_thuc_cua_bo=d["pt"],
            to_hop_id=DANH_MUC.to_hop.get(d["toHop"]) if d["toHop"] else None,
            diem_chuan=d["diem"],
            thang_diem=d["thang"],
        )
        for d in DATA["diemChuanDemo"]
    )


class DanhGiaTuCsdlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        engine = create_engine("sqlite://")
        for model in _BANG:
            model.__table__.create(engine)
        cls.db = Session(engine)
        _nap_danh_muc(cls.db)
        for ten in ("mau_BKA_2026.json", "mau_NTH_2026.json"):
            nhap_quy_tac(cls.db, _mau(ten), danh_muc=DANH_MUC)
        for de_an in cls.db.scalars(select(M.DatsTuyenSinh)):
            de_an.trang_thai_xet_tuyen = 2
        cls.db.commit()
        _CACHE.clear()
        cls.ho_so = ho_so_tu_preset(KET_QUA_JS["ho_so"]["A"]["ho_so"])

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _khoa_js(self) -> dict:
        """Kết quả JS của hồ sơ A theo khóa (trường, mã xét tuyển, tên chương trình, mã công thức, tổ hợp)."""
        ctr = {c["id"]: c for c in DATA["chuongTrinh"]}
        ct = {c["id"]: c["ma"] for c in DATA["congThuc"]}
        return {
            (ctr[p["ctr"]]["truong"], ctr[p["ctr"]]["maXt"], ctr[p["ctr"]]["ten"], ct[p["ct"]], p["toHop"]): p
            for p in KET_QUA_JS["ho_so"]["A"]["phuong_an"]
        }

    def test_quy_tac_nap_tu_csdl_cho_ket_qua_giong_ban_js(self):
        qtn = tai_quy_tac(self.db, 2026)
        kq = tinh_phuong_an(qtn.quy_tac, self.ho_so, 2026, HOM_NAY.isoformat(), qtn.diem_chuan)
        ctr = {c.id: c for c in qtn.quy_tac.chuong_trinh}
        ten = dict(self.db.execute(select(M.DatsChuongTrinhDaoTao.id, M.DatsChuongTrinhDaoTao.ten_chuong_trinh)).all())
        ma_ct = {c.id: c.ma for c in qtn.quy_tac.cong_thuc}
        thuc = {
            (ctr[p.chuong_trinh_id].ma_truong, ctr[p.chuong_trinh_id].ma_xet_tuyen, ten[p.chuong_trinh_id],
             ma_ct[p.cong_thuc_id], p.ma_to_hop.removeprefix("BKA-") if p.ma_to_hop else None): p
            for p in kq.phuong_an
        }
        js = self._khoa_js()
        self.assertEqual(set(thuc), set(js))
        for khoa, p in thuc.items():
            mong_doi = js[khoa]
            self.assertEqual(
                (p.diem_goc, p.diem_cong, p.diem_uu_tien, p.diem_xet, p.du_dieu_kien, p.ly_do, p.chenh_lech_30),
                (mong_doi["goc"], mong_doi["cong"], mong_doi["ut"], mong_doi["xet"], mong_doi["du"], mong_doi["lyDo"],
                 mong_doi["chenh"]),
                str(khoa),
            )
        self.assertEqual(len(xep_hang(qtn.quy_tac, self.ho_so, kq)), 119)

    def test_cache_dung_lai_va_lam_moi_khi_doi_trang_thai(self):
        lan_1 = tai_quy_tac(self.db, 2026)
        self.assertIs(tai_quy_tac(self.db, 2026), lan_1)
        de_an = self.db.scalars(select(M.DatsTuyenSinh).where(M.DatsTuyenSinh.ma_truong == "NTH")).one()
        de_an.trang_thai_xet_tuyen = 1
        self.db.flush()
        try:
            lan_2 = tai_quy_tac(self.db, 2026)
            self.assertIsNot(lan_2, lan_1)
            self.assertEqual({c.ma_truong for c in lan_2.quy_tac.chuong_trinh}, {"BKA"})
        finally:
            de_an.trang_thai_xet_tuyen = 2
            self.db.commit()

    def test_luu_ket_qua_danh_gia(self):
        kq = chay_danh_gia(
            self.db,
            KetQuaChuyenHoSo(ho_so=self.ho_so, gia_dinh=["giả định thử"]),
            nam=2026,
            ma_thiet_bi="thiet-bi-thu-01",
            hom_nay=HOM_NAY,
        )
        self.db.commit()
        self.assertEqual((kq.so_chuong_trinh, kq.so_truong), (119, 2))
        lan = self.db.get(M.XtLanDanhGia, kq.lan_danh_gia_id)
        self.assertEqual((lan.ma_thiet_bi, lan.nguoi_dung_id, lan.so_chuong_trinh), ("thiet-bi-thu-01", None, 119))
        self.assertEqual(lan.gia_dinh, ["giả định thử"])
        dong = self.db.scalars(
            select(M.XtKetQuaChuongTrinh).where(M.XtKetQuaChuongTrinh.lan_danh_gia_id == lan.id).order_by(M.XtKetQuaChuongTrinh.thu_hang)
        ).all()
        self.assertEqual([d.thu_hang for d in dong], list(range(1, 120)))
        # Dòng xếp hạng nào cũng trỏ tới phương án tốt nhất đã lưu của chính chương trình đó.
        for d in dong[:10]:
            pa = self.db.get(M.XtKetQuaPhuongAn, d.ket_qua_phuong_an_id)
            self.assertEqual(pa.de_an_chuong_trinh_id, d.de_an_chuong_trinh_id)
        self.assertGreater(
            self.db.scalar(select(func.count()).select_from(M.XtKetQuaPhuongAn).where(M.XtKetQuaPhuongAn.lan_danh_gia_id == lan.id)),
            119,
        )

    def test_loc_theo_nganh(self):
        bf1 = self.db.scalars(select(M.DatsChuongTrinhDaoTao).where(M.DatsChuongTrinhDaoTao.ma_xet_tuyen == "BF1")).one()
        nganh = M.DmNganhDaoTao(ma_nhom_nganh="74202", ma_nganh="7420202", ten_nganh="Kỹ thuật sinh học", ten_tieng_anh="", trinh_do="ĐH")
        self.db.add(nganh)
        self.db.flush()
        tai_quy_tac(self.db, 2026)  # cache đã có trước khi gắn ngành
        bf1.nganh_dao_tao_id = nganh.id
        self.db.commit()
        # Không xóa cache: gắn ngành phải tự làm mới cache quy tắc.
        kq = chay_danh_gia(
            self.db, KetQuaChuyenHoSo(ho_so=self.ho_so), nam=2026, ma_nganh="7420202", ma_thiet_bi="thiet-bi-thu-02", hom_nay=HOM_NAY
        )
        self.db.commit()
        self.assertEqual((kq.so_chuong_trinh, kq.so_truong), (1, 1))

    def test_nam_chua_co_de_an_dang_ap_dung(self):
        self.assertIsNone(chay_danh_gia(self.db, KetQuaChuyenHoSo(ho_so=self.ho_so), nam=2030, ma_thiet_bi="thiet-bi-thu-03"))


class NoiVaoTimTruongTests(unittest.TestCase):
    """_danh_gia_xet_tuyen trong luồng POST /tim-truong-phu-hop."""

    @classmethod
    def setUpClass(cls):
        DanhGiaTuCsdlTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def _luot(self, nam=2026):
        payload = TimTruongPhuHopRequest(
            ma_yeu_cau=f"yeu-cau-{nam}-{id(self)}",
            ma_nganh="7480201",
            nam_tuyen_sinh=nam,
            ma_thiet_bi="thiet-bi-khach-01",
            du_lieu_nang_luc={"diem_thi_thu": {"A00": 27, "A01": 26}},
        )
        # Bảng tn_lich_su_tim_truong_phu_hop dùng cú pháp mặc định riêng của MySQL nên không tạo được trên SQLite;
        # _danh_gia_xet_tuyen chỉ đọc id và gán hai thuộc tính của lượt tìm.
        self.__class__._so_luot = getattr(self.__class__, "_so_luot", 0) + 1
        item = SimpleNamespace(id=self._so_luot, phien_ban_thuat_toan="loc-co-ban-v1", du_lieu_ket_qua={"truong": []})
        return item, payload

    def test_khach_co_ket_qua_xet_tuyen(self):
        item, payload = self._luot()
        _danh_gia_xet_tuyen(self.db, item, payload, None)
        self.db.commit()
        self.assertEqual(item.phien_ban_thuat_toan, "xt-v1")
        xt = item.du_lieu_ket_qua["xet_tuyen"]
        lan = self.db.get(M.XtLanDanhGia, xt["lan_danh_gia_id"])
        self.assertEqual((lan.lich_su_tim_truong_id, lan.ma_thiet_bi), (item.id, "thiet-bi-khach-01"))
        self.assertIn("Điểm từng môn ước tính từ tổng điểm thi thử theo khối", lan.gia_dinh)
        self.assertEqual(item.du_lieu_ket_qua["truong"], [])

    def test_nam_khong_co_de_an_ap_dung_giu_nguyen(self):
        item, payload = self._luot(nam=2030)
        _danh_gia_xet_tuyen(self.db, item, payload, None)
        self.assertEqual((item.phien_ban_thuat_toan, item.du_lieu_ket_qua), ("loc-co-ban-v1", {"truong": []}))

    def test_bo_tinh_loi_khong_lam_hong_luot_tim(self):
        item, payload = self._luot()
        with patch("app.api.v1.endpoints.tn_tim_truong_phu_hop.chay_danh_gia", side_effect=RuntimeError("lỗi thử")):
            with self.assertLogs("app.api.v1.endpoints.tn_tim_truong_phu_hop", level="ERROR"):
                _danh_gia_xet_tuyen(self.db, item, payload, None)
        self.assertEqual(item.phien_ban_thuat_toan, "loc-co-ban-v1")
        self.db.commit()  # transaction chính vẫn dùng được sau khi savepoint lỗi


if __name__ == "__main__":
    unittest.main()
