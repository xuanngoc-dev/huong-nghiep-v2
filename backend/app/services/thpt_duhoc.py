"""Logic dùng chung cho các danh mục du học THPT có liên kết (hướng đi, quốc gia).

Bảng con (ngành, chi phí, thủ tục, kênh kết nối) luôn thuộc một hướng đi; quốc gia có thể NULL (áp dụng chung
cho cả hướng đi), nếu có thì quốc gia phải thuộc đúng hướng đi đó.
"""

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.dm_thpt_duhoc import DmThptDuhocHuongDi, DmThptDuhocQuocGia


def _loi(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def kiem_tra_huong_di(db: Session, ids: list[int]) -> dict[int, DmThptDuhocHuongDi]:
    """Mọi hướng đi trong danh sách phải tồn tại; trả về map id → hướng đi."""
    unique = list(dict.fromkeys(ids))
    found = {
        item.id: item
        for item in db.scalars(select(DmThptDuhocHuongDi).where(DmThptDuhocHuongDi.id.in_(unique))).all()
    }
    missing = [str(item_id) for item_id in unique if item_id not in found]
    if missing:
        raise _loi(f"Không tìm thấy hướng đi du học có id = {', '.join(missing)}")
    return found


def kiem_tra_lien_ket(
    db: Session, cap: list[tuple[int, int | None]]
) -> tuple[dict[int, DmThptDuhocHuongDi], dict[int, DmThptDuhocQuocGia]]:
    """Kiểm tra các cặp (hướng đi, quốc gia): hướng đi và quốc gia tồn tại, quốc gia thuộc đúng hướng đi."""
    huong_di = kiem_tra_huong_di(db, [huong_id for huong_id, _ in cap])
    qg_ids = list(dict.fromkeys(qg_id for _, qg_id in cap if qg_id is not None))
    quoc_gia = {
        item.id: item
        for item in db.scalars(select(DmThptDuhocQuocGia).where(DmThptDuhocQuocGia.id.in_(qg_ids))).all()
    } if qg_ids else {}
    missing = [str(qg_id) for qg_id in qg_ids if qg_id not in quoc_gia]
    if missing:
        raise _loi(f"Không tìm thấy quốc gia du học có id = {', '.join(missing)}")
    for huong_id, qg_id in cap:
        if qg_id is None:
            continue
        qg = quoc_gia[qg_id]
        if qg.thpt_duhoc_huong_di_id != huong_id:
            raise _loi(
                f"Quốc gia {qg.ten_quoc_gia} (id = {qg_id}) không thuộc hướng đi {huong_di[huong_id].ten_huong} "
                f"(id = {huong_id})"
            )
    return huong_di, quoc_gia


def thong_tin_lien_ket(huong: DmThptDuhocHuongDi | None, qg: DmThptDuhocQuocGia | None) -> dict:
    """Mã/tên hướng đi và quốc gia để ghép vào bản ghi trả về."""
    return {
        "ma_huong": huong.ma_huong if huong else None,
        "ten_huong": huong.ten_huong if huong else None,
        "ma_quoc_gia": qg.ma_quoc_gia if qg else None,
        "ten_quoc_gia": qg.ten_quoc_gia if qg else None,
    }


def lay_lien_ket(db: Session, item) -> dict:
    """Thông tin liên kết của một bản ghi con."""
    qg_id = item.thpt_duhoc_quoc_gia_id
    return thong_tin_lien_ket(
        db.get(DmThptDuhocHuongDi, item.thpt_duhoc_huong_di_id), db.get(DmThptDuhocQuocGia, qg_id) if qg_id else None
    )


def danh_sach_con(db: Session, model, filters: list, order_by: list, page: int, page_size: int):
    """Truy vấn bảng con kèm hướng đi (join) và quốc gia (outer join). Trả về (các dòng (item, huong, qg), tổng)."""
    base = (
        select(model, DmThptDuhocHuongDi, DmThptDuhocQuocGia)
        .join(DmThptDuhocHuongDi, model.thpt_duhoc_huong_di_id == DmThptDuhocHuongDi.id)
        .outerjoin(DmThptDuhocQuocGia, model.thpt_duhoc_quoc_gia_id == DmThptDuhocQuocGia.id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(base.order_by(*order_by).offset((page - 1) * page_size).limit(page_size)).all()
    return rows, total


def loc_lien_ket(model, q_cot: list, q: str | None, huong_di_id: int | None, quoc_gia_id: int | None) -> list:
    """Bộ lọc chung: từ khóa trên các cột của bảng con và tên hướng đi/quốc gia, cùng hướng đi, quốc gia."""
    filters = []
    if q and q.strip():
        pattern = like_pattern(q.strip())
        cot = [*q_cot, DmThptDuhocHuongDi.ten_huong, DmThptDuhocQuocGia.ten_quoc_gia]
        filters.append(or_(*(c.like(pattern, escape="\\") for c in cot)))
    if huong_di_id is not None:
        filters.append(model.thpt_duhoc_huong_di_id == huong_di_id)
    if quoc_gia_id is not None:
        filters.append(model.thpt_duhoc_quoc_gia_id == quoc_gia_id)
    return filters
