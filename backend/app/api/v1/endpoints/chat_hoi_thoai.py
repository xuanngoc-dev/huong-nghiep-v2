from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.db.session import get_db
from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.nguoi_dung import NguoiDung
from app.schemas.chat_hoi_thoai import ChatPhienChiTiet, ChatPhienItem, ChatPhienPage, ChatTinNhanItem

router = APIRouter(prefix="/hoi-thoai", tags=["hoi-thoai"], dependencies=[Depends(get_admin_user)])

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


@router.get("/phien", response_model=ChatPhienPage)
def danh_sach_phien(
    q: str | None = Query(default=None, max_length=255),
    trang_thai: Literal["dang_hoat_dong", "da_dong", "luu_tru"] | None = Query(default=None),
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

    nguon = select(ChatConversation, NguoiDung).outerjoin(NguoiDung, ChatConversation.user_id == NguoiDung.id)
    total = db.scalar(
        select(func.count())
        .select_from(ChatConversation)
        .outerjoin(NguoiDung, ChatConversation.user_id == NguoiDung.id)
        .where(*dieu_kien)
    ) or 0
    rows = db.execute(
        nguon.where(*dieu_kien)
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


@router.get("/phien/{item_id}", response_model=ChatPhienChiTiet)
def chi_tiet_phien(item_id: int, db: Session = Depends(get_db)) -> ChatPhienChiTiet:
    """Thông tin một phiên hội thoại và toàn bộ tin nhắn theo thứ tự gửi."""
    phien = db.get(ChatConversation, item_id)
    if phien is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không tìm thấy phiên hội thoại có id = {item_id}",
        )
    nguoi = db.get(NguoiDung, phien.user_id) if phien.user_id else None
    tin_nhan = list(
        db.scalars(select(ChatMessage).where(ChatMessage.phien_chat_id == phien.id).order_by(ChatMessage.id))
    )
    return ChatPhienChiTiet(
        phien=_item(phien, nguoi, tin_nhan[-1] if tin_nhan else None),
        tin_nhan=[ChatTinNhanItem.model_validate(m) for m in tin_nhan],
    )
