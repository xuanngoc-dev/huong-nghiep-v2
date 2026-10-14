import logging
import re

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat, TinNhan
from app.services.tai_lieu import build_context

logger = logging.getLogger(__name__)

_SYSTEM = """Bạn là trợ lý định hướng nghề nghiệp và tư vấn tuyển sinh đại học năm 2026.
QUY TẮC BẮT BUỘC:
1. CHỈ sử dụng thông tin trong phần TÀI LIỆU TUYỂN SINH được cung cấp bên dưới để trả lời.
2. TUYỆT ĐỐI KHÔNG tự bịa số liệu, mã ngành, tổ hợp môn, chỉ tiêu, học phí hay phương thức xét tuyển.
3. TUYỆT ĐỐI KHÔNG lấy thông tin từ bên ngoài tài liệu được cung cấp.
4. Nếu tài liệu không chứa thông tin cần tìm, hãy thông báo rõ ràng: "Hiện tại trong dữ liệu đề án tuyển sinh chưa có thông tin về vấn đề này."
5. Khi trích dẫn thông tin, hãy nêu rõ tên trường đại học (tuyệt đối không nhắc đến tên file hay định dạng kỹ thuật như .json).
6. Trả lời bằng tiếng Việt lịch sự, dễ hiểu, dùng danh sách gạch đầu dòng rõ ràng."""


def _normalize_openai_model(model_id: str) -> str:
    m = model_id.strip().lower()
    if m in ("6.0-luna", "6.0 luna", "6.0_luna", "gpt-6.0-luna", "gpt-6-luna", "luna"):
        return "gpt-6-luna"
    if m in ("6.0-sol", "6.0 sol", "6.0_sol", "gpt-6.0-sol", "gpt-6-sol", "sol"):
        return "gpt-6-sol"
    return model_id.strip()


def _normalize_gemini_model(model_id: str) -> str:
    m = model_id.strip().lower()
    if m in ("3.5-flash-lite", "3.5 flash-lite", "3.5_flash_lite", "gemini-3.5", "gemini-3.5-flash-lite"):
        return "gemini-3.5-flash-lite"
    if m in ("3.8-flash", "3.8 flash", "3.8_flash", "gemini-3.8", "gemini-3.8-flash"):
        return "gemini-3.8-flash"
    if m in ("3.5-flash", "gemini-3.5-flash"):
        return "gemini-3.5-flash"
    if m in ("flash-lite-latest", "gemini-flash-lite-latest"):
        return "gemini-flash-lite-latest"
    return model_id.strip()


def danh_sach_model() -> list[ModelChat]:
    """Trả về danh sách model cho Google Gemini và OpenAI GPT."""
    gemini_key_ready = bool(settings.gemini_api_key.strip())
    openai_key_ready = bool(settings.openai_api_key.strip())

    configured_gemini = _normalize_gemini_model(settings.gemini_model.strip() or "gemini-3.5-flash-lite")
    configured_openai = _normalize_openai_model(settings.openai_model.strip() or "gpt-6-luna")

    gemini_ten = (
        "Google Gemini 3.5 Flash-Lite"
        if "3.5" in configured_gemini
        else ("Google Gemini 3.8 Flash" if "3.8" in configured_gemini else configured_gemini)
    )
    gemini_desc = (
        "Google Gemini 3.5 Flash-Lite (ổn định, phản hồi cực nhanh, không nghẽn)"
        if "3.5" in configured_gemini
        else "Google Gemini (tốc độ cao, tối ưu phân tích đề án tuyển sinh)"
    )

    return [
        ModelChat(
            id=configured_gemini,
            ten=gemini_ten,
            nha_cung_cap="Google",
            phi=False,
            mo_ta=gemini_desc,
            san_sang=gemini_key_ready,
            provider="gemini",
        ),
        ModelChat(
            id=configured_openai,
            ten="OpenAI GPT-6.0 Luna",
            nha_cung_cap="OpenAI",
            phi=True,
            mo_ta="OpenAI GPT-6.0 Luna (thế hệ GPT-6 mới nhất, 1.05M context)",
            san_sang=openai_key_ready,
            provider="openai",
        ),
    ]


def get_provider(model_id: str) -> str:
    m = model_id.lower()
    if "gemini" in m:
        return "gemini"
    if any(k in m for k in ("gpt", "luna", "sol", "astra", "o1", "o3", "o4", "chatgpt")):
        return "openai"
    if model_id == settings.gemini_model.strip():
        return "gemini"
    return "openai"


def hoi(payload: HoiChatRequest) -> HoiChatResponse:
    provider = get_provider(payload.model_id)

    if provider == "gemini":
        if not settings.gemini_api_key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chưa cấu hình GEMINI_API_KEY trong file .env.",
            )
        resolved_model_id = _normalize_gemini_model(payload.model_id)
    else:
        if not settings.openai_api_key.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Chưa cấu hình OPENAI_API_KEY trong file .env.",
            )
        resolved_model_id = _normalize_openai_model(payload.model_id)

    context, used = build_context(payload.cau_hoi)
    if not used:
        return HoiChatResponse(
            tra_loi=(
                "Chưa tìm thấy dữ liệu tài liệu tuyển sinh phù hợp với câu hỏi. "
                "Hãy kiểm tra thư mục data_dh_json hoặc tải file lên hệ thống."
            ),
            model_id=resolved_model_id,
            model_ten=resolved_model_id,
            tai_lieu=[],
        )

    system = f"{_SYSTEM}\n\nTÀI LIỆU TUYỂN SINH:\n{context}"
    history = payload.lich_su[-12:]

    try:
        if provider == "gemini":
            answer = _ask_gemini(resolved_model_id, system, history, payload.cau_hoi)
        else:
            answer = _ask_openai(resolved_model_id, system, history, payload.cau_hoi)
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model phản hồi quá lâu (timeout). Hãy thử lại hoặc chọn model khác.",
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning("Chat provider error: %s", exc.__class__.__name__)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không kết nối được với nhà cung cấp AI. Kiểm tra mạng và API key.",
        ) from exc

    all_models = danh_sach_model()
    model_obj = next((m for m in all_models if m.id == resolved_model_id), None)
    ten_hien_thi = model_obj.ten if model_obj else resolved_model_id

    logger.info("chat provider=%s model=%s files=%s", provider, resolved_model_id, len(used))
    return HoiChatResponse(
        tra_loi=answer,
        model_id=resolved_model_id,
        model_ten=ten_hien_thi,
        tai_lieu=used,
    )


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

    models_to_try = [model_id]
    for fallback in ("gemini-3.5-flash-lite", "gemini-flash-lite-latest"):
        if fallback not in models_to_try:
            models_to_try.append(fallback)

    last_response: httpx.Response | None = None
    for idx, current_model in enumerate(models_to_try):
        response = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent",
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
        last_response = response
        if response.status_code == 200:
            break
        # Nếu model bị quá tải (503 high demand) hoặc nghẽn (429) và vẫn còn model dự phòng
        if response.status_code in {503, 429} and idx < len(models_to_try) - 1:
            logger.warning(
                "Gemini model %s gap loi %s, tu dong thu fallback sang %s",
                current_model,
                response.status_code,
                models_to_try[idx + 1],
            )
            continue
        break

    if last_response is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể kết nối tới Google Gemini. Kiểm tra kết nối mạng.",
        )

    data = _json_or_error(last_response)
    if last_response.status_code >= 400:
        _raise_provider(last_response.status_code, data)
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

    body = {
        "model": model_id,
        "messages": messages,
        "max_completion_tokens": 4096,
    }
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key.strip()}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=60,
    )
    data = _json_or_error(response)
    if response.status_code >= 400:
        err_msg = str(data.get("error", {}).get("message") or "")
        # Fallback to max_tokens nếu model cũ không nhận max_completion_tokens
        if "max_completion_tokens" in err_msg:
            body.pop("max_completion_tokens", None)
            body["max_tokens"] = 4096
            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key.strip()}",
                    "Content-Type": "application/json",
                },
                json=body,
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
        detail = "Model đang hết hạn mức (rate limit / quota). Hãy thử model khác hoặc đợi một lát."
    elif status_code == 404:
        detail = "Model không tồn tại hoặc tài khoản chưa được cấp quyền dùng model này."
    else:
        detail = "Nhà cung cấp AI từ chối yêu cầu."
    if message:
        detail = f"{detail} {message}"
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def _safe_message(text: str) -> str:
    compact = " ".join(text.split())
    if not compact or re.search(r"(AIza|sk-|api[_ -]?key|bearer )", compact, flags=re.IGNORECASE):
        return ""
    return compact[:240]
