from app.core.config import settings
from app.schemas.chat import HoiChatRequest, HoiChatResponse, ModelChat


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
        "Google Gemini: tra cứu dữ liệu tuyển sinh."
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
            timeout_giay=settings.chat_timeout_seconds,
        ),
        ModelChat(
            id=configured_openai,
            ten=f"OpenAI {configured_openai}",
            nha_cung_cap="OpenAI",
            phi=True,
            mo_ta="Trợ lý tra cứu và diễn giải dữ liệu tuyển sinh.",
            san_sang=openai_key_ready,
            provider="openai",
            timeout_giay=settings.chat_timeout_seconds,
        ),
    ]


async def hoi(payload: HoiChatRequest) -> HoiChatResponse:
    from app.services.chat_stream import answer

    return await answer(payload)
