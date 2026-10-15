"""Local UI fixture: real retrieval/routes, deterministic AI stream, no provider calls.

Run from backend: python -B tests/preview_chat.py
Run Vite with DEV_API_TARGET=http://127.0.0.1:13060 to inspect the chat UI offline.
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
import uvicorn

from app.api.v1.endpoints import chat
from app.core.logging import register_request_logging
from app.services import chat_stream
from app.services.hoi_dap import danh_sach_model

configured = danh_sach_model()


def preview_models():
    return [m.model_copy(update={"san_sang": True, "ten": f"{m.ten} (kiểm thử)"}) for m in configured]


async def preview_provider(prepared):
    yield "model", {"model_id": prepared.model.id, "model_ten": prepared.model.ten}
    data = json.loads(prepared.result.context)
    results = data.get("ket_qua", []) if isinstance(data, dict) else []
    output = "**Kiểm thử giao diện — phản hồi AI giả lập.**\n\n"
    output += f"Có {len(prepared.result.sources)} nguồn dữ liệu phù hợp.\n\n| Trường | Số chương trình |\n| --- | --- |\n"
    for result in results:
        output += f"| {result['truong']['ten_truong']} [{result['nguon']}] | {result['so_chuong_trinh_phu_hop']} |\n"
    for index in range(0, len(output), 35):
        await asyncio.sleep(0.08)
        yield "delta", {"text": output[index:index + 35]}


chat.danh_sach_model = preview_models
chat_stream.danh_sach_model = preview_models
chat_stream._provider = preview_provider
app = FastAPI(title="Chat UI fixture — no external AI calls")
app.include_router(chat.router, prefix="/api/v1")
register_request_logging(app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=13060)
