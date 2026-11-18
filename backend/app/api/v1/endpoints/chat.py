import logging
from contextlib import aclosing
from functools import partial
from time import perf_counter

import anyio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials

from app.api.deps import bearer_scheme, get_current_user
from app.db.session import SessionLocal
from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat
from app.services import luu_chat
from app.services.chat_stream import encode_event, events, prepare
from app.services.hoi_dap import danh_sach_model, hoi
from app.services.tai_lieu import resolve_inside

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


def _nguoi_hoi(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> int | None:
    """Id người hỏi khi token hợp lệ; không có token hoặc token sai / hết hạn thì vẫn chat như khách."""
    if credentials is None or not credentials.credentials:
        return None
    db = SessionLocal()
    try:
        return get_current_user(credentials, db).id
    except HTTPException:
        return None
    finally:
        db.close()


def _ghi(ham, *args, **kwargs):
    """Chạy một hàm ghi của luu_chat trong session riêng; lỗi chỉ ghi log, không làm hỏng việc chat."""
    db = SessionLocal()
    try:
        ket_qua = ham(db, *args, **kwargs)
        db.commit()
        return ket_qua
    except Exception:
        db.rollback()
        logger.exception("Không lưu được hội thoại chat")
        return None
    finally:
        db.close()


def _luu_cau_hoi(db, payload: HoiChatRequest, user_id: int | None) -> tuple[int, str]:
    phien = luu_chat.luu_cau_hoi(
        db, payload.ma_phien, user_id, payload.ma_khach_vang_lai, payload.cau_hoi, payload.model_id
    )
    return phien.id, phien.ma_dinh_danh


async def _mo_phien(payload: HoiChatRequest, user_id: int | None) -> tuple[int, str] | None:
    """(id, mã) của phiên vừa ghi câu hỏi; None nếu không lưu được."""
    return await anyio.to_thread.run_sync(partial(_ghi, _luu_cau_hoi, payload, user_id))


async def _luu_tra_loi(phien, *, tra_loi, model_ai, nguon, usage, started, loi) -> None:
    if phien is None:
        return
    await anyio.to_thread.run_sync(
        partial(
            _ghi,
            luu_chat.luu_tra_loi,
            phien[0],
            tra_loi=tra_loi,
            model_ai=model_ai,
            nguon=nguon,
            usage=usage,
            thoi_gian_ms=round((perf_counter() - started) * 1000),
            loi=loi,
        )
    )


@router.get("/model", response_model=list[ModelChat])
def get_models() -> list[ModelChat]:
    """Danh sách model hỏi đáp và trạng thái đã có API key."""
    return danh_sach_model()


@router.post("/hoi", response_model=HoiChatResponse)
async def post_hoi(payload: HoiChatRequest, user_id: int | None = Depends(_nguoi_hoi)) -> HoiChatResponse:
    """Hỏi đáp dựa trên các file json/txt trong thư mục tài liệu; câu hỏi và câu trả lời được lưu vào phiên chat."""
    phien = await _mo_phien(payload, user_id)
    started = perf_counter()
    try:
        ket_qua = await hoi(payload)
    except HTTPException as exc:
        await _luu_tra_loi(
            phien, tra_loi="", model_ai=payload.model_id, nguon=None, usage=None, started=started, loi=str(exc.detail)
        )
        raise
    await _luu_tra_loi(
        phien,
        tra_loi=ket_qua.tra_loi,
        model_ai=ket_qua.model_id,
        nguon=[item.model_dump(mode="json") for item in ket_qua.nguon],
        usage=None,
        started=started,
        loi=None,
    )
    ket_qua.ma_phien = phien[1] if phien else None
    return ket_qua


@router.post("/hoi/stream")
async def post_hoi_stream(payload: HoiChatRequest, user_id: int | None = Depends(_nguoi_hoi)):
    """Hỏi đáp dạng stream (SSE). Sự kiện `meta` có `ma_phien` để frontend gửi lại ở câu hỏi sau."""
    phien = await _mo_phien(payload, user_id)
    started = perf_counter()
    try:
        prepared = await prepare(payload)
    except HTTPException as exc:
        await _luu_tra_loi(
            phien, tra_loi="", model_ai=payload.model_id, nguon=None, usage=None, started=started, loi=str(exc.detail)
        )
        raise

    async def stream():
        tra_loi, xong, loi = "", None, None
        try:
            async with aclosing(events(prepared)) as response_events:
                async for event, data in response_events:
                    if event == "meta" and phien:
                        data = {**data, "ma_phien": phien[1]}
                    elif event == "delta":
                        tra_loi += data.get("text", "")
                    elif event == "done":
                        xong = data
                    elif event == "error":
                        loi = data.get("message")
                    yield encode_event(event, data)
        finally:
            if xong is None and loi is None:
                loi = "Người dùng dừng hoặc ngắt kết nối trước khi trả lời xong."
            # Lưu cả khi client ngắt kết nối (task bị hủy): chạy trong vùng không bị hủy.
            with anyio.CancelScope(shield=True):
                await _luu_tra_loi(
                    phien,
                    tra_loi=(xong or {}).get("tra_loi") or tra_loi,
                    model_ai=(xong or {}).get("model_id") or prepared.model.id,
                    nguon=(xong or {}).get("nguon"),
                    usage=prepared.usage,
                    started=started,
                    loi=loi,
                )

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/nguon/{ten}")
def get_nguon(ten: str):
    """Nguồn dữ liệu công khai dùng để đối chiếu câu trả lời tuyển sinh."""
    path = resolve_inside(ten)
    if not path.is_file():
        raise HTTPException(400, f"Không tìm thấy nguồn dữ liệu có tên = {ten}")
    if path.suffix.lower() == ".json":
        media_type = "application/json; charset=utf-8"
    else:
        media_type = "text/plain; charset=utf-8"
    return FileResponse(path, filename=path.name, media_type=media_type)
