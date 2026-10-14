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
    """Xây dựng ngữ cảnh từ tài liệu tuyển sinh (data_dh_json hoặc thư mục tai_lieu).
    Hỗ trợ trích xuất thông minh cho dữ liệu JSON tuyển sinh 4 tầng (trường, ngành, phương thức, tổ hợp)
    và trích xuất tổng quát cho file văn bản khác.
    """
    root = tai_lieu_root()
    if not root.exists():
        return "", []

    files = [
        path
        for path in root.iterdir()
        if path.is_file() and not path.name.startswith(".") and path.suffix.lower() in ALLOWED_SUFFIXES
    ]
    if not files:
        return "", []

    q_lower = cau_hoi.lower()
    q_tokens = _tokens(cau_hoi)

    ranked: list[tuple[int, str, str]] = []

    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace").strip()
        except OSError:
            continue

        if path.suffix.lower() == ".json":
            score, piece = _process_admission_json(path, text, q_lower, q_tokens)
            if piece:
                ranked.append((score, path.name, piece))
                continue

        # File txt hoặc JSON thông thường
        score = len(q_tokens & _tokens(text[:30_000]))
        ranked.append((score, path.name, text))

    ranked.sort(key=lambda item: (-item[0], item[1].lower()))

    chunks: list[str] = []
    used: list[str] = []
    remaining = MAX_CONTEXT_CHARS

    for score, name, text in ranked:
        if remaining < 400:
            break
        # Nếu điểm bằng 0 khi đã có các file khớp tốt hơn thì bỏ qua
        if score == 0 and len(used) >= 2:
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


def _process_admission_json(
    path: Path, raw_text: str, q_lower: str, q_tokens: set[str]
) -> tuple[int, str]:
    """Phân tích dữ liệu JSON tuyển sinh đại học để trích xuất ngữ cảnh chính xác nhất."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return 0, raw_text[:MAX_FILE_CHARS]

    if not (isinstance(data, dict) and "truong" in data and "danh_sach_nganh" in data):
        # JSON thông thường
        score = len(q_tokens & _tokens(raw_text[:30_000]))
        return score, raw_text[:MAX_FILE_CHARS]

    truong = data.get("truong", {})
    ma_truong = str(truong.get("ma_truong", "")).strip().lower()
    ten_truong = str(truong.get("ten_truong", "")).strip().lower()

    uni_score = 0
    # Khớp mã trường (vd: NEU, HUST, BKA, UTE, PTIT...)
    if ma_truong and ma_truong in q_lower:
        uni_score += 150

    # Khớp từ khóa tên trường
    school_words = [
        w for w in re.findall(r"\w+", ten_truong)
        if len(w) > 2 and w not in ("trường", "đại", "học", "thành", "phố", "tỉnh")
    ]
    overlap_school = [w for w in school_words if w in q_tokens]
    if len(overlap_school) >= 2:
        uni_score += 60 + len(overlap_school) * 15
    elif len(overlap_school) == 1 and overlap_school[0] in ("neu", "hust", "ueh", "ptit", "ute", "hub"):
        uni_score += 100

    nganh_list = data.get("danh_sach_nganh", [])
    matched_nganh: list[dict] = []

    for ng in nganh_list:
        ten_ng = str(ng.get("ten_nganh", "")).lower()
        ma_ng = str(ng.get("ma_nganh", "")).lower()
        ma_xt = str(ng.get("ma_xet_tuyen", "")).lower()

        if ma_ng and ma_ng in q_lower:
            matched_nganh.append(ng)
            continue
        if ma_xt and ma_xt in q_lower:
            matched_nganh.append(ng)
            continue
        if len(ten_ng) > 3 and ten_ng in q_lower:
            matched_nganh.append(ng)
            continue

        ng_words = [w for w in re.findall(r"\w+", ten_ng) if len(w) > 2 and w not in ("ngành", "chuyên", "nghiệp")]
        if len(ng_words) >= 2:
            ov = [w for w in ng_words if w in q_tokens]
            if len(ov) >= len(ng_words) * 0.7:
                matched_nganh.append(ng)

    total_score = uni_score + len(matched_nganh) * 20

    # Nếu không khớp trường và không khớp ngành nào, trả về điểm overlap thông thường
    if total_score == 0:
        base_score = len(q_tokens & _tokens(raw_text[:20_000]))
        return base_score, ""

    # Tạo đối tượng ngữ cảnh tối ưu
    if matched_nganh:
        # Giới hạn số ngành nếu trùng quá nhiều
        selected_nganh = matched_nganh[:15]
        context_dict = {
            "truong": truong,
            "nganh_phu_hop": selected_nganh,
        }
    else:
        # Câu hỏi chung về trường: gửi thông tin trường + danh mục tất cả các ngành (tên, mã, chỉ tiêu)
        summary_nganh = [
            {
                "ma_nganh": ng.get("ma_nganh"),
                "ma_xet_tuyen": ng.get("ma_xet_tuyen"),
                "ten_nganh": ng.get("ten_nganh"),
                "chi_tieu_nganh": ng.get("chi_tieu_nganh"),
            }
            for ng in nganh_list
        ]
        context_dict = {
            "truong": truong,
            "danh_sach_tat_ca_nganh": summary_nganh,
        }

    compact = json.dumps(context_dict, ensure_ascii=False, separators=(",", ":"))
    return total_score, compact


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
