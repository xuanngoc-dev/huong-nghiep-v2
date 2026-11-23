import json
import unittest
from pathlib import Path

from sqlalchemy import select

import app.models as M
from app.services.dats_import import DatsImportError
from app.services.thu_thap_tuyen_sinh_import import import_approved_admission, validate_admission_payload
from tests.hoi_quy_xet_tuyen import DANH_MUC_MA, tao_csdl


MAU_XDA = (
    Path(__file__).resolve().parents[2] / "docs" / "de-an-tuyen-sinh" / "chuan_du_lieu" / "du_lieu_mau_da_sua.json"
)


class AnhXaPhuongThucTests(unittest.TestCase):
    def setUp(self):
        self.mau = json.loads(MAU_XDA.read_text(encoding="utf-8"))
        self.chuong_trinh = self.mau["dats_tuyen_sinh"]["dats_chuong_trinh_dao_tao"]
        self.quy_tac = self.mau["quy_tac_xet_tuyen"]

    def test_cms_chan_ma_phuong_thuc_bo_chua_xac_dinh(self):
        phuong_thuc = self.chuong_trinh[0]["dats_phuong_thuc"][0]
        cong_thuc = self.quy_tac["cong_thuc"][0]
        khoa_ma = "ma_phuong_thuc_cua_bo"
        for dong, duong_dan in (
            (phuong_thuc, "dats_phuong_thuc/0"),
            (cong_thuc, "quy_tac_xet_tuyen/cong_thuc/0"),
        ):
            ma_goc = dong.pop(khoa_ma)
            with self.subTest(duong_dan=duong_dan, thieu_khoa=True):
                with self.assertRaisesRegex(DatsImportError, f"{duong_dan}/{khoa_ma}: cần nhập dữ liệu"):
                    validate_admission_payload(self.mau, "XDA", 2026)
            for ma in (None, "", "   "):
                with self.subTest(duong_dan=duong_dan, ma=ma):
                    dong[khoa_ma] = ma
                    with self.assertRaisesRegex(DatsImportError, f"{duong_dan}/{khoa_ma}: cần nhập dữ liệu"):
                        validate_admission_payload(self.mau, "XDA", 2026)
            dong[khoa_ma] = ma_goc
        self.assertTrue(validate_admission_payload(self.mau, "XDA", 2026))

    def test_tsa_spt_chung_ma_bo_phai_xac_dinh_duoc_dong_phuong_thuc(self):
        pt = next(
            pt for ct in self.chuong_trinh for pt in ct["dats_phuong_thuc"]
            if pt.get("ma_phuong_thuc_cua_truong") == "402_SPT"
        )
        pt["cong_thuc_tinh_diem"] = None
        with self.assertRaisesRegex(DatsImportError, "cần đúng một phương thức đề án cho công thức HUCE_SPT_2026"):
            validate_admission_payload(self.mau, "XDA", 2026)

    def test_phuong_thuc_da_duyet_chua_co_quy_tac_van_luu_duoc(self):
        chuong_trinh = self.quy_tac["chuong_trinh"][0]
        pt = chuong_trinh["phuong_an"].pop(0)
        khoa = (chuong_trinh["ma_chuong_trinh"], pt["ma_cong_thuc"])
        assert khoa not in validate_admission_payload(self.mau, "XDA", 2026)

    def test_bi_danh_to_hop_cung_duoc_doi_chieu(self):
        pt = self.chuong_trinh[0]["dats_phuong_thuc"][0]
        pt["to_hop_ids"] = pt["to_hop_mon_hoc"]
        pt["to_hop_mon_hoc"] = None
        pt["dats_phuong_thuc_to_hop"] = []
        self.assertTrue(validate_admission_payload(self.mau, "XDA", 2026))
        pt["to_hop_ids"] = ["A00"]
        with self.assertRaisesRegex(DatsImportError, "mã tổ hợp không khớp"):
            validate_admission_payload(self.mau, "XDA", 2026)

    def test_mot_phuong_thuc_co_nhieu_cong_thuc_khi_tham_chieu_ro_rang(self):
        quy_tac_ct = self.quy_tac["chuong_trinh"][0]
        phuong_an = quy_tac_ct["phuong_an"][0]
        ma_goc, ma_moi = phuong_an["ma_cong_thuc"], "THPT_BO_SUNG"
        cong_thuc = next(ct for ct in self.quy_tac["cong_thuc"] if ct["ma_cong_thuc"] == ma_goc)
        self.quy_tac["cong_thuc"].append({**cong_thuc, "ma_cong_thuc": ma_moi})
        quy_tac_ct["phuong_an"].append({**phuong_an, "ma_cong_thuc": ma_moi, "ma_phuong_thuc_cua_truong": "THPT"})

        anh_xa = validate_admission_payload(self.mau, "XDA", 2026)

        ma_chuong_trinh = quy_tac_ct["ma_chuong_trinh"]
        self.assertEqual(anh_xa[ma_chuong_trinh, ma_goc], anh_xa[ma_chuong_trinh, ma_moi])

    def test_cung_ma_va_ten_o_hai_co_so_khong_ghi_nham_chuong_trinh(self):
        db, _ = tao_csdl("XDA")
        self.addCleanup(db.close)
        for model in (M.DmPhuongThucTuyenSinh, M.DmThanhTichHocTapNghienCuu):
            model.__table__.create(db.get_bind())
        dm = json.loads(DANH_MUC_MA.read_text(encoding="utf-8"))
        db.add_all(
            M.DmPhuongThucTuyenSinh(ma_phuong_thuc=x["ma"], ten_phuong_thuc=x["ten"])
            for x in dm["phuong_thuc_cua_bo"]
        )
        db.add_all(
            M.DmThanhTichHocTapNghienCuu(ma_thanh_tich=x["ma"], ten_thanh_tich=x["ten"]) for x in dm["thanh_tich"]
        )
        db.add_all(
            M.DmNganhDaoTao(ma_nhom_nganh=x["ma"][:5], ma_nganh=x["ma"], ten_nganh=x["ten"], ten_tieng_anh="", trinh_do="ĐH")
            for x in dm["nganh"]
        )
        db.commit()
        ct_mot, ct_hai = self.chuong_trinh[:2]
        quy_tac_mot, quy_tac_hai = self.quy_tac["chuong_trinh"][:2]
        ma = ct_mot["ma_xet_tuyen"]
        ma_cu = ct_hai["ma_xet_tuyen"]
        self.quy_tac["diem_chuan"] = [d for d in self.quy_tac["diem_chuan"] if d["ma_xet_tuyen"] != ma_cu]
        ct_mot["ten_chuong_trinh"] = "  Kiến  trúc "
        ct_hai.update(ma_xet_tuyen=ma, ten_chuong_trinh="Kiến trúc", co_so_id=2)
        quy_tac_mot["ten_chuong_trinh"] = "Kiến trúc"
        quy_tac_hai.update(ma_xet_tuyen=ma, ten_chuong_trinh="Kiến trúc", ma_co_so="NC")

        import_approved_admission(db, self.mau, "XDA", 2026, 1)
        cac_co_so = db.execute(
            select(M.DatsTruSo.ten_co_so, M.XtPhuongAn.de_an_chuong_trinh_id, M.DatsPhuongThuc.de_an_chuong_trinh_id)
            .select_from(M.XtPhuongAn)
            .join(M.DatsPhuongThuc, M.DatsPhuongThuc.id == M.XtPhuongAn.de_an_phuong_thuc_id)
            .join(M.DatsChuongTrinhDaoTao, M.DatsChuongTrinhDaoTao.id == M.XtPhuongAn.de_an_chuong_trinh_id)
            .join(M.DatsTruSo, M.DatsTruSo.id == M.DatsChuongTrinhDaoTao.co_so_id)
            .where(M.DatsChuongTrinhDaoTao.ma_xet_tuyen == ma)
            .distinct()
        ).all()
        self.assertEqual({co_so for co_so, _, _ in cac_co_so}, {cs["ten_co_so"] for cs in self.quy_tac["co_so"]})
        self.assertTrue(all(id_ct == id_ct_pt for _, id_ct, id_ct_pt in cac_co_so))


if __name__ == "__main__":
    unittest.main()
