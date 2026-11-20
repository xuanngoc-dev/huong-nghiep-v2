from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, tuple_
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thcs_huong_di import DmThcsHuongDi, DmThcsHuongDiTieuChi, DmThcsTieuChi
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thcs_huong_di import (
    DmThcsHuongDiTieuChiDeleteMany,
    DmThcsHuongDiTieuChiPage,
    DmThcsHuongDiTieuChiPublic,
    DmThcsHuongDiTieuChiUpdate,
    DmThcsHuongDiTieuChiWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)
from app.services.thcs_huong_di import kiem_tra_huong_di, kiem_tra_tieu_chi
from app.services.thcs_huong_di import like_pattern as _like_pattern

router = APIRouter(prefix="/danh-muc/thcs/huong-di-tieu-chi", tags=["danh-muc"])


def _base_query():
    return (
        select(DmThcsHuongDiTieuChi, DmThcsHuongDi, DmThcsTieuChi)
        .join(DmThcsHuongDi, DmThcsHuongDiTieuChi.thcs_huong_di_id == DmThcsHuongDi.id)
        .join(DmThcsTieuChi, DmThcsHuongDiTieuChi.thcs_tieu_chi_id == DmThcsTieuChi.id)
    )


def _to_public(item: DmThcsHuongDiTieuChi, huong: DmThcsHuongDi, tieu_chi: DmThcsTieuChi) -> DmThcsHuongDiTieuChiPublic:
    """Ghép liên kết với mã/tên hướng đi và tiêu chí."""
    return DmThcsHuongDiTieuChiPublic(
        thcs_huong_di_id=item.thcs_huong_di_id,
        ma_huong=huong.ma_huong,
        ten_huong=huong.ten_huong,
        thcs_tieu_chi_id=item.thcs_tieu_chi_id,
        ma_tieu_chi=tieu_chi.ma_tieu_chi,
        ten_tieu_chi=tieu_chi.ten_tieu_chi,
        nhom_tieu_chi=tieu_chi.nhom_tieu_chi,
        diem_phu_hop=item.diem_phu_hop,
        nhan_dinh_tu_van=item.nhan_dinh_tu_van,
    )


def _load_or_400(
    db: Session, thcs_huong_di_id: int, thcs_tieu_chi_id: int
) -> tuple[DmThcsHuongDiTieuChi, DmThcsHuongDi, DmThcsTieuChi]:
    """Lấy một liên kết theo khóa ghép kèm hướng đi và tiêu chí. Không có thì trả 400 kèm thông báo cụ thể."""
    row = db.execute(
        _base_query().where(
            DmThcsHuongDiTieuChi.thcs_huong_di_id == thcs_huong_di_id,
            DmThcsHuongDiTieuChi.thcs_tieu_chi_id == thcs_tieu_chi_id,
        )
    ).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Không tìm thấy điểm phù hợp hướng đi - tiêu chí có "
                f"thcs_huong_di_id = {thcs_huong_di_id}, thcs_tieu_chi_id = {thcs_tieu_chi_id}"
            ),
        )
    return row[0], row[1], row[2]


def _ensure_chua_co(db: Session, cap: list[tuple[int, int]]) -> None:
    """Từ chối nếu cặp hướng đi - tiêu chí trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    trung = sorted({c for c in cap if cap.count(c) > 1})
    if trung:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cặp (hướng đi, tiêu chí) bị trùng trong dữ liệu: " + ", ".join(f"({a}, {b})" for a, b in trung),
        )
    da_co = db.execute(
        select(DmThcsHuongDiTieuChi.thcs_huong_di_id, DmThcsHuongDiTieuChi.thcs_tieu_chi_id).where(
            tuple_(DmThcsHuongDiTieuChi.thcs_huong_di_id, DmThcsHuongDiTieuChi.thcs_tieu_chi_id).in_(cap)
        )
    ).all()
    if da_co:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hướng đi đã có điểm cho tiêu chí này: " + ", ".join(f"({a}, {b})" for a, b in da_co),
        )


@router.get("", response_model=DmThcsHuongDiTieuChiPage)
def list_thcs_huong_di_tieu_chi(
    q: str | None = Query(default=None, max_length=255),
    thcs_huong_di_id: int | None = Query(default=None, ge=1),
    thcs_tieu_chi_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThcsHuongDiTieuChiPage:
    """Lấy danh sách điểm phù hợp hướng đi - tiêu chí có phân trang. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmThcsHuongDi.ma_huong.like(pattern, escape="\\"),
                DmThcsHuongDi.ten_huong.like(pattern, escape="\\"),
                DmThcsTieuChi.ma_tieu_chi.like(pattern, escape="\\"),
                DmThcsTieuChi.ten_tieu_chi.like(pattern, escape="\\"),
            )
        )
    if thcs_huong_di_id is not None:
        filters.append(DmThcsHuongDiTieuChi.thcs_huong_di_id == thcs_huong_di_id)
    if thcs_tieu_chi_id is not None:
        filters.append(DmThcsHuongDiTieuChi.thcs_tieu_chi_id == thcs_tieu_chi_id)

    base = _base_query().where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(
            DmThcsHuongDi.thu_tu_hien_thi.asc(),
            DmThcsHuongDi.id.asc(),
            DmThcsTieuChi.thu_tu_hien_thi.asc(),
            DmThcsTieuChi.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmThcsHuongDiTieuChiPage(
        items=[_to_public(*row) for row in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{thcs_huong_di_id}/{thcs_tieu_chi_id}", response_model=DmThcsHuongDiTieuChiPublic)
def get_thcs_huong_di_tieu_chi(
    thcs_huong_di_id: int,
    thcs_tieu_chi_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThcsHuongDiTieuChiPublic:
    """Lấy chi tiết điểm phù hợp của một hướng đi với một tiêu chí."""
    return _to_public(*_load_or_400(db, thcs_huong_di_id, thcs_tieu_chi_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thcs_huong_di_tieu_chi_bulk(
    payload: list[DmThcsHuongDiTieuChiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Chấm điểm nhiều cặp hướng đi - tiêu chí cùng lúc."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách điểm phù hợp trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 điểm phù hợp mỗi lần"
        )
    kiem_tra_huong_di(db, [item.thcs_huong_di_id for item in payload])
    kiem_tra_tieu_chi(db, [item.thcs_tieu_chi_id for item in payload])
    _ensure_chua_co(db, [(item.thcs_huong_di_id, item.thcs_tieu_chi_id) for item in payload])
    db.add_all([DmThcsHuongDiTieuChi(**item.model_dump()) for item in payload])
    db.commit()
    return KetQuaThemNhieu(created=len(payload))


@router.post("", response_model=DmThcsHuongDiTieuChiPublic, status_code=status.HTTP_201_CREATED)
def create_thcs_huong_di_tieu_chi(
    payload: DmThcsHuongDiTieuChiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsHuongDiTieuChiPublic:
    """Chấm điểm phù hợp của một hướng đi với một tiêu chí."""
    kiem_tra_huong_di(db, [payload.thcs_huong_di_id])
    kiem_tra_tieu_chi(db, [payload.thcs_tieu_chi_id])
    _ensure_chua_co(db, [(payload.thcs_huong_di_id, payload.thcs_tieu_chi_id)])
    db.add(DmThcsHuongDiTieuChi(**payload.model_dump()))
    db.commit()
    return _to_public(*_load_or_400(db, payload.thcs_huong_di_id, payload.thcs_tieu_chi_id))


@router.put("/{thcs_huong_di_id}/{thcs_tieu_chi_id}", response_model=DmThcsHuongDiTieuChiPublic)
def update_thcs_huong_di_tieu_chi(
    thcs_huong_di_id: int,
    thcs_tieu_chi_id: int,
    payload: DmThcsHuongDiTieuChiUpdate,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThcsHuongDiTieuChiPublic:
    """Cập nhật điểm phù hợp và nhận định tư vấn (không đổi được hướng đi/tiêu chí)."""
    item, huong, tieu_chi = _load_or_400(db, thcs_huong_di_id, thcs_tieu_chi_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, huong, tieu_chi)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thcs_huong_di_tieu_chi_many(
    payload: DmThcsHuongDiTieuChiDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều điểm phù hợp theo danh sách khóa ghép. Cặp không tồn tại thì bỏ qua."""
    cap = list(dict.fromkeys((k.thcs_huong_di_id, k.thcs_tieu_chi_id) for k in payload.items))
    items = db.scalars(
        select(DmThcsHuongDiTieuChi).where(
            tuple_(DmThcsHuongDiTieuChi.thcs_huong_di_id, DmThcsHuongDiTieuChi.thcs_tieu_chi_id).in_(cap)
        )
    ).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{thcs_huong_di_id}/{thcs_tieu_chi_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thcs_huong_di_tieu_chi(
    thcs_huong_di_id: int,
    thcs_tieu_chi_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa điểm phù hợp của một hướng đi với một tiêu chí."""
    item, _huong, _tieu_chi = _load_or_400(db, thcs_huong_di_id, thcs_tieu_chi_id)
    db.delete(item)
    db.commit()
