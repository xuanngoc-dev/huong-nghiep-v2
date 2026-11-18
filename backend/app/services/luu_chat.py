"""Lưu hội thoại với trợ lý vào chat_conversations / chat_messages.

Mỗi lượt hỏi: tìm phiên theo mã phiên (UUID) do frontend gửi, chưa có hoặc không thuộc người hỏi thì tạo phiên mới;
ghi một tin nhắn `user` (câu hỏi) và sau khi trả lời xong một tin nhắn `bot` (câu trả lời / lỗi).
Phiên bị quản trị kết thúc (`da_dong`) hoặc lưu trữ (`luu_tru`) thì không nhận câu hỏi mới (`PhienDaKetThuc`).
Các hàm nhận Session để test được; nơi gọi tự commit. Lỗi khi lưu không được làm hỏng việc chat (nơi gọi bắt lỗi).
"""

import uuid
from datetime import datetime

from sqlalchemy import case, select, update
from sqlalchemy.orm import Session

from app.models.chat_conversations import ChatConversation
from app.models.chat_messages import ChatMessage
from app.models.nguoi_dung_thong_tin import NguoiDungThongTin

_DO_DAI_TIEU_DE = 120
DANG_HOAT_DONG = "dang_hoat_dong"


class PhienDaKetThuc(Exception):
    """Phiên của người hỏi đã kết thúc / lưu trữ: không ghi tiếp, nơi gọi báo người dùng mở hội thoại mới."""


def _uuid_hop_le(value: str | None) -> str | None:
    try:
        return str(uuid.UUID(str(value))) if value else None
    except ValueError:
        return None


def _thuoc_nguoi_hoi(phien: ChatConversation, user_id: int | None, ma_khach: str | None) -> bool:
    """Phiên của thành viên chỉ chính thành viên đó ghi tiếp; phiên của khách chỉ đúng thiết bị đó ghi tiếp."""
    if phien.user_id is not None:
        return phien.user_id == user_id
    return user_id is None and bool(ma_khach) and phien.ma_khach_vang_lai == ma_khach


def _tieu_de(cau_hoi: str) -> str:
    dong = " ".join(cau_hoi.split())
    return dong if len(dong) <= _DO_DAI_TIEU_DE else dong[: _DO_DAI_TIEU_DE - 1] + "…"


def tim_phien(db: Session, ma_phien: str | None, user_id: int | None, ma_khach: str | None) -> ChatConversation | None:
    """Phiên có mã `ma_phien` thuộc người hỏi; mã không hợp lệ / chưa có / của người khác thì None."""
    ma = _uuid_hop_le(ma_phien)
    phien = db.scalar(select(ChatConversation).where(ChatConversation.ma_dinh_danh == ma)) if ma else None
    return phien if phien is not None and _thuoc_nguoi_hoi(phien, user_id, ma_khach) else None


def ket_thuc_phien(db: Session, ma_phien: str | None, user_id: int | None, ma_khach: str | None) -> ChatConversation | None:
    """Người hỏi tự kết thúc phiên của mình (lệnh /end); phiên không thuộc người hỏi thì None. Đã kết thúc thì giữ nguyên."""
    phien = tim_phien(db, ma_phien, user_id, ma_khach)
    if phien is None or phien.trang_thai != DANG_HOAT_DONG:
        return phien
    phien.trang_thai = "da_dong"
    phien.du_lieu_bo_sung = {
        **(phien.du_lieu_bo_sung or {}),
        "ket_thuc_boi": "nguoi_dung",
        "ket_thuc_luc": datetime.now().isoformat(timespec="seconds"),
    }
    db.flush()
    return phien


def mo_phien(
    db: Session, ma_phien: str | None, user_id: int | None, ma_khach: str | None, cau_hoi: str, model_ai: str | None
) -> ChatConversation:
    """Lấy phiên theo mã; chưa có / mã không hợp lệ / không thuộc người hỏi thì tạo phiên mới (tiêu đề = câu hỏi đầu).

    Phiên của người hỏi đã kết thúc thì raise `PhienDaKetThuc`.
    """
    ma = _uuid_hop_le(ma_phien)
    phien = db.scalar(select(ChatConversation).where(ChatConversation.ma_dinh_danh == ma)) if ma else None
    if phien is not None and not _thuoc_nguoi_hoi(phien, user_id, ma_khach):
        phien, ma = None, None
    if phien is not None and phien.trang_thai != DANG_HOAT_DONG:
        raise PhienDaKetThuc(phien.ma_dinh_danh)
    if phien is None:
        phien = ChatConversation(
            user_id=user_id,
            ma_dinh_danh=ma or str(uuid.uuid4()),
            ma_khach_vang_lai=None if user_id else ma_khach,
            tieu_de=_tieu_de(cau_hoi),
            model_ai=model_ai,
            so_tin_nhan=0,
        )
        db.add(phien)
        db.flush()
    return phien


def _them_tin_nhan(db: Session, phien: ChatConversation, **values) -> ChatMessage:
    tin_nhan = ChatMessage(phien_chat_id=phien.id, ma_khach_vang_lai=phien.ma_khach_vang_lai, **values)
    db.add(tin_nhan)
    phien.so_tin_nhan = (phien.so_tin_nhan or 0) + 1
    phien.tin_nhan_cuoi_luc = datetime.now()
    db.flush()
    return tin_nhan


def luu_cau_hoi(
    db: Session,
    ma_phien: str | None,
    user_id: int | None,
    ma_khach: str | None,
    cau_hoi: str,
    model_ai: str | None,
    yeu_cau_token: bool = False,
) -> ChatConversation:
    """Mở (hoặc tạo) phiên và ghi câu hỏi của người dùng. Trả phiên để ghi câu trả lời sau.

    yeu_cau_token: thành viên hết token thì raise HetToken. Kiểm tra sau khi mở phiên để phiên đã kết thúc
    được báo trước (PhienDaKetThuc); nơi gọi rollback nên không lưu gì.
    """
    phien = mo_phien(db, ma_phien, user_id, ma_khach, cau_hoi, model_ai)
    if yeu_cau_token:
        kiem_tra_token(db, user_id)
    if model_ai:
        phien.model_ai = model_ai
    _them_tin_nhan(db, phien, loai_nguoi_gui="user", nguoi_gui_id=user_id, noi_dung_tin_nhan=cau_hoi)
    return phien


class HetToken(Exception):
    """Thành viên đã hết token AI (chỉ khi bật CHAT_YEU_CAU_TOKEN): không hỏi AI, nơi gọi mời nạp gói token."""


def kiem_tra_token(db: Session, user_id: int | None) -> None:
    """Thành viên còn token khả dụng thì cho hỏi; hết thì raise HetToken. Khách vãng lai không có tài khoản token."""
    if user_id is None:
        return
    con_lai = db.scalar(
        select(NguoiDungThongTin.so_luong_token_kha_dung).where(NguoiDungThongTin.nguoi_dung_id == user_id)
    )
    if not con_lai or con_lai <= 0:
        raise HetToken(user_id)


def tong_token(usage: dict | None) -> int:
    """Tổng token một lần gọi AI: dùng tổng nhà cung cấp trả về (gồm cả token suy luận của Gemini) nếu có."""
    usage = usage or {}
    tong = usage.get("total_tokens") or usage.get("totalTokenCount")
    if tong:
        return int(tong)
    vao, ra = _so_token(usage)
    return (vao or 0) + (ra or 0)


def tru_token(db: Session, user_id: int | None, so_token: int) -> None:
    """Sau một lượt trả lời của thành viên: cộng token đã dùng, trừ token khả dụng (không xuống dưới 0).

    Cập nhật bằng một câu UPDATE để hai lượt chat đồng thời không ghi đè số dư của nhau.
    """
    if user_id is None or so_token <= 0:
        return
    kha_dung = NguoiDungThongTin.so_luong_token_kha_dung
    db.execute(
        update(NguoiDungThongTin)
        .where(NguoiDungThongTin.nguoi_dung_id == user_id)
        .values(
            so_luong_token_da_dung=NguoiDungThongTin.so_luong_token_da_dung + so_token,
            so_luong_token_kha_dung=case((kha_dung > so_token, kha_dung - so_token), else_=0),
        )
    )


def _so_token(usage: dict | None) -> tuple[int | None, int | None]:
    """Số token vào / ra theo cách đặt tên của từng nhà cung cấp (OpenAI, Gemini, Anthropic)."""
    usage = usage or {}
    vao = usage.get("prompt_tokens") or usage.get("promptTokenCount") or usage.get("input_tokens")
    ra = usage.get("completion_tokens") or usage.get("candidatesTokenCount") or usage.get("output_tokens")
    return (int(vao) if vao else None, int(ra) if ra else None)


def luu_tra_loi(
    db: Session,
    phien_id: int,
    *,
    tra_loi: str,
    model_ai: str | None,
    nguon: list | None,
    usage: dict | None,
    thoi_gian_ms: int | None,
    loi: str | None = None,
    usage_lap_ke_hoach: dict | None = None,
) -> ChatMessage | None:
    """Ghi câu trả lời của bot (kể cả trả lời dở / lỗi) vào phiên `phien_id`.

    Phiên của thành viên: trừ token khả dụng / cộng token đã dùng bằng tổng token lượt này (bước lập kế hoạch
    tra cứu + bước trả lời). so_token_vao / so_token_ra của tin nhắn chỉ ghi bước trả lời như trước.
    """
    phien = db.get(ChatConversation, phien_id)
    if phien is None:
        return None
    vao, ra = _so_token(usage)
    tru_token(db, phien.user_id, tong_token(usage) + tong_token(usage_lap_ke_hoach))
    return _them_tin_nhan(
        db,
        phien,
        loai_nguoi_gui="bot",
        nguoi_gui_id=None,
        noi_dung_phan_hoi=tra_loi or None,
        nguon_tham_khao=nguon or None,
        model_ai=model_ai,
        so_token_vao=vao,
        so_token_ra=ra,
        thoi_gian_phan_hoi_ms=thoi_gian_ms,
        trang_thai="loi" if loi else "thanh_cong",
        loi_chi_tiet=loi,
    )
