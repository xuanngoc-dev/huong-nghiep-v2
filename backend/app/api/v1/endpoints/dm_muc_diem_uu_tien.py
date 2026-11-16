"""Mức điểm cộng khu vực / đối tượng ưu tiên theo năm (bước 5.1 KE_HOACH_TRIEN_KHAI.md).

Bộ tính xét tuyển lấy dòng khớp năm tuyển sinh; mã không có dòng nào khớp dùng diem_cong của danh mục.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_doi_tuong_uu_tien import DmDoiTuongUuTien
from app.models.dm_khu_vuc_uu_tien import DmKhuVucUuTien
from app.models.dm_muc_diem_uu_tien import DmMucDiemUuTien
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_muc_diem_uu_tien import (
    DmMucDiemUuTienDeleteMany,
    DmMucDiemUuTienDeleteManyResult,
    DmMucDiemUuTienPage,
    DmMucDiemUuTienPublic,
    DmMucDiemUuTienWrite,
)

router = APIRouter(prefix="/danh-muc/muc-diem-uu-tien", tags=["danh-muc"])

_TEN_LOAI = {"KHU_VUC": "khu vực", "DOI_TUONG": "đối tượng"}


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _get_or_400(db: Session, item_id: int) -> DmMucDiemUuTien:
    """Lấy một bản ghi theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmMucDiemUuTien, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy mức điểm ưu tiên có id = {item_id}",
        )
    return item


def _ten_theo_ma(db: Session) -> dict[tuple[str, str], str]:
    ten = {("KHU_VUC", ma): t for ma, t in db.execute(select(DmKhuVucUuTien.ma_khu_vuc, DmKhuVucUuTien.ten_khu_vuc))}
    ten.update(
        {("DOI_TUONG", ma): t for ma, t in db.execute(select(DmDoiTuongUuTien.ma_doi_tuong, DmDoiTuongUuTien.ten_doi_tuong))}
    )
    return ten


def _cong_khai(item: DmMucDiemUuTien, ten: dict[tuple[str, str], str]) -> DmMucDiemUuTienPublic:
    out = DmMucDiemUuTienPublic.model_validate(item)
    out.ten = ten.get((item.loai, item.ma))
    return out


def _kiem_tra(db: Session, payload: DmMucDiemUuTienWrite, bo_qua_id: int | None = None) -> None:
    """Mã phải có trong danh mục; khoảng năm không chồng lên mức khác của cùng mã."""
    if (payload.loai, payload.ma) not in _ten_theo_ma(db):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy {_TEN_LOAI[payload.loai]} ưu tiên có mã = {payload.ma}",
        )
    chong = db.scalars(
        select(DmMucDiemUuTien).where(
            DmMucDiemUuTien.loai == payload.loai,
            DmMucDiemUuTien.ma == payload.ma,
            DmMucDiemUuTien.id != (bo_qua_id or 0),
            DmMucDiemUuTien.nam_ap_dung_tu <= (payload.nam_ap_dung_den or 9999),
            func.coalesce(DmMucDiemUuTien.nam_ap_dung_den, 9999) >= payload.nam_ap_dung_tu,
        )
    ).first()
    if chong is not None:
        den = chong.nam_ap_dung_den or "nay"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã {payload.ma} đã có mức điểm áp dụng {chong.nam_ap_dung_tu}–{den}, trùng khoảng năm",
        )


@router.get("", response_model=DmMucDiemUuTienPage)
def list_muc_diem_uu_tien(
    q: str | None = Query(default=None, max_length=150),
    loai: str | None = Query(default=None, pattern="^(KHU_VUC|DOI_TUONG)$"),
    nam: int | None = Query(default=None, ge=2000, le=2100, description="Chỉ lấy mức áp dụng cho năm này"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> DmMucDiemUuTienPage:
    """Danh sách mức điểm ưu tiên theo năm, lọc theo mã / căn cứ, loại và năm. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(DmMucDiemUuTien.ma.like(pattern, escape="\\"), DmMucDiemUuTien.can_cu.like(pattern, escape="\\"))
        )
    if loai:
        filters.append(DmMucDiemUuTien.loai == loai)
    if nam is not None:
        filters.append(DmMucDiemUuTien.nam_ap_dung_tu <= nam)
        filters.append(func.coalesce(DmMucDiemUuTien.nam_ap_dung_den, 9999) >= nam)

    total = db.scalar(select(func.count()).select_from(DmMucDiemUuTien).where(*filters)) or 0
    items = db.scalars(
        select(DmMucDiemUuTien)
        .where(*filters)
        .order_by(DmMucDiemUuTien.loai, DmMucDiemUuTien.ma, DmMucDiemUuTien.nam_ap_dung_tu.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    ten = _ten_theo_ma(db)
    return DmMucDiemUuTienPage(items=[_cong_khai(i, ten) for i in items], total=total, page=page, page_size=page_size)


@router.get("/{item_id}", response_model=DmMucDiemUuTienPublic)
def get_muc_diem_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmMucDiemUuTienPublic:
    """Chi tiết một mức điểm ưu tiên theo id."""
    return _cong_khai(_get_or_400(db, item_id), _ten_theo_ma(db))


@router.post("", response_model=DmMucDiemUuTienPublic, status_code=status.HTTP_201_CREATED)
def create_muc_diem_uu_tien(
    payload: DmMucDiemUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmMucDiemUuTienPublic:
    """Thêm mức điểm ưu tiên cho một khoảng năm."""
    _kiem_tra(db, payload)
    item = DmMucDiemUuTien(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _cong_khai(item, _ten_theo_ma(db))


@router.put("/{item_id}", response_model=DmMucDiemUuTienPublic)
def update_muc_diem_uu_tien(
    item_id: int,
    payload: DmMucDiemUuTienWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmMucDiemUuTienPublic:
    """Cập nhật một mức điểm ưu tiên."""
    item = _get_or_400(db, item_id)
    _kiem_tra(db, payload, bo_qua_id=item_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    item.cap_nhat_luc = datetime.now()
    db.commit()
    db.refresh(item)
    return _cong_khai(item, _ten_theo_ma(db))


@router.delete("", response_model=DmMucDiemUuTienDeleteManyResult)
def delete_muc_diem_uu_tien_many(
    payload: DmMucDiemUuTienDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmMucDiemUuTienDeleteManyResult:
    """Xóa nhiều mức điểm ưu tiên theo danh sách id."""
    items = db.scalars(select(DmMucDiemUuTien).where(DmMucDiemUuTien.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return DmMucDiemUuTienDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_muc_diem_uu_tien(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một mức điểm ưu tiên theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()
