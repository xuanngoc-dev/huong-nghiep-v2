"""Chạy thử bộ tính cho một đề án bất kể trạng thái (bước 5.4 KE_HOACH_TRIEN_KHAI.md).

Dùng để đối chiếu đề án "thử nghiệm" trên dữ liệu thật trước khi chuyển sang "đang áp dụng". Kết quả cùng dạng file
`tests/du_lieu/hoi_quy_xet_tuyen/<MA_TRUONG>_<NAM>/ket_qua/<ten>.json` nên lưu được thành kết quả mong đợi.
Không dùng cache, không ghi gì vào CSDL.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.services.xet_tuyen.bo_tinh import tinh_phuong_an, xep_hang
from app.services.xet_tuyen.danh_gia import QuyTacNam, _nap_quy_tac
from app.services.xet_tuyen.mo_hinh import HoSoXetTuyen

TRUONG_PHUONG_AN = ("diem_goc", "diem_cong", "diem_uu_tien", "diem_xet", "du_dieu_kien", "ly_do", "chenh_lech_30")


def khoa_phuong_an(ma_xet_tuyen, ten, ma_cong_thuc, ma_to_hop) -> tuple:
    return (ma_xet_tuyen or "", ten, ma_cong_thuc, ma_to_hop or "")


def ket_qua_dang_bang(db: Session, qtn: QuyTacNam, hs: HoSoXetTuyen, *, hom_nay: date) -> dict:
    """Kết quả của một hồ sơ: số phương án, số chương trình xếp hạng, từng phương án và thứ tự xếp hạng.

    Tổ hợp riêng lưu có tiền tố mã trường (`BKA-K01`); kết quả ghi mã như trong file đề án (`K01`).
    """
    ids = [c.id for c in qtn.quy_tac.chuong_trinh]
    ten_ct = dict(
        db.execute(
            select(DatsChuongTrinhDaoTao.id, DatsChuongTrinhDaoTao.ten_chuong_trinh).where(DatsChuongTrinhDaoTao.id.in_(ids))
        ).all()
    )
    ctr = {c.id: c for c in qtn.quy_tac.chuong_trinh}
    ma_cong_thuc = {c.id: c.ma for c in qtn.quy_tac.cong_thuc}

    def ma_to_hop(ma: str | None, ma_truong: str) -> str | None:
        return ma.removeprefix(f"{ma_truong}-") if ma else None

    kq = tinh_phuong_an(qtn.quy_tac, hs, qtn.nam, hom_nay.isoformat(), qtn.diem_chuan)
    dong = xep_hang(qtn.quy_tac, hs, kq)
    phuong_an = []
    for p in kq.phuong_an:
        c = ctr[p.chuong_trinh_id]
        phuong_an.append(
            {
                "ma_xet_tuyen": c.ma_xet_tuyen,
                "ten_chuong_trinh": ten_ct[p.chuong_trinh_id],
                "ma_cong_thuc": ma_cong_thuc[p.cong_thuc_id],
                "ma_to_hop": ma_to_hop(p.ma_to_hop, c.ma_truong),
                **{k: getattr(p, k) for k in TRUONG_PHUONG_AN},
            }
        )
    phuong_an.sort(key=lambda x: khoa_phuong_an(x["ma_xet_tuyen"], x["ten_chuong_trinh"], x["ma_cong_thuc"], x["ma_to_hop"]))
    return {
        "so_phuong_an": len(phuong_an),
        "so_chuong_trinh": len(dong),
        "phuong_an": phuong_an,
        "xep_hang": [
            {
                "ma_xet_tuyen": ctr[d.chuong_trinh_id].ma_xet_tuyen,
                "ten_chuong_trinh": ten_ct[d.chuong_trinh_id],
                "ma_cong_thuc": ma_cong_thuc[d.phuong_an.cong_thuc_id],
                "ma_to_hop": ma_to_hop(d.phuong_an.ma_to_hop, d.ma_truong),
                "diem_phu_hop": d.diem_phu_hop,
                "xep_loai": d.xep_loai,
            }
            for d in dong
        ],
    }


def chay_thu_de_an(db: Session, de_an_id: int, nam: int, hs: HoSoXetTuyen, *, hom_nay: date) -> dict:
    return ket_qua_dang_bang(db, _nap_quy_tac(db, nam, de_an_ids=[de_an_id]), hs, hom_nay=hom_nay)
