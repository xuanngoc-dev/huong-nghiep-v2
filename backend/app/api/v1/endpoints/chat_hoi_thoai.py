from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user, get_current_user
from app.db.session import get_db
from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.nguoi_dung import NguoiDung
from app.services import luu_chat
from app.schemas.chat_hoi_thoai import (
    ChatPhienChiTiet,
    ChatPhienDoiTieuDe,
    ChatPhienItem,
    ChatPhienPage,
    ChatPhienTrangThai,
    ChatTinNhanItem,
)

router = APIRouter(prefix="/hoi-thoai", tags=["hoi-thoai"], dependencies=[Depends(get_admin_user)])
# Thành viên xem hội thoại của chính mình; include trước router quản trị.
cua_toi_router = APIRouter(prefix="/hoi-thoai/cua-toi", tags=["hoi-thoai"])

_DO_DAI_XEM_TRUOC = 160


def _like_pattern(value: str) -> str:
    """Tạo mẫu tìm kiếm LIKE an toàn: bọc dấu % và escape các ký tự %, _ cùng dấu gạch chéo ngược."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def _xem_truoc(tin_nhan: ChatMessage | None) -> str | None:
    if tin_nhan is None:
        return None
    noi_dung = " ".join((tin_nhan.noi_dung_tin_nhan or tin_nhan.noi_dung_phan_hoi or tin_nhan.loi_chi_tiet or "").split())
    return noi_dung if len(noi_dung) <= _DO_DAI_XEM_TRUOC else noi_dung[: _DO_DAI_XEM_TRUOC - 1] + "…"


def _item(phien: ChatConversation, nguoi: NguoiDung | None, cuoi: ChatMessage | None) -> ChatPhienItem:
    return ChatPhienItem(
        id=phien.id,
        ma_dinh_danh=phien.ma_dinh_danh,
        tieu_de=phien.tieu_de,
        trang_thai=phien.trang_thai,
        user_id=phien.user_id,
        ho_ten=nguoi.ho_ten if nguoi else None,
        email=nguoi.email if nguoi else None,
        ma_khach_vang_lai=phien.ma_khach_vang_lai,
        model_ai=phien.model_ai,
        so_tin_nhan=phien.so_tin_nhan or 0,
        tin_nhan_cuoi_luc=phien.tin_nhan_cuoi_luc,
        tin_nhan_cuoi=_xem_truoc(cuoi),
        created_at=phien.created_at,
    )


def _tin_nhan_cuoi(db: Session, phien_ids: list[int]) -> dict[int, ChatMessage]:
    """Tin nhắn gần nhất của mỗi phiên."""
    if not phien_ids:
        return {}
    cuoi_ids = select(func.max(ChatMessage.id)).where(ChatMessage.phien_chat_id.in_(phien_ids)).group_by(
        ChatMessage.phien_chat_id
    )
    return {m.phien_chat_id: m for m in db.scalars(select(ChatMessage).where(ChatMessage.id.in_(cuoi_ids)))}


def _phien_or_400(db: Session, ma_phien: str) -> ChatConversation:
    """Phiên theo mã định danh (UUID) hoặc id số; không có thì 400."""
    if ma_phien.isdigit():
        phien = db.get(ChatConversation, int(ma_phien))
    else:
        phien = db.scalar(select(ChatConversation).where(ChatConversation.ma_dinh_danh == ma_phien))
    if phien is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy phiên hội thoại có mã = {ma_phien}",
        )
    return phien


def _trang_phien(db: Session, dieu_kien: list, page: int, page_size: int) -> ChatPhienPage:
    """Một trang phiên thỏa điều kiện, phiên có tin nhắn mới nhất trước, kèm xem trước tin nhắn cuối."""
    total = db.scalar(
        select(func.count())
        .select_from(ChatConversation)
        .outerjoin(NguoiDung, ChatConversation.user_id == NguoiDung.id)
        .where(*dieu_kien)
    ) or 0
    rows = db.execute(
        select(ChatConversation, NguoiDung)
        .outerjoin(NguoiDung, ChatConversation.user_id == NguoiDung.id)
        .where(*dieu_kien)
        .order_by(
            ChatConversation.tin_nhan_cuoi_luc.is_(None),
            ChatConversation.tin_nhan_cuoi_luc.desc(),
            ChatConversation.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    cuoi = _tin_nhan_cuoi(db, [phien.id for phien, _ in rows])
    items = [_item(phien, nguoi, cuoi.get(phien.id)) for phien, nguoi in rows]
    return ChatPhienPage(items=items, total=total, page=page, page_size=page_size)


def _chi_tiet(db: Session, phien: ChatConversation) -> ChatPhienChiTiet:
    nguoi = db.get(NguoiDung, phien.user_id) if phien.user_id else None
    tin_nhan = list(
        db.scalars(select(ChatMessage).where(ChatMessage.phien_chat_id == phien.id).order_by(ChatMessage.id))
    )
    return ChatPhienChiTiet(
        phien=_item(phien, nguoi, tin_nhan[-1] if tin_nhan else None),
        tin_nhan=[ChatTinNhanItem.model_validate(m) for m in tin_nhan],
    )


def _item_cua(db: Session, phien: ChatConversation) -> ChatPhienItem:
    nguoi = db.get(NguoiDung, phien.user_id) if phien.user_id else None
    return _item(phien, nguoi, _tin_nhan_cuoi(db, [phien.id]).get(phien.id))


@router.get("/phien", response_model=ChatPhienPage)
def danh_sach_phien(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: Literal["dang_hoat_dong", "da_dong"] | None = Query(default=None),
    doi_tuong: Literal["thanh-vien", "khach"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
) -> ChatPhienPage:
    """Danh sách phiên hội thoại với trợ lý, phiên có tin nhắn mới nhất trước.

    Tìm theo tiêu đề, mã phiên, mã khách, họ tên hoặc email người dùng; lọc theo trạng thái và thành viên / khách.
    """
    dieu_kien = []
    if q and q.strip():
        pattern = _like_pattern(q.strip())
        dieu_kien.append(
            or_(
                ChatConversation.tieu_de.like(pattern, escape="\\"),
                ChatConversation.ma_dinh_danh.like(pattern, escape="\\"),
                ChatConversation.ma_khach_vang_lai.like(pattern, escape="\\"),
                NguoiDung.ho_ten.like(pattern, escape="\\"),
                NguoiDung.email.like(pattern, escape="\\"),
            )
        )
    if trang_thai:
        dieu_kien.append(ChatConversation.trang_thai == trang_thai)
    if doi_tuong == "thanh-vien":
        dieu_kien.append(ChatConversation.user_id.is_not(None))
    elif doi_tuong == "khach":
        dieu_kien.append(ChatConversation.user_id.is_(None))
    return _trang_phien(db, dieu_kien, page, page_size)


@router.get("/phien/{ma_phien}", response_model=ChatPhienChiTiet)
def chi_tiet_phien(ma_phien: str, db: Session = Depends(get_db)) -> ChatPhienChiTiet:
    """Thông tin một phiên hội thoại và toàn bộ tin nhắn theo thứ tự gửi.

    `ma_phien` là mã định danh (UUID, dùng trên URL trang quản trị) hoặc id số của phiên.
    """
    return _chi_tiet(db, _phien_or_400(db, ma_phien))


@router.patch("/phien/{ma_phien}/trang-thai", response_model=ChatPhienItem)
def doi_trang_thai_phien(
    ma_phien: str, payload: ChatPhienTrangThai, db: Session = Depends(get_db)
) -> ChatPhienItem:
    """Kết thúc (`da_dong`) hoặc mở lại (`dang_hoat_dong`) một phiên.

    Phiên đã kết thúc thì người dùng không hỏi tiếp được trong phiên đó (API chat trả 409).
    """
    phien = _phien_or_400(db, ma_phien)
    phien.trang_thai = payload.trang_thai
    db.commit()
    db.refresh(phien)
    return _item_cua(db, phien)


@router.patch("/phien/{ma_phien}/tieu-de", response_model=ChatPhienItem)
def doi_tieu_de_phien(ma_phien: str, payload: ChatPhienDoiTieuDe, db: Session = Depends(get_db)) -> ChatPhienItem:
    """Quản trị đổi tiêu đề một phiên hội thoại (mặc định là câu hỏi đầu tiên của người dùng)."""
    phien = _phien_or_400(db, ma_phien)
    phien.tieu_de = payload.tieu_de
    db.commit()
    db.refresh(phien)
    return _item_cua(db, phien)


@router.delete("/phien/{ma_phien}", status_code=status.HTTP_204_NO_CONTENT)
def xoa_phien(ma_phien: str, db: Session = Depends(get_db)) -> Response:
    """Xóa một phiên cùng toàn bộ tin nhắn của phiên."""
    phien = _phien_or_400(db, ma_phien)
    db.execute(delete(ChatMessage).where(ChatMessage.phien_chat_id == phien.id))
    db.delete(phien)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@cua_toi_router.get("", response_model=ChatPhienPage)
def danh_sach_hoi_thoai_cua_toi(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: Literal["dang-hoat-dong", "da-ket-thuc"] | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1),
    nguoi_dung: NguoiDung = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatPhienPage:
    """Các cuộc hội thoại của thành viên đang đăng nhập, mới nhất trước.

    Tìm theo tiêu đề; `da-ket-thuc` là phiên đã kết thúc (`da_dong`).
    """
    dieu_kien = [ChatConversation.user_id == nguoi_dung.id]
    if q and q.strip():
        dieu_kien.append(ChatConversation.tieu_de.like(_like_pattern(q.strip()), escape="\\"))
    if trang_thai == "dang-hoat-dong":
        dieu_kien.append(ChatConversation.trang_thai == luu_chat.DANG_HOAT_DONG)
    elif trang_thai == "da-ket-thuc":
        dieu_kien.append(ChatConversation.trang_thai != luu_chat.DANG_HOAT_DONG)
    return _trang_phien(db, dieu_kien, page, page_size)


def _phien_cua_toi_or_400(db: Session, ma_phien: str, nguoi_dung: NguoiDung) -> ChatConversation:
    """Phiên (theo mã định danh UUID) của thành viên đang đăng nhập; của người khác cũng báo không tìm thấy."""
    phien = db.scalar(select(ChatConversation).where(ChatConversation.ma_dinh_danh == ma_phien))
    if phien is None or phien.user_id != nguoi_dung.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy phiên hội thoại có mã = {ma_phien}",
        )
    return phien


@cua_toi_router.get("/{ma_phien}", response_model=ChatPhienChiTiet)
def chi_tiet_hoi_thoai_cua_toi(
    ma_phien: str,
    nguoi_dung: NguoiDung = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatPhienChiTiet:
    """Toàn bộ tin nhắn một cuộc hội thoại của thành viên đang đăng nhập (`ma_phien` là mã định danh UUID)."""
    return _chi_tiet(db, _phien_cua_toi_or_400(db, ma_phien, nguoi_dung))


@cua_toi_router.patch("/{ma_phien}/tieu-de", response_model=ChatPhienItem)
def doi_tieu_de_hoi_thoai_cua_toi(
    ma_phien: str,
    payload: ChatPhienDoiTieuDe,
    nguoi_dung: NguoiDung = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatPhienItem:
    """Thành viên đổi tiêu đề cuộc hội thoại của mình (mặc định là câu hỏi đầu tiên)."""
    phien = _phien_cua_toi_or_400(db, ma_phien, nguoi_dung)
    phien.tieu_de = payload.tieu_de
    db.commit()
    db.refresh(phien)
    return _item_cua(db, phien)


@cua_toi_router.post("/{ma_phien}/ket-thuc", response_model=ChatPhienItem)
def ket_thuc_hoi_thoai_cua_toi(
    ma_phien: str,
    nguoi_dung: NguoiDung = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatPhienItem:
    """Thành viên tự kết thúc cuộc hội thoại của mình; sau đó không hỏi tiếp được. Đã kết thúc thì giữ nguyên."""
    phien = _phien_cua_toi_or_400(db, ma_phien, nguoi_dung)
    luu_chat.ket_thuc_phien(db, phien.ma_dinh_danh, nguoi_dung.id, None)
    db.commit()
    db.refresh(phien)
    return _item_cua(db, phien)
