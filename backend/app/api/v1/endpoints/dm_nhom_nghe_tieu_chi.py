from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select, tuple_
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_nhom_nghe_di_lam import DmNhomNgheDiLam, DmNhomNgheTieuChi, DmTieuChiGoiY
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_nhom_nghe_di_lam import (
    DmNhomNgheTieuChiDeleteMany,
    DmNhomNgheTieuChiPage,
    DmNhomNgheTieuChiPublic,
    DmNhomNgheTieuChiUpdate,
    DmNhomNgheTieuChiWrite,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
)

router = APIRouter(prefix="/danh-muc/nhom-nghe-tieu-chi", tags=["danh-muc"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _base_query():
    return (
        select(DmNhomNgheTieuChi, DmNhomNgheDiLam, DmTieuChiGoiY)
        .join(DmNhomNgheDiLam, DmNhomNgheTieuChi.nhom_nghe_di_lam_id == DmNhomNgheDiLam.id)
        .join(DmTieuChiGoiY, DmNhomNgheTieuChi.tieu_chi_goi_y_id == DmTieuChiGoiY.id)
    )


def _to_public(item: DmNhomNgheTieuChi, nhom: DmNhomNgheDiLam, tieu_chi: DmTieuChiGoiY) -> DmNhomNgheTieuChiPublic:
    """Ghép liên kết với mã/tên nhóm nghề và tiêu chí."""
    return DmNhomNgheTieuChiPublic(
        nhom_nghe_di_lam_id=item.nhom_nghe_di_lam_id,
        ma_nhom=nhom.ma_nhom,
        ten_nhom=nhom.ten_nhom,
        tieu_chi_goi_y_id=item.tieu_chi_goi_y_id,
        ma_tieu_chi=tieu_chi.ma_tieu_chi,
        ten_tieu_chi=tieu_chi.ten_tieu_chi,
        nhom_tieu_chi=tieu_chi.nhom_tieu_chi,
        diem_phu_hop=item.diem_phu_hop,
        ghi_chu=item.ghi_chu,
    )


def _load_or_400(
    db: Session, nhom_nghe_di_lam_id: int, tieu_chi_goi_y_id: int
) -> tuple[DmNhomNgheTieuChi, DmNhomNgheDiLam, DmTieuChiGoiY]:
    """Lấy một liên kết theo khóa ghép kèm nhóm nghề và tiêu chí. Không có thì trả 400 kèm thông báo cụ thể."""
    row = db.execute(
        _base_query().where(
            DmNhomNgheTieuChi.nhom_nghe_di_lam_id == nhom_nghe_di_lam_id,
            DmNhomNgheTieuChi.tieu_chi_goi_y_id == tieu_chi_goi_y_id,
        )
    ).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Không tìm thấy liên kết nhóm nghề - tiêu chí có "
                f"nhom_nghe_di_lam_id = {nhom_nghe_di_lam_id}, tieu_chi_goi_y_id = {tieu_chi_goi_y_id}"
            ),
        )
    return row[0], row[1], row[2]


def _ensure_ton_tai(db: Session, nhom_ids: list[int], tieu_chi_ids: list[int]) -> None:
    """Kiểm tra mọi nhóm nghề và tiêu chí được tham chiếu đều tồn tại."""
    nhom_ids = list(dict.fromkeys(nhom_ids))
    tieu_chi_ids = list(dict.fromkeys(tieu_chi_ids))
    co_nhom = set(db.scalars(select(DmNhomNgheDiLam.id).where(DmNhomNgheDiLam.id.in_(nhom_ids))).all())
    thieu_nhom = [str(i) for i in nhom_ids if i not in co_nhom]
    if thieu_nhom:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy nhóm nghề đi làm có id = {', '.join(thieu_nhom)}",
        )
    co_tieu_chi = set(db.scalars(select(DmTieuChiGoiY.id).where(DmTieuChiGoiY.id.in_(tieu_chi_ids))).all())
    thieu_tieu_chi = [str(i) for i in tieu_chi_ids if i not in co_tieu_chi]
    if thieu_tieu_chi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy tiêu chí gợi ý có id = {', '.join(thieu_tieu_chi)}",
        )


def _ensure_chua_co(db: Session, cap: list[tuple[int, int]]) -> None:
    """Từ chối nếu cặp nhóm nghề - tiêu chí trùng trong dữ liệu gửi lên hoặc đã có trong hệ thống."""
    trung = sorted({c for c in cap if cap.count(c) > 1})
    if trung:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cặp (nhóm nghề, tiêu chí) bị trùng trong dữ liệu: " + ", ".join(f"({a}, {b})" for a, b in trung),
        )
    da_co = db.execute(
        select(DmNhomNgheTieuChi.nhom_nghe_di_lam_id, DmNhomNgheTieuChi.tieu_chi_goi_y_id).where(
            tuple_(DmNhomNgheTieuChi.nhom_nghe_di_lam_id, DmNhomNgheTieuChi.tieu_chi_goi_y_id).in_(cap)
        )
    ).all()
    if da_co:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nhóm nghề đã gắn tiêu chí này: " + ", ".join(f"({a}, {b})" for a, b in da_co),
        )


@router.get("", response_model=DmNhomNgheTieuChiPage)
def list_nhom_nghe_tieu_chi(
    q: str | None = Query(default=None, max_length=255),
    nhom_nghe_di_lam_id: int | None = Query(default=None, ge=1),
    tieu_chi_goi_y_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmNhomNgheTieuChiPage:
    """Lấy danh sách liên kết nhóm nghề - tiêu chí có phân trang. Không cần đăng nhập."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNhomNgheDiLam.ma_nhom.like(pattern, escape="\\"),
                DmNhomNgheDiLam.ten_nhom.like(pattern, escape="\\"),
                DmTieuChiGoiY.ma_tieu_chi.like(pattern, escape="\\"),
                DmTieuChiGoiY.ten_tieu_chi.like(pattern, escape="\\"),
            )
        )
    if nhom_nghe_di_lam_id is not None:
        filters.append(DmNhomNgheTieuChi.nhom_nghe_di_lam_id == nhom_nghe_di_lam_id)
    if tieu_chi_goi_y_id is not None:
        filters.append(DmNhomNgheTieuChi.tieu_chi_goi_y_id == tieu_chi_goi_y_id)

    base = _base_query().where(*filters)
    total = db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = db.execute(
        base.order_by(DmNhomNgheDiLam.ma_nhom.asc(), DmNhomNgheTieuChi.diem_phu_hop.desc(), DmTieuChiGoiY.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNhomNgheTieuChiPage(
        items=[_to_public(*row) for row in rows], total=total, page=page, page_size=page_size
    )


@router.get("/{nhom_nghe_di_lam_id}/{tieu_chi_goi_y_id}", response_model=DmNhomNgheTieuChiPublic)
def get_nhom_nghe_tieu_chi(
    nhom_nghe_di_lam_id: int,
    tieu_chi_goi_y_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmNhomNgheTieuChiPublic:
    """Lấy chi tiết một liên kết nhóm nghề - tiêu chí."""
    return _to_public(*_load_or_400(db, nhom_nghe_di_lam_id, tieu_chi_goi_y_id))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_nhom_nghe_tieu_chi_bulk(
    payload: list[DmNhomNgheTieuChiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Gắn nhiều tiêu chí cho nhóm nghề cùng lúc."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách liên kết trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 liên kết mỗi lần")
    _ensure_ton_tai(db, [item.nhom_nghe_di_lam_id for item in payload], [item.tieu_chi_goi_y_id for item in payload])
    _ensure_chua_co(db, [(item.nhom_nghe_di_lam_id, item.tieu_chi_goi_y_id) for item in payload])
    db.add_all([DmNhomNgheTieuChi(**item.model_dump()) for item in payload])
    db.commit()
    return KetQuaThemNhieu(created=len(payload))


@router.post("", response_model=DmNhomNgheTieuChiPublic, status_code=status.HTTP_201_CREATED)
def create_nhom_nghe_tieu_chi(
    payload: DmNhomNgheTieuChiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNhomNgheTieuChiPublic:
    """Gắn một tiêu chí cho nhóm nghề kèm điểm phù hợp."""
    _ensure_ton_tai(db, [payload.nhom_nghe_di_lam_id], [payload.tieu_chi_goi_y_id])
    _ensure_chua_co(db, [(payload.nhom_nghe_di_lam_id, payload.tieu_chi_goi_y_id)])
    db.add(DmNhomNgheTieuChi(**payload.model_dump()))
    db.commit()
    return _to_public(*_load_or_400(db, payload.nhom_nghe_di_lam_id, payload.tieu_chi_goi_y_id))


@router.put("/{nhom_nghe_di_lam_id}/{tieu_chi_goi_y_id}", response_model=DmNhomNgheTieuChiPublic)
def update_nhom_nghe_tieu_chi(
    nhom_nghe_di_lam_id: int,
    tieu_chi_goi_y_id: int,
    payload: DmNhomNgheTieuChiUpdate,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmNhomNgheTieuChiPublic:
    """Cập nhật điểm phù hợp và ghi chú của một liên kết (không đổi được nhóm nghề/tiêu chí)."""
    item, nhom, tieu_chi = _load_or_400(db, nhom_nghe_di_lam_id, tieu_chi_goi_y_id)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, nhom, tieu_chi)


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_nhom_nghe_tieu_chi_many(
    payload: DmNhomNgheTieuChiDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều liên kết theo danh sách khóa ghép. Cặp không tồn tại thì bỏ qua."""
    cap = list(dict.fromkeys((k.nhom_nghe_di_lam_id, k.tieu_chi_goi_y_id) for k in payload.items))
    items = db.scalars(
        select(DmNhomNgheTieuChi).where(
            tuple_(DmNhomNgheTieuChi.nhom_nghe_di_lam_id, DmNhomNgheTieuChi.tieu_chi_goi_y_id).in_(cap)
        )
    ).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{nhom_nghe_di_lam_id}/{tieu_chi_goi_y_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nhom_nghe_tieu_chi(
    nhom_nghe_di_lam_id: int,
    tieu_chi_goi_y_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một liên kết nhóm nghề - tiêu chí."""
    item, _nhom, _tieu_chi = _load_or_400(db, nhom_nghe_di_lam_id, tieu_chi_goi_y_id)
    db.delete(item)
    db.commit()
