import io
import ipaddress
import mimetypes
import re
import shutil
import socket
import tarfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote, unquote, urljoin, urlparse

import httpx

from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.thu_vien import ThuVienItem

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_SUFFIXES = {".mp4", ".webm", ".mov", ".m4v"}
ARCHIVE_SUFFIXES = {
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".tgz",
    ".bz2",
    ".tbz2",
    ".xz",
    ".txz",
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
}
ALLOWED_SUFFIXES = IMAGE_SUFFIXES | VIDEO_SUFFIXES | ARCHIVE_SUFFIXES
_COMPOUND_SUFFIXES = (".tar.gz", ".tar.bz2", ".tar.xz", ".tgz", ".tbz2", ".txz")
_FORBIDDEN = re.compile(r'[\x00-\x1f\\/:*?"<>|]')
_CHUNK = 1024 * 1024
_MAX_EXTRACT_BYTES = 500 * 1024 * 1024
_MAX_EXTRACT_FILES = 2000


def thu_vien_root() -> Path:
    """Thư mục lưu ảnh, video, file nén và thư mục con. Mặc định là backend/thu_vien."""
    configured = settings.thu_vien_dir.strip()
    base = Path(__file__).resolve().parents[2]
    path = Path(configured) if configured else base / "thu_vien"
    if not path.is_absolute():
        path = base / path
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def media_type_for(filename: str) -> str:
    suffix = _suffix(filename)
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".png":
        return "image/png"
    if suffix == ".gif":
        return "image/gif"
    if suffix == ".webp":
        return "image/webp"
    if suffix in {".mp4", ".m4v"}:
        return "video/mp4"
    if suffix == ".webm":
        return "video/webm"
    if suffix == ".mov":
        return "video/quicktime"
    if suffix == ".zip":
        return "application/zip"
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"


def list_thu_vien(thu_muc: str = "") -> list[ThuVienItem]:
    directory = _require_dir(thu_muc)
    root = thu_vien_root()
    items: list[ThuVienItem] = []
    for path in directory.iterdir():
        if path.name.startswith(".") or path.is_symlink():
            continue
        if not path.is_file() and not path.is_dir():
            continue
        items.append(_item(path, root))
    items.sort(key=lambda item: (not item.la_thu_muc, item.ten.lower()))
    return items


_CONTENT_SUFFIX = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/quicktime": ".mov",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
    "application/vnd.rar": ".rar",
    "application/x-rar-compressed": ".rar",
    "application/x-7z-compressed": ".7z",
    "application/gzip": ".gz",
    "application/x-tar": ".tar",
    "application/x-bzip2": ".bz2",
    "application/x-xz": ".xz",
}


def save_thu_vien(filename: str, source: BinaryIO, thu_muc: str = "") -> ThuVienItem:
    directory = _require_dir(thu_muc)
    stored = _upload_name(filename)
    path = _unique_path(directory, stored)
    try:
        _write_checked(path, source)
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return _item(path, thu_vien_root())


def tai_tu_url(url: str, thu_muc: str = "") -> ThuVienItem:
    """Tải file từ URL công khai và lưu như một lần upload từ thiết bị."""
    current = _public_http_url(url)
    content = bytearray()
    filename = "tep"
    redirects = 0
    timeout = httpx.Timeout(20.0, read=120.0)
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        while True:
            with client.stream(
                "GET",
                current,
                headers={"User-Agent": "DinhHuongNghe/thu-vien"},
            ) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    redirects += 1
                    if redirects > 5:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="URL chuyển hướng quá nhiều lần.",
                        )
                    location = response.headers.get("location")
                    if not location:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="URL chuyển hướng không hợp lệ.",
                        )
                    current = _public_http_url(urljoin(current, location))
                    continue
                if response.status_code >= 400:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Không tải được file từ URL.",
                    )
                filename = _name_from_download(response.headers, current)
                for chunk in response.iter_bytes():
                    if not chunk:
                        continue
                    content.extend(chunk)
                    if len(content) > settings.thu_vien_max_bytes:
                        mb = settings.thu_vien_max_bytes // (1024 * 1024)
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File vượt quá dung lượng tối đa ({mb} MB).",
                        )
                break
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File trống.")
    return save_thu_vien(filename, io.BytesIO(bytes(content)), thu_muc)


def resolve_thu_vien(relative: str) -> Path:
    path = _resolve(relative, allow_root=False)
    if path.is_symlink() or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy file.")
    return path


def delete_thu_vien(relative: str) -> None:
    path = _resolve(relative, allow_root=False)
    if path.is_symlink() or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục cần xóa.")
    if path.is_dir():
        shutil.rmtree(path)
        return
    path.unlink()


def tao_thu_muc(thu_muc: str, ten: str) -> ThuVienItem:
    parent = _require_dir(thu_muc)
    name = _clean_name(ten)
    path = parent / name
    if path.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên thư mục đã tồn tại.")
    path.mkdir(parents=False)
    return _item(path, thu_vien_root())


def doi_ten(relative: str, ten_moi: str) -> ThuVienItem:
    path = _resolve(relative, allow_root=False)
    if path.is_symlink() or not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục cần đổi tên.")
    name = _clean_name(ten_moi)
    target = path.with_name(name)
    if target.exists():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên mới đã tồn tại.")
    path.rename(target)
    return _item(target, thu_vien_root())


def nen_muc(thu_muc: str, danh_sach: list[str], ten_tep: str) -> ThuVienItem:
    directory = _require_dir(thu_muc)
    root = thu_vien_root()
    paths = [_child_of(directory, item) for item in danh_sach]
    name = _clean_name(ten_tep)
    if not name.lower().endswith(".zip"):
        name = f"{name}.zip"
    destination = _unique_path(directory, name)
    total = 0
    files: list[tuple[Path, str]] = []
    for path in paths:
        if path.resolve() == destination.resolve():
            continue
        files.extend(_collect_files(path, path.name))
    for file_path, _arc in files:
        total += file_path.stat().st_size
        if total > _MAX_EXTRACT_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dung lượng các mục được chọn vượt quá 500 MB.",
            )
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không có file để nén.")
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path, arcname in files:
            archive.write(file_path, arcname)
    return _item(destination, root)


def sao_chep(danh_sach: list[str], thu_muc_dich: str) -> int:
    return _dat_vao(danh_sach, thu_muc_dich, di_chuyen=False)


def di_chuyen(danh_sach: list[str], thu_muc_dich: str) -> int:
    return _dat_vao(danh_sach, thu_muc_dich, di_chuyen=True)


def xoa_nhieu(danh_sach: list[str]) -> int:
    paths = _without_nested(_existing_sources(danh_sach))
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    if not paths:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục cần xóa.")
    return len(paths)


def giai_nen(relative: str) -> ThuVienItem:
    path = _resolve(relative, allow_root=False)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chỉ giải nén được file nén.")
    suffix = _suffix(path.name)
    if suffix not in ARCHIVE_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File không phải định dạng nén được hỗ trợ.")
    destination = _unique_path(path.parent, path.name[: -len(suffix)] or "giai-nen")
    destination.mkdir()
    try:
        if suffix == ".zip":
            _extract_zip(path, destination)
        elif suffix in {".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz", ".gz", ".bz2", ".xz"}:
            _extract_tar(path, destination)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hiện giải nén được ZIP và TAR. File RAR hoặc 7Z vẫn lưu được trong thư viện.",
            )
    except HTTPException:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(destination, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không giải nén được file.",
        ) from exc
    return _item(destination, thu_vien_root())


def _write_checked(path: Path, source: BinaryIO) -> None:
    written = 0
    header = b""
    with path.open("wb") as target:
        while True:
            chunk = source.read(_CHUNK)
            if not chunk:
                break
            written += len(chunk)
            if written > settings.thu_vien_max_bytes:
                mb = settings.thu_vien_max_bytes // (1024 * 1024)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File vượt quá dung lượng tối đa ({mb} MB).",
                )
            if len(header) < 512:
                header += chunk[: 512 - len(header)]
            target.write(chunk)
    if written == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File trống.")
    if not _matches_signature(_suffix(path.name), header):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nội dung file không khớp định dạng ảnh, video hoặc file nén.",
        )


def _extract_zip(path: Path, destination: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        members = [info for info in archive.infolist() if not info.is_dir()]
        _guard_extract(sum(info.file_size for info in members), len(members))
        for info in members:
            relative = _safe_archive_name(info.filename)
            if relative is None or relative.parts[:1] == ("__MACOSX",):
                continue
            target = _within(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def _extract_tar(path: Path, destination: Path) -> None:
    try:
        archive = tarfile.open(path)
    except tarfile.TarError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File nén không hợp lệ.") from exc
    with archive:
        members = [info for info in archive.getmembers() if info.isfile()]
        _guard_extract(sum(max(info.size, 0) for info in members), len(members))
        for info in members:
            relative = _safe_archive_name(info.name)
            if relative is None:
                continue
            target = _within(destination, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(info)
            if source is None:
                continue
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)


def _guard_extract(total: int, count: int) -> None:
    if count > _MAX_EXTRACT_FILES or total > _MAX_EXTRACT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File nén quá lớn hoặc có quá nhiều file bên trong.",
        )


def _safe_archive_name(name: str) -> Path | None:
    raw = (name or "").replace("\\", "/").strip("/")
    if not raw:
        return None
    parts: list[str] = []
    for part in raw.split("/"):
        if part in {"", "."}:
            continue
        if part == ".." or part.startswith(".") or _FORBIDDEN.search(part):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File nén chứa đường dẫn không an toàn.")
        parts.append(part)
    if not parts:
        return None
    return Path(*parts)


def _collect_files(path: Path, arc_prefix: str) -> list[tuple[Path, str]]:
    if path.is_symlink():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không nén liên kết.")
    if path.is_file():
        return [(path, arc_prefix)]
    found: list[tuple[Path, str]] = []
    for child in path.rglob("*"):
        if child.is_symlink() or any(part.startswith(".") for part in child.relative_to(path).parts):
            continue
        if child.is_file():
            found.append((child, f"{arc_prefix}/{child.relative_to(path).as_posix()}"))
    return found


def _dat_vao(danh_sach: list[str], thu_muc_dich: str, *, di_chuyen: bool) -> int:
    destination = _require_dir(thu_muc_dich)
    sources = _without_nested(_existing_sources(danh_sach))
    done = 0
    for source in sources:
        if source == destination or source in destination.parents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể chuyển một thư mục vào chính nó hoặc thư mục con của nó.",
            )
        if di_chuyen and source.parent == destination:
            continue
        target = _unique_path(destination, source.name)
        if di_chuyen:
            shutil.move(source, target)
        elif source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        done += 1
    if done == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không có mục nào cần dán.")
    return done


def _existing_sources(danh_sach: list[str]) -> list[Path]:
    paths: list[Path] = []
    for relative in danh_sach:
        path = _resolve(relative, allow_root=False)
        if path.is_symlink() or not path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục đã chọn.")
        paths.append(path)
    return paths


def _without_nested(paths: list[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return [path for path in unique if not any(path != other and other in path.parents for other in unique)]


def _child_of(directory: Path, relative: str) -> Path:
    path = _resolve(relative, allow_root=False)
    if path.parent != directory:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ nén được các mục đang mở trong thư mục hiện tại.",
        )
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy mục cần nén.")
    return path


def _require_dir(relative: str) -> Path:
    path = thu_vien_root() if not (relative or "").strip() else _resolve(relative, allow_root=False)
    if path.is_symlink() or not path.is_dir():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thư mục.")
    return path


def _resolve(relative: str, *, allow_root: bool) -> Path:
    root = thu_vien_root()
    parts = _parts(relative)
    if not parts:
        if allow_root:
            return root
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đường dẫn không hợp lệ.")
    path = root.joinpath(*parts).resolve()
    if path != root and root not in path.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đường dẫn không hợp lệ.")
    return path


def _within(root: Path, relative: Path) -> Path:
    path = (root / relative).resolve()
    if path != root and root not in path.parents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File nén chứa đường dẫn không an toàn.")
    return path


def _parts(relative: str) -> list[str]:
    raw = (relative or "").strip().replace("\\", "/").strip("/")
    if not raw:
        return []
    parts: list[str] = []
    for part in raw.split("/"):
        if part in {"", "."}:
            continue
        if part == ".." or part.startswith(".") or _FORBIDDEN.search(part):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đường dẫn không hợp lệ.")
        parts.append(part)
    return parts


def _clean_name(name: str) -> str:
    base = Path(name or "").name.replace("\x00", "")
    base = _FORBIDDEN.sub("", base)
    base = re.sub(r"\s+", " ", base).strip(" .")
    if not base or base in {".", ".."} or base.startswith("."):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tên không hợp lệ.")
    return base[:180]


def _public_http_url(url: str) -> str:
    raw = (url or "").strip()
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ nhận URL http hoặc https.",
        )
    host = parsed.hostname.strip("[]")
    if host.lower() in {"localhost"} or host.lower().endswith(".local"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không tải file từ địa chỉ nội bộ.",
        )
    try:
        ipaddress.ip_address(host)
        addresses = [host]
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, parsed.port or 0)
        except socket.gaierror as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không phân giải được URL.",
            ) from exc
        addresses = [item[4][0] for item in infos]
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if any(
            (
                ip.is_private,
                ip.is_loopback,
                ip.is_link_local,
                ip.is_reserved,
                ip.is_multicast,
                ip.is_unspecified,
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không tải file từ địa chỉ nội bộ.",
            )
    return raw


def _name_from_download(headers, url: str) -> str:
    disposition = headers.get("content-disposition", "")
    match = re.search(r"filename\*=UTF-8''([^;]+)|filename=\"?([^\";]+)\"?", disposition, re.IGNORECASE)
    if match:
        picked = unquote((match.group(1) or match.group(2) or "").strip())
        if picked:
            return Path(picked).name
    path_name = unquote(Path(urlparse(url).path).name)
    content_type = headers.get("content-type", "").split(";", 1)[0].strip().lower()
    suffix = _CONTENT_SUFFIX.get(content_type, "")
    if path_name and _suffix(path_name) in ALLOWED_SUFFIXES:
        return path_name
    stem = Path(path_name).stem if path_name else "tep"
    return f"{stem or 'tep'}{suffix}" if suffix else (path_name or "tep")


def _upload_name(filename: str) -> str:
    base = _clean_name(filename)
    if _suffix(base) not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chỉ nhận ảnh, video hoặc file nén ZIP, RAR, 7Z, TAR.",
        )
    return base


def _unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    suffix = _suffix(filename)
    stem = filename[: -len(suffix)] if suffix else filename
    index = 2
    while True:
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def _suffix(filename: str) -> str:
    lower = filename.lower()
    for suffix in _COMPOUND_SUFFIXES:
        if lower.endswith(suffix):
            return suffix
    return Path(lower).suffix


def _matches_signature(suffix: str, header: bytes) -> bool:
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix == ".gif":
        return header.startswith((b"GIF87a", b"GIF89a"))
    if suffix == ".webp":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    if suffix == ".webm":
        return header.startswith(b"\x1a\x45\xdf\xa3")
    if suffix in {".mp4", ".m4v", ".mov"}:
        return len(header) >= 8 and header[4:8] == b"ftyp"
    if suffix == ".zip":
        return header.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
    if suffix == ".rar":
        return header.startswith(b"Rar!")
    if suffix == ".7z":
        return header.startswith(b"7z\xbc\xaf'\x1c")
    if suffix in {".gz", ".tgz", ".tar.gz"}:
        return header.startswith(b"\x1f\x8b")
    if suffix in {".bz2", ".tbz2", ".tar.bz2"}:
        return header.startswith(b"BZh")
    if suffix in {".xz", ".txz", ".tar.xz"}:
        return header.startswith(b"\xfd7zXZ\x00")
    if suffix == ".tar":
        return len(header) >= 262 and header[257:262] == b"ustar"
    return False


def _loai(path: Path) -> str:
    if path.is_dir():
        return "thu_muc"
    suffix = _suffix(path.name)
    if suffix in IMAGE_SUFFIXES:
        return "hinh_anh"
    if suffix in VIDEO_SUFFIXES:
        return "video"
    if suffix in ARCHIVE_SUFFIXES:
        return "nen"
    return "tep"


def _item(path: Path, root: Path) -> ThuVienItem:
    stat = path.stat()
    relative = path.relative_to(root).as_posix()
    kind = _loai(path)
    public = None
    if path.is_file():
        encoded = "/".join(quote(part) for part in Path(relative).parts)
        public = f"{settings.api_v1_prefix}/thu-vien/tep/{encoded}"
    return ThuVienItem(
        ten=path.name,
        duong_dan_tuong_doi=relative,
        loai=kind,  # type: ignore[arg-type]
        la_thu_muc=path.is_dir(),
        kich_thuoc=None if path.is_dir() else stat.st_size,
        duong_dan=public,
        cap_nhat=datetime.fromtimestamp(stat.st_mtime),
    )
