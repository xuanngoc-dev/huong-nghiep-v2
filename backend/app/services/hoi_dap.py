import logging
import re

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat, TinNhan
from app.services.tai_lieu import build_context

logger = logging.getLogger(__name__)

_MODELS: tuple[dict, ...] = (
    {
        "id": "gemini-3.5-flash-lite",
        "ten": "Gemini 3.5 Flash-Lite",
        "nha_cung_cap": "Google",
        "phi": False,
        "mo_ta": "Miễn phí trong hạn mức Google AI Studio",
        "provider": "gemini",
    },
    {
        "id": "gemini-3.8-flash",
        "ten": "Gemini 3.8 Flash",
        "nha_cung_cap": "Google",
        "phi": False,
        "mo_ta": "Miễn phí hạn mức thấp, mạnh hơn Flash-Lite",
        "provider": "gemini",
    },
    {
        "id": "gpt-5-mini",
        "ten": "GPT-5 mini",
        "nha_cung_cap": "OpenAI",
        "phi": True,
        "mo_ta": "GPT có phí, bản gọn cho hỏi đáp tài liệu",
        "provider": "openai",
    },
    {
        "id": "gpt-5",
        "ten": "GPT-5",
        "nha_cung_cap": "OpenAI",
        "phi": True,
        "mo_ta": "GPT có phí, bản mạnh hơn",
        "provider": "openai",
    },
)

_SYSTEM = """Bạn là trợ lý định hướng nghề.
Chỉ dùng thông tin trong phần TÀI LIỆU để trả lời.
Nếu tài liệu không chứa câu trả lời, nói rõ là không thấy trong tài liệu đã cung cấp.
Không bịa số liệu, mã ngành hay điều kiện tuyển sinh.
Trả lời bằng tiếng Việt, rõ ràng, ngắn gọn.
Khi trích thông tin, nhắc tên file nguồn."""


def danh_sach_model() -> list[ModelChat]:
    return [
        ModelChat(
            id=item["id"],
            ten=item["ten"],
            nha_cung_cap=item["nha_cung_cap"],
            phi=item["phi"],
            mo_ta=item["mo_ta"],
            san_sang=_has_key(item["provider"]),
        )
        for item in _MODELS
    ]


def hoi(payload: HoiChatRequest) -> HoiChatResponse:
    model = next((item for item in _MODELS if item["id"] == payload.model_id), None)
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model không được hỗ trợ.")
    if not _has_key(model["provider"]):
        env_name = "GEMINI_API_KEY" if model["provider"] == "gemini" else "OPENAI_API_KEY"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Chưa cấu hình {env_name} trong backend/.env.",
        )

    context, used = build_context(payload.cau_hoi)
    if not used:
        return HoiChatResponse(
            tra_loi=(
                "Chưa có tài liệu để hỏi. Hãy tải file .json hoặc .txt trên màn này, "
                "hoặc bỏ file vào thư mục backend/tai_lieu."
            ),
            model_id=model["id"],
            model_ten=model["ten"],
            tai_lieu=[],
        )

    system = f"{_SYSTEM}\n\nTÀI LIỆU:\n{context}"
    history = payload.lich_su[-12:]
    try:
        if model["provider"] == "gemini":
            answer = _ask_gemini(model["id"], system, history, payload.cau_hoi)
        else:
            answer = _ask_openai(model["id"], system, history, payload.cau_hoi)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model phản hồi quá lâu. Hãy thử lại hoặc chọn model khác.",
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning("Chat provider error: %s", exc.__class__.__name__)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không gọi được model. Kiểm tra mạng và API key.",
        ) from exc

    logger.info("chat model=%s files=%s", model["id"], len(used))
    return HoiChatResponse(
        tra_loi=answer,
        model_id=model["id"],
        model_ten=model["ten"],
        tai_lieu=used,
    )


def _has_key(provider: str) -> bool:
    if provider == "gemini":
        return bool(settings.gemini_api_key.strip())
    return bool(settings.openai_api_key.strip())


def _ask_gemini(model_id: str, system: str, history: list[TinNhan], question: str) -> str:
    contents = []
    for message in history:
        contents.append(
            {
                "role": "user" if message.vai_tro == "user" else "model",
                "parts": [{"text": message.noi_dung}],
            }
        )
    contents.append({"role": "user", "parts": [{"text": question}]})
    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent",
        headers={
            "x-goog-api-key": settings.gemini_api_key.strip(),
            "Content-Type": "application/json",
        },
        json={
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096},
        },
        timeout=60,
    )
    data = _json_or_error(response)
    if response.status_code >= 400:
        _raise_provider(response.status_code, data)
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    texts = [part.get("text", "") for part in parts if part.get("text") and not part.get("thought")]
    answer = "\n".join(text.strip() for text in texts if text.strip())
    return answer or "Model không trả về nội dung. Hãy thử lại hoặc chọn model khác."


def _ask_openai(model_id: str, system: str, history: list[TinNhan], question: str) -> str:
    messages = [{"role": "system", "content": system}]
    for message in history:
        messages.append(
            {
                "role": "user" if message.vai_tro == "user" else "assistant",
                "content": message.noi_dung,
            }
        )
    messages.append({"role": "user", "content": question})
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key.strip()}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_id,
            "messages": messages,
            "max_completion_tokens": 4096,
        },
        timeout=60,
    )
    data = _json_or_error(response)
    if response.status_code >= 400:
        _raise_provider(response.status_code, data)
    answer = data.get("choices", [{}])[0].get("message", {}).get("content") or ""
    return answer.strip() or "Model không trả về nội dung. Hãy thử lại hoặc chọn model khác."


def _json_or_error(response: httpx.Response) -> dict:
    try:
        data = response.json()
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def _raise_provider(status_code: int, data: dict) -> None:
    raw = ""
    error = data.get("error")
    if isinstance(error, dict):
        raw = str(error.get("message") or "")
    elif isinstance(error, str):
        raw = error
    message = _safe_message(raw)
    if status_code in {401, 403}:
        detail = "API key không hợp lệ hoặc không có quyền dùng model này."
    elif status_code == 429:
        detail = "Model đang hết hạn mức. Hãy thử model khác hoặc đợi một lát."
    elif status_code == 404:
        detail = "Model không tồn tại hoặc tài khoản chưa được cấp model này."
    else:
        detail = "Model từ chối yêu cầu."
    if message:
        detail = f"{detail} {message}"
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _safe_message(text: str) -> str:
    compact = " ".join(text.split())
    if not compact or re.search(r"(AIza|sk-|api[_ -]?key|bearer )", compact, flags=re.IGNORECASE):
        return ""
    return compact[:240]
