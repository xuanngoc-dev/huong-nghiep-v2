"""Nhập một đề án tuyển sinh và các bảng dats_ đi kèm từ JSON một trường, một năm."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import String, Text, select
from sqlalchemy.orm import Session

from app.models.dats_chinh_sach_uu_tien_xet_tuyen import DatsChinhSachUuTienXetTuyen
from app.models.dats_chinh_sach_xet_tuyen_thang import DatsChinhSachXetTuyenThang
from app.models.dats_chuong_trinh_dao_tao import DatsChuongTrinhDaoTao
from app.models.dats_co_so_vat_chat import DatsCoSoVatChat
from app.models.dats_diem_cong import DatsDiemCong
from app.models.dats_dieu_kien_du_tuyen import DatsDieuKienDuTuyen
from app.models.dats_doi_tuong_du_tuyen import DatsDoiTuongDuTuyen
from app.models.dats_ho_so_du_tuyen import DatsHoSoDuTuyen
from app.models.dats_ke_hoach_tuyen_sinh import DatsKeHoachTuyenSinh
from app.models.dats_lien_he_tuyen_sinh import DatsLienHeTuyenSinh
from app.models.dats_nhan_su import DatsNhanSu
from app.models.dats_phuong_thuc import DatsPhuongThuc
from app.models.dats_phuong_thuc_to_hop import DatsPhuongThucToHop
from app.models.dats_quy_doi_diem_trung_tuyen import DatsQuyDoiDiemTrungTuyen
from app.models.dats_quy_doi_nguong_dau_vao import DatsQuyDoiNguongDauVao
from app.models.dats_quy_mo_dao_tao import DatsQuyMoDaoTao
from app.models.dats_quy_tac_phan_bo import DatsQuyTacPhanBo
from app.models.dats_tieu_chi_xet_tuyen import DatsTieuChiXetTuyen
from app.models.dats_trinh_do_nganh import DatsTrinhDoNganh
from app.models.dats_tru_so import DatsTruSo
from app.models.dats_tuyen_sinh import DatsTuyenSinh
from app.models.dats_ty_le_viec_lam import DatsTyLeViecLam
from app.models.dats_website import DatsWebsite
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc
from app.models.dm_truong import DmTruong

_MAX_ROWS = 5000
_MA_TO_HOP = re.compile(r"ma_to_hop\s*=\s*([A-Za-z0-9._-]+)")
_SKIP_COLUMNS = {"id", "tao_luc", "cap_nhat_luc"}

# Khóa ngoại trỏ tới bản ghi dats_ vừa tạo trong cùng file, không phải danh mục.
_DATS_FK = {
    "de_an_id": "dats_tuyen_sinh",
    "de_an_chuong_trinh_id": "dats_chuong_trinh_dao_tao",
    "de_an_phuong_thuc_id": "dats_phuong_thuc",
    "doi_tuong_du_tuyen_id": "dats_doi_tuong_du_tuyen",
    "co_so_id": "dats_tru_so",
}
_CATALOG_KIND = {
    "nganh_dao_tao_id": "nganh",
    "to_hop_id": "to_hop",
    "phuong_thuc_nguon_id": "phuong_thuc",
    "phuong_thuc_dich_id": "phuong_thuc",
    "to_hop_nguon_id": "to_hop",
    "to_hop_dich_id": "to_hop",
}

# object = một bản ghi; list = nhiều bản ghi. Thứ tự tôn trọng khóa ngoại.
_TABLES: list[tuple[str, type, str]] = [
    ("dats_tuyen_sinh", DatsTuyenSinh, "object"),
    ("dats_tru_so", DatsTruSo, "list"),
    ("dats_website", DatsWebsite, "list"),
    ("dats_lien_he_tuyen_sinh", DatsLienHeTuyenSinh, "list"),
    ("dats_chuong_trinh_dao_tao", DatsChuongTrinhDaoTao, "list"),
    ("dats_ke_hoach_tuyen_sinh", DatsKeHoachTuyenSinh, "list"),
    ("dats_phuong_thuc", DatsPhuongThuc, "list"),
    ("dats_phuong_thuc_to_hop", DatsPhuongThucToHop, "list"),
    ("dats_nhan_su", DatsNhanSu, "list"),
    ("dats_co_so_vat_chat", DatsCoSoVatChat, "list"),
    ("dats_quy_mo_dao_tao", DatsQuyMoDaoTao, "list"),
    ("dats_ty_le_viec_lam", DatsTyLeViecLam, "list"),
    ("dats_trinh_do_nganh", DatsTrinhDoNganh, "list"),
    ("dats_doi_tuong_du_tuyen", DatsDoiTuongDuTuyen, "list"),
    ("dats_dieu_kien_du_tuyen", DatsDieuKienDuTuyen, "list"),
    ("dats_tieu_chi_xet_tuyen", DatsTieuChiXetTuyen, "list"),
    ("dats_diem_cong", DatsDiemCong, "list"),
    ("dats_quy_tac_phan_bo", DatsQuyTacPhanBo, "list"),
    ("dats_ho_so_du_tuyen", DatsHoSoDuTuyen, "list"),
    ("dats_quy_doi_nguong_dau_vao", DatsQuyDoiNguongDauVao, "list"),
    ("dats_quy_doi_diem_trung_tuyen", DatsQuyDoiDiemTrungTuyen, "list"),
    ("dats_chinh_sach_xet_tuyen_thang", DatsChinhSachXetTuyenThang, "list"),
    ("dats_chinh_sach_uu_tien_xet_tuyen", DatsChinhSachUuTienXetTuyen, "list"),
]
_MODELS = {name: model for name, model, _kind in _TABLES}
_KINDS = {name: kind for name, _model, kind in _TABLES}


class DatsImportError(ValueError):
    """Dữ liệu JSON không nhập được. Thông điệp dành cho người dùng."""


@dataclass(frozen=True)
class CatalogIndex:
    phuong_thuc_by_code: dict[str, int] = field(default_factory=dict)
    phuong_thuc_ids: set[int] = field(default_factory=set)
    to_hop_by_code: dict[str, int] = field(default_factory=dict)
    to_hop_ids: set[int] = field(default_factory=set)
    nganh_ids: set[int] = field(default_factory=set)


@dataclass
class PreparedRow:
    table: str
    source_id: int | None
    values: dict


def import_document(db: Session, truong_id: int, nam_tuyen_sinh: int, document: dict) -> tuple[int, dict[str, int]]:
    """Lưu toàn bộ JSON trong một transaction. Id trong file chỉ dùng để nối khóa ngoại."""
    if db.get(DmTruong, truong_id) is None:
        raise DatsImportError("Trường học không tồn tại")
    catalogs = _load_catalogs(db, document)
    rows = prepare_import(document, truong_id=truong_id, nam_tuyen_sinh=nam_tuyen_sinh, catalogs=catalogs)
    return _apply(db, rows)


def prepare_import(
    document: dict,
    *,
    truong_id: int,
    nam_tuyen_sinh: int,
    catalogs: CatalogIndex,
) -> list[PreparedRow]:
    """Chuẩn hóa JSON thành các dòng chờ ghi. Khóa ngoại dats_ vẫn là id gốc trong file."""
    if not isinstance(document, dict):
        raise DatsImportError("JSON phải là một object một trường, một năm")
    unknown = sorted(key for key in document if key.startswith("dats_") and key not in _MODELS)
    if unknown:
        raise DatsImportError(f"Chưa hỗ trợ bảng: {', '.join(unknown)}")

    prepared: list[PreparedRow] = []
    seen_ids: dict[str, set[int]] = defaultdict(set)
    for table, _model, kind in _TABLES:
        raw_rows = _section(document, table, kind)
        if len(raw_rows) > _MAX_ROWS:
            raise DatsImportError(f"{table} vượt quá {_MAX_ROWS} dòng")
        for index, raw in enumerate(raw_rows, start=1):
            label = f"{table} dòng {index}"
            if not isinstance(raw, dict):
                raise DatsImportError(f"{label} không phải object")
            source_id = _source_id(raw, table, label)
            if source_id is not None:
                if source_id in seen_ids[table]:
                    raise DatsImportError(f"{label} trùng id {source_id}")
                seen_ids[table].add(source_id)
            values = _values(raw, table, label, truong_id, nam_tuyen_sinh, catalogs)
            prepared.append(PreparedRow(table=table, source_id=source_id, values=values))
    if not any(row.table == "dats_tuyen_sinh" for row in prepared):
        raise DatsImportError("Thiếu object dats_tuyen_sinh")
    return prepared


def _section(document: dict, table: str, kind: str) -> list:
    if table not in document or document[table] is None:
        if kind == "object":
            raise DatsImportError("Thiếu object dats_tuyen_sinh")
        return []
    value = document[table]
    if kind == "object":
        if not isinstance(value, dict):
            raise DatsImportError("dats_tuyen_sinh phải là một object")
        return [value]
    if not isinstance(value, list):
        raise DatsImportError(f"{table} phải là một mảng")
    return value


def _source_id(raw: dict, table: str, label: str) -> int | None:
    if "id" not in _MODELS[table].__table__.columns:
        return None
    value = raw.get("id")
    if value is None or value == "":
        raise DatsImportError(f"{label} thiếu id để liên kết các bảng trong file")
    number = _as_int(value, f"{label} có id không hợp lệ")
    if number < 1:
        raise DatsImportError(f"{label} có id không hợp lệ")
    return number


def _values(raw: dict, table: str, label: str, truong_id: int, nam_tuyen_sinh: int, catalogs: CatalogIndex) -> dict:
    columns = {column.name: column for column in _MODELS[table].__table__.columns}
    values: dict = {}
    for name, column in columns.items():
        if name in _SKIP_COLUMNS:
            continue
        if table == "dats_tuyen_sinh" and name == "truong_id":
            values[name] = truong_id
            continue
        if name == "nam_tuyen_sinh":
            values[name] = nam_tuyen_sinh
            continue
        if name == "ma_phuong_thuc_cua_bo" and table == "dats_phuong_thuc":
            supplied = raw.get(name)
            if supplied in (None, ""):
                supplied = raw.get("ma_phuong_thuc_cua_truong")
            code = _known_method_code(catalogs, supplied)
            if code is None:
                raise DatsImportError(f"{label} thiếu ma_phuong_thuc_cua_bo hoặc mã phương thức có trong danh mục")
            values[name] = code
            continue
        if name not in raw or raw[name] is None or raw[name] == "":
            if name == "to_hop_id" and table == "dats_phuong_thuc_to_hop":
                values[name] = _require_catalog(
                    _lookup_code(catalogs.to_hop_by_code, _combo_code(raw)),
                    f"{label} thiếu to_hop_id hoặc mã tổ hợp có trong danh mục",
                )
                continue
            if not column.nullable and not column.primary_key:
                raise DatsImportError(f"{label} thiếu {name}")
            values[name] = None
            continue
        values[name] = _coerce(column, raw[name], label, catalogs)
    return values


def _coerce(column, value, label: str, catalogs: CatalogIndex):
    name = column.name
    kind = _kind(column)
    if name in _DATS_FK:
        number = _as_int(value, f"{label} có {name} không hợp lệ")
        if number < 1:
            raise DatsImportError(f"{label} có {name} không hợp lệ")
        return number
    if name in _CATALOG_KIND:
        number = _as_int(value, f"{label} có {name} không hợp lệ")
        _ensure_catalog_id(catalogs, _CATALOG_KIND[name], number, f"{label} có {name} không có trong danh mục")
        return number
    if kind == "text":
        text = str(value).strip()
        if not text:
            if column.nullable:
                return None
            raise DatsImportError(f"{label} thiếu {name}")
        limit = getattr(column.type, "length", None)
        if limit and len(text) > limit:
            raise DatsImportError(f"{label} có {name} dài quá {limit} ký tự")
        return text
    if kind == "int":
        number = _as_int(value, f"{label} có {name} không hợp lệ")
        if number < 0 or number > _int_max(column):
            raise DatsImportError(f"{label} có {name} không hợp lệ")
        return number
    if kind == "decimal":
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise DatsImportError(f"{label} có {name} không hợp lệ") from None
    if kind == "bool":
        if isinstance(value, bool):
            return value
        if value in (0, 1, "0", "1"):
            return bool(int(value))
        raise DatsImportError(f"{label} có {name} không hợp lệ")
    if kind == "date":
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        text = str(value).strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
            raise DatsImportError(f"{label} có {name} phải theo dạng YYYY-MM-DD")
        try:
            return date.fromisoformat(text)
        except ValueError:
            raise DatsImportError(f"{label} có {name} không hợp lệ") from None
    if kind == "json":
        if isinstance(value, (dict, list)):
            return value
        raise DatsImportError(f"{label} có {name} phải là object hoặc mảng JSON")
    raise DatsImportError(f"{label} có cột {name} chưa được hỗ trợ")


def _kind(column) -> str:
    type_name = column.type.__class__.__name__
    if type_name == "JSON":
        return "json"
    if type_name == "Boolean":
        return "bool"
    if type_name == "Date":
        return "date"
    if type_name == "DateTime":
        return "datetime"
    if type_name in {"Numeric", "DECIMAL"}:
        return "decimal"
    if isinstance(column.type, (String, Text)) or type_name in {"String", "Text", "VARCHAR"}:
        return "text"
    if "INT" in type_name.upper():
        return "int"
    return type_name


def _int_max(column) -> int:
    type_name = column.type.__class__.__name__
    unsigned = bool(getattr(column.type, "unsigned", False))
    if type_name in {"SMALLINT", "SmallInteger"}:
        return 65535 if unsigned else 32767
    if type_name in {"INTEGER", "Integer"}:
        return 4_294_967_295 if unsigned else 2_147_483_647
    return 18_446_744_073_709_551_615 if unsigned else 9_223_372_036_854_775_807


def _as_int(value, message: str) -> int:
    if isinstance(value, bool) or isinstance(value, float):
        raise DatsImportError(message)
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise DatsImportError(message) from None
    return number


def _known_method_code(catalogs: CatalogIndex, code) -> str | None:
    if code is None:
        return None
    text = str(code).strip().upper()
    if not text or text not in catalogs.phuong_thuc_by_code:
        return None
    return text


def _lookup_code(mapping: dict[str, int], code) -> int | None:
    if code is None:
        return None
    text = str(code).strip().upper()
    if not text:
        return None
    return mapping.get(text)


def _combo_code(raw: dict) -> str | None:
    explicit = raw.get("ma_to_hop")
    if explicit not in (None, ""):
        return str(explicit)
    note = raw.get("ghi_chu")
    if not isinstance(note, str):
        return None
    match = _MA_TO_HOP.search(note)
    return match.group(1) if match else None


def _require_catalog(value: int | None, message: str) -> int:
    if value is None:
        raise DatsImportError(message)
    return value


def _ensure_catalog_id(catalogs: CatalogIndex, kind: str, value: int, message: str) -> None:
    if kind == "phuong_thuc" and value not in catalogs.phuong_thuc_ids:
        raise DatsImportError(message)
    if kind == "to_hop" and value not in catalogs.to_hop_ids:
        raise DatsImportError(message)
    if kind == "nganh" and value not in catalogs.nganh_ids:
        raise DatsImportError(message)


def _apply(db: Session, rows: list[PreparedRow]) -> tuple[int, dict[str, int]]:
    maps: dict[str, dict[int, int]] = defaultdict(dict)
    counts: Counter[str] = Counter()
    de_an_id = None
    now = datetime.now()
    for row in rows:
        obj = _MODELS[row.table]()
        for key, value in row.values.items():
            if key in _DATS_FK and value is not None:
                target = _DATS_FK[key]
                mapped = maps[target].get(value)
                if mapped is None:
                    raise DatsImportError(f"{row.table} tham chiếu {target} id {value} không có trong file")
                value = mapped
            setattr(obj, key, value)
        if row.table == "dats_tuyen_sinh":
            obj.tao_luc = now
            obj.cap_nhat_luc = now
        db.add(obj)
        db.flush()
        if row.source_id is not None:
            maps[row.table][row.source_id] = obj.id
        if row.table == "dats_tuyen_sinh":
            de_an_id = obj.id
        counts[row.table] += 1
    if de_an_id is None:
        raise DatsImportError("Thiếu object dats_tuyen_sinh")
    return de_an_id, dict(counts)


def _load_catalogs(db: Session, document: dict) -> CatalogIndex:
    method_codes: set[str] = set()
    method_ids: set[int] = set()
    combo_codes: set[str] = set()
    combo_ids: set[int] = set()
    nganh_ids: set[int] = set()
    for table, kind in _KINDS.items():
        for raw in _section_or_empty(document, table, kind):
            if not isinstance(raw, dict):
                continue
            _collect_ref(raw.get("phuong_thuc_nguon_id"), method_ids)
            _collect_ref(raw.get("phuong_thuc_dich_id"), method_ids)
            _collect_ref(raw.get("to_hop_id"), combo_ids)
            _collect_ref(raw.get("to_hop_nguon_id"), combo_ids)
            _collect_ref(raw.get("to_hop_dich_id"), combo_ids)
            _collect_ref(raw.get("nganh_dao_tao_id"), nganh_ids)
            if table == "dats_phuong_thuc":
                code = raw.get("ma_phuong_thuc_cua_bo")
                if code in (None, ""):
                    code = raw.get("ma_phuong_thuc_cua_truong")
                if code not in (None, ""):
                    method_codes.add(str(code).strip().upper())
            if table == "dats_phuong_thuc_to_hop" and raw.get("to_hop_id") in (None, ""):
                code = _combo_code(raw)
                if code:
                    combo_codes.add(code.strip().upper())

    phuong_thuc_by_code: dict[str, int] = {}
    found_method_ids: set[int] = set()
    if method_codes or method_ids:
        stmt = select(DmPhuongThucTuyenSinh.id, DmPhuongThucTuyenSinh.ma_phuong_thuc)
        rows = db.execute(stmt).all()
        for item_id, code in rows:
            found_method_ids.add(item_id)
            if code:
                phuong_thuc_by_code[str(code).strip().upper()] = item_id
    to_hop_by_code: dict[str, int] = {}
    found_combo_ids: set[int] = set()
    if combo_codes or combo_ids:
        rows = db.execute(select(DmToHopMonHoc.id, DmToHopMonHoc.ma_to_hop)).all()
        for item_id, code in rows:
            found_combo_ids.add(item_id)
            if code:
                to_hop_by_code[str(code).strip().upper()] = item_id
    found_nganh_ids: set[int] = set()
    if nganh_ids:
        found_nganh_ids = set(db.scalars(select(DmNganhDaoTao.id).where(DmNganhDaoTao.id.in_(nganh_ids))).all())
    return CatalogIndex(
        phuong_thuc_by_code={code: phuong_thuc_by_code[code] for code in method_codes if code in phuong_thuc_by_code},
        phuong_thuc_ids=found_method_ids,
        to_hop_by_code={code: to_hop_by_code[code] for code in combo_codes if code in to_hop_by_code},
        to_hop_ids=found_combo_ids,
        nganh_ids=found_nganh_ids,
    )


def _section_or_empty(document: dict, table: str, kind: str) -> list:
    if not isinstance(document, dict) or table not in document or document[table] is None:
        return []
    value = document[table]
    if kind == "object" and isinstance(value, dict):
        return [value]
    if kind == "list" and isinstance(value, list):
        return value
    return []


def _collect_ref(value, bucket: set[int]) -> None:
    if value in (None, "") or isinstance(value, bool):
        return
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return
    if number >= 1:
        bucket.add(number)
