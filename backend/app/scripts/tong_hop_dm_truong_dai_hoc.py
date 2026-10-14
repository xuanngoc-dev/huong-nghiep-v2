"""Tổng hợp danh sách trường cao đẳng, học viện, đại học để import dm_truong_dai_hoc.

Nguồn mã trường, tên, tỉnh/thành và website:

- https://daihoc.com.vn/danh-ba-truong (đại học, học viện)
- https://caodang.com.vn/danh-ba-truong (cao đẳng)

Địa chỉ cơ sở chính lấy thêm từ danh sách cơ sở được công nhận của VN-NARIC
khi bản ghi không thuộc cụm dữ liệu bị lặp sai (cùng mã DAC, địa chỉ Sơn Tây,
website hcmiu.edu.vn).

Email, điện thoại, học phí, năm thành lập và tên viết tắt không có dạng dữ liệu
ổn định trên các nguồn này nên để null.

Chạy từ thư mục backend (máy này không có lệnh python ở ngoài virtualenv):

    .venv/bin/python -m app.scripts.tong_hop_dm_truong_dai_hoc
    .venv/bin/python -m app.scripts.tong_hop_dm_truong_dai_hoc --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

import httpx

USER_AGENT = (
    "Mozilla/5.0 (compatible; dinh-huong-nghe/dm-truong-dai-hoc; +https://localhost)"
)
SITEMAPS = (
    "https://daihoc.com.vn/sitemap-danh-ba-truong.xml",
    "https://caodang.com.vn/sitemap-danh-ba-truong.xml",
)
NARIC_URL = "http://en.naric.edu.vn/vietnam-recognised-bodies"

_ROW_RE = re.compile(
    r"<tr>\s*"
    r"<td>\s*(?P<stt>\d+)\s*</td>\s*"
    r"<td>\s*(?P<code>.*?)\s*</td>\s*"
    r"<td>\s*(?P<name>.*?)\s*</td>\s*"
    r"<td>\s*(?P<english>.*?)\s*</td>\s*"
    r"<td>\s*(?P<address>.*?)\s*</td>\s*"
    r"<td>\s*(?:<a\s+href=\"(?P<url>[^\"]*)\"[^>]*>.*?</a>)?\s*</td>\s*"
    r"</tr>",
    re.IGNORECASE | re.DOTALL,
)
_H1_RE = re.compile(r"<h1>\s*(.*?)\s*</h1>", re.DOTALL)
_EN_RE = re.compile(r"</h1>\s*<p>\s*(.*?)\s*</p>", re.DOTALL)
_CODE_RE = re.compile(
    r"<span>\s*Mã tuyển sinh\s*</span>\s*<b>\s*([^<]+?)\s*</b>",
    re.DOTALL,
)
_PROVINCE_RE = re.compile(
    r"<span>\s*Tỉnh,\s*thành\s*</span>\s*<b>\s*(.*?)\s*</b>",
    re.DOTALL,
)
_LEVEL_RE = re.compile(
    r"<span>\s*Loại hình\s*</span>\s*<b>\s*([^<]+?)\s*</b>",
    re.DOTALL,
)
_WEB_RE = re.compile(r'data-out="([^"]+)"\s+data-k="web"')
_VIETNAMESE_RE = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]",
    re.IGNORECASE,
)
_LOWER_NAME_WORDS = frozenset(
    {"và", "của", "với", "các", "cho", "tại", "trong", "về", "học", "đẳng", "viện"}
)

_KHU_VUC_ALIASES: tuple[tuple[str, str], ...] = (
    ("thừa thiên huế", "Thừa Thiên Huế"),
    ("thua thien hue", "Thừa Thiên Huế"),
    ("bà rịa - vũng tàu", "Bà Rịa - Vũng Tàu"),
    ("bà rịa – vũng tàu", "Bà Rịa - Vũng Tàu"),
    ("ba ria - vung tau", "Bà Rịa - Vũng Tàu"),
    ("bà rịa vũng tàu", "Bà Rịa - Vũng Tàu"),
    ("thành phố hồ chí minh", "Hồ Chí Minh"),
    ("tp. hồ chí minh", "Hồ Chí Minh"),
    ("tp hồ chí minh", "Hồ Chí Minh"),
    ("ho chi minh city", "Hồ Chí Minh"),
    ("hồ chí minh", "Hồ Chí Minh"),
    ("ho chi minh", "Hồ Chí Minh"),
    ("tp.hcm", "Hồ Chí Minh"),
    ("tphcm", "Hồ Chí Minh"),
    ("đắk lắk", "Đắk Lắk"),
    ("đăk lăk", "Đắk Lắk"),
    ("dak lak", "Đắk Lắk"),
    ("đắk nông", "Đắk Nông"),
    ("hà nội", "Hà Nội"),
    ("ha noi", "Hà Nội"),
    ("hanoi", "Hà Nội"),
    ("hải phòng", "Hải Phòng"),
    ("hai phong", "Hải Phòng"),
    ("đà nẵng", "Đà Nẵng"),
    ("da nang", "Đà Nẵng"),
    ("cần thơ", "Cần Thơ"),
    ("can tho", "Cần Thơ"),
    ("an giang", "An Giang"),
    ("bắc giang", "Bắc Giang"),
    ("bắc kạn", "Bắc Kạn"),
    ("bắc ninh", "Bắc Ninh"),
    ("bến tre", "Bến Tre"),
    ("bình định", "Bình Định"),
    ("bình dương", "Bình Dương"),
    ("bình phước", "Bình Phước"),
    ("bình thuận", "Bình Thuận"),
    ("cà mau", "Cà Mau"),
    ("cao bằng", "Cao Bằng"),
    ("điện biên", "Điện Biên"),
    ("đồng nai", "Đồng Nai"),
    ("đồng tháp", "Đồng Tháp"),
    ("gia lai", "Gia Lai"),
    ("hà giang", "Hà Giang"),
    ("hà nam", "Hà Nam"),
    ("hà tĩnh", "Hà Tĩnh"),
    ("hải dương", "Hải Dương"),
    ("hậu giang", "Hậu Giang"),
    ("hòa bình", "Hòa Bình"),
    ("hưng yên", "Hưng Yên"),
    ("khánh hòa", "Khánh Hòa"),
    ("khánh hoà", "Khánh Hòa"),
    ("kiên giang", "Kiên Giang"),
    ("kon tum", "Kon Tum"),
    ("lai châu", "Lai Châu"),
    ("lâm đồng", "Lâm Đồng"),
    ("lạng sơn", "Lạng Sơn"),
    ("lào cai", "Lào Cai"),
    ("long an", "Long An"),
    ("nam định", "Nam Định"),
    ("nghệ an", "Nghệ An"),
    ("ninh bình", "Ninh Bình"),
    ("ninh thuận", "Ninh Thuận"),
    ("phú thọ", "Phú Thọ"),
    ("phú yên", "Phú Yên"),
    ("quảng bình", "Quảng Bình"),
    ("quảng nam", "Quảng Nam"),
    ("quảng ngãi", "Quảng Ngãi"),
    ("quảng ninh", "Quảng Ninh"),
    ("quảng trị", "Quảng Trị"),
    ("sóc trăng", "Sóc Trăng"),
    ("sơn la", "Sơn La"),
    ("tây ninh", "Tây Ninh"),
    ("thái bình", "Thái Bình"),
    ("thái nguyên", "Thái Nguyên"),
    ("thanh hóa", "Thanh Hóa"),
    ("thanh hoá", "Thanh Hóa"),
    ("tiền giang", "Tiền Giang"),
    ("trà vinh", "Trà Vinh"),
    ("tuyên quang", "Tuyên Quang"),
    ("vĩnh long", "Vĩnh Long"),
    ("vĩnh phúc", "Vĩnh Phúc"),
    ("yên bái", "Yên Bái"),
    ("huế", "Huế"),
)

_NHOM_NGANH_RULES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("y duoc", "y te", "dieu duong", "y khoa", "y hoc", "duoc"), "Y - Dược"),
    (("su pham", "giao duc"), "Giáo dục"),
    (("luat", "phap ly"), "Luật"),
    (("ngoai ngu", "ngoai giao", "ngon ngu"), "Ngoại ngữ"),
    (("nong nghiep", "lam nghiep", "thuy san", "nong lam"), "Nông - Lâm - Ngư"),
    (
        ("van hoa", "nghe thuat", "my thuat", "am nhac", "san khau", "dien anh"),
        "Văn hóa - Nghệ thuật",
    ),
    (("du lich", "khach san"), "Du lịch - Dịch vụ"),
    (
        ("cong an", "an ninh", "quan su", "quoc phong", "canh sat", "bien phong", "hau can"),
        "An ninh - Quốc phòng",
    ),
    (("kinh te", "tai chinh", "ngan hang", "thuong mai", "ke toan"), "Kinh tế"),
    (
        (
            "bach khoa",
            "ky thuat",
            "cong nghe",
            "cong nghiep",
            "xay dung",
            "giao thong",
            "kien truc",
            "dia chat",
            "dien luc",
            "hang hai",
            "hang khong",
        ),
        "Kỹ thuật - Công nghệ",
    ),
)


def fold(text: str) -> str:
    """Bỏ dấu và đưa về chữ thường để so khớp tên."""
    normalized = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    without_marks = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    lowered = without_marks.lower()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", lowered)).strip()


def _separate_camel(name: str) -> str:
    """Tách 'phạmLạng' thành 'phạm Lạng'. Không đụng tên viết HOA toàn bộ."""
    if len(name) < 2:
        return name
    chars = [name[0]]
    for prev, char in zip(name, name[1:]):
        if prev.islower() and char.isupper():
            chars.append(" ")
        chars.append(char)
    return "".join(chars)


def name_key(name: str) -> str:
    """Khóa so trùng: bỏ 'trường' đứng đầu và các từ địa danh viết tắt."""
    name = _separate_camel(name)
    folded = fold(name)
    folded = re.sub(r"\b(thanh pho|viet nam|tp)\b", " ", folded)
    folded = re.sub(r"^truong\s+", "", folded)
    return re.sub(r"\s+", " ", folded).strip()


def _plain(raw: str) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(raw))
    return re.sub(r"\s+", " ", text).strip()


def clean_code(raw: str | None) -> str:
    return re.sub(r"[^A-Z0-9]", "", (raw or "").strip().upper())[:20]


def is_target_school(name: str) -> bool:
    folded = f" {fold(name)} "
    if " trung cap " in folded or " trung hoc " in folded:
        if not any(token in folded for token in (" dai hoc ", " cao dang ", " hoc vien ")):
            return False
    if any(token in folded for token in (" dai hoc ", " hoc vien ", " cao dang ", " nhac vien ")):
        return True
    return bool(set(folded.split()) & {"dh", "cd", "hv"})


def normalize_school_name(name: str) -> str:
    cleaned = re.sub(r"\s+", " ", _separate_camel(name)).strip(" .")
    letters = [char for char in cleaned if char.isalpha()]
    if not letters:
        return cleaned
    if sum(char.isupper() for char in letters) / len(letters) < 0.8:
        return cleaned
    words: list[str] = []
    for index, word in enumerate(cleaned.lower().split(" ")):
        if index and word in _LOWER_NAME_WORDS:
            words.append(word)
            continue
        parts = re.split(r"([-–—/])", word)
        words.append(
            "".join(
                piece if piece in "-–—/" or not piece else piece[:1].upper() + piece[1:]
                for piece in parts
            )
        )
    return " ".join(words)


def extract_khu_vuc(address: str | None) -> str | None:
    if not address:
        return None
    lowered = address.casefold()
    spans: list[tuple[int, int, str]] = []
    for needle, canonical in _KHU_VUC_ALIASES:
        start = 0
        needle_folded = needle.casefold()
        while True:
            index = lowered.find(needle_folded, start)
            if index < 0:
                break
            spans.append((index, index + len(needle_folded), canonical))
            start = index + len(needle_folded)
    kept = [
        span
        for span in spans
        if not any(
            other[0] <= span[0]
            and other[1] >= span[1]
            and other[1] - other[0] > span[1] - span[0]
            for other in spans
        )
    ]
    if not kept:
        return None
    return max(kept, key=lambda span: (span[0], span[1] - span[0]))[2]


def infer_loai_hinh(name: str) -> str | None:
    folded = fold(name)
    if "dan lap" in folded:
        return "Dân lập"
    if "tu thuc" in folded:
        return "Tư thục"
    return None


def infer_nhom_nganh(name: str) -> str | None:
    folded = f" {fold(name)} "
    for phrases, label in _NHOM_NGANH_RULES:
        if any(f" {phrase} " in folded for phrase in phrases):
            return label
    if re.search(r"\by\b", folded):
        return "Y - Dược"
    return None


def _website_host(url: str | None) -> str | None:
    if not url:
        return None
    host = urlparse(unescape(url).strip()).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host or None


def clean_website(url: str | None) -> str | None:
    if not url:
        return None
    cleaned = unescape(url).strip()
    if not cleaned.startswith(("http://", "https://")):
        return None
    host = urlparse(cleaned).netloc.lower()
    if not host or "google." in host or "daihoc.com.vn" in host or "caodang.com.vn" in host:
        return None
    if len(cleaned) > 255:
        return None
    return cleaned


def _blank(value: str | None, limit: int) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned[:limit] or None


def clean_area(value: str | None) -> str | None:
    text = _blank(value, 80)
    if not text:
        return None
    text = re.sub(r"^(TP\.|Thành phố)\s+", "", text).strip()
    return text[:50] or None


def plausible_admission_code(code: str) -> bool:
    """Mã tuyển sinh Bộ GD&ĐT thường dài 2–6 ký tự. Bỏ mã 1 chữ (A, D, E...)."""
    return 2 <= len(code) <= 6 and any(char.isalpha() for char in code)


def is_corrupt_naric(row: dict[str, str | None]) -> bool:
    """Cụm bản ghi NARIC bị gán chung mã, địa chỉ và website của một trường khác."""
    address = (row.get("dia_chi") or "").casefold()
    website = (row.get("website") or "").casefold()
    if "thanh vị" in address and "sơn tây" in address:
        return True
    name = fold(row.get("ten_truong") or "")
    english = (row.get("ten_tieng_anh") or "").lower()
    if "hcmiu.edu.vn" in website and "quoc te" not in name and "international" not in english:
        return True
    return False


def _fetch(client: httpx.Client, url: str) -> str:
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            response = client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as exc:
            last_error = exc
            time.sleep(0.4 * (attempt + 1))
    raise RuntimeError(f"Không tải được {url}: {last_error}")


def _profile_urls(client: httpx.Client) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for sitemap in SITEMAPS:
        html = _fetch(client, sitemap)
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", html):
            if "/ho-so/" not in loc or loc in seen:
                continue
            seen.add(loc)
            urls.append(loc)
    return urls


def parse_profile(html: str) -> dict[str, str | None] | None:
    name_match = _H1_RE.search(html)
    if name_match is None:
        return None
    name = _plain(name_match.group(1))
    if not name or not is_target_school(name):
        return None
    english = None
    english_match = _EN_RE.search(html)
    if english_match is not None:
        candidate = _plain(english_match.group(1))
        if candidate and not _VIETNAMESE_RE.search(candidate) and len(candidate) <= 255:
            english = candidate
    code_match = _CODE_RE.search(html)
    province_match = _PROVINCE_RE.search(html)
    web_match = _WEB_RE.search(html)
    level_match = _LEVEL_RE.search(html)
    return {
        "ma_truong": clean_code(code_match.group(1) if code_match else ""),
        "ten_truong": name,
        "ten_tieng_anh": english,
        "khu_vuc": _plain(province_match.group(1)) if province_match else None,
        "website": web_match.group(1) if web_match else None,
        "cap": _plain(level_match.group(1)) if level_match else None,
    }


def fetch_profiles(client: httpx.Client, cache_path: Path, refresh: bool) -> list[dict[str, str | None]]:
    cache: dict[str, dict[str, str | None]] = {}
    if cache_path.exists() and not refresh:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    urls = _profile_urls(client)
    pending = [url for url in urls if url not in cache]
    print(f"Hồ sơ danh bạ: {len(urls)} ({len(pending)} cần tải)")

    def load(url: str) -> tuple[str, dict[str, str | None] | None]:
        try:
            return url, parse_profile(_fetch(client, url))
        except RuntimeError:
            return url, None

    if pending:
        done = 0
        with ThreadPoolExecutor(max_workers=8) as pool:
            for url, record in pool.map(load, pending):
                done += 1
                if record is not None:
                    cache[url] = record
                if done % 100 == 0 or done == len(pending):
                    print(f"  đã tải {done}/{len(pending)}")
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_text(
                        json.dumps(cache, ensure_ascii=False),
                        encoding="utf-8",
                    )
    failed = [url for url in urls if url not in cache]
    if failed:
        print(f"Không đọc được {len(failed)} hồ sơ, ví dụ: {failed[0]}")
    return [cache[url] for url in urls if url in cache]


def _last_page(html: str) -> int:
    pages = [int(value) for value in re.findall(r"page=(\d+)", html)]
    return max(pages) if pages else 1


def fetch_naric_rows(client: httpx.Client) -> list[dict[str, str | None]]:
    first_html = _fetch(client, f"{NARIC_URL}?page=1")
    last = _last_page(first_html)
    pages = {1: first_html}
    if last > 1:
        with ThreadPoolExecutor(max_workers=6) as pool:
            fetched = pool.map(
                lambda page: (page, _fetch(client, f"{NARIC_URL}?page={page}")),
                range(2, last + 1),
            )
            pages.update(dict(fetched))

    by_no: dict[int, dict[str, str | None]] = {}
    for html in pages.values():
        for match in _ROW_RE.finditer(html):
            number = int(match.group("stt"))
            by_no.setdefault(
                number,
                {
                    "ma_truong": _plain(match.group("code")),
                    "ten_truong": _plain(match.group("name")),
                    "ten_tieng_anh": _plain(match.group("english")),
                    "dia_chi": _plain(match.group("address")),
                    "website": unescape(match.group("url") or "").strip(),
                },
            )
    return [by_no[key] for key in sorted(by_no)]


def _record(
    *,
    code: str,
    name: str,
    english: str | None,
    area: str | None,
    address: str | None,
    website: str | None,
) -> dict:
    school_name = normalize_school_name(name)[:255]
    return {
        "ma_truong": code,
        "ten_truong": school_name,
        "ten_viet_tat": None,
        "ten_tieng_anh": _blank(english, 255),
        "khu_vuc": clean_area(area),
        "dia_chi": _blank(address, 5000),
        "loai_hinh_dao_tao": infer_loai_hinh(school_name),
        "nhom_nganh": infer_nhom_nganh(school_name),
        "website": clean_website(website),
        "email": None,
        "so_dien_thoai": None,
        "hoc_phi_trung_binh": None,
        "nam_thanh_lap": None,
        "trang_thai": 1,
        "gioi_thieu": None,
    }


def _fill_missing(item: dict, source: dict) -> None:
    if not item["dia_chi"] and source.get("dia_chi"):
        item["dia_chi"] = _blank(source.get("dia_chi"), 5000)
    if not item["ten_tieng_anh"] and source.get("ten_tieng_anh"):
        item["ten_tieng_anh"] = _blank(source.get("ten_tieng_anh"), 255)
    if not item["website"] and source.get("website"):
        item["website"] = clean_website(source.get("website"))
    if not item["khu_vuc"]:
        item["khu_vuc"] = clean_area(source.get("khu_vuc")) or extract_khu_vuc(item["dia_chi"])


def compile_schools(
    profiles: list[dict[str, str | None]],
    naric_rows: list[dict[str, str | None]],
) -> tuple[list[dict], dict[str, int]]:
    stats = {
        "ho_so": len(profiles),
        "bo_khong_ma": 0,
        "gop_ma": 0,
        "bo_sung_naric": 0,
        "co_dia_chi": 0,
    }
    items_by_code: dict[str, dict] = {}
    uncoded: list[dict[str, str | None]] = []
    for profile in profiles:
        name = str(profile.get("ten_truong") or "").strip()
        if not name:
            continue
        code = clean_code(profile.get("ma_truong"))
        if not code:
            uncoded.append(profile)
            continue
        record = _record(
            code=code,
            name=name,
            english=profile.get("ten_tieng_anh"),
            area=profile.get("khu_vuc"),
            address=None,
            website=profile.get("website"),
        )
        current = items_by_code.get(code)
        if current is None:
            items_by_code[code] = record
            continue
        stats["gop_ma"] += 1
        _fill_missing(current, record)

    by_name: dict[str, dict] = {}
    for item in items_by_code.values():
        by_name.setdefault(name_key(item["ten_truong"]), item)
    for profile in uncoded:
        item = by_name.get(name_key(str(profile["ten_truong"])))
        if item is None:
            continue
        _fill_missing(item, profile)
        stats["gop_ma"] += 1

    naric_by_code: dict[str, list[dict[str, str | None]]] = {}
    naric_by_name: dict[str, list[dict[str, str | None]]] = {}
    for row in naric_rows:
        if is_corrupt_naric(row) or not is_target_school(str(row.get("ten_truong") or "")):
            continue
        code = clean_code(row.get("ma_truong"))
        if not plausible_admission_code(code):
            continue
        naric_by_code.setdefault(code, []).append(row)
        naric_by_name.setdefault(name_key(str(row["ten_truong"])), []).append(row)

    for item in items_by_code.values():
        rows = naric_by_code.get(item["ma_truong"], []) + naric_by_name.get(
            name_key(item["ten_truong"]), []
        )
        if not rows:
            continue
        chosen = max(rows, key=lambda row: len(row.get("dia_chi") or ""))
        _fill_missing(item, chosen)

    names = set(by_name)
    hosts = {
        host
        for item in items_by_code.values()
        if (host := _website_host(item.get("website")))
    }
    for code, rows in naric_by_code.items():
        if code in items_by_code or len({name_key(str(row["ten_truong"])) for row in rows}) != 1:
            continue
        row = rows[0]
        key = name_key(str(row["ten_truong"]))
        host = _website_host(row.get("website"))
        if key in names or (host and host in hosts):
            continue
        address = _blank(row.get("dia_chi"), 5000)
        record = _record(
            code=code,
            name=str(row["ten_truong"]),
            english=row.get("ten_tieng_anh"),
            area=extract_khu_vuc(address),
            address=address,
            website=row.get("website"),
        )
        items_by_code[code] = record
        names.add(key)
        if host:
            hosts.add(host)
        stats["bo_sung_naric"] += 1

    still_uncoded = [profile for profile in uncoded if name_key(str(profile["ten_truong"])) not in names]
    seen_uncoded: set[str] = set()
    for profile in still_uncoded:
        key = name_key(str(profile["ten_truong"]))
        if key in seen_uncoded or key in names:
            stats["gop_ma"] += 1
            continue
        seen_uncoded.add(key)
        matches = [
            row
            for row in naric_by_name.get(key, [])
            if clean_code(row.get("ma_truong")) not in items_by_code
        ]
        codes = list(dict.fromkeys(clean_code(row.get("ma_truong")) for row in matches))
        if len(codes) != 1:
            stats["bo_khong_ma"] += 1
            continue
        row = matches[0]
        host = _website_host(profile.get("website") or row.get("website"))
        if host and host in hosts:
            stats["gop_ma"] += 1
            continue
        address = _blank(row.get("dia_chi"), 5000)
        items_by_code[codes[0]] = _record(
            code=codes[0],
            name=str(profile["ten_truong"]),
            english=profile.get("ten_tieng_anh") or row.get("ten_tieng_anh"),
            area=profile.get("khu_vuc") or extract_khu_vuc(address),
            address=address,
            website=profile.get("website") or row.get("website"),
        )
        names.add(key)
        if host:
            hosts.add(host)
        stats["bo_sung_naric"] += 1

    items = list(items_by_code.values())
    stats["co_dia_chi"] = sum(1 for item in items if item["dia_chi"])
    items.sort(key=lambda item: fold(item["ten_truong"]))
    return items, stats


def validate_items(items: list[dict]) -> None:
    from app.schemas.dm_truong_dai_hoc import DmTruongDaiHocWrite

    codes: set[str] = set()
    for item in items:
        model = DmTruongDaiHocWrite.model_validate(item)
        if model.ma_truong in codes:
            raise ValueError(f"Mã trường trùng sau khi chuẩn hóa: {model.ma_truong}")
        codes.add(model.ma_truong)
        item["ma_truong"] = model.ma_truong


def default_output_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "dm_truong_dai_hoc.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tổng hợp JSON trường cao đẳng, học viện, đại học")
    parser.add_argument("-o", "--output", type=Path, default=default_output_path())
    parser.add_argument("--refresh", action="store_true", help="Tải lại hồ sơ, bỏ qua cache")
    args = parser.parse_args(argv)

    cache_path = args.output.parent / ".cache" / "ho_so_truong.json"
    with httpx.Client(
        timeout=30,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    ) as client:
        profiles = fetch_profiles(client, cache_path, args.refresh)
        print("Đang tải danh sách VN-NARIC để lấy địa chỉ...")
        naric_rows = fetch_naric_rows(client)

    items, stats = compile_schools(profiles, naric_rows)
    validate_items(items)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def level(name: str) -> str:
        folded = fold(name)
        if "hoc vien" in folded or "nhac vien" in folded:
            return "hoc_vien"
        if "cao dang" in folded:
            return "cao_dang"
        return "dai_hoc"

    levels = {"dai_hoc": 0, "hoc_vien": 0, "cao_dang": 0}
    for item in items:
        levels[level(item["ten_truong"])] += 1
    print(f"Hồ sơ đọc được: {stats['ho_so']}")
    print(f"Bỏ vì không có mã trường: {stats['bo_khong_ma']}")
    print(f"Gộp hồ sơ trùng mã: {stats['gop_ma']}")
    print(f"Bổ sung từ NARIC (mã chưa có trong danh bạ): {stats['bo_sung_naric']}")
    print(
        "Trong file: "
        f"{levels['dai_hoc']} đại học, {levels['hoc_vien']} học viện, {levels['cao_dang']} cao đẳng"
    )
    print(f"Có địa chỉ: {stats['co_dia_chi']}")
    print(f"Có website: {sum(1 for item in items if item['website'])}")
    print(f"Có khu vực: {sum(1 for item in items if item['khu_vuc'])}")
    print(f"Ghi {len(items)} trường vào {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
