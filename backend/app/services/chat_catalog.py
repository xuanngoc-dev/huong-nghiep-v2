"""School metadata for semantic lookup, without geographic or score heuristics."""
import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path


def _name(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower().replace("đ", "d"))
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"^truong\s+", "", value).strip()


@lru_cache(maxsize=2)
def _catalog(signature: tuple) -> tuple[dict, dict]:
    path = Path(__file__).resolve().parents[2] / "data" / "dm_truong_dai_hoc.json"
    try:
        rows = json.loads(path.read_text(encoding="utf-8-sig"))
        return ({str(r["ma_truong"]): r for r in rows}, {_name(r["ten_truong"]): r for r in rows})
    except (OSError, ValueError, KeyError, TypeError):
        return {}, {}


def school_location(school: dict) -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "dm_truong_dai_hoc.json"
    try:
        stat = path.stat()
        codes, names = _catalog((stat.st_mtime_ns, stat.st_size))
    except OSError:
        codes, names = {}, {}
    entry = codes.get(str(school.get("ma_truong"))) or names.get(_name(school.get("ten_truong", "")), {})
    result = {}
    for key in ("khu_vuc", "dia_chi"):
        value = school.get(key) or entry.get(key)
        if isinstance(value, str) and value:
            result[key] = value
    return result


def lookup_catalog(docs) -> list[dict]:
    result = []
    for doc in docs:
        if not doc.data:
            continue
        school = doc.data["truong"]
        methods = set()
        for record in doc.data["danh_sach_nganh"]:
            for method in record.get("phuong_thuc_tuyen_sinh", []):
                if method.get("ma_phuong_thuc"):
                    methods.add(str(method["ma_phuong_thuc"]))
        result.append({"ma_truong": str(school.get("ma_truong", "")), "ten_truong": school["ten_truong"],
                       "nam": school.get("nam_tuyen_sinh"), "phuong_thuc": sorted(methods),
                       **school_location(school)})
    return result
