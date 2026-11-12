from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.dm_nganh_hoc_theo_truong import DmNganhHocTheoTruong
from app.models.dm_truong import DmTruong
from app.schemas.dats_tuyen_sinh import TruongDaoTaoPage
from app.schemas.dm_nganh_hoc_theo_truong import (
    DmNganhHocTheoTruongDeleteMany,
    DmNganhHocTheoTruongDeleteManyResult,
    DmNganhHocTheoTruongPage,
    DmNganhHocTheoTruongPublic,
    DmNganhHocTheoTruongWrite,
    DmNganhTheoTruongImport,
    DmNganhTheoTruongImportChuongTrinh,
    DmNganhTheoTruongImportResult,
    DmNganhTheoTruongKiemTra,
    DmNganhTheoTruongKiemTraResult,
)
from app.services.tim_truong import truong_theo_nganh

router = APIRouter(
    prefix="/danh-muc/nganh-hoc-theo-truong",
    tags=["danh-muc"],
    dependencies=[Depends(get_admin_user)],
)

# Tra cứu công khai, không cần đăng nhập. Phải include trước `router` để không bị `/{item_id}` bắt mất.
public_router = APIRouter(prefix="/danh-muc/nganh-hoc-theo-truong", tags=["danh-muc"])

_LOI_LUU = "Không lưu được ngành đào tạo, hãy kiểm tra lại mã trường"
_IMPORT_TOI_DA = 100


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _to_public(item: DmNganhHocTheoTruong, ten_truong: str | None) -> DmNganhHocTheoTruongPublic:
    data = DmNganhHocTheoTruongPublic.model_validate(item)
    data.ten_truong = ten_truong
    return data


def _ten_truong(db: Session, ma_truong: str) -> str | None:
    return db.scalar(select(DmTruong.ten_truong).where(DmTruong.ma_truong == ma_truong))


def _get_or_404(db: Session, item_id: int) -> DmNganhHocTheoTruong:
    """Lấy một bản ghi theo id. Trả lỗi 404 nếu không tồn tại."""
    item = db.get(DmNganhHocTheoTruong, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ngành đào tạo")
    return item


def _ensure_truong(db: Session, ma_truong: str) -> str:
    """Kiểm tra mã trường có trong dm_truong, trả về tên trường."""
    ten = _ten_truong(db, ma_truong)
    if ten is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trường học không tồn tại")
    return ten


@router.get("", response_model=DmNganhHocTheoTruongPage)
def list_nganh_hoc_theo_truong(
    q: str | None = Query(default=None, max_length=255),
    ma_truong: str | None = Query(default=None, max_length=20),
    nam_hoc: int | None = Query(default=None, ge=2000, le=2100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> DmNganhHocTheoTruongPage:
    """Lấy danh sách ngành đào tạo theo trường có phân trang.

    Lọc theo từ khóa (mã ngành, mã xét tuyển, tên ngành, tên chương trình), mã trường và năm học.
    """
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmNganhHocTheoTruong.ma_nganh.like(pattern, escape="\\"),
                DmNganhHocTheoTruong.ma_xet_tuyen.like(pattern, escape="\\"),
                DmNganhHocTheoTruong.ten_nganh.like(pattern, escape="\\"),
                DmNganhHocTheoTruong.ten_chuong_trinh.like(pattern, escape="\\"),
            )
        )
    if ma_truong and ma_truong.strip():
        filters.append(DmNganhHocTheoTruong.ma_truong == ma_truong.strip().upper())
    if nam_hoc is not None:
        filters.append(DmNganhHocTheoTruong.nam_hoc == nam_hoc)

    count_stmt = select(func.count()).select_from(DmNganhHocTheoTruong)
    stmt = select(DmNganhHocTheoTruong, DmTruong.ten_truong).outerjoin(
        DmTruong, DmTruong.ma_truong == DmNganhHocTheoTruong.ma_truong
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            DmNganhHocTheoTruong.nam_hoc.desc(),
            DmNganhHocTheoTruong.ma_truong.asc(),
            DmNganhHocTheoTruong.ma_xet_tuyen.asc(),
            DmNganhHocTheoTruong.id.asc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DmNganhHocTheoTruongPage(
        items=[_to_public(item, ten) for item, ten in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/nam-hoc", response_model=list[int])
def list_nam_hoc(db: Session = Depends(get_db)) -> list[int]:
    """Các năm học đang có dữ liệu, mới nhất trước, dùng cho bộ lọc."""
    return list(
        db.scalars(
            select(DmNganhHocTheoTruong.nam_hoc)
            .distinct()
            .order_by(DmNganhHocTheoTruong.nam_hoc.desc())
        ).all()
    )


def _khoa_noi_dung(ct: DmNganhTheoTruongImportChuongTrinh | DmNganhHocTheoTruong) -> tuple:
    """Khóa theo toàn bộ thông tin ngành, dùng để nhận diện khi một mã xét tuyển có nhiều ngành."""
    return (
        (ct.ma_nganh or "").upper(),
        (ct.ten_nganh or "").lower(),
        (ct.ten_chuong_trinh or "").lower(),
    )


@router.post("/bulk/kiem-tra", response_model=DmNganhTheoTruongKiemTraResult)
def kiem_tra_truong_import(
    payload: DmNganhTheoTruongKiemTra,
    db: Session = Depends(get_db),
) -> DmNganhTheoTruongKiemTraResult:
    """Trả về các mã trường chưa có trong dm_truong, để kiểm tra trước khi import theo lô."""
    ma_truongs = {ma.strip().upper() for ma in payload.ma_truong if ma and ma.strip()}
    found = {ma.upper() for ma in db.scalars(select(DmTruong.ma_truong).where(DmTruong.ma_truong.in_(ma_truongs)))}
    return DmNganhTheoTruongKiemTraResult(thieu=sorted(ma_truongs - found))


@router.post("/bulk", response_model=DmNganhTheoTruongImportResult)
def import_nganh_hoc_theo_truong(
    payload: list[DmNganhTheoTruongImport],
    db: Session = Depends(get_db),
) -> DmNganhTheoTruongImportResult:
    """Import ngành theo trường từ JSON.

    Mỗi phần tử là một trường kèm năm tuyển sinh và danh sách chương trình đào tạo.
    Mã ngành, mã xét tuyển, tên ngành... được phép để trống; chương trình không có thông tin nào bị bỏ qua.
    Một mã xét tuyển được phép có nhiều ngành. Ngành đã có được cập nhật, chưa có thì thêm mới.
    Cả lô bị từ chối nếu có mã trường không tồn tại.
    """
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách trường trống")
    if len(payload) > _IMPORT_TOI_DA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chỉ import tối đa {_IMPORT_TOI_DA} trường mỗi lần",
        )

    ma_truongs = {truong.ma_truong for truong in payload}
    found = {ma.upper() for ma in db.scalars(select(DmTruong.ma_truong).where(DmTruong.ma_truong.in_(ma_truongs)))}
    missing = sorted(ma_truongs - found)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã trường không tồn tại: {', '.join(missing)}",
        )

    # Gom theo (trường, năm, mã xét tuyển); dòng giống hệt nhau trong file chỉ giữ một.
    nhom_file: dict[tuple, dict[tuple, DmNganhTheoTruongImportChuongTrinh]] = {}
    bo_qua = 0
    for truong in payload:
        for ct in truong.chuong_trinh_dao_tao:
            if ct.is_empty():
                bo_qua += 1
                continue
            nhom = (truong.ma_truong, truong.nam_tuyen_sinh, ct.ma_xet_tuyen or None)
            nhom_file.setdefault(nhom, {})[_khoa_noi_dung(ct)] = ct

    nhom_db: dict[tuple, list[DmNganhHocTheoTruong]] = {}
    for item in db.scalars(
        select(DmNganhHocTheoTruong).where(
            DmNganhHocTheoTruong.ma_truong.in_(ma_truongs),
            DmNganhHocTheoTruong.nam_hoc.in_({truong.nam_tuyen_sinh for truong in payload}),
        )
    ):
        nhom = (item.ma_truong.upper(), item.nam_hoc, (item.ma_xet_tuyen or "").upper() or None)
        nhom_db.setdefault(nhom, []).append(item)

    them_moi = cap_nhat = 0

    def cap_nhat_item(item: DmNganhHocTheoTruong, ct: DmNganhTheoTruongImportChuongTrinh) -> None:
        values = ct.model_dump()
        # Ghi chú trong file để trống thì giữ ghi chú đang có.
        if values["ghi_chu"] is None:
            values.pop("ghi_chu")
        for field, value in values.items():
            setattr(item, field, value)

    for (ma_truong, nam_hoc, ma_xet_tuyen), cac_nganh in nhom_file.items():
        da_co = nhom_db.get((ma_truong, nam_hoc, ma_xet_tuyen), [])
        # Mã xét tuyển chỉ có một ngành ở cả file và hệ thống: cập nhật thẳng ngành đó.
        if ma_xet_tuyen and len(cac_nganh) == 1 and len(da_co) == 1:
            cap_nhat_item(da_co[0], next(iter(cac_nganh.values())))
            cap_nhat += 1
            continue
        # Còn lại (mã có nhiều ngành, hoặc không có mã): khớp theo toàn bộ thông tin ngành.
        theo_noi_dung = {_khoa_noi_dung(item): item for item in da_co}
        for khoa, ct in cac_nganh.items():
            item = theo_noi_dung.get(khoa)
            if item is None:
                db.add(DmNganhHocTheoTruong(ma_truong=ma_truong, nam_hoc=nam_hoc, **ct.model_dump()))
                them_moi += 1
            else:
                cap_nhat_item(item, ct)
                cap_nhat += 1

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_LOI_LUU) from None
    return DmNganhTheoTruongImportResult(
        created=len(payload),
        them_moi=them_moi,
        cap_nhat=cap_nhat,
        bo_qua=bo_qua,
    )


@router.get("/{item_id}", response_model=DmNganhHocTheoTruongPublic)
def get_nganh_hoc_theo_truong(item_id: int, db: Session = Depends(get_db)) -> DmNganhHocTheoTruongPublic:
    """Lấy chi tiết một ngành đào tạo theo id."""
    item = _get_or_404(db, item_id)
    return _to_public(item, _ten_truong(db, item.ma_truong))


@router.post("", response_model=DmNganhHocTheoTruongPublic, status_code=status.HTTP_201_CREATED)
def create_nganh_hoc_theo_truong(
    payload: DmNganhHocTheoTruongWrite,
    db: Session = Depends(get_db),
) -> DmNganhHocTheoTruongPublic:
    """Thêm một ngành đào tạo cho trường. Từ chối nếu trùng mã xét tuyển ở cùng trường và năm học."""
    ten_truong = _ensure_truong(db, payload.ma_truong)
    item = DmNganhHocTheoTruong(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_LOI_LUU) from None
    db.refresh(item)
    return _to_public(item, ten_truong)


@router.put("/{item_id}", response_model=DmNganhHocTheoTruongPublic)
def update_nganh_hoc_theo_truong(
    item_id: int,
    payload: DmNganhHocTheoTruongWrite,
    db: Session = Depends(get_db),
) -> DmNganhHocTheoTruongPublic:
    """Cập nhật toàn bộ thông tin một ngành đào tạo theo id."""
    item = _get_or_404(db, item_id)
    ten_truong = _ensure_truong(db, payload.ma_truong)
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_LOI_LUU) from None
    db.refresh(item)
    return _to_public(item, ten_truong)


@router.delete("", response_model=DmNganhHocTheoTruongDeleteManyResult)
def delete_nganh_hoc_theo_truong_many(
    payload: DmNganhHocTheoTruongDeleteMany,
    db: Session = Depends(get_db),
) -> DmNganhHocTheoTruongDeleteManyResult:
    """Xóa nhiều ngành đào tạo theo danh sách id."""
    items = db.scalars(select(DmNganhHocTheoTruong).where(DmNganhHocTheoTruong.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy ngành đào tạo để xóa")
    for item in items:
        db.delete(item)
    db.commit()
    return DmNganhHocTheoTruongDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nganh_hoc_theo_truong(item_id: int, db: Session = Depends(get_db)) -> None:
    """Xóa một ngành đào tạo theo id."""
    item = _get_or_404(db, item_id)
    db.delete(item)
    db.commit()


@public_router.get("/truong-dao-tao", response_model=TruongDaoTaoPage)
def list_truong_theo_nganh(
    ma_nganh: str = Query(..., min_length=1, max_length=20),
    q: str | None = Query(default=None, max_length=255),
    vung_mien: str | None = Query(default=None, max_length=20),
    loai_co_so: str | None = Query(default=None, max_length=50),
    ten_tinh_thanh: str | None = Query(default=None, max_length=100),
    nam_tuyen_sinh: int | None = Query(default=None, ge=2000, le=2100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TruongDaoTaoPage:
    """Liệt kê trường đào tạo một ngành trong năm học, dựa trên dm_nganh_hoc_theo_truong.

    Lấy các mã trường có mã ngành này, rồi ghép thông tin trường từ dm_truong.
    """
    return truong_theo_nganh(
        db,
        ma_nganh=ma_nganh,
        nam_tuyen_sinh=nam_tuyen_sinh,
        q=q,
        vung_mien=vung_mien,
        loai_co_so=loai_co_so,
        ten_tinh_thanh=ten_tinh_thanh,
        page=page,
        page_size=page_size,
        ket_hop_phuong_thuc=False,
    )
