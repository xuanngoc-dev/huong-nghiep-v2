from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_chuong_trinh_dao_tao import (
    DatsChuongTrinhDaoTaoDeleteMany,
    DatsChuongTrinhDaoTaoDeleteManyResult,
    DatsChuongTrinhDaoTaoFields,
    DatsChuongTrinhDaoTaoImportRequest,
    DatsChuongTrinhDaoTaoImportResult,
    DatsChuongTrinhDaoTaoPage,
    DatsChuongTrinhDaoTaoPublic,
    DatsChuongTrinhDaoTaoWrite,
)

router = APIRouter(prefix="/chuong-trinh-dao-tao", tags=["chuong-trinh-dao-tao"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _duration(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _to_public(
    item: DatsChuongTrinhDaoTao,
    de_an: DatsTuyenSinh,
    truong: DmTruong,
    nganh: DmNganhDaoTao | None,
    co_so: DatsTruSo | None,
) -> DatsChuongTrinhDaoTaoPublic:
    """Ghép chương trình với đề án, trường, ngành và cơ sở để trả về cho client."""
    return DatsChuongTrinhDaoTaoPublic(
        id=item.id,
        de_an_id=item.de_an_id,
        ten_de_an=de_an.ten_de_an,
        truong_id=de_an.truong_id,
        ma_truong=truong.ma_truong or "",
        ten_truong=truong.ten_truong,
        nam_tuyen_sinh=de_an.nam_tuyen_sinh,
        nganh_dao_tao_id=item.nganh_dao_tao_id,
        ma_nganh=nganh.ma_nganh if nganh else None,
        ten_nganh=nganh.ten_nganh if nganh else None,
        ma_xet_tuyen=item.ma_xet_tuyen,
        ten_chuong_trinh=item.ten_chuong_trinh,
        trinh_do_dao_tao=item.trinh_do_dao_tao,
        hinh_thuc_dao_tao=item.hinh_thuc_dao_tao,
        co_so_id=item.co_so_id,
        ten_co_so=co_so.ten_co_so if co_so else None,
        thoi_gian_dao_tao_nam=_duration(item.thoi_gian_dao_tao_nam),
        ngon_ngu_dao_tao=item.ngon_ngu_dao_tao,
        chi_tieu_tuyen_sinh=item.chi_tieu_tuyen_sinh,
        kieu_phan_bo_chi_tieu=item.kieu_phan_bo_chi_tieu,
        ghi_chu=item.ghi_chu,
    )


def _joined():
    return (
        select(DatsChuongTrinhDaoTao, DatsTuyenSinh, DmTruong, DmNganhDaoTao, DatsTruSo)
        .join(DatsTuyenSinh, DatsChuongTrinhDaoTao.de_an_id == DatsTuyenSinh.id)
        .join(DmTruong, DatsTuyenSinh.truong_id == DmTruong.id)
        .outerjoin(DmNganhDaoTao, DatsChuongTrinhDaoTao.nganh_dao_tao_id == DmNganhDaoTao.id)
        .outerjoin(DatsTruSo, DatsChuongTrinhDaoTao.co_so_id == DatsTruSo.id)
    )


def _load_row(db: Session, item_id: int):
    """Lấy một chương trình kèm đề án, trường, ngành và cơ sở. Trả lỗi 404 nếu không có."""
    row = db.execute(_joined().where(DatsChuongTrinhDaoTao.id == item_id)).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy chương trình đào tạo")
    return row[0], row[1], row[2], row[3], row[4]


def _ensure_de_an(db: Session, de_an_id: int) -> DatsTuyenSinh:
    de_an = db.get(DatsTuyenSinh, de_an_id)
    if de_an is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đề án tuyển sinh không tồn tại")
    return de_an


def _format_ids(ids: list[int]) -> str:
    shown = [str(item_id) for item_id in ids[:20]]
    extra = len(ids) - len(shown)
    text = ", ".join(shown)
    if extra:
        return f"{text} và {extra} id khác"
    return text


def _ensure_refs(db: Session, de_an_id: int, rows: list[DatsChuongTrinhDaoTaoFields]) -> None:
    """Kiểm tra ngành và cơ sở tồn tại. Cơ sở phải thuộc đúng đề án đã chọn."""
    nganh_ids = list(dict.fromkeys(item.nganh_dao_tao_id for item in rows if item.nganh_dao_tao_id is not None))
    if nganh_ids:
        found = set(db.scalars(select(DmNganhDaoTao.id).where(DmNganhDaoTao.id.in_(nganh_ids))).all())
        missing = [item_id for item_id in nganh_ids if item_id not in found]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ngành đào tạo không tồn tại: {_format_ids(missing)}",
            )

    co_so_ids = list(dict.fromkeys(item.co_so_id for item in rows if item.co_so_id is not None))
    if not co_so_ids:
        return
    campuses = db.scalars(select(DatsTruSo).where(DatsTruSo.id.in_(co_so_ids))).all()
    found_campus = {item.id: item for item in campuses}
    missing = [item_id for item_id in co_so_ids if item_id not in found_campus]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cơ sở không tồn tại: {_format_ids(missing)}",
        )
    wrong = [item_id for item_id, campus in found_campus.items() if campus.de_an_id != de_an_id]
    if wrong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cơ sở không thuộc đề án đã chọn: {_format_ids(wrong)}",
        )


def _apply(item: DatsChuongTrinhDaoTao, de_an_id: int, payload: DatsChuongTrinhDaoTaoFields) -> None:
    """Gán dữ liệu vào bản ghi. de_an_id luôn lấy từ đề án đã chọn, không lấy từ JSON."""
    item.de_an_id = de_an_id
    for key, value in payload.model_dump().items():
        setattr(item, key, value)


@router.get("", response_model=DatsChuongTrinhDaoTaoPage)
def list_chuong_trinh(
    q: str | None = Query(default=None, max_length=255),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    truong_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoPage:
    """Lấy danh sách chương trình có phân trang. Lọc theo từ khóa, trường và năm của đề án."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DatsChuongTrinhDaoTao.ten_chuong_trinh.like(pattern, escape="\\"),
                DatsChuongTrinhDaoTao.ma_xet_tuyen.like(pattern, escape="\\"),
                DatsTuyenSinh.ten_de_an.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                cast(DatsTuyenSinh.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if nam_tuyen_sinh is not None:
        filters.append(DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh)
    if truong_id is not None:
        filters.append(DatsTuyenSinh.truong_id == truong_id)

    joined = (
        DatsChuongTrinhDaoTao.__table__.join(DatsTuyenSinh, DatsChuongTrinhDaoTao.de_an_id == DatsTuyenSinh.id).join(
            DmTruong, DatsTuyenSinh.truong_id == DmTruong.id
        )
    )
    count_stmt = select(func.count()).select_from(joined)
    stmt = _joined()
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            DatsTuyenSinh.nam_tuyen_sinh.desc(),
            DmTruong.ten_truong.asc(),
            DatsChuongTrinhDaoTao.ma_xet_tuyen.asc(),
            DatsChuongTrinhDaoTao.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DatsChuongTrinhDaoTaoPage(
        items=[_to_public(item, de_an, truong, nganh, co_so) for item, de_an, truong, nganh, co_so in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=DatsChuongTrinhDaoTaoPublic)
def get_chuong_trinh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoPublic:
    """Lấy chi tiết một chương trình đào tạo theo id."""
    return _to_public(*_load_row(db, item_id))


@router.post("/import", response_model=DatsChuongTrinhDaoTaoImportResult, status_code=status.HTTP_201_CREATED)
def import_chuong_trinh(
    payload: DatsChuongTrinhDaoTaoImportRequest,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoImportResult:
    """Nhập một mảng chương trình vào đúng đề án đã chọn. id trong JSON không được lưu."""
    _ensure_de_an(db, payload.de_an_id)
    _ensure_refs(db, payload.de_an_id, payload.du_lieu)
    items = []
    for data in payload.du_lieu:
        item = DatsChuongTrinhDaoTao()
        _apply(item, payload.de_an_id, data)
        items.append(item)
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được chương trình đào tạo",
        ) from None
    return DatsChuongTrinhDaoTaoImportResult(created=len(items))


@router.post("", response_model=DatsChuongTrinhDaoTaoPublic, status_code=status.HTTP_201_CREATED)
def create_chuong_trinh(
    payload: DatsChuongTrinhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoPublic:
    """Thêm một chương trình đào tạo vào đề án đã chọn."""
    _ensure_de_an(db, payload.de_an_id)
    _ensure_refs(db, payload.de_an_id, [payload])
    item = DatsChuongTrinhDaoTao()
    _apply(item, payload.de_an_id, payload)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được chương trình đào tạo",
        ) from None
    db.refresh(item)
    return _to_public(*_load_row(db, item.id))


@router.put("/{item_id}", response_model=DatsChuongTrinhDaoTaoPublic)
def update_chuong_trinh(
    item_id: int,
    payload: DatsChuongTrinhDaoTaoWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoPublic:
    """Cập nhật một chương trình đào tạo. Có thể chuyển sang đề án khác."""
    item, _de_an, _truong, _nganh, _co_so = _load_row(db, item_id)
    _ensure_de_an(db, payload.de_an_id)
    _ensure_refs(db, payload.de_an_id, [payload])
    _apply(item, payload.de_an_id, payload)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được chương trình đào tạo",
        ) from None
    return _to_public(*_load_row(db, item_id))


@router.delete("", response_model=DatsChuongTrinhDaoTaoDeleteManyResult)
def delete_chuong_trinh_many(
    payload: DatsChuongTrinhDaoTaoDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsChuongTrinhDaoTaoDeleteManyResult:
    """Xóa nhiều chương trình đào tạo theo danh sách id."""
    items = db.scalars(select(DatsChuongTrinhDaoTao).where(DatsChuongTrinhDaoTao.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy chương trình đào tạo để xóa",
        )
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chương trình đang được sử dụng, không thể xóa",
        ) from None
    return DatsChuongTrinhDaoTaoDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chuong_trinh(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một chương trình đào tạo theo id."""
    item, _de_an, _truong, _nganh, _co_so = _load_row(db, item_id)
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chương trình đang được sử dụng, không thể xóa",
        ) from None
