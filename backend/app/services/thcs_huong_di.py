"""Logic dùng chung cho các danh mục hướng đi sau THCS có liên kết tới hướng đi, tiêu chí."""

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.dm_thcs_huong_di import DmThcsHuongDi, DmThcsTieuChi


def like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _kiem_tra_ton_tai(db: Session, model, ids: list[int], nhan: str) -> dict:
    unique = list(dict.fromkeys(ids))
    found = {item.id: item for item in db.scalars(select(model).where(model.id.in_(unique))).all()}
    missing = [str(item_id) for item_id in unique if item_id not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy {nhan} có id = {', '.join(missing)}",
        )
    return found


def kiem_tra_huong_di(db: Session, ids: list[int]) -> dict[int, DmThcsHuongDi]:
    """Mọi hướng đi trong danh sách phải tồn tại; trả về map id → hướng đi."""
    return _kiem_tra_ton_tai(db, DmThcsHuongDi, ids, "hướng đi THCS")


def kiem_tra_tieu_chi(db: Session, ids: list[int]) -> dict[int, DmThcsTieuChi]:
    """Mọi tiêu chí trong danh sách phải tồn tại; trả về map id → tiêu chí."""
    return _kiem_tra_ton_tai(db, DmThcsTieuChi, ids, "tiêu chí THCS")


def thong_tin_huong_di(huong: DmThcsHuongDi | None) -> dict:
    """Mã/tên hướng đi để ghép vào bản ghi con trả về."""
    return {"ma_huong": huong.ma_huong if huong else None, "ten_huong": huong.ten_huong if huong else None}


def danh_sach_con(db: Session, model, filters: list, order_by: list, page: int, page_size: int):
    """Truy vấn bảng con kèm hướng đi (join). Trả về (các dòng (item, huong), tổng)."""
    base = (
        select(model, DmThcsHuongDi)
        .join(DmThcsHuongDi, model.thcs_huong_di_id == DmThcsHuongDi.id)
        .where(*filters)
    )
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(base.order_by(*order_by).offset((page - 1) * page_size).limit(page_size)).all()
    return rows, total
