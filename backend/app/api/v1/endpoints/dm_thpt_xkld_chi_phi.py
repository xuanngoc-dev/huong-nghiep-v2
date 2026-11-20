from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.dm_thpt_xkld import DmThptXkldChiPhi, DmThptXkldNhomNghe, DmThptXkldThiTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dm_thpt_xkld import (
    DmThptXkldChiPhiPage,
    DmThptXkldChiPhiPublic,
    DmThptXkldChiPhiWrite,
    DmThptXkldDeleteMany,
    KetQuaThemNhieu,
    KetQuaXoaNhieu,
    LoaiChiPhiXkld,
)
from app.services.thpt_xkld import (
    danh_sach_con,
    kiem_tra_lien_ket,
    lay_lien_ket,
    loc_lien_ket,
    thong_tin_lien_ket,
)

router = APIRouter(prefix="/danh-muc/thpt-xkld/chi-phi", tags=["danh-muc"])


def _get_or_400(db: Session, item_id: int) -> DmThptXkldChiPhi:
    """Lấy một khoản chi phí XKLĐ theo id. Trả lỗi 400 kèm thông báo nếu không tồn tại."""
    item = db.get(DmThptXkldChiPhi, item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy khoản chi phí XKLĐ có id = {item_id}",
        )
    return item


def _to_public(item: DmThptXkldChiPhi, lien_ket: dict) -> DmThptXkldChiPhiPublic:
    """Ghép bản ghi với mã, tên nhóm nghề và thị trường."""
    return DmThptXkldChiPhiPublic(
        id=item.id,
        thpt_xkld_nhom_nghe_id=item.thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id=item.thpt_xkld_thi_truong_id,
        loai_chi_phi=item.loai_chi_phi,
        ten_khoan_chi=item.ten_khoan_chi,
        chi_phi_min=item.chi_phi_min,
        chi_phi_max=item.chi_phi_max,
        don_vi_tien=item.don_vi_tien,
        chi_phi_quy_doi_vnd_text=item.chi_phi_quy_doi_vnd_text,
        ghi_chu=item.ghi_chu,
        **lien_ket,
    )


@router.get("", response_model=DmThptXkldChiPhiPage)
def list_thpt_xkld_chi_phi(
    q: str | None = Query(default=None, max_length=255),
    thpt_xkld_nhom_nghe_id: int | None = Query(default=None, ge=1),
    thpt_xkld_thi_truong_id: int | None = Query(default=None, ge=1),
    loai_chi_phi: LoaiChiPhiXkld | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
) -> DmThptXkldChiPhiPage:
    """Lấy danh sách khoản chi phí XKLĐ có phân trang và bộ lọc, không cần đăng nhập."""
    filters = loc_lien_ket(
        DmThptXkldChiPhi,
        [DmThptXkldChiPhi.ten_khoan_chi],
        q,
        thpt_xkld_nhom_nghe_id,
        thpt_xkld_thi_truong_id,
    )
    if loai_chi_phi:
        filters.append(DmThptXkldChiPhi.loai_chi_phi == loai_chi_phi)
    rows, total = danh_sach_con(
        db,
        DmThptXkldChiPhi,
        filters,
        [
            DmThptXkldChiPhi.thpt_xkld_nhom_nghe_id.asc(),
            # Dòng chung của nhóm nghề (không gắn thị trường) xếp trước.
            DmThptXkldThiTruong.thu_tu_hien_thi.is_(None).desc(),
            DmThptXkldThiTruong.thu_tu_hien_thi.asc(),
            DmThptXkldChiPhi.loai_chi_phi.asc(),
            DmThptXkldChiPhi.id.asc(),
        ],
        page,
        page_size,
    )
    return DmThptXkldChiPhiPage(
        items=[_to_public(item, thong_tin_lien_ket(nhom, tt)) for item, nhom, tt in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DmThptXkldChiPhiPublic)
def get_thpt_xkld_chi_phi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DmThptXkldChiPhiPublic:
    """Lấy chi tiết một khoản chi phí XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    return _to_public(item, lay_lien_ket(db, item))


@router.post("/bulk", response_model=KetQuaThemNhieu, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_chi_phi_bulk(
    payload: list[DmThptXkldChiPhiWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaThemNhieu:
    """Thêm nhiều khoản chi phí XKLĐ cùng lúc.

    Từ chối nếu nhóm nghề/thị trường không tồn tại hoặc thị trường không thuộc nhóm nghề.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách khoản chi phí XKLĐ trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 bản ghi mỗi lần")
    kiem_tra_lien_ket(db, [(item.thpt_xkld_nhom_nghe_id, item.thpt_xkld_thi_truong_id) for item in payload])
    items = [DmThptXkldChiPhi(**item.model_dump()) for item in payload]
    db.add_all(items)
    db.commit()
    return KetQuaThemNhieu(created=len(items))


@router.post("", response_model=DmThptXkldChiPhiPublic, status_code=status.HTTP_201_CREATED)
def create_thpt_xkld_chi_phi(
    payload: DmThptXkldChiPhiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldChiPhiPublic:
    """Thêm một khoản chi phí XKLĐ."""
    nhom, tt = _lien_ket_mot(db, payload)
    item = DmThptXkldChiPhi(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.put("/{item_id}", response_model=DmThptXkldChiPhiPublic)
def update_thpt_xkld_chi_phi(
    item_id: int,
    payload: DmThptXkldChiPhiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> DmThptXkldChiPhiPublic:
    """Cập nhật toàn bộ thông tin một khoản chi phí XKLĐ theo id."""
    item = _get_or_400(db, item_id)
    nhom, tt = _lien_ket_mot(db, payload)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return _to_public(item, thong_tin_lien_ket(nhom, tt))


@router.delete("", response_model=KetQuaXoaNhieu)
def delete_thpt_xkld_chi_phi_many(
    payload: DmThptXkldDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> KetQuaXoaNhieu:
    """Xóa nhiều khoản chi phí XKLĐ theo danh sách id. Id không tồn tại thì bỏ qua."""
    items = db.scalars(select(DmThptXkldChiPhi).where(DmThptXkldChiPhi.id.in_(payload.ids))).all()
    for item in items:
        db.delete(item)
    db.commit()
    return KetQuaXoaNhieu(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thpt_xkld_chi_phi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_admin_user),
) -> None:
    """Xóa một khoản chi phí XKLĐ theo id."""
    db.delete(_get_or_400(db, item_id))
    db.commit()


def _lien_ket_mot(
    db: Session, payload: DmThptXkldChiPhiWrite
) -> tuple[DmThptXkldNhomNghe, DmThptXkldThiTruong | None]:
    """Kiểm tra liên kết của một bản ghi; trả về nhóm nghề và thị trường (nếu có)."""
    nhom_id, tt_id = payload.thpt_xkld_nhom_nghe_id, payload.thpt_xkld_thi_truong_id
    nhom_nghe, thi_truong = kiem_tra_lien_ket(db, [(nhom_id, tt_id)])
    return nhom_nghe[nhom_id], thi_truong.get(tt_id) if tt_id else None
