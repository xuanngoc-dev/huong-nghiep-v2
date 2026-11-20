"""Logic dùng chung cho các danh mục XKLĐ THPT có liên kết (nhóm nghề, thị trường).

Bảng con (nghề cụ thể, chi phí, thủ tục, kênh kết nối) luôn thuộc một nhóm nghề; thị trường có thể NULL (áp dụng chung
cho cả nhóm nghề), nếu có thì thị trường phải thuộc đúng nhóm nghề đó.
"""

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.dm_thpt_xkld import DmThptXkldNhomNghe, DmThptXkldThiTruong


def _loi(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def kiem_tra_nhom_nghe(db: Session, ids: list[int]) -> dict[int, DmThptXkldNhomNghe]:
    """Mọi nhóm nghề trong danh sách phải tồn tại; trả về map id → nhóm nghề."""
    unique = list(dict.fromkeys(ids))
    found = {
        item.id: item
        for item in db.scalars(select(DmThptXkldNhomNghe).where(DmThptXkldNhomNghe.id.in_(unique))).all()
    }
    missing = [str(item_id) for item_id in unique if item_id not in found]
    if missing:
        raise _loi(f"Không tìm thấy nhóm nghề XKLĐ có id = {', '.join(missing)}")
    return found


def kiem_tra_lien_ket(
    db: Session, cap: list[tuple[int, int | None]]
) -> tuple[dict[int, DmThptXkldNhomNghe], dict[int, DmThptXkldThiTruong]]:
    """Kiểm tra các cặp (nhóm nghề, thị trường): nhóm nghề và thị trường tồn tại, thị trường thuộc đúng nhóm nghề."""
    nhom_nghe = kiem_tra_nhom_nghe(db, [nhom_id for nhom_id, _ in cap])
    tt_ids = list(dict.fromkeys(tt_id for _, tt_id in cap if tt_id is not None))
    thi_truong = {
        item.id: item
        for item in db.scalars(select(DmThptXkldThiTruong).where(DmThptXkldThiTruong.id.in_(tt_ids))).all()
    } if tt_ids else {}
    missing = [str(tt_id) for tt_id in tt_ids if tt_id not in thi_truong]
    if missing:
        raise _loi(f"Không tìm thấy thị trường XKLĐ có id = {', '.join(missing)}")
    for nhom_id, tt_id in cap:
        if tt_id is None:
            continue
        tt = thi_truong[tt_id]
        if tt.thpt_xkld_nhom_nghe_id != nhom_id:
            raise _loi(
                f"Thị trường {tt.ten_quoc_gia} (id = {tt_id}) không thuộc nhóm nghề {nhom_nghe[nhom_id].ten_nhom} "
                f"(id = {nhom_id})"
            )
    return nhom_nghe, thi_truong


def thong_tin_lien_ket(nhom: DmThptXkldNhomNghe | None, tt: DmThptXkldThiTruong | None) -> dict:
    """Mã/tên nhóm nghề và thị trường để ghép vào bản ghi trả về."""
    return {
        "ma_nhom": nhom.ma_nhom if nhom else None,
        "ten_nhom": nhom.ten_nhom if nhom else None,
        "ma_quoc_gia": tt.ma_quoc_gia if tt else None,
        "ten_quoc_gia": tt.ten_quoc_gia if tt else None,
    }


def lay_lien_ket(db: Session, item) -> dict:
    """Thông tin liên kết của một bản ghi con."""
    tt_id = item.thpt_xkld_thi_truong_id
    return thong_tin_lien_ket(
        db.get(DmThptXkldNhomNghe, item.thpt_xkld_nhom_nghe_id), db.get(DmThptXkldThiTruong, tt_id) if tt_id else None
    )


def danh_sach_con(db: Session, model, filters: list, order_by: list, page: int, page_size: int):
    """Truy vấn bảng con kèm nhóm nghề (join) và thị trường (outer join). Trả về (các dòng (item, nhom, tt), tổng)."""
    base = (
        select(model, DmThptXkldNhomNghe, DmThptXkldThiTruong)
        .join(DmThptXkldNhomNghe, model.thpt_xkld_nhom_nghe_id == DmThptXkldNhomNghe.id)
        .outerjoin(DmThptXkldThiTruong, model.thpt_xkld_thi_truong_id == DmThptXkldThiTruong.id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(base.order_by(*order_by).offset((page - 1) * page_size).limit(page_size)).all()
    return rows, total


def loc_lien_ket(model, q_cot: list, q: str | None, nhom_nghe_id: int | None, thi_truong_id: int | None) -> list:
    """Bộ lọc chung: từ khóa trên các cột của bảng con và tên nhóm nghề/thị trường, cùng nhóm nghề, thị trường."""
    filters = []
    if q and q.strip():
        pattern = like_pattern(q.strip())
        cot = [*q_cot, DmThptXkldNhomNghe.ten_nhom, DmThptXkldThiTruong.ten_quoc_gia]
        filters.append(or_(*(c.like(pattern, escape="\\") for c in cot)))
    if nhom_nghe_id is not None:
        filters.append(model.thpt_xkld_nhom_nghe_id == nhom_nghe_id)
    if thi_truong_id is not None:
        filters.append(model.thpt_xkld_thi_truong_id == thi_truong_id)
    return filters
