"""Chuyển hồ sơ năng lực cũ (JSON trinh_do_hoc_van) sang các bảng hs_* (bước 4.4 KE_HOACH_TRIEN_KHAI.md).

Cách dùng (chạy trên bản sao CSDL trước):
    cd backend && .venv/bin/python -m app.scripts.chuyen_ho_so_xet_tuyen [bao_cao.md]          # chạy thử, không ghi
    cd backend && .venv/bin/python -m app.scripts.chuyen_ho_so_xet_tuyen --ghi [bao_cao.md]    # ghi thật

- Chỉ tạo hồ sơ cho thành viên chưa có hồ sơ hs_*; người đã có thì bỏ qua (không ghi đè).
- Quy tắc chuyển theo quyết định đã chốt: NN1 = Tiếng Anh, NN2 = Tiếng Pháp; học lực suy từ điểm trung bình;
  năm tốt nghiệp = năm hiện tại.
- Mã không có trong danh mục (môn CN, GDDP..., chứng chỉ, bài thi, thành tích lạ) không chuyển được: ghi vào báo cáo.
- Không sửa JSON cũ. Mỗi người ghi trong savepoint riêng; một người lỗi không ảnh hưởng người khác.
"""

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.hs_ho_so import HsHoSo
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin
from app.schemas.hs_ho_so import HoSoXetTuyenWrite
from app.services.ho_so_xet_tuyen import DanhMucMa, ghi_ho_so, tu_trinh_do_hoc_van
from app.services.xet_tuyen.chuyen_ho_so import MON_NGOAI_NGU_CU, DanhMucHoSo


@dataclass
class KetQuaNguoi:
    nguoi_dung_id: int
    trang_thai: str  # chuyen / bo_qua / loi
    so_diem_mon: int = 0
    khong_chuyen: list[str] = field(default_factory=list)
    ghi_chu: str = ""


def chuan_bi(
    profile: NguoiDungThongTin, *, nam: int, dm: DanhMucMa, dm_ho_so: DanhMucHoSo
) -> tuple[HoSoXetTuyenWrite, list[str]]:
    """Hồ sơ hs_* dựng từ JSON cũ, bỏ các dòng có mã ngoài danh mục; trả kèm danh sách dòng không chuyển được."""
    hv = profile.trinh_do_hoc_van or {}
    khong_chuyen: list[str] = []
    for ma in ((hv.get("diem_thi_thpt_quoc_gia") or {}).get("du_kien") or {}):
        ma_moi = MON_NGOAI_NGU_CU.get(str(ma).upper(), str(ma).upper())
        if ma_moi not in dm.mon:
            khong_chuyen.append(f"điểm thi môn {ma}")
    for lop, theo_mon in (hv.get("diem_trung_binh_hoc_ba") or {}).items():
        theo_mon = theo_mon.get("hoc_luc", theo_mon) if isinstance(theo_mon, dict) else {}
        for ma in theo_mon or {}:
            ma_moi = MON_NGOAI_NGU_CU.get(str(ma).upper(), str(ma).upper())
            if ma_moi not in dm.mon:
                khong_chuyen.append(f"học bạ lớp {lop} môn {ma}")
    for c in hv.get("chung_chi_ngoai_ngu") or []:
        ma = str(c.get("ma", "")).upper()
        if ma not in dm.chung_chi:
            khong_chuyen.append(f"chứng chỉ {ma}")
        elif not c.get("thanh_tich"):
            khong_chuyen.append(f"chứng chỉ {ma} (không có điểm / cấp độ)")
    for b in hv.get("bai_thi_danh_gia_nang_luc") or []:
        ma = str(b.get("ma", "")).upper()
        if ma not in dm.bai_thi:
            khong_chuyen.append(f"bài thi {ma}")
    for t in hv.get("thanh_tich_hoc_tap_nghien_cuu") or []:
        ma = str(t.get("ma", "")).upper()
        if ma not in dm.thanh_tich:
            khong_chuyen.append(f"thành tích {ma}")

    payload = tu_trinh_do_hoc_van(profile, nam_tuyen_sinh=nam, danh_muc=dm_ho_so)
    payload = payload.model_copy(
        update={
            "ten_ho_so": "Hồ sơ chính (chuyển từ hồ sơ năng lực)",
            "diem_mon": [d for d in payload.diem_mon if d.ma_mon in dm.mon],
            "chung_chi": [c for c in payload.chung_chi if c.ma_chung_chi in dm.chung_chi],
            "diem_bai_thi": [b for b in payload.diem_bai_thi if b.ma_bai_thi in dm.bai_thi],
            "thanh_tich": [t for t in payload.thanh_tich if t.ma_thanh_tich in dm.thanh_tich],
        }
    )
    return payload, khong_chuyen


def chuyen(db: Session, *, ghi: bool, nam: int | None = None) -> list[KetQuaNguoi]:
    nam = nam or datetime.now().year
    dm = DanhMucMa.tu_csdl(db)
    dm_ho_so = DanhMucHoSo.tu_csdl(db)
    da_co = set(db.scalars(select(HsHoSo.nguoi_dung_id).where(HsHoSo.nguoi_dung_id.is_not(None))))
    ket_qua: list[KetQuaNguoi] = []
    for profile in db.scalars(
        select(NguoiDungThongTin).where(NguoiDungThongTin.trinh_do_hoc_van.is_not(None)).order_by(NguoiDungThongTin.id)
    ):
        if profile.nguoi_dung_id in da_co:
            ket_qua.append(KetQuaNguoi(profile.nguoi_dung_id, "bo_qua", ghi_chu="đã có hồ sơ xét tuyển"))
            continue
        try:
            payload, khong_chuyen = chuan_bi(profile, nam=nam, dm=dm, dm_ho_so=dm_ho_so)
            if ghi:
                with db.begin_nested():
                    hs = HsHoSo(nguoi_dung_id=profile.nguoi_dung_id, la_ho_so_chinh=True)
                    db.add(hs)
                    ghi_ho_so(db, hs, payload, dm)
            ket_qua.append(
                KetQuaNguoi(profile.nguoi_dung_id, "chuyen", so_diem_mon=len(payload.diem_mon), khong_chuyen=khong_chuyen)
            )
        except Exception as exc:  # noqa: BLE001 - ghi lỗi từng người vào báo cáo, chạy tiếp người khác
            ket_qua.append(KetQuaNguoi(profile.nguoi_dung_id, "loi", ghi_chu=str(exc)[:300]))
    return ket_qua


def bao_cao(ket_qua: list[KetQuaNguoi], *, ghi: bool) -> str:
    dem = {t: sum(1 for k in ket_qua if k.trang_thai == t) for t in ("chuyen", "bo_qua", "loi")}
    dong = [
        "# Chuyển hồ sơ năng lực sang hồ sơ xét tuyển hs_*",
        "",
        f"Thời điểm: {datetime.now():%d/%m/%Y %H:%M}. Chế độ: {'GHI THẬT' if ghi else 'chạy thử (không ghi)'}.",
        "",
        "| Kết quả | Số người |",
        "|---|---|",
        f"| {'Đã chuyển' if ghi else 'Sẽ chuyển'} | {dem['chuyen']} |",
        f"| Bỏ qua (đã có hồ sơ xét tuyển) | {dem['bo_qua']} |",
        f"| Lỗi | {dem['loi']} |",
        "",
    ]
    co_bo = [k for k in ket_qua if k.khong_chuyen]
    dong += ["## Dòng không chuyển được", ""]
    if co_bo:
        dong += ["| Người dùng | Không chuyển được |", "|---|---|"]
        dong += [f"| {k.nguoi_dung_id} | {', '.join(k.khong_chuyen)} |" for k in co_bo]
    else:
        dong.append("Không có.")
    loi = [k for k in ket_qua if k.trang_thai == "loi"]
    if loi:
        dong += ["", "## Lỗi", "", "| Người dùng | Lỗi |", "|---|---|"]
        dong += [f"| {k.nguoi_dung_id} | {k.ghi_chu.replace('|', '/')} |" for k in loi]
    return "\n".join(dong) + "\n"


def main(argv: list[str]) -> int:
    ghi = "--ghi" in argv
    file_bao_cao = next((a for a in argv if not a.startswith("--")), None)
    db = SessionLocal()
    try:
        ket_qua = chuyen(db, ghi=ghi)
        if ghi:
            db.commit()
        else:
            db.rollback()
    finally:
        db.close()
    noi_dung = bao_cao(ket_qua, ghi=ghi)
    if file_bao_cao:
        Path(file_bao_cao).write_text(noi_dung, encoding="utf-8")
        print(f"Đã ghi báo cáo vào {file_bao_cao}")
    else:
        print(noi_dung)
    return 1 if any(k.trang_thai == "loi" for k in ket_qua) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
