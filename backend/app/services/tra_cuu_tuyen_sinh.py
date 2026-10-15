"""Tra cứu bản ghi tuyển sinh. Không dùng điểm từ khóa chung để chọn trường."""
import json
import math
import re
import unicodedata
from copy import deepcopy
from dataclasses import dataclass, field
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote, urlparse

from app.core.config import settings
from app.schemas.chat import KeHoachTraCuu, NguCanhChat, NguonChat, TinNhan
from app.services.tai_lieu import tai_lieu_root
from app.services.chat_catalog import school_location

CONTEXT_BUDGET = settings.chat_detail_context_max_chars
STOP = set("truong dai hoc hoc vien thanh pho tinh phan hieu tru so co so nam tuyen sinh cho cac nhung cua va voi la co duoc nhu the nao bao nhieu gi o tai sao thi hoi ve biet em minh toi ban nganh chuong trinh".split())
LOCATIONS = set("ha noi ho chi minh da nang vinh long bac nam".split())
FILE_WORDS = STOP | LOCATIONS | set("bach khoa thuy loi xay dung cong nghiep su pham ky thuat tai chinh kinh te thuong chuan tang".split())


@lru_cache(maxsize=4096)
def normalize(text: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", str(text))
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", s)
    value = unicodedata.normalize("NFD", s.lower().replace("đ", "d"))
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    value = re.sub(r"tp[.\s]*hcm|tphcm", "ho chi minh", value)
    value = re.sub(r"\bcntt\b", "cong nghe thong tin", value)
    value = re.sub(r"\bqtkd\b", "quan tri kinh doanh", value)
    value = re.sub(r"\bttnt\b|\bnganh ai\b", "nganh tri tue nhan tao", value)
    value = re.sub(r"\bktpm\b", "ky thuat phan mem", value)
    value = re.sub(r"\blogistic\b", "logistics", value)
    value = re.sub(r"\bdgnl\b", "danh gia nang luc", value)
    value = re.sub(r"\bdh\b", "dai hoc", value)
    return " ".join(re.findall(r"[a-z0-9]+", value))


def contains(text: str, phrase: str) -> bool:
    return bool(phrase) and f" {phrase} " in f" {text} "


def _method_matches(method: dict, filters: set[str]) -> bool:
    if not filters:
        return True
    exact_terms = {normalize(str(method.get(k) or "")) for k in ("ma_phuong_thuc", "loai_phuong_thuc")} - {""}
    ten_method = normalize(str(method.get("ten_phuong_thuc") or ""))
    loai_method = normalize(str(method.get("loai_phuong_thuc") or ""))
    extra_terms = set()
    if isinstance(method.get("cong_thuc_tinh_diem"), dict):
        extra_terms.update(normalize(str(k)) for k in method["cong_thuc_tinh_diem"].keys())
    for cond in method.get("dieu_kien_phu") or []:
        if isinstance(cond, dict):
            cond_type = str(cond.get("loai") or "")
            if any(k in cond_type for k in ("CHUNG_CHI", "DANH_GIA_TU_DUY", "DANH_GIA_NANG_LUC", "KY_THI", "THANH_TICH")):
                val = cond.get("gia_tri")
                if isinstance(val, list):
                    extra_terms.update(normalize(str(x)) for x in val)
                elif isinstance(val, str):
                    extra_terms.add(normalize(val))
            if cond.get("nguon_diem") and str(cond.get("nguon_diem")).upper() not in {"HOC_BA", "THI_THPT"}:
                extra_terms.add(normalize(str(cond["nguon_diem"])))

    for f in filters:
        if f in exact_terms:
            return True
        if contains(ten_method, f) or contains(loai_method, f) or (ten_method and f == ten_method):
            return True
        if f in extra_terms or any(contains(term, f) for term in extra_terms):
            return True
    return False


def valid_admission_data(data: dict) -> bool:
    school = data.get("truong")
    records = data.get("danh_sach_nganh")
    if not isinstance(school, dict) or not isinstance(school.get("ten_truong"), str) or not isinstance(records, list):
        return False
    for record in records:
        if not isinstance(record, dict):
            return False
        if any(record.get(k) is not None and not isinstance(record[k], (str, int)) for k in ("ten_nganh", "ten_chuong_trinh", "ma_nganh", "ma_xet_tuyen")):
            return False
        methods = record.get("phuong_thuc_tuyen_sinh") or []
        if not isinstance(methods, list):
            return False
        for method in methods:
            if not isinstance(method, dict):
                return False
            combinations = method.get("to_hop_mon") or []
            if not isinstance(combinations, list) or any(not isinstance(c, dict) for c in combinations):
                return False
            method["to_hop_mon"] = combinations
        record["phuong_thuc_tuyen_sinh"] = methods
    return True


@dataclass
class Document:
    name: str
    updated: datetime
    data: dict | None
    text: str
    aliases: set[str]
    school_name: str
    school_words: set[str]


@dataclass
class SearchResult:
    context: str = ""
    sources: list[NguonChat] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    message: str = ""
    suggestions: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    scope: NguCanhChat | None = None
    ask_ai_to_clarify: bool = False


@lru_cache(maxsize=2)
def _load_documents(root: str, signature: tuple) -> tuple[Document, ...]:
    documents = []
    for name, _, _ in signature:
        path = Path(root) / name
        try:
            text = path.read_text(encoding="utf-8-sig")
            parsed = json.loads(text) if path.suffix.lower() == ".json" else None
            data = parsed if isinstance(parsed, dict) and isinstance(parsed.get("truong"), dict) and isinstance(parsed.get("danh_sach_nganh"), list) else None
            if data and not valid_admission_data(data):
                continue
            school = data["truong"] if data else {}
            name_normal = normalize(school.get("ten_truong", path.stem.replace("_", " ")))
            aliases = {normalize(school.get("ma_truong", ""))}
            aliases.update(w for w in re.findall(r"[a-zA-Z]+", path.stem.lower()) if len(w) >= 3 and w not in FILE_WORDS)
            for alias in school.get("aliases", []) if isinstance(school.get("aliases"), list) else []:
                aliases.add(normalize(alias))
            documents.append(Document(name, datetime.fromtimestamp(path.stat().st_mtime, timezone.utc), data, text,
                                      aliases - {""}, name_normal, set(name_normal.split()) - STOP))
        except (OSError, ValueError, TypeError):
            continue
    return tuple(documents)


def documents() -> tuple[Document, ...]:
    root = tai_lieu_root()
    signature = []
    for path in sorted(root.iterdir()):
        if path.is_file() and not path.is_symlink() and not path.name.startswith(".") and path.suffix.lower() in {".json", ".txt"}:
            try:
                stat = path.stat()
                signature.append((path.name, stat.st_mtime_ns, stat.st_size))
            except OSError:
                continue
    return _load_documents(str(root), tuple(signature))


def _schools(query: str, docs: list[Document]) -> tuple[list[Document], bool]:
    explicit = [d for d in docs if any(contains(query, a) for a in d.aliases)]
    if explicit:
        # Shared aliases can refer to multiple campuses. Ask unless comparison was requested.
        shared = len(explicit) > 1 and not any(contains(query, normalize(d.data["truong"].get("ma_truong", ""))) for d in explicit)
        return explicit, shared and not _comparison(query)
    tokens = set(query.split())
    scores = []
    for doc in docs:
        core = doc.school_words - LOCATIONS
        overlap = core & tokens
        distinctive = any(contains(query, p) and contains(doc.school_name, p) for p in ("bach khoa", "su pham ky thuat"))
        if len(overlap) < 2 or (len(overlap) / max(1, len(core)) < 0.6 and not distinctive):
            continue
        locations = doc.school_words & LOCATIONS
        score = len(overlap) * 10 + len(locations & tokens) * 8
        for location in ("ha noi", "ho chi minh", "da nang"):
            if contains(query, location) and not contains(doc.school_name, location):
                score -= 30
        scores.append((score, doc))
    if not scores:
        return [], False
    best = max(s for s, _ in scores)
    selected = [d for s, d in scores if s == best and s > 0]
    if _comparison(query):
        named = [d for s, d in scores if s > 0 and (d.school_words - LOCATIONS) <= tokens]
        if len(named) > 1:
            return named, False
    return selected, len(selected) > 1


def _comparison(query: str) -> bool:
    return any(contains(query, phrase) for phrase in ("so sanh", "so voi", "khac nhau", "giua"))


def _broad_schools(query: str) -> bool:
    return any(contains(query, p) for p in ("truong nao", "nhung truong", "cac truong", "tat ca truong"))


def _names_school(query: str) -> bool:
    return bool(re.search(r"\b(?:truong|dai hoc|hoc vien) (?!nay\b|do\b|nao\b|co\b|nganh\b|la\b|va\b|thi\b|voi\b|ma\b)\w+", query))


def _names_major(query: str, selected: list[Document]) -> bool:
    match = re.search(r"\b(?:nganh|chuong trinh) (\w+)", query)
    if not match:
        return False
    word = match[1]
    return word not in STOP | {"nay", "do", "truong", "tai", "phu"} and not any(word in d.aliases for d in selected)


def _major_phrases(query: str, docs: list[Document]) -> list[str]:
    # A school's name can itself contain a major (Kinh tế, Tài chính, Công nghệ...).
    for doc in docs:
        names = [doc.school_name, normalize(doc.data["truong"].get("ten_truong", "").split("(")[0])]
        for name in names:
            if name and contains(query, name):
                query = re.sub(r"(?<!\w)" + re.escape(name) + r"(?!\w)", " ", query, count=1)
        short_name = re.sub(r"^(truong )?(dai hoc|hoc vien) ", "", names[-1]).strip()
        if len(short_name.split()) >= 3 and contains(query, short_name):
            query = re.sub(r"(?<!\w)" + re.escape(short_name) + r"(?!\w)", " ", query, count=1)
    query = " ".join(query.split())
    found = set()
    for doc in docs:
        for record in doc.data["danh_sach_nganh"]:
            for key in ("ten_nganh", "ten_chuong_trinh", "ma_nganh", "ma_xet_tuyen"):
                phrase = normalize(record.get(key, ""))
                if phrase and phrase not in STOP and contains(query, phrase):
                    found.add(phrase)
                if key in {"ten_nganh", "ten_chuong_trinh"}:
                    prefix = " ".join(phrase.split()[:2])
                    if len(phrase.split()) > 2 and prefix not in {"cong nghe", "ky thuat", "quan tri", "kinh doanh", "khoa hoc", "ngon ngu"} and contains(query, prefix):
                        found.add(prefix)
                    for keyword in ("logistics", "marketing", "fintech", "business", "design", "finance", "cybersecurity"):
                        if contains(query, keyword) and contains(phrase, keyword):
                            found.add(keyword)
    # Keep the most specific entity, while preserving alternatives joined by 'hoặc'.
    return sorted(p for p in found if not any(p != other and contains(other, p) for other in found))


def _intents(query: str) -> set[str]:
    patterns = {
        "to_hop": ("to hop", "mon thi", "mon xet"),
        "diem": ("diem", "diem chuan", "diem san"),
        "chi_tieu": ("chi tieu", "so luong"),
        "hoc_phi": ("hoc phi", "chi phi"),
        "dieu_kien": ("dieu kien", "yeu cau", "du dieu kien", "quy doi", "cong thuc", "ielts", "sat", "tsa", "hsa", "hoc ba"),
        "phuong_thuc": ("phuong thuc", "cach xet", "xet tuyen"),
        "danh_sach": ("truong nao", "nhung truong", "cac truong", "nganh nao", "nhung nganh", "cac nganh", "danh sach"),
        "dinh_huong": ("tot nhat", "nen hoc", "nen chon", "phu hop", "goi y", "tu van"),
    }
    result = {key for key, phrases in patterns.items() if any(contains(query, p) for p in phrases)}
    # A stated score is also a request for score data, even when the user asks
    # conversationally whether they can get into a major or school.
    if re.search(r"\b\d{1,2}(?:\s\d)?\s*(?:diem|d)\b", query):
        result.add("diem")
    if re.search(r"\b[a-z]\d{2}\b", query):
        result.add("to_hop")
    return result


def _clean(value):
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items() if v is not None and v != [] and v != {}}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    return value


def _project(record: dict, intents: set[str], detailed: bool, combinations: set[str]) -> dict:
    keys = {"ma_nganh", "ma_xet_tuyen", "ten_nganh", "ten_chuong_trinh", "chi_tieu_nganh"}
    if "hoc_phi" in intents:
        keys.update(k for k in record if "phi" in k or "chi_phi" in k)
    if "dieu_kien" in intents or detailed:
        keys.add("dieu_kien_nganh")
    result = {k: v for k, v in record.items() if k in keys}
    if intents - {"danh_sach", "hoc_phi"} or detailed:
        methods = []
        for method in record.get("phuong_thuc_tuyen_sinh", []):
            if not isinstance(method, dict):
                continue
            if "diem" in intents and not detailed and not (intents & {"dieu_kien", "phuong_thuc"}):
                has_score = method.get("diem_chuan") is not None or method.get("diem_san") is not None
                has_score = has_score or any(isinstance(c, dict) and c.get("diem_chuan") is not None for c in method.get("to_hop_mon", []))
                if not has_score:
                    continue
            if combinations and not any(contains(normalize(json.dumps(c, ensure_ascii=False)), code) for c in method.get("to_hop_mon", [] ) for code in combinations):
                continue
            method_keys = {"ma_phuong_thuc", "ten_phuong_thuc", "loai_phuong_thuc", "nhom_phuong_thuc_truong", "dien_xet_tuyen", "ghi_chu", "thang_diem"}
            if "diem" in intents:
                method_keys.update({"diem_chuan", "diem_san", "to_hop_mon"})
            if "to_hop" in intents:
                method_keys.add("to_hop_mon")
            if "chi_tieu" in intents:
                method_keys.add("chi_tieu_phuong_thuc")
            if "dieu_kien" in intents or "phuong_thuc" in intents or detailed:
                method_keys.update({"dieu_kien_phu", "cong_thuc_tinh_diem", "quy_doi_diem", "diem_cong_uu_tien", "to_hop_mon", "diem_san", "tieu_chi_dong_diem"})
            if detailed:
                method_keys.update(method)
            projected = {k: v for k, v in method.items() if k in method_keys}
            if "diem" in intents and "to_hop" not in intents and not detailed:
                projected["to_hop_mon"] = [{k: v for k, v in combo.items() if k in {"ma_to_hap", "ma_to_hop", "diem_chuan", "ghi_chu"}}
                                            for combo in method.get("to_hop_mon", []) if isinstance(combo, dict)]
            if combinations and "to_hop_mon" in projected:
                projected["to_hop_mon"] = [c for c in projected["to_hop_mon"] if any(contains(normalize(json.dumps(c, ensure_ascii=False)), code) for code in combinations)]
            methods.append(projected)
        result["phuong_thuc_tuyen_sinh"] = methods
    return _clean(result)


def _intern_notes(records: list[list[dict]]) -> dict:
    """Reference identical long notes without merging distinct program conditions."""
    counts = Counter()

    def visit(value, replace=False):
        if isinstance(value, dict):
            for key, item in list(value.items()):
                if key in {"ghi_chu", "cong_thuc_tinh_diem"} and isinstance(item, str) and len(item) > 100:
                    if replace and item in ids:
                        value[key] = {"tham_chieu_chu_thich": ids[item]}
                    elif not replace:
                        counts[item] += 1
                else:
                    visit(item, replace)
        elif isinstance(value, list):
            for item in value:
                visit(item, replace)
    visit(records)
    ids = {note: f"C{i + 1}" for i, (note, count) in enumerate(counts.items()) if count > 1}
    visit(records, True)
    return {reference: note for note, reference in ids.items()}


def _source(doc: Document, index: int) -> NguonChat:
    school = doc.data["truong"] if doc.data else {}
    original = next((school.get(k) for k in ("url_nguon", "nguon_url", "url", "link_de_an") if isinstance(school.get(k), str) and urlparse(school[k]).scheme in {"https", "http"}), None)
    year = school.get("nam_tuyen_sinh")
    return NguonChat(id=index, ten=school.get("ten_truong", doc.name), ma_truong=str(school.get("ma_truong", "")),
                     nam=int(year) if str(year).isdigit() else None, cap_nhat=doc.updated,
                     duong_dan=f"{settings.api_v1_prefix}/chat/nguon/{quote(doc.name)}", url_goc=original)


def _number(value):
    if isinstance(value, bool):
        return None
    try:
        number = float(str(value).replace(",", "."))
        return number if math.isfinite(number) else None
    except (ValueError, TypeError):
        return None


def _overview(record: dict) -> dict:
    result = {k: record[k] for k in ("ma_nganh", "ma_xet_tuyen", "ten_nganh", "ten_chuong_trinh", "chi_tieu_nganh") if record.get(k) is not None}
    if result.get("ten_nganh") == result.get("ten_chuong_trinh"):
        result.pop("ten_chuong_trinh", None)
    # Columnar values remove repeated JSON keys, not admission facts or cutoffs.
    result["phuong_thuc_tom_tat"] = [
        [m.get("ma_phuong_thuc"), m.get("loai_phuong_thuc") or m.get("ten_phuong_thuc"), m.get("thang_diem"),
         m.get("diem_chuan"), m.get("diem_san"),
         [[c.get("ma_to_hap") or c.get("ma_to_hop"), c.get("diem_chuan")] for c in m.get("to_hop_mon", [])]]
        for m in record.get("phuong_thuc_tuyen_sinh", [])]
    return result


def _planned_search(plan: KeHoachTraCuu, docs: list[Document]) -> SearchResult:
    if plan.khong_can_tra_cuu:
        return SearchResult(message="Lượt này không cần tra cứu bản ghi tuyển sinh. " + plan.can_lam_ro,
                            scope=plan.ngu_canh, ask_ai_to_clarify=True)
    candidates, ranks = [], []
    combinations = set(plan.to_hop)
    method_filters = {normalize(m) for m in plan.phuong_thuc}
    detailed = plan.che_do == "chi_tiet" or any(f in {"sat", "act", "ielts", "tsa", "hsa", "alevel", "a level", "ap", "ib", "toefl"} for f in method_filters)
    comparing = any(v is not None for v in (plan.diem_tu, plan.diem_den, plan.diem_muc_tieu))
    for doc in docs:
        school = doc.data["truong"]
        if plan.ma_truong and str(school.get("ma_truong")) not in plan.ma_truong:
            continue
        if plan.nam and str(school.get("nam_tuyen_sinh")) not in {str(y) for y in plan.nam}:
            continue
        school_data = {k: school[k] for k in ("ten_truong", "ma_truong", "nam_tuyen_sinh") if k in school}
        school_data.update(school_location(school))
        if detailed:
            school_data.update({k: v for k, v in school.items() if k == "dieu_kien_chung" or "phi" in k})
        for record in doc.data["danh_sach_nganh"]:
            identity = normalize(" ".join(str(record.get(k) or "") for k in ("ma_nganh", "ma_xet_tuyen", "ten_nganh", "ten_chuong_trinh")))
            if plan.nganh and not any(contains(identity, normalize(m)) for m in plan.nganh):
                continue
            methods, cutoffs = [], []
            for method in record.get("phuong_thuc_tuyen_sinh", []):
                if method_filters and not _method_matches(method, method_filters):
                    continue
                if plan.thang_diem is not None and _number(method.get("thang_diem")) != plan.thang_diem:
                    continue
                combos = method.get("to_hop_mon", [])
                if combinations:
                    combos = [c for c in combos if str(c.get("ma_to_hap") or c.get("ma_to_hop") or "").upper() in combinations]
                    if not combos:
                        continue
                kept, scores = [], []
                for combo in combos or [{}]:
                    cutoff = _number(combo.get("diem_chuan") if combo.get("diem_chuan") is not None else method.get("diem_chuan"))
                    if plan.diem_tu is not None and (cutoff is None or cutoff < plan.diem_tu):
                        continue
                    if plan.diem_den is not None and (cutoff is None or cutoff > plan.diem_den):
                        continue
                    kept.append(combo)
                    if cutoff is not None:
                        scores.append(cutoff)
                if not kept or (comparing and not scores):
                    continue
                methods.append({**method, "to_hop_mon": [c for c in kept if c]})
                cutoffs.extend(scores)
            if not methods:
                continue
            filtered = {**record, "phuong_thuc_tuyen_sinh": methods}
            projected = deepcopy(filtered) if detailed else _overview(filtered)
            if plan.sap_xep == "gan_diem" and plan.diem_muc_tieu is not None:
                rank = min((abs(p - plan.diem_muc_tieu) for p in cutoffs), default=math.inf)
            elif plan.sap_xep == "diem_tang":
                rank = min(cutoffs, default=math.inf)
            elif plan.sap_xep == "diem_giam":
                rank = -max(cutoffs) if cutoffs else math.inf
            else:
                rank = 0
            candidates.append((doc, school_data, projected))
            ranks.append(rank)
    if not candidates:
        return SearchResult(message="Không tìm thấy bản ghi khớp kế hoạch tra cứu. " + plan.can_lam_ro,
                            scope=plan.ngu_canh, ask_ai_to_clarify=True)
    candidates = [row for _, row in sorted(zip(ranks, candidates), key=lambda item: item[0])]
    for index, (_, _, record) in enumerate(candidates, 1):
        record["thu_tu_tra_cuu"] = index
    return _pack_context(candidates, set(plan.thong_tin), plan.ngu_canh, len(candidates), {
        "bo_loc": plan.model_dump(exclude={"ngu_canh"}),
        "chi_tiet_dieu_kien": detailed,
        "cot_phuong_thuc_tom_tat": ["ma_phuong_thuc", "loai_hoac_ten", "thang_diem", "diem_chuan", "diem_san", "to_hop"],
        "cot_to_hop": ["ma_to_hop", "diem_chuan_rieng"],
        "quy_uoc": "Điểm chuẩn riêng của tổ hợp nếu có được ưu tiên hơn điểm chuẩn phương thức; null là thiếu dữ liệu. Tổng quan chưa bao gồm đầy đủ điều kiện và công thức tính điểm."},
        budget=settings.chat_detail_context_max_chars if detailed else settings.chat_context_max_chars)


def _pack_context(candidates: list, intents: set[str], scope: NguCanhChat, total: int,
                  plan: dict | None = None, budget: int | None = None) -> SearchResult:
    """Budget complete selected records and only the notes/sources they use."""
    counts = Counter(doc.name for doc, _, _ in candidates)
    budget = CONTEXT_BUDGET if budget is None else budget

    def build(chosen):
        results, used, groups = [], [], {}
        for doc, school, record in chosen:
            if doc.name not in groups:
                used.append(doc)
                group = {"nguon": len(used), "truong": school,
                         "so_chuong_trinh_phu_hop": counts[doc.name], "chuong_trinh": []}
                groups[doc.name] = group
                results.append(group)
            groups[doc.name]["chuong_trinh"].append(deepcopy(record))
        notes = _intern_notes([r["chuong_trinh"] for r in results])
        payload = {"loai_thong_tin": sorted(intents), "tong_chuong_trinh": total,
                   "so_chuong_trinh_gui": len(chosen), "chi_tiet_day_du": len(chosen) == total,
                   "quy_uoc": "Thiếu dữ liệu không có nghĩa là điểm bằng 0. Chỉ có dữ liệu điểm sàn không xác nhận được điểm chuẩn.",
                   "chu_thich": notes, "ket_qua": results}
        if plan is not None:
            payload["ke_hoach_tra_cuu"] = plan
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":")), used

    chosen = []
    context, used = build(chosen)
    for candidate in candidates:
        proposed, proposed_docs = build([*chosen, candidate])
        if len(proposed) <= budget:
            chosen.append(candidate)
            context, used = proposed, proposed_docs
    if not chosen:
        return SearchResult(message="Dữ liệu chi tiết cho yêu cầu này quá dài. Hãy hỏi riêng một chương trình hoặc phương thức để xem đầy đủ.", scope=scope)
    notes = []
    if len(chosen) < total:
        notes.append(f"Có {total} chương trình khớp bộ lọc tra cứu; phần được cung cấp gồm {len(chosen)} chương trình. Đây chưa phải toàn bộ kết quả.")
    return SearchResult(context=context, sources=[_source(d, i + 1) for i, d in enumerate(used)],
                        files=[d.name for d in used], notes=notes, scope=scope)


def search(question: str, history: list[TinNhan] | None = None, scope: NguCanhChat | None = None,
           plan: KeHoachTraCuu | None = None) -> SearchResult:
    all_docs = list(documents())
    docs = [d for d in all_docs if d.data]
    if plan is not None:
        result = _planned_search(plan, docs)
        if not result.context and any(not d.data for d in all_docs):
            prose = search(question, history, scope)
            prose_names = {d.name for d in all_docs if not d.data}
            if prose.context and set(prose.files).issubset(prose_names):
                prose.scope = plan.ngu_canh
                return prose
        return result
    query = normalize(question)
    selected, ambiguous = _schools(query, docs)
    majors = _major_phrases(query, docs)
    intents = _intents(query)
    prior_schools = [d for d in docs if scope and str(d.data["truong"].get("ma_truong")) in scope.ma_truong]
    prior_majors = _major_phrases(" ".join(scope.nganh), docs) if scope else []
    prior_year = scope.nam if scope else None
    for message in (history or [])[-30:]:
        if message.vai_tro != "user":
            continue
        old_query = normalize(message.noi_dung)
        old_years = re.findall(r"\b20\d{2}\b", old_query)
        if old_years:
            prior_year = int(old_years[-1])
        old_schools, old_ambiguous = _schools(old_query, docs)
        if _broad_schools(old_query) or (not old_schools and _names_school(old_query)):
            prior_schools = []
            prior_majors = []
        if old_schools and not old_ambiguous:
            if {d.name for d in old_schools} != {d.name for d in prior_schools} and not contains(old_query, "con"):
                prior_majors = []
            prior_schools = old_schools
        old_majors = _major_phrases(old_query, docs)
        if old_majors:
            prior_majors = old_majors
        elif "danh_sach" in _intents(old_query) or _names_major(old_query, old_schools):
            prior_majors = []
    broad_schools = _broad_schools(query)
    if not selected and not broad_schools and _names_school(query):
        return SearchResult(message="Không tìm thấy trường/cơ sở người dùng vừa nêu trong dữ liệu hiện có.", scope=NguCanhChat(), ask_ai_to_clarify=True)
    if not majors and not (intents & {"danh_sach", "dinh_huong"}) and _names_major(query, selected):
        return SearchResult(message="Không nhận diện được ngành/chương trình người dùng vừa nêu trong dữ liệu hiện có.", scope=NguCanhChat(), ask_ai_to_clarify=True)
    if not selected and not broad_schools and (intents or contains(query, "con") or contains(query, "truong nay")):
        selected = prior_schools
    same_school = {d.name for d in selected} == {d.name for d in prior_schools}
    if not majors and "danh_sach" not in intents and (same_school or contains(query, "con")):
        majors = prior_majors
    if ambiguous:
        options = [f"{d.data['truong']['ten_truong']} ({d.data['truong'].get('ma_truong', '')})" for d in selected]
        return SearchResult(message="Bạn muốn hỏi trường/cơ sở nào?\n\n" + "\n".join(f"- {o}" for o in options), suggestions=options)
    if not selected and not majors and not (broad_schools or "danh_sach" in intents):
        # Uploaded prose remains searchable, but unrelated files are never sent as a fallback.
        meaningful = set(query.split()) - STOP - LOCATIONS
        texts = []
        used = []
        size = 0
        for doc in all_docs:
            if doc.data:
                continue
            paragraphs = [p for p in re.split(r"\n\s*\n", doc.text) if len(meaningful & set(normalize(p).split())) >= 2]
            kept = []
            for paragraph in paragraphs:
                if size + len(paragraph) <= CONTEXT_BUDGET:
                    kept.append(paragraph)
                    size += len(paragraph)
            if kept:
                used.append(doc)
                texts.append({"nguon": len(used), "van_ban": kept})
        if texts:
            return SearchResult(context=json.dumps(texts, ensure_ascii=False), sources=[_source(d, i + 1) for i, d in enumerate(used)], files=[d.name for d in used], scope=NguCanhChat())
        message = "Mình chưa xác định được thông tin cần tra cứu. Bạn hãy cho biết tên trường, ngành hoặc mã xét tuyển."
        if any(contains(query, p) for p in ("phu hop", "huong nghiep", "chon nghe")):
            message = "Để tư vấn ngành phù hợp, bạn hãy chia sẻ sở thích, môn học mạnh và khu vực muốn học. Hiện mình có thể giúp tra cứu, so sánh thông tin tuyển sinh trong dữ liệu đã có."
        return SearchResult(message=message, suggestions=["Những trường nào có ngành Công nghệ thông tin?", "Phương thức xét tuyển Marketing NEU?"])
    selected_codes = [str(d.data["truong"].get("ma_truong", "")) for d in selected]
    years = set(re.findall(r"\b20\d{2}\b", query))
    if not years and prior_year:
        years = {str(prior_year)}
    next_scope = (scope or NguCanhChat()).model_copy(update={"ma_truong": selected_codes, "nganh": majors[:20],
                                                         "nam": int(sorted(years)[-1]) if years else None})
    selected = selected or docs
    if years:
        selected = [d for d in selected if str(d.data["truong"].get("nam_tuyen_sinh")) in years]
    combinations = set(re.findall(r"\b[a-z]\d{2}\b", query))
    candidates, program_lists = [], []
    for doc in selected:
        matches = []
        for record in doc.data["danh_sach_nganh"]:
            identity = normalize(" ".join(str(record.get(k, "")) for k in ("ten_nganh", "ten_chuong_trinh", "ma_nganh", "ma_xet_tuyen")))
            if majors and not any(contains(identity, major) for major in majors):
                continue
            if combinations and not any(contains(normalize(json.dumps(m.get("to_hop_mon", []), ensure_ascii=False)), code) for m in record.get("phuong_thuc_tuyen_sinh", []) if isinstance(m, dict) for code in combinations):
                continue
            projected = _project(record, intents, bool(majors and not intents), combinations)
            if "diem" in intents and not projected.get("phuong_thuc_tuyen_sinh"):
                continue
            matches.append(projected)
        if not matches:
            continue
        school_keys = {"ten_truong", "ma_truong", "nam_tuyen_sinh"}
        if "dieu_kien" in intents or "phuong_thuc" in intents:
            school_keys.add("dieu_kien_chung")
        if "hoc_phi" in intents:
            school_keys.update(k for k in doc.data["truong"] if "phi" in k)
        school = {k: v for k, v in doc.data["truong"].items() if k in school_keys}
        school.update(school_location(doc.data["truong"]))
        program_lists.append([(doc, school, record) for record in matches])
    if not program_lists:
        return SearchResult(message="Không tìm thấy bản ghi khớp với các điều kiện tra cứu trong dữ liệu hiện có.", scope=next_scope, ask_ai_to_clarify=True)
    total = sum(map(len, program_lists))
    candidates = [rows[index] for index in range(max(map(len, program_lists))) for rows in program_lists if index < len(rows)]
    return _pack_context(candidates, intents, next_scope, total)
