"""Migration 20261210_0083: cột giới thiệu nhóm nghề, yêu cầu bằng cấp / chính quy của nghề và dữ liệu mẫu."""

import importlib.util
import unittest
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.ext.compiler import compiles

_THU_MUC = Path(__file__).resolve().parents[1] / "alembic/versions"


@compiles(TINYINT, "sqlite")
def _tinyint_sqlite(type_, compiler, **kw):
    return "INTEGER"


_COT_NHOM_0069 = (
    "id", "ma_nhom", "ten_nhom", "mo_ta_dac_diem", "loai_hinh_dau_vao", "thoi_gian_dao_tao_text",
    "thoi_gian_dao_tao_thang_min", "thoi_gian_dao_tao_thang_max", "dieu_kien_dau_vao", "muc_luong_text",
    "luong_khoi_diem_min", "luong_khoi_diem_max", "luong_kinh_nghiem_max", "danh_gia_trien_vong",
    "lo_trinh_phat_trien", "nhom_muc_tieu", "ma_holland",
)


def _tao_bang_truoc_0083(conn, goc) -> None:
    """Bảng như sau migration 0069 (chưa có cột của 0083) kèm dữ liệu mẫu của 0069.

    Không chạy thẳng 0069 vì nó dùng ON UPDATE CURRENT_TIMESTAMP riêng của MySQL.
    """
    meta = sa.MetaData()
    nhom = sa.Table(
        "dm_nhom_nghe_di_lam", meta,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ma_nhom", sa.String(50), unique=True, nullable=False),
        sa.Column("ten_nhom", sa.String(255), nullable=False),
        sa.Column("mo_ta_dac_diem", sa.Text, nullable=False),
        *[sa.Column(ten, sa.Text) for ten in _COT_NHOM_0069[4:]],
        sa.Column("trang_thai", sa.Integer, nullable=False, server_default="1"),
    )
    nghe = sa.Table(
        "dm_nghe_cu_the_di_lam", meta,
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("nhom_nghe_di_lam_id", sa.Integer, nullable=False),
        sa.Column("ten_nghe", sa.String(255), nullable=False),
        sa.Column("mo_ta_ngan", sa.Text),
        sa.Column("yeu_cau_them", sa.String(500)),
    )
    tieu_chi = sa.Table(
        "dm_tieu_chi_goi_y", meta,
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ma_tieu_chi", sa.String(50)), sa.Column("ten_tieu_chi", sa.String(255)),
        sa.Column("nhom_tieu_chi", sa.String(100)),
    )
    lien_ket = sa.Table(
        "dm_nhom_nghe_tieu_chi", meta,
        sa.Column("nhom_nghe_di_lam_id", sa.Integer, primary_key=True),
        sa.Column("tieu_chi_goi_y_id", sa.Integer, primary_key=True),
        sa.Column("diem_phu_hop", sa.Integer), sa.Column("ghi_chu", sa.String(500)),
    )
    meta.create_all(conn)
    conn.execute(nhom.insert(), [dict(zip(_COT_NHOM_0069, dong, strict=True)) for dong in goc.NHOM_NGHE])
    conn.execute(nghe.insert(), [
        dict(zip(("nhom_nghe_di_lam_id", "ten_nghe", "mo_ta_ngan", "yeu_cau_them"), dong, strict=True))
        for dong in goc.NGHE_CU_THE
    ])
    conn.execute(tieu_chi.insert(), [
        dict(zip(("id", "ma_tieu_chi", "ten_tieu_chi", "nhom_tieu_chi"), dong, strict=True)) for dong in goc.TIEU_CHI
    ])
    conn.execute(lien_ket.insert(), [
        dict(zip(("nhom_nghe_di_lam_id", "tieu_chi_goi_y_id", "diem_phu_hop", "ghi_chu"), dong, strict=True))
        for dong in goc.NHOM_NGHE_TIEU_CHI
    ])


def _nap(ten_file: str):
    spec = importlib.util.spec_from_file_location(ten_file, _THU_MUC / ten_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MigrationNhomNgheGioiThieuTests(unittest.TestCase):
    def setUp(self):
        self.goc = _nap("20261126_0069_dm_nhom_nghe_di_lam.py")
        self.mod = _nap("20261210_0083_nhom_nghe_gioi_thieu_bang_cap.py")
        self.engine = sa.create_engine("sqlite://")

    def _dem(self, conn, bang):
        return conn.scalar(sa.text(f"SELECT COUNT(*) FROM {bang}"))

    def test_upgrade_hai_lan_roi_downgrade(self):
        with self.engine.begin() as conn, Operations.context(MigrationContext.configure(conn)):
            _tao_bang_truoc_0083(conn, self.goc)
            nghe_goc = self._dem(conn, "dm_nghe_cu_the_di_lam")
            tieu_chi_goc = self._dem(conn, "dm_nhom_nghe_tieu_chi")
            # Quản trị đã tự sửa một mục giới thiệu: migration không được ghi đè.
            self.mod.upgrade()
            conn.execute(sa.text(
                "UPDATE dm_nhom_nghe_di_lam SET ket_luan = 'Quản trị đã sửa' WHERE ma_nhom = 'LAM_DEP'"
            ))
            self.mod.upgrade()

            so_nhom = self._dem(conn, "dm_nhom_nghe_di_lam")
            self.assertEqual(so_nhom, 8 + len(self.mod.NHOM_MOI))
            tong_nghe = sum(len(ds) for ds in self.mod.NGHE.values())
            self.assertEqual(self._dem(conn, "dm_nghe_cu_the_di_lam"), tong_nghe)
            self.assertGreater(self._dem(conn, "dm_nhom_nghe_tieu_chi"), tieu_chi_goc)
            # Mọi nhóm đều có đủ 6 mục giới thiệu.
            thieu = conn.scalar(sa.text(
                "SELECT COUNT(*) FROM dm_nhom_nghe_di_lam WHERE "
                + " OR ".join(f"{cot} IS NULL" for cot in self.mod.COT_GIOI_THIEU)
            ))
            self.assertEqual(thieu, 0)
            self.assertEqual(conn.scalar(sa.text(
                "SELECT ket_luan FROM dm_nhom_nghe_di_lam WHERE ma_nhom = 'LAM_DEP'"
            )), "Quản trị đã sửa")
            # Nghề cũ được điền bằng cấp; nghề cần chính quy được đánh dấu.
            self.assertEqual(conn.scalar(sa.text(
                "SELECT yeu_cau_bang_cap FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Lái xe tải'"
            )), "Giấy phép lái xe hạng C trở lên")
            self.assertEqual(conn.scalar(sa.text(
                "SELECT bat_buoc_dao_tao_chinh_quy FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Bác sĩ'"
            )), 1)
            self.assertIsNone(conn.scalar(sa.text(
                "SELECT bat_buoc_dao_tao_chinh_quy FROM dm_nghe_cu_the_di_lam WHERE ten_nghe = 'Hộ lý bệnh viện'"
            )))

            self.mod.downgrade()
            self.assertEqual(self._dem(conn, "dm_nhom_nghe_di_lam"), 8)
            self.assertEqual(self._dem(conn, "dm_nghe_cu_the_di_lam"), nghe_goc)
            self.assertEqual(self._dem(conn, "dm_nhom_nghe_tieu_chi"), tieu_chi_goc)
            cot_nghe = {c["name"] for c in sa.inspect(conn).get_columns("dm_nghe_cu_the_di_lam")}
            self.assertFalse({"yeu_cau_bang_cap", "bat_buoc_dao_tao_chinh_quy"} & cot_nghe)

    def test_du_lieu_mau_hop_le(self):
        ma_nhom = {n["ma_nhom"] for n in self.mod.NHOM_MOI} | {
            "CONG_NHAN_SAN_XUAT", "BAN_HANG_DICH_VU", "GIAO_HANG_VAN_TAI", "DIEN_CO_KHI", "BEP_NHA_HANG", "LAM_DEP",
            "KY_NANG_SO", "KINH_DOANH_ONLINE",
        }
        self.assertEqual(set(self.mod.GIOI_THIEU), ma_nhom)
        self.assertEqual(set(self.mod.NGHE), ma_nhom)
        for ma, ds in self.mod.NGHE.items():
            ten = [n[0] for n in ds]
            self.assertEqual(len(ten), len(set(ten)), f"Trùng tên nghề trong {ma}")
            for _, _, _, bang_cap, chinh_quy in ds:
                self.assertIn(chinh_quy, (None, 1))
                if chinh_quy:
                    self.assertTrue(bang_cap, "Nghề bắt buộc chính quy phải ghi bằng cấp")
                self.assertTrue(bang_cap is None or len(bang_cap) <= 255)
        for nhom in self.mod.NHOM_MOI:
            self.assertLessEqual(len(nhom["danh_gia_trien_vong"]), 255)
            self.assertLessEqual(len(nhom["muc_luong_text"]), 100)
            self.assertLessEqual(len(nhom["thoi_gian_dao_tao_text"]), 100)
            self.assertLessEqual(nhom["luong_khoi_diem_min"], nhom["luong_khoi_diem_max"])


if __name__ == "__main__":
    unittest.main()
