import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.chat import TaiLieuItem

ALLOWED_SUFFIXES = {".json", ".txt"}
MAX_CONTEXT_CHARS = 100_000
MAX_FILE_CHARS = 40_000


def tai_lieu_root() -> Path:
    configured = settings.tai_lieu_dir.strip()
    path = Path(configured) if configured else Path("tai_lieu")
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def safe_name(filename: str) -> str:
    base = Path(filename or "").name.replace("\x00", "").strip()
    base = re.sub(r"[^\w.\- ]+", "_", base, flags=re.UNICODE)
    base = re.sub(r"\s+", " ", base).strip(" .")
    if not base or base.startswith("."):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ.")
    suffix = Path(base).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ nhận file .json hoặc .txt.",
        )
    if len(base) > 180:
        base = f"{Path(base).stem[:160].rstrip(' .')}{suffix}"
    return base


def resolve_inside(filename: str) -> Path:
    root = tai_lieu_root()
    path = (root / safe_name(filename)).resolve()
    if path.parent != root:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ.")
    return path


def list_tai_lieu() -> list[TaiLieuItem]:
    root = tai_lieu_root()
    items: list[TaiLieuItem] = []
    for path in root.iterdir():
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        stat = path.stat()
        items.append(
            TaiLieuItem(
                ten=path.name,
                kich_thuoc=stat.st_size,
                cap_nhat=datetime.fromtimestamp(stat.st_mtime),
            )
        )
    items.sort(key=lambda item: item.ten.lower())
    return items


def save_tai_lieu(filename: str, data: bytes) -> TaiLieuItem:
    if len(data) > settings.tai_lieu_max_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File vượt quá 2 MB.")
    if not data.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File trống.")

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File phải là văn bản UTF-8.",
        ) from exc

    path = resolve_inside(filename)
    if path.suffix.lower() == ".json":
        try:
            json.loads(text)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File JSON không hợp lệ.",
            ) from exc
    elif "\x00" in text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File không phải văn bản.")

    path = _unique_path(path)
    path.write_text(text, encoding="utf-8")
    stat = path.stat()
    return TaiLieuItem(
        ten=path.name,
        kich_thuoc=stat.st_size,
        cap_nhat=datetime.fromtimestamp(stat.st_mtime),
    )


def delete_tai_lieu(filename: str) -> None:
    path = resolve_inside(filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy tài liệu.")
    path.unlink()


def build_context(cau_hoi: str) -> tuple[str, list[str]]:
    root = tai_lieu_root()
    files = [
        path
        for path in root.iterdir()
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in ALLOWED_SUFFIXES
    ]
    if not files:
        return "", []

    question_tokens = _tokens(cau_hoi)
    ranked: list[tuple[int, str, str]] = []
    for path in files:
        text = _read_for_prompt(path)
        score = len(question_tokens & _tokens(text[:20_000]))
        ranked.append((score, path.name, text))
    ranked.sort(key=lambda item: (-item[0], item[1].lower()))

    chunks: list[str] = []
    used: list[str] = []
    remaining = MAX_CONTEXT_CHARS
    for _score, name, text in ranked:
        if remaining < 400:
            break
        piece = text
        clipped = False
        if len(piece) > min(MAX_FILE_CHARS, remaining):
            piece = piece[: min(MAX_FILE_CHARS, remaining)].rstrip()
            clipped = True
        note = " (đã cắt bớt vì quá dài)" if clipped else ""
        chunks.append(f"### {name}{note}\n{piece}")
        used.append(name)
        remaining -= len(piece)
    return "\n\n".join(chunks), used


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    index = 2
    while True:
        candidate = path.with_name(f"{stem}-{index}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def _read_for_prompt(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if path.suffix.lower() != ".json":
        return text
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text
    compact = json.dumps(parsed, ensure_ascii=False, separators=(",", ":"))
    if len(compact) <= 8_000:
        return json.dumps(parsed, ensure_ascii=False, indent=2)
    return compact


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"\w+", text.lower(), flags=re.UNICODE) if len(token) > 1}
