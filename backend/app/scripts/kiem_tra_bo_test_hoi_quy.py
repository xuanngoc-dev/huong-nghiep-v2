"""Đối chiếu đề án trong CSDL với bộ test hồi quy xét tuyển (bước 5.4 KE_HOACH_TRIEN_KHAI.md).

Cách dùng (trên máy có mã nguồn, trỏ tới CSDL cần kiểm):
    cd backend && .venv/bin/python -m app.scripts.kiem_tra_bo_test_hoi_quy

Báo cho từng đề án "thử nghiệm" / "đang áp dụng":
- THIẾU: chưa có thư mục tests/du_lieu/hoi_quy_xet_tuyen/<MA_TRUONG>_<NAM> → chưa được chuyển sang "đang áp dụng".
- LỆCH: file de_an.json của bộ test khác file đã import lần gần nhất (so mã băm) → cập nhật bộ test hoặc import lại.
- ĐỦ: có bộ test và đúng file đã import.
Trả mã thoát 1 nếu có đề án "đang áp dụng" bị THIẾU hoặc LỆCH. Chỉ đọc CSDL.
"""

import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.xt_lich_su_import import XtLichSuImport

THU_MUC_MAC_DINH = Path(__file__).resolve().parents[2] / "tests" / "du_lieu" / "hoi_quy_xet_tuyen"
TEN_TRANG_THAI = {1: "thử nghiệm", 2: "đang áp dụng"}


def ma_bam_file(du_lieu: dict) -> str:
    """Cùng cách băm với API import quy tắc (`POST /de-an-tuyen-sinh/{id}/quy-tac/import`)."""
    return hashlib.sha256(json.dumps(du_lieu, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


@dataclass
class DongKiemTra:
    de_an_id: int
    ma_truong: str
    nam: int
    trang_thai: int
    ket_luan: str  # DU / THIEU / LECH
    ghi_chu: str = ""


def kiem_tra(db: Session, thu_muc: Path = THU_MUC_MAC_DINH) -> list[DongKiemTra]:
    ket_qua = []
    for de_an in db.scalars(
        select(DatsTuyenSinh)
        .where(DatsTuyenSinh.trang_thai_xet_tuyen.in_((1, 2)))
        .order_by(DatsTuyenSinh.nam_tuyen_sinh.desc(), DatsTuyenSinh.ma_truong)
    ):
        dong = DongKiemTra(de_an.id, de_an.ma_truong, de_an.nam_tuyen_sinh, de_an.trang_thai_xet_tuyen, "DU")
        file = thu_muc / f"{de_an.ma_truong}_{de_an.nam_tuyen_sinh}" / "de_an.json"
        if not file.exists():
            dong.ket_luan, dong.ghi_chu = "THIEU", f"chưa có {file.parent.name}/"
        else:
            lan_cuoi = db.scalars(
                select(XtLichSuImport).where(XtLichSuImport.de_an_id == de_an.id).order_by(XtLichSuImport.id.desc())
            ).first()
            if lan_cuoi is None or not lan_cuoi.ma_bam:
                dong.ket_luan, dong.ghi_chu = "LECH", "đề án chưa có lần import quy tắc nào có mã băm"
            elif lan_cuoi.ma_bam != ma_bam_file(json.loads(file.read_text(encoding="utf-8"))):
                dong.ket_luan = "LECH"
                dong.ghi_chu = f"de_an.json khác file import lúc {lan_cuoi.tao_luc:%d/%m/%Y %H:%M} ({lan_cuoi.ten_file or 'không tên'})"
        ket_qua.append(dong)
    return ket_qua


def main(argv: list[str]) -> int:
    thu_muc = Path(argv[0]) if argv else THU_MUC_MAC_DINH
    db = SessionLocal()
    try:
        ket_qua = kiem_tra(db, thu_muc)
    finally:
        db.rollback()
        db.close()
    if not ket_qua:
        print("Chưa có đề án nào ở trạng thái thử nghiệm hoặc đang áp dụng.")
        return 0
    nhan = {"DU": "ĐỦ", "THIEU": "THIẾU", "LECH": "LỆCH"}
    for d in ket_qua:
        print(f"[{nhan[d.ket_luan]:5}] {d.ma_truong} {d.nam} (id {d.de_an_id}, {TEN_TRANG_THAI[d.trang_thai]}) {d.ghi_chu}")
    loi = [d for d in ket_qua if d.trang_thai == 2 and d.ket_luan != "DU"]
    if loi:
        print(f"\n{len(loi)} đề án đang áp dụng chưa có bộ test hồi quy khớp với quy tắc đã import.")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
