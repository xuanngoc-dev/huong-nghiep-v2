"""Đọc JSON tuyển sinh trong thư mục TAI_LIEU_DIR để kiểm tra trên giao diện."""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import HTTPException, status

from app.schemas.kiem_tra_du_lieu import TruongTuyenSinhTomTat
from app.services.tai_lieu import tai_lieu_root


def danh_sach_truong() -> list[TruongTuyenSinhTomTat]:
    return list(_corpus(str(tai_lieu_root()), _signature(tai_lieu_root())).items)


def noi_dung_truong(ten_tep: str) -> dict:
    name = _ten_tep_hop_le(ten_tep)
    corpus = _corpus(str(tai_lieu_root()), _signature(tai_lieu_root()))
    item = next((row for row in corpus.items if row.ten_tep == name), None)
    if item is None or name not in corpus.files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy dữ liệu trường.")
    data = corpus.files[name]
    if data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File JSON không hợp lệ.")
    return {"ten_tep": name, "hop_le": item.hop_le, "du_lieu": data}


def _ten_tep_hop_le(ten_tep: str) -> str:
    name = (ten_tep or "").strip()
    if (
        not name
        or "/" in name
        or "\\" in name
        or name != Path(name).name
        or name.startswith(".")
        or Path(name).suffix.lower() != ".json"
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên file không hợp lệ.")
    return name


def _signature(root: Path) -> tuple:
    rows = []
    if not root.exists():
        return tuple()
    for path in sorted(root.iterdir(), key=lambda item: item.name.lower()):
        if not path.is_file() or path.is_symlink() or path.name.startswith(".") or path.suffix.lower() != ".json":
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        rows.append((path.name, stat.st_mtime_ns, stat.st_size))
    return tuple(rows)


class _Corpus:
    def __init__(self, items: tuple[TruongTuyenSinhTomTat, ...], files: dict) -> None:
        self.items = items
        self.files = files


@lru_cache(maxsize=2)
def _corpus(root: str, signature: tuple) -> _Corpus:
    items: list[TruongTuyenSinhTomTat] = []
    files: dict = {}
    base = Path(root)
    for name, _, _ in signature:
        path = base / name
        try:
            parsed = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            items.append(_tom_tat(name, None))
            files[name] = None
            continue
        files[name] = parsed
        items.append(_tom_tat(name, parsed))
    items.sort(key=lambda item: (item.ten_truong.lower(), item.ten_tep.lower()))
    return _Corpus(tuple(items), files)


def _tom_tat(name: str, data) -> TruongTuyenSinhTomTat:
    school = data.get("truong") if isinstance(data, dict) and isinstance(data.get("truong"), dict) else {}
    records = data.get("danh_sach_nganh") if isinstance(data, dict) else None
    so_nganh, so_ban_ghi, so_phuong_thuc = _dem(records)
    ten = school.get("ten_truong")
    ten_truong = ten.strip() if isinstance(ten, str) and ten.strip() else Path(name).stem
    ma = school.get("ma_truong")
    loai = school.get("loai_hinh")
    return TruongTuyenSinhTomTat(
        ten_tep=name,
        ma_truong=str(ma).strip() if ma is not None else "",
        ten_truong=ten_truong,
        loai_hinh=loai.strip() if isinstance(loai, str) and loai.strip() else None,
        nam_tuyen_sinh=_nam(school.get("nam_tuyen_sinh")),
        so_nganh=so_nganh,
        so_phuong_thuc=so_phuong_thuc,
        so_ban_ghi_phuong_thuc=so_ban_ghi,
        hop_le=_hop_le(data),
    )


def _hop_le(data) -> bool:
    if not isinstance(data, dict):
        return False
    school = data.get("truong")
    records = data.get("danh_sach_nganh")
    if not isinstance(school, dict) or not isinstance(school.get("ten_truong"), str) or not school["ten_truong"].strip():
        return False
    if not isinstance(records, list):
        return False
    for record in records:
        if not isinstance(record, dict):
            return False
        methods = record.get("phuong_thuc_tuyen_sinh", [])
        if methods is None:
            continue
        if not isinstance(methods, list) or any(not isinstance(method, dict) for method in methods):
            return False
    return True


def _dem(records) -> tuple[int, int, int]:
    if not isinstance(records, list):
        return 0, 0, 0
    so_nganh = 0
    so_ban_ghi = 0
    nhom: set[tuple[str, str, str]] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        so_nganh += 1
        methods = record.get("phuong_thuc_tuyen_sinh") or []
        if not isinstance(methods, list):
            continue
        for method in methods:
            if not isinstance(method, dict):
                continue
            so_ban_ghi += 1
            nhom.add(
                (
                    str(method.get("ma_phuong_thuc") or ""),
                    str(method.get("ten_phuong_thuc") or ""),
                    str(method.get("loai_phuong_thuc") or ""),
                )
            )
    return so_nganh, so_ban_ghi, len(nhom)


def _nam(value) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None
