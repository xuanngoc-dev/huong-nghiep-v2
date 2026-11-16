"""Bộ test hồi quy nhiều trường (bước 3.8 KE_HOACH_TRIEN_KHAI.md): phần dùng chung cho test và script cập nhật.

Mỗi trường một thư mục `tests/du_lieu/hoi_quy_xet_tuyen/<MA_TRUONG>_<NAM>/` (xem README.md trong thư mục đó):
`de_an.json` (file chuẩn, kèm điểm chuẩn mốc), `ho_so/<ten>.json`, `ket_qua/<ten>.json`.
`chay_truong(thu_muc)` import đề án vào SQLite bằng bộ import thật, chuyển sang "đang áp dụng", nạp quy tắc từ CSDL
như khi chạy thật rồi tính cho từng hồ sơ; trả kết quả cùng dạng với file ket_qua để so sánh.

Cập nhật kết quả mong đợi của một trường (chỉ sau khi đã đối chiếu tay các số):
    cd backend && .venv/bin/python -m tests.hoi_quy_xet_tuyen <MA_TRUONG>_<NAM> --ghi
"""

import importlib.util
import json
import sys
from dataclasses import fields
from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.dialects.mysql import BIGINT, ENUM, INTEGER, SMALLINT, TINYINT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session

import app.models as M
from app.services.dats_import import _TABLES
from app.services.xet_tuyen.bo_tinh import tinh_phuong_an, xep_hang
from app.services.xet_tuyen.danh_gia import _CACHE, tai_quy_tac
from app.services.xet_tuyen.mo_hinh import (
    BaiThiTinh,
    ChungChiTinh,
    HoSoXetTuyen,
    KetQuaNamHocTinh,
    ThanhTichTinh,
)
from app.services.xet_tuyen_ghi import nhap_quy_tac
from app.services.xet_tuyen_import import DanhMucXetTuyen

THU_MUC = Path(__file__).resolve().parent / "du_lieu" / "hoi_quy_xet_tuyen"
DANH_MUC_MA = Path(__file__).resolve().parent / "du_lieu" / "xet_tuyen" / "danh_muc_ma.json"
# Ngày cố định để chứng chỉ còn hạn / hết hạn không đổi theo ngày chạy test.
HOM_NAY = date(2026, 7, 1)
# Điểm ưu tiên khu vực, đối tượng theo Thông tư 06/2026 (Phụ lục II).
KHU_VUC = {"KV1": 0.75, "KV2-NT": 0.5, "KV2": 0.25, "KV3": 0}
DOI_TUONG = {"01": 2, "02": 2, "03": 2, "04": 1, "05": 1, "06": 1}

_TRUONG_PHUONG_AN = (
    "diem_goc",
    "diem_cong",
    "diem_uu_tien",
    "diem_xet",
    "du_dieu_kien",
    "ly_do",
    "chenh_lech_30",
)


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
]


def _migration_0058():
    path = Path(__file__).resolve().parents[1] / "alembic" / "versions" / "20261117_0058_xt_quy_tac_xet_tuyen.py"
    spec = importlib.util.spec_from_file_location("migration_0058_hoi_quy", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tao_csdl(ma_truong: str) -> tuple[Session, DanhMucXetTuyen]:
    """CSDL SQLite có danh mục (id theo danh_muc_ma.json) và bộ tiêu chí mặc định như migration 0058."""
    engine = create_engine("sqlite://")
    for model in _BANG:
        model.__table__.create(engine)
    db = Session(engine)
    dm = json.loads(DANH_MUC_MA.read_text(encoding="utf-8"))
    danh_muc = DanhMucXetTuyen.tu_file(DANH_MUC_MA)
    db.add_all(M.DmTruong(ma_truong=x["ma"], ten_truong=x["ten"]) for x in dm["truong"])
    db.add_all(
        M.DmMonHoc(id=i, ma_mon_hoc=x["ma"], ten_mon_hoc=x["ten"], nhom_mon=x.get("nhom"))
        for i, x in enumerate(dm["mon_hoc"], start=1)
    )
    for i, x in enumerate(dm["to_hop"], start=1):
        vi_tri = x.get("vi_tri") or []
        db.add(M.DmToHopMonHoc(id=i, ma_to_hop=x["ma"], ten_to_hop=x["ten"], ds_mon_hoc=[m for ds in vi_tri for m in ds]))
        for thu_tu, ds in enumerate(vi_tri, start=1):
            for ma in ds:
                db.add(M.DmToHopMonHocChiTiet(to_hop_id=i, mon_hoc_id=danh_muc.mon[ma], thu_tu_mon=thu_tu))
    db.add_all(M.DmBaiThiDanhGia(id=i, ma_bai_thi=x["ma"], ten_bai_thi=x["ten"]) for i, x in enumerate(dm["bai_thi"], 1))
    db.add_all(
        M.DmBangCapChungChi(id=i, ma_chung_chi=x["ma"], ten_chung_chi=x["ten"]) for i, x in enumerate(dm["chung_chi"], 1)
    )
    db.add_all(
        M.DmTinhThanh(id=i, ma_tinh=x["ma"], ten_tinh=x["ten"], khu_vuc=x.get("vung"))
        for i, x in enumerate(dm["tinh_thanh"], 1)
    )
    db.add_all(M.DmKhuVucUuTien(ma_khu_vuc=ma, ten_khu_vuc=ma, diem_cong=d) for ma, d in KHU_VUC.items())
    db.add_all(M.DmDoiTuongUuTien(ma_doi_tuong=ma, ten_doi_tuong=ma, diem_cong=d) for ma, d in DOI_TUONG.items())
    mig = _migration_0058()
    bo = M.XtBoTieuChi(ma_bo=mig.BO_TIEU_CHI[0], ten_bo=mig.BO_TIEU_CHI[1], mac_dinh=True)
    db.add(bo)
    db.flush()
    db.add_all(M.XtTieuChiPhuHop(bo_tieu_chi_id=bo.id, ma_tieu_chi=ma, trong_so=w) for ma, w, _mo_ta in mig.TIEU_CHI)
    db.add_all(
        M.XtMucPhuHop(bo_tieu_chi_id=bo.id, loai_muc=loai, gia_tri_tu=tu, gia_tri_den=den, diem=diem, nhan=nhan)
        for loai, tu, den, diem, nhan in mig.MUC_PHU_HOP
    )
    db.commit()
    return db, danh_muc


def ho_so_tu_dict(d: dict) -> HoSoXetTuyen:
    """Hồ sơ mẫu dạng JSON (tên trường như HoSoXetTuyen) → HoSoXetTuyen."""
    ten = {f.name for f in fields(HoSoXetTuyen)}
    lap = {k: v for k, v in d.items() if k in ten}
    lap["nam_hoc"] = {int(lop): KetQuaNamHocTinh(**v) for lop, v in (d.get("nam_hoc") or {}).items()}
    lap["hoc_ba"] = {mon: {int(lop): v for lop, v in theo.items()} for mon, theo in (d.get("hoc_ba") or {}).items()}
    lap["bai_thi"] = [BaiThiTinh(**b) for b in d.get("bai_thi") or []]
    lap["chung_chi"] = [ChungChiTinh(**c) for c in d.get("chung_chi") or []]
    lap["thanh_tich"] = [ThanhTichTinh(**t) for t in d.get("thanh_tich") or []]
    return HoSoXetTuyen(**lap)


def _khoa(ma_xet_tuyen, ten, ma_cong_thuc, ma_to_hop) -> tuple:
    return (ma_xet_tuyen or "", ten, ma_cong_thuc, ma_to_hop or "")


def chay_truong(thu_muc: Path) -> dict[str, dict]:
    """Kết quả của mọi hồ sơ trong thư mục một trường, cùng dạng file ket_qua/<ten>.json."""
    de_an = json.loads((thu_muc / "de_an.json").read_text(encoding="utf-8"))
    ma_truong, nam = de_an["ma_truong"], de_an["nam_tuyen_sinh"]
    db, danh_muc = tao_csdl(ma_truong)
    try:
        # truong.json (không bắt buộc): thông tin dm_truong cần cho tiêu chí vị trí, ví dụ {"ma_tinh_thanh": "01"}.
        file_truong = thu_muc / "truong.json"
        if file_truong.exists():
            truong = db.scalars(select(M.DmTruong).where(M.DmTruong.ma_truong == ma_truong)).one()
            for cot, gia_tri in json.loads(file_truong.read_text(encoding="utf-8")).items():
                setattr(truong, cot, gia_tri)
        nhap_quy_tac(db, de_an, danh_muc=danh_muc)
        for d in db.scalars(select(M.DatsTuyenSinh)):
            d.trang_thai_xet_tuyen = 2
        db.commit()
        _CACHE.clear()
        qtn = tai_quy_tac(db, nam)
        _CACHE.clear()
        ten_ct = dict(db.execute(select(M.DatsChuongTrinhDaoTao.id, M.DatsChuongTrinhDaoTao.ten_chuong_trinh)).all())
        ctr = {c.id: c for c in qtn.quy_tac.chuong_trinh}
        ma_cong_thuc = {c.id: c.ma for c in qtn.quy_tac.cong_thuc}
        tien_to = f"{ma_truong}-"

        def ma_to_hop(ma):
            # Tổ hợp riêng lưu có tiền tố mã trường; kết quả mong đợi ghi mã như trong file đề án.
            return ma.removeprefix(tien_to) if ma else None

        ket_qua = {}
        for file_ho_so in sorted((thu_muc / "ho_so").glob("*.json")):
            hs = ho_so_tu_dict(json.loads(file_ho_so.read_text(encoding="utf-8")))
            kq = tinh_phuong_an(qtn.quy_tac, hs, nam, HOM_NAY.isoformat(), qtn.diem_chuan)
            dong = xep_hang(qtn.quy_tac, hs, kq)
            phuong_an = []
            for p in kq.phuong_an:
                c = ctr[p.chuong_trinh_id]
                phuong_an.append(
                    {
                        "ma_xet_tuyen": c.ma_xet_tuyen,
                        "ten_chuong_trinh": ten_ct[p.chuong_trinh_id],
                        "ma_cong_thuc": ma_cong_thuc[p.cong_thuc_id],
                        "ma_to_hop": ma_to_hop(p.ma_to_hop),
                        **{k: getattr(p, k) for k in _TRUONG_PHUONG_AN},
                    }
                )
            phuong_an.sort(key=lambda x: _khoa(x["ma_xet_tuyen"], x["ten_chuong_trinh"], x["ma_cong_thuc"], x["ma_to_hop"]))
            ket_qua[file_ho_so.stem] = {
                "so_phuong_an": len(phuong_an),
                "so_chuong_trinh": len(dong),
                "phuong_an": phuong_an,
                "xep_hang": [
                    {
                        "ma_xet_tuyen": ctr[d.chuong_trinh_id].ma_xet_tuyen,
                        "ten_chuong_trinh": ten_ct[d.chuong_trinh_id],
                        "ma_cong_thuc": ma_cong_thuc[d.phuong_an.cong_thuc_id],
                        "ma_to_hop": ma_to_hop(d.phuong_an.ma_to_hop),
                        "diem_phu_hop": d.diem_phu_hop,
                        "xep_loai": d.xep_loai,
                    }
                    for d in dong
                ],
            }
        return ket_qua
    finally:
        db.close()


def cac_truong() -> list[Path]:
    return sorted(p for p in THU_MUC.iterdir() if p.is_dir() and (p / "de_an.json").exists())


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    thu_muc = THU_MUC / argv[0]
    ket_qua = chay_truong(thu_muc)
    for ten, kq in ket_qua.items():
        print(f"{ten}: {kq['so_phuong_an']} phương án, {kq['so_chuong_trinh']} chương trình xếp hạng")
    if "--ghi" in argv:
        (thu_muc / "ket_qua").mkdir(exist_ok=True)
        for ten, kq in ket_qua.items():
            (thu_muc / "ket_qua" / f"{ten}.json").write_text(
                json.dumps(kq, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
            )
        print(f"Đã ghi {len(ket_qua)} file kết quả mong đợi vào {thu_muc / 'ket_qua'}")
    else:
        print("Chưa ghi gì; thêm --ghi để ghi đè kết quả mong đợi.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
