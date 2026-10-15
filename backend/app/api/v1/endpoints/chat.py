from contextlib import aclosing

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat
from app.services.hoi_dap import danh_sach_model, hoi
from app.services.chat_stream import encode_event, events, prepare
from app.services.tai_lieu import resolve_inside

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/model", response_model=list[ModelChat])
def get_models() -> list[ModelChat]:
    """Danh sách model hỏi đáp và trạng thái đã có API key."""
    return danh_sach_model()


@router.post("/hoi", response_model=HoiChatResponse)
async def post_hoi(payload: HoiChatRequest) -> HoiChatResponse:
    """Hỏi đáp dựa trên các file json/txt trong thư mục tài liệu."""
    return await hoi(payload)


@router.post("/hoi/stream")
async def post_hoi_stream(payload: HoiChatRequest):
    prepared = await prepare(payload)

    async def stream():
        async with aclosing(events(prepared)) as response_events:
            async for event, data in response_events:
                yield encode_event(event, data)

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
        raise HTTPException(404, "Không tìm thấy nguồn dữ liệu.")
    return FileResponse(path, filename=path.name, media_type="application/json" if path.suffix.lower() == ".json" else "text/plain")
