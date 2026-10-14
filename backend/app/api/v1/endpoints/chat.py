from fastapi import APIRouter

from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat
from app.services.hoi_dap import danh_sach_model, hoi

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/model", response_model=list[ModelChat])
def get_models() -> list[ModelChat]:
    """Danh sách model hỏi đáp và trạng thái đã có API key."""
    return danh_sach_model()


@router.post("/hoi", response_model=HoiChatResponse)
def post_hoi(payload: HoiChatRequest) -> HoiChatResponse:
    """Hỏi đáp dựa trên các file json/txt trong thư mục tài liệu."""
    return hoi(payload)
