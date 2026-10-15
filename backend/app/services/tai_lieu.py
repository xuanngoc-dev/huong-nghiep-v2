import json
import re
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.chat import TaiLieuItem, TinNhan

ALLOWED_SUFFIXES = {".json", ".txt"}
MAX_CONTEXT_CHARS = 100_000
MAX_FILE_CHARS = 40_000


def tai_lieu_root() -> Path:
    """Trả về thư mục tài liệu:
    1. Ưu tiên thư mục cấu hình trong settings.tai_lieu_dir (nếu có).
    2. Nếu không cấu hình: tự động trỏ đến data_dh_json ở thư mục gốc nếu tồn tại.
    3. Fallback về backend/tai_lieu.
    """
    configured = settings.tai_lieu_dir.strip()
    base_backend = Path(__file__).resolve().parents[2]
    base_root = Path(__file__).resolve().parents[3]

    if configured:
        p = Path(configured)
        if p.is_absolute() and p.exists() and p.is_dir():
            return p.resolve()
        for candidate in (base_root / configured, base_backend / configured, Path(configured)):
            if candidate.exists() and candidate.is_dir():
                return candidate.resolve()

    # Mặc định: kiểm tra thư mục data_dh_json ở thư mục gốc
    default_data_dh = base_root / "data_dh_json"
    if default_data_dh.exists() and default_data_dh.is_dir():
        return default_data_dh.resolve()

    # Fallback về backend/tai_lieu
    fallback = base_backend / "tai_lieu"
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback.resolve()


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
    if not root.exists():
        return items

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
        mb = settings.tai_lieu_max_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File vượt quá dung lượng tối đa ({mb} MB).",
        )
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
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File JSON không hợp lệ.",
            ) from exc
        if isinstance(parsed, dict) and "truong" in parsed and "danh_sach_nganh" in parsed:
            from app.services.tra_cuu_tuyen_sinh import valid_admission_data

            if not valid_admission_data(parsed):
                raise HTTPException(status_code=400, detail="Cấu trúc tuyển sinh không hợp lệ: kiểm tra trường, danh sách ngành, phương thức và tổ hợp.")
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


def build_context(cau_hoi: str, lich_su: list[TinNhan] | None = None) -> tuple[str, list[str]]:
    from app.services.tra_cuu_tuyen_sinh import search

    result = search(cau_hoi, lich_su)
    return result.context, result.files


def _unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
        index += 1
