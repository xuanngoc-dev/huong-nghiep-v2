import json
import unicodedata
from typing import Any

from starlette.responses import JSONResponse


def chuan_hoa_utf8(value: Any) -> Any:
    """Đưa chữ về dạng Unicode NFC để JSON UTF-8 ổn định, kể cả tiếng Việt."""
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, dict):
        return {
            chuan_hoa_utf8(key) if isinstance(key, str) else key: chuan_hoa_utf8(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [chuan_hoa_utf8(item) for item in value]
    return value


class Utf8JSONResponse(JSONResponse):
    """JSON trả về bằng UTF-8, không escape ký tự ngoài ASCII."""

    media_type = "application/json; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return json.dumps(
            chuan_hoa_utf8(content),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
