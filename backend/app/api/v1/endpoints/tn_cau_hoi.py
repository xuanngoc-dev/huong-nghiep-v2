from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.dm_loai_cau_hoi import DmLoaiCauHoi
from app.models.dm_nhom_tinh_cach_holland import DmNhomTinhCachHolland
from app.models.nguoi_dung import NguoiDung
from app.models.tn_cau_hoi_trac_nghiem import TnCauHoiTracNghiem
from app.models.tn_cau_tra_loi import TnCauTraLoi
from app.schemas.tn_cau_hoi_trac_nghiem import (
    TnCauHoiTracNghiemBulkResult,
    TnCauHoiTracNghiemDeleteMany,
    TnCauHoiTracNghiemDeleteManyResult,
    TnCauHoiTracNghiemPage,
    TnCauHoiTracNghiemPublic,
    TnCauHoiTracNghiemWrite,
    TnCauTraLoiPublic,
    TnCauTraLoiWrite,
)

router = APIRouter(prefix="/trac-nghiem/cau-hoi", tags=["trac-nghiem"])


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _ensure_holland(db: Session, codes: list[str]) -> None:
    """Kiểm tra mọi mã Holland đều có trong danh mục nhóm tính cách Holland."""
    unique = list(dict.fromkeys(codes))
    found = set(
        db.scalars(select(DmNhomTinhCachHolland.ma_nhom).where(DmNhomTinhCachHolland.ma_nhom.in_(unique))).all()
    )
    missing = [code for code in unique if code not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mã Holland không tồn tại: {', '.join(missing)}",
        )


def _ensure_loai(db: Session, ids: list[int]) -> None:
    """Kiểm tra mọi loại câu hỏi trong danh sách đều tồn tại."""
    unique = list(dict.fromkeys(ids))
    found = set(db.scalars(select(DmLoaiCauHoi.id).where(DmLoaiCauHoi.id.in_(unique))).all())
    missing = [str(item_id) for item_id in unique if item_id not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Loại câu hỏi không tồn tại: {', '.join(missing)}",
        )


def _answers_of(db: Session, question_ids: list[int]) -> dict[int, list[TnCauTraLoi]]:
    """Lấy đáp án của các câu hỏi, nhóm theo câu hỏi và sắp theo id."""
    grouped: dict[int, list[TnCauTraLoi]] = defaultdict(list)
    if not question_ids:
        return grouped
    rows = db.scalars(
        select(TnCauTraLoi)
        .where(TnCauTraLoi.cau_hoi_id.in_(question_ids))
        .order_by(TnCauTraLoi.id.asc())
    ).all()
    for row in rows:
        grouped[row.cau_hoi_id].append(row)
    return grouped


def _to_answer(item: TnCauTraLoi) -> TnCauTraLoiPublic:
    """Chuyển một đáp án sang dữ liệu trả về cho client."""
    return TnCauTraLoiPublic.model_validate(item)


def _to_public(
    item: TnCauHoiTracNghiem,
    loai: DmLoaiCauHoi,
    answers: list[TnCauTraLoi],
) -> TnCauHoiTracNghiemPublic:
    """Ghép câu hỏi với tên loại câu hỏi và danh sách đáp án."""
    return TnCauHoiTracNghiemPublic(
        id=item.id,
        ma_holand=item.ma_holand,
        loai_cau_hoi_id=item.loai_cau_hoi_id,
        ten_loai_cau_hoi=loai.ten_loai_cau_hoi,
        noi_dung_cau_hoi=item.noi_dung_cau_hoi,
        ghi_chu=item.ghi_chu,
        trang_thai=item.trang_thai,
        cau_tra_loi=[_to_answer(answer) for answer in answers],
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _load_pair(db: Session, item_id: int) -> tuple[TnCauHoiTracNghiem, DmLoaiCauHoi]:
    """Lấy một câu hỏi kèm loại câu hỏi. Trả lỗi 404 nếu câu hỏi không tồn tại."""
    row = db.execute(
        select(TnCauHoiTracNghiem, DmLoaiCauHoi)
        .join(DmLoaiCauHoi, TnCauHoiTracNghiem.loai_cau_hoi_id == DmLoaiCauHoi.id)
        .where(TnCauHoiTracNghiem.id == item_id)
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi trắc nghiệm")
    return row[0], row[1]


def _sync_answers(db: Session, question_id: int, answers: list[TnCauTraLoiWrite]) -> None:
    """Đồng bộ đáp án của một câu hỏi: cập nhật dòng có id, thêm dòng mới, xóa dòng không còn trong danh sách."""
    existing = {
        item.id: item
        for item in db.scalars(select(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id == question_id)).all()
    }
    kept: set[int] = set()
    for answer in answers:
        if answer.id is None:
            db.add(
                TnCauTraLoi(
                    cau_hoi_id=question_id,
                    noi_dung_cau_tra_loi=answer.noi_dung_cau_tra_loi,
                    diem=answer.diem,
                )
            )
            continue
        row = existing.get(answer.id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Đáp án không thuộc câu hỏi này",
            )
        row.noi_dung_cau_tra_loi = answer.noi_dung_cau_tra_loi
        row.diem = answer.diem
        kept.add(answer.id)
    for answer_id, row in existing.items():
        if answer_id not in kept:
            db.delete(row)


def _create_question(db: Session, payload: TnCauHoiTracNghiemWrite) -> TnCauHoiTracNghiem:
    """Tạo một câu hỏi và các đáp án đi kèm trong cùng một giao dịch."""
    item = TnCauHoiTracNghiem(
        ma_holand=payload.ma_holand,
        loai_cau_hoi_id=payload.loai_cau_hoi_id,
        noi_dung_cau_hoi=payload.noi_dung_cau_hoi,
        ghi_chu=payload.ghi_chu,
        trang_thai=payload.trang_thai,
    )
    db.add(item)
    db.flush()
    for answer in payload.cau_tra_loi:
        db.add(
            TnCauTraLoi(
                cau_hoi_id=item.id,
                noi_dung_cau_tra_loi=answer.noi_dung_cau_tra_loi,
                diem=answer.diem,
            )
        )
    return item


@router.get("", response_model=TnCauHoiTracNghiemPage)
def list_cau_hoi(
    q: str | None = Query(default=None, max_length=255),
    ma_holand: str | None = Query(default=None, max_length=20),
    loai_cau_hoi_id: int | None = Query(default=None, ge=1),
    trang_thai: int | None = Query(default=None, ge=0, le=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemPage:
    """Lấy danh sách câu hỏi trắc nghiệm có phân trang, kèm đáp án. Lọc theo từ khóa, mã Holland, loại và trạng thái."""
    filters = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        filters.append(
            or_(
                TnCauHoiTracNghiem.noi_dung_cau_hoi.like(pattern, escape="\\"),
                TnCauHoiTracNghiem.ghi_chu.like(pattern, escape="\\"),
                TnCauHoiTracNghiem.ma_holand.like(pattern, escape="\\"),
                DmLoaiCauHoi.ten_loai_cau_hoi.like(pattern, escape="\\"),
            )
        )
    if ma_holand and ma_holand.strip():
        filters.append(TnCauHoiTracNghiem.ma_holand == ma_holand.strip().upper())
    if loai_cau_hoi_id is not None:
        filters.append(TnCauHoiTracNghiem.loai_cau_hoi_id == loai_cau_hoi_id)
    if trang_thai is not None:
        filters.append(TnCauHoiTracNghiem.trang_thai == trang_thai)

    joined = TnCauHoiTracNghiem.__table__.join(
        DmLoaiCauHoi, TnCauHoiTracNghiem.loai_cau_hoi_id == DmLoaiCauHoi.id
    )
    count_stmt = select(func.count()).select_from(joined)
    stmt = select(TnCauHoiTracNghiem, DmLoaiCauHoi).join(
        DmLoaiCauHoi, TnCauHoiTracNghiem.loai_cau_hoi_id == DmLoaiCauHoi.id
    )
    if filters:
        count_stmt = count_stmt.where(*filters)
        stmt = stmt.where(*filters)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(TnCauHoiTracNghiem.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    answers = _answers_of(db, [item.id for item, _loai in rows])
    return TnCauHoiTracNghiemPage(
        items=[_to_public(item, loai, answers.get(item.id, [])) for item, loai in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{item_id}", response_model=TnCauHoiTracNghiemPublic)
def get_cau_hoi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemPublic:
    """Lấy chi tiết một câu hỏi trắc nghiệm kèm danh sách đáp án."""
    item, loai = _load_pair(db, item_id)
    answers = _answers_of(db, [item.id]).get(item.id, [])
    return _to_public(item, loai, answers)


@router.post("/bulk", response_model=TnCauHoiTracNghiemBulkResult, status_code=status.HTTP_201_CREATED)
def create_cau_hoi_bulk(
    payload: list[TnCauHoiTracNghiemWrite],
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemBulkResult:
    """Thêm nhiều câu hỏi cùng đáp án. Từ chối nếu mã Holland hoặc loại câu hỏi không tồn tại."""
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Danh sách câu hỏi trống")
    if len(payload) > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ thêm tối đa 500 câu hỏi mỗi lần")
    _ensure_holland(db, [item.ma_holand for item in payload])
    _ensure_loai(db, [item.loai_cau_hoi_id for item in payload])
    for item in payload:
        _create_question(db, item)
    db.commit()
    return TnCauHoiTracNghiemBulkResult(created=len(payload))


@router.post("", response_model=TnCauHoiTracNghiemPublic, status_code=status.HTTP_201_CREATED)
def create_cau_hoi(
    payload: TnCauHoiTracNghiemWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemPublic:
    """Thêm một câu hỏi trắc nghiệm và các đáp án đi kèm."""
    _ensure_holland(db, [payload.ma_holand])
    _ensure_loai(db, [payload.loai_cau_hoi_id])
    item = _create_question(db, payload)
    db.commit()
    saved, loai = _load_pair(db, item.id)
    answers = _answers_of(db, [saved.id]).get(saved.id, [])
    return _to_public(saved, loai, answers)


@router.put("/{item_id}", response_model=TnCauHoiTracNghiemPublic)
def update_cau_hoi(
    item_id: int,
    payload: TnCauHoiTracNghiemWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemPublic:
    """Cập nhật câu hỏi và đồng bộ toàn bộ đáp án theo danh sách gửi lên."""
    item, _loai = _load_pair(db, item_id)
    _ensure_holland(db, [payload.ma_holand])
    _ensure_loai(db, [payload.loai_cau_hoi_id])
    item.ma_holand = payload.ma_holand
    item.loai_cau_hoi_id = payload.loai_cau_hoi_id
    item.noi_dung_cau_hoi = payload.noi_dung_cau_hoi
    item.ghi_chu = payload.ghi_chu
    item.trang_thai = payload.trang_thai
    _sync_answers(db, item.id, payload.cau_tra_loi)
    db.commit()
    saved, loai = _load_pair(db, item.id)
    answers = _answers_of(db, [saved.id]).get(saved.id, [])
    return _to_public(saved, loai, answers)


@router.delete("", response_model=TnCauHoiTracNghiemDeleteManyResult)
def delete_cau_hoi_many(
    payload: TnCauHoiTracNghiemDeleteMany,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauHoiTracNghiemDeleteManyResult:
    """Xóa nhiều câu hỏi theo danh sách id. Đáp án của các câu hỏi đó bị xóa theo."""
    items = db.scalars(select(TnCauHoiTracNghiem).where(TnCauHoiTracNghiem.id.in_(payload.ids))).all()
    if not items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy câu hỏi trắc nghiệm để xóa")
    for item in items:
        db.delete(item)
    db.commit()
    return TnCauHoiTracNghiemDeleteManyResult(deleted=len(items))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cau_hoi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một câu hỏi trắc nghiệm theo id. Đáp án của câu hỏi bị xóa theo."""
    item, _loai = _load_pair(db, item_id)
    db.delete(item)
    db.commit()


@router.get("/{item_id}/cau-tra-loi", response_model=list[TnCauTraLoiPublic])
def list_cau_tra_loi(
    item_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> list[TnCauTraLoiPublic]:
    """Lấy danh sách đáp án của một câu hỏi."""
    _load_pair(db, item_id)
    return [_to_answer(item) for item in _answers_of(db, [item_id]).get(item_id, [])]


@router.post(
    "/{item_id}/cau-tra-loi",
    response_model=TnCauTraLoiPublic,
    status_code=status.HTTP_201_CREATED,
)
def create_cau_tra_loi(
    item_id: int,
    payload: TnCauTraLoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauTraLoi:
    """Thêm một đáp án cho câu hỏi."""
    _load_pair(db, item_id)
    count = db.scalar(select(func.count()).select_from(TnCauTraLoi).where(TnCauTraLoi.cau_hoi_id == item_id)) or 0
    if count >= 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mỗi câu hỏi chỉ có tối đa 20 đáp án")
    item = TnCauTraLoi(
        cau_hoi_id=item_id,
        noi_dung_cau_tra_loi=payload.noi_dung_cau_tra_loi,
        diem=payload.diem,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}/cau-tra-loi/{answer_id}", response_model=TnCauTraLoiPublic)
def update_cau_tra_loi(
    item_id: int,
    answer_id: int,
    payload: TnCauTraLoiWrite,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> TnCauTraLoi:
    """Cập nhật nội dung và điểm của một đáp án."""
    _load_pair(db, item_id)
    item = db.get(TnCauTraLoi, answer_id)
    if item is None or item.cau_hoi_id != item_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đáp án")
    item.noi_dung_cau_tra_loi = payload.noi_dung_cau_tra_loi
    item.diem = payload.diem
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}/cau-tra-loi/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cau_tra_loi(
    item_id: int,
    answer_id: int,
    db: Session = Depends(get_db),
    _: NguoiDung = Depends(get_current_user),
) -> None:
    """Xóa một đáp án của câu hỏi."""
    _load_pair(db, item_id)
    item = db.get(TnCauTraLoi, answer_id)
    if item is None or item.cau_hoi_id != item_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đáp án")
    db.delete(item)
    db.commit()
