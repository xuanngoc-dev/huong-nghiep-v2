from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import String, and_, case, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_tinh_thanh import DmTinhThanh
from app.models.dm_truong import DmTruong
from app.models.nguoi_dung import NguoiDung
from app.schemas.dats_tuyen_sinh import (
    DatsImportRequest,
    DatsImportResult,
    DatsTuyenSinhBulkResult,
    DatsTuyenSinhChiTiet,
    DatsTuyenSinhDeleteMany,
    DatsTuyenSinhDeleteManyResult,
    DatsTuyenSinhPage,
    DatsTuyenSinhPublic,
    DatsTuyenSinhWrite,
    TruongDaoTaoPage,
    TruongDaoTaoPublic,
)
from app.services.dats_detail import load_de_an_bang
from app.services.dats_import import DatsImportError, delete_de_an_children, import_document

router = APIRouter(prefix="/de-an-tuyen-sinh", tags=["de-an-tuyen-sinh"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _to_public(item: DatsTuyenSinh, truong: DmTruong) -> DatsTuyenSinhPublic:
    """Ghép đề án với mã và tên trường để trả về cho client."""
    return DatsTuyenSinhPublic(
        id=item.id,
        truong_id=truong.id,
        ma_truong=item.ma_truong,
        ten_truong=truong.ten_truong,
        nam_tuyen_sinh=item.nam_tuyen_sinh,
        chi_tieu=item.chi_tieu,
        ten_de_an=item.ten_de_an,
        hinh_thuc_dao_tao=item.hinh_thuc_dao_tao if isinstance(item.hinh_thuc_dao_tao, list) else None,
        gioi_thieu=item.gioi_thieu,
        ngay_cong_bo=item.ngay_cong_bo,
        nguon_du_lieu_url=item.nguon_du_lieu_url,
        trang_thai=item.trang_thai,
        ghi_chu=item.ghi_chu,
        tao_luc=item.tao_luc,
        cap_nhat_luc=item.cap_nhat_luc,
    )


def _ensure_truong(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã trường trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(code.strip() for code in codes if code and code.strip()))
    found = set(db.scalars(select(DmTruong.ma_truong).where(DmTruong.ma_truong.in_(unique))).all())
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trường học không tồn tại: {', '.join(missing)}",
        )


def _truong_by_code(db: Session, ma_truong: str) -> DmTruong:
    truong = db.scalar(select(DmTruong).where(DmTruong.ma_truong == ma_truong))
    if truong is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Trường học không tồn tại")
    return truong


def _apply(item: DatsTuyenSinh, payload: DatsTuyenSinhWrite, *, creating: bool) -> None:
    """Gán dữ liệu form vào bản ghi và cập nhật mốc thời gian."""
    now = datetime.now()
    for key, value in payload.model_dump().items():
        setattr(item, key, value)
    if creating:
        item.tao_luc = now
    item.cap_nhat_luc = now


def _load_pair(db: Session, item_id: int) -> tuple[DatsTuyenSinh, DmTruong]:
    """Lấy một đề án kèm trường. Trả lỗi 404 nếu đề án không tồn tại."""
    row = db.execute(
        select(DatsTuyenSinh, DmTruong)
        .join(DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong)
        .where(DatsTuyenSinh.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đề án tuyển sinh")
    return row[0], row[1]


@router.get("", response_model=DatsTuyenSinhPage)
def list_de_an(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: str | None = Query(default=None, max_length=20),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    ma_truong: str | None = Query(default=None, max_length=20),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPage:
    """Lấy danh sách đề án tuyển sinh có phân trang. Lọc theo từ khóa, trường, năm và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DatsTuyenSinh.ten_de_an.like(pattern, escape="\\"),
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                cast(DatsTuyenSinh.nam_tuyen_sinh, String).like(pattern, escape="\\"),
            )
        )
    if trang_thai and trang_thai.strip():
        filters.append(DatsTuyenSinh.trang_thai == trang_thai.strip())
    if nam_tuyen_sinh is not None:
        filters.append(DatsTuyenSinh.nam_tuyen_sinh == nam_tuyen_sinh)
    if ma_truong and ma_truong.strip():
        filters.append(DatsTuyenSinh.ma_truong == ma_truong.strip())

    joined = DatsTuyenSinh.__table__.join(DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong)
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(DatsTuyenSinh, DmTruong).join(DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong)
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(
            DatsTuyenSinh.nam_tuyen_sinh.desc(),
            DmTruong.ten_truong.asc(),
            DatsTuyenSinh.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return DatsTuyenSinhPage(
        items=[_to_public(item, truong) for item, truong in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/truong-dao-tao", response_model=TruongDaoTaoPage)
def list_truong_dao_tao(
    ma_nganh: str = Query(..., min_length=1, max_length=20),
    q: str | None = Query(default=None, max_length=255),
    vung_mien: str | None = Query(default=None, max_length=20),
    loai_co_so: str | None = Query(default=None, max_length=50),
    ten_tinh_thanh: str | None = Query(default=None, max_length=100),
    nam_tuyen_sinh: int | None = Query(default=None, ge=1990, le=2100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TruongDaoTaoPage:
    """Liệt kê trường có chương trình của ngành trong một năm tuyển sinh. Không cần đăng nhập."""
    year = nam_tuyen_sinh if nam_tuyen_sinh is not None else datetime.now().year
    code = ma_nganh.strip()
    major = db.scalar(select(DmNganhDaoTao).where(DmNganhDaoTao.ma_nganh == code))
    if major is None:
        return TruongDaoTaoPage(items=[], total=0, page=page, page_size=page_size)
    filters = [
        DatsTuyenSinh.nam_tuyen_sinh == year,
        or_(
            DatsChuongTrinhDaoTao.nganh_dao_tao_id == major.id,
            DatsChuongTrinhDaoTao.ten_chuong_trinh == major.ten_nganh,
            DatsChuongTrinhDaoTao.id.in_(
                select(DatsTrinhDoNganh.de_an_chuong_trinh_id).where(DatsTrinhDoNganh.ma_nganh_chuan == code)
            ),
        ),
    ]
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                DmTruong.ten_truong.like(pattern, escape="\\"),
                DmTruong.ma_truong.like(pattern, escape="\\"),
                DmTruong.ten_viet_tat.like(pattern, escape="\\"),
                DmTruong.ten_tieng_anh.like(pattern, escape="\\"),
            )
        )
    khu_vuc_hien_thi = func.coalesce(func.nullif(DmTruong.vung_mien, ""), DmTinhThanh.khu_vuc)
    loai_hien_thi = case(
        (and_(DmTruong.loai_co_so.isnot(None), DmTruong.loai_co_so != ""), DmTruong.loai_co_so),
        (DmTruong.ten_truong.like("%Học viện%"), "Học viện"),
        (DmTruong.ten_truong.like("%Cao đẳng%"), "Cao đẳng"),
        (DmTruong.ten_truong.like("%Đại học%"), "Đại học"),
        else_=None,
    )
    if vung_mien and vung_mien.strip():
        filters.append(khu_vuc_hien_thi == vung_mien.strip())
    if loai_co_so and loai_co_so.strip():
        filters.append(loai_hien_thi == loai_co_so.strip())
    if ten_tinh_thanh and ten_tinh_thanh.strip():
        filters.append(DmTruong.ten_tinh_thanh == ten_tinh_thanh.strip())

    joined = (
        DatsChuongTrinhDaoTao.__table__.join(DatsTuyenSinh, DatsChuongTrinhDaoTao.de_an_id == DatsTuyenSinh.id)
        .join(DmTruong, DatsTuyenSinh.ma_truong == DmTruong.ma_truong)
        .outerjoin(
            DmTinhThanh,
            or_(
                and_(
                    DmTruong.ma_tinh_thanh.isnot(None),
                    DmTruong.ma_tinh_thanh != "",
                    DmTruong.ma_tinh_thanh == DmTinhThanh.ma_tinh,
                ),
                and_(
                    or_(DmTruong.ma_tinh_thanh.is_(None), DmTruong.ma_tinh_thanh == ""),
                    DmTruong.ten_tinh_thanh == DmTinhThanh.ten_tinh,
                ),
            ),
        )
    )
    school_columns = (
        DmTruong.ma_truong,
        DmTruong.ten_truong,
        DmTruong.ten_viet_tat,
        DmTruong.ten_tieng_anh,
        DmTruong.loai_hinh,
        DmTruong.ten_tinh_thanh,
        DmTruong.dia_chi_tru_so,
        DmTruong.website,
        DmTruong.website_tuyen_sinh,
        DmTruong.anh_dai_dien_url,
    )
    total = db.scalar(
        select(func.count(func.distinct(DmTruong.ma_truong))).select_from(joined).where(*filters)
    ) or 0
    rows = db.execute(
        select(
            *school_columns,
            func.max(loai_hien_thi),
            func.max(khu_vuc_hien_thi),
            func.count(func.distinct(DatsChuongTrinhDaoTao.id)),
            func.sum(DatsChuongTrinhDaoTao.chi_tieu_tuyen_sinh),
        )
        .select_from(joined)
        .where(*filters)
        .group_by(*school_columns)
        .order_by(DmTruong.ten_truong.asc(), DmTruong.ma_truong.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = []
    for row in rows:
        quota = row[13]
        items.append(
            TruongDaoTaoPublic(
                ma_truong=row[0],
                ten_truong=row[1],
                ten_viet_tat=row[2],
                ten_tieng_anh=row[3],
                loai_hinh=row[4],
                ten_tinh_thanh=row[5],
                dia_chi_tru_so=row[6],
                website=row[7],
                website_tuyen_sinh=row[8],
                anh_dai_dien_url=row[9],
                loai_co_so=row[10],
                vung_mien=row[11],
                nam_tuyen_sinh=year,
                so_chuong_trinh=int(row[12] or 0),
                chi_tieu=int(quota) if quota is not None else None,
            )
        )
    return TruongDaoTaoPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/{item_id}/chi-tiet", response_model=DatsTuyenSinhChiTiet)
def get_de_an_chi_tiet(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhChiTiet:
    """Lấy đề án và mọi bảng dats_ liên quan để xem chi tiết."""
    item, truong = _load_pair(db, item_id)
    return DatsTuyenSinhChiTiet(de_an=_to_public(item, truong), bang=load_de_an_bang(db, item.id))


@router.get("/{item_id}", response_model=DatsTuyenSinhPublic)
def get_de_an(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Lấy chi tiết một đề án tuyển sinh theo id, kèm tên trường."""
    item, truong = _load_pair(db, item_id)
    return _to_public(item, truong)


@router.post("/bulk", response_model=DatsTuyenSinhBulkResult, status_code=status.HTTP_201_CREATED)
def create_de_an_bulk(
    payload: list[DatsTuyenSinhWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhBulkResult:
    """Thêm nhiều đề án cùng lúc. Từ chối nếu trường học không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách đề án tuyển sinh trống")
    if len(payload) > 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ thêm tối đa 500 đề án tuyển sinh mỗi lần",
        )

    _ensure_truong(db, [item.ma_truong for item in payload])
    items = []
    for data in payload:
        item = DatsTuyenSinh()
        _apply(item, data, creating=True)
        items.append(item)
    db.add_all(items)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    return DatsTuyenSinhBulkResult(created=len(items))


@router.post("/import", response_model=DatsImportResult, status_code=status.HTTP_201_CREATED)
def import_de_an(
    payload: DatsImportRequest,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsImportResult:
    """Nhập một đề án và các bảng dats_ lồng trong JSON, trong một transaction."""
    try:
        de_an_id, counts = import_document(db, payload.ma_truong, payload.nam_tuyen_sinh, payload.du_lieu)
        db.commit()
    except DatsImportError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from None
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được dữ liệu đề án",
        ) from None
    return DatsImportResult(de_an_id=de_an_id, counts=counts)


@router.post("", response_model=DatsTuyenSinhPublic, status_code=status.HTTP_201_CREATED)
def create_de_an(
    payload: DatsTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Thêm một đề án tuyển sinh. Từ chối nếu trường học không tồn tại."""
    _ensure_truong(db, [payload.ma_truong])
    item = DatsTuyenSinh()
    _apply(item, payload, creating=True)
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    db.refresh(item)
    truong = _truong_by_code(db, item.ma_truong)
    return _to_public(item, truong)


@router.put("/{item_id}", response_model=DatsTuyenSinhPublic)
def update_de_an(
    item_id: int,
    payload: DatsTuyenSinhWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhPublic:
    """Cập nhật toàn bộ thông tin một đề án tuyển sinh theo id."""
    item, _truong = _load_pair(db, item_id)
    _ensure_truong(db, [payload.ma_truong])
    _apply(item, payload, creating=False)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không lưu được đề án tuyển sinh",
        ) from None
    db.refresh(item)
    truong = _truong_by_code(db, item.ma_truong)
    return _to_public(item, truong)


@router.delete("", response_model=DatsTuyenSinhDeleteManyResult)
def delete_de_an_many(
    payload: DatsTuyenSinhDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> DatsTuyenSinhDeleteManyResult:
    """Xóa nhiều đề án tuyển sinh theo danh sách id."""
    items = db.scalars(select(DatsTuyenSinh).where(DatsTuyenSinh.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy đề án tuyển sinh để xóa",
        )
    delete_de_an_children(db, [item.id for item in items])
    for item in items:
        db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đề án đang được sử dụng, không thể xóa",
        ) from None
    return DatsTuyenSinhDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_de_an(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một đề án tuyển sinh theo id."""
    item, _truong = _load_pair(db, item_id)
    delete_de_an_children(db, [item.id])
    db.delete(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Đề án đang được sử dụng, không thể xóa",
        ) from None
