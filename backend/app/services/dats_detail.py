"""Đọc các bảng dats_ của một đề án để hiển thị chi tiết.

Khóa ngoại nội bộ được đổi thành tên đọc được. Id danh mục được ghép mã và tên.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
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
from app.models.dats_ty_le_viec_lam import DatsTyLeViecLam
from app.models.dats_website import DatsWebsite
from app.models.dm_nganh_dao_tao import DmNganhDaoTao
from app.models.dm_phuong_thuc_tuyen_sinh import DmPhuongThucTuyenSinh
from app.models.dm_to_hop_mon_hoc import DmToHopMonHoc

_SKIP = {"de_an_id", "tao_luc", "cap_nhat_luc"}
_FK = {
    "de_an_chuong_trinh_id",
    "de_an_phuong_thuc_id",
    "nganh_dao_tao_id",
    "co_so_id",
    "doi_tuong_du_tuyen_id",
    "to_hop_id",
    "phuong_thuc_nguon_id",
    "phuong_thuc_dich_id",
    "to_hop_nguon_id",
    "to_hop_dich_id",
}


@dataclass
class DeAnRows:
    campuses: list = field(default_factory=list)
    websites: list = field(default_factory=list)
    contacts: list = field(default_factory=list)
    programs: list = field(default_factory=list)
    plans: list = field(default_factory=list)
    methods: list = field(default_factory=list)
    combos: list = field(default_factory=list)
    staff: list = field(default_factory=list)
    facilities: list = field(default_factory=list)
    scales: list = field(default_factory=list)
    jobs: list = field(default_factory=list)
    levels: list = field(default_factory=list)
    audiences: list = field(default_factory=list)
    conditions: list = field(default_factory=list)
    criteria: list = field(default_factory=list)
    bonuses: list = field(default_factory=list)
    allocations: list = field(default_factory=list)
    dossiers: list = field(default_factory=list)
    thresholds: list = field(default_factory=list)
    conversions: list = field(default_factory=list)
    direct_admissions: list = field(default_factory=list)
    priorities: list = field(default_factory=list)


@dataclass
class DetailLookups:
    programs: dict[int, str] = field(default_factory=dict)
    methods: dict[int, str] = field(default_factory=dict)
    campuses: dict[int, str] = field(default_factory=dict)
    audiences: dict[int, str] = field(default_factory=dict)
    majors: dict[int, str] = field(default_factory=dict)
    subjects: dict[int, str] = field(default_factory=dict)
    catalog_methods: dict[int, str] = field(default_factory=dict)


def code_name(code: str | None, name: str | None, item_id: int | None = None) -> str:
    """Ghép mã và tên. Khi cả hai trống thì trả về #id nếu có id."""
    cleaned_code = (code or "").strip()
    cleaned_name = (name or "").strip()
    if cleaned_code and cleaned_name:
        return f"{cleaned_code} — {cleaned_name}"
    if cleaned_code or cleaned_name:
        return cleaned_code or cleaned_name
    return f"#{item_id}" if item_id is not None else ""


def _jsonable(value):
    if isinstance(value, Decimal):
        text = format(value, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    return value


def _ref(mapping: dict[int, str], item_id: int | None) -> str | None:
    if item_id is None:
        return None
    return mapping.get(item_id) or f"#{item_id}"


def _dump(item, extra: dict | None = None) -> dict:
    data = {"row_key": str(getattr(item, "id"))}
    hidden = _SKIP | _FK
    for column in item.__table__.columns:
        if column.name in hidden or column.name == "id":
            continue
        data[column.name] = _jsonable(getattr(item, column.name))
    if extra:
        data.update(extra)
    return data


def _scope(item, lookups: DetailLookups) -> dict:
    """Nhãn chương trình, phương thức, cơ sở, ngành và đối tượng nếu bản ghi có khóa đó."""
    extra = {}
    if hasattr(item, "de_an_chuong_trinh_id"):
        extra["chuong_trinh"] = _ref(lookups.programs, item.de_an_chuong_trinh_id)
    if hasattr(item, "de_an_phuong_thuc_id"):
        extra["phuong_thuc"] = _ref(lookups.methods, item.de_an_phuong_thuc_id)
    if hasattr(item, "co_so_id"):
        extra["ten_co_so"] = _ref(lookups.campuses, item.co_so_id)
    if hasattr(item, "nganh_dao_tao_id"):
        extra["nganh"] = _ref(lookups.majors, item.nganh_dao_tao_id)
    if hasattr(item, "doi_tuong_du_tuyen_id"):
        extra["doi_tuong"] = _ref(lookups.audiences, item.doi_tuong_du_tuyen_id)
    if hasattr(item, "phuong_thuc_nguon_id"):
        extra["phuong_thuc_nguon"] = _ref(lookups.catalog_methods, item.phuong_thuc_nguon_id)
        extra["to_hop_nguon"] = _ref(lookups.subjects, item.to_hop_nguon_id)
        extra["phuong_thuc_dich"] = _ref(lookups.catalog_methods, item.phuong_thuc_dich_id)
        extra["to_hop_dich"] = _ref(lookups.subjects, item.to_hop_dich_id)
    return extra


def _rows(items, lookups: DetailLookups) -> list[dict]:
    return [_dump(item, _scope(item, lookups)) for item in items]


def assemble_bang(rows: DeAnRows, lookups: DetailLookups) -> dict[str, list[dict]]:
    """Chuyển các bản ghi đã tải thành dữ liệu hiển thị, giữ thứ tự bảng của đề án."""
    combos = []
    for item in rows.combos:
        combos.append(
            {
                "row_key": f"{item.de_an_phuong_thuc_id}-{item.to_hop_id}",
                "phuong_thuc": _ref(lookups.methods, item.de_an_phuong_thuc_id),
                "to_hop": _ref(lookups.subjects, item.to_hop_id),
                "thu_tu_hien_thi": item.thu_tu_hien_thi,
                "ghi_chu": item.ghi_chu,
            }
        )
    return {
        "dats_tru_so": _rows(rows.campuses, lookups),
        "dats_website": _rows(rows.websites, lookups),
        "dats_lien_he_tuyen_sinh": _rows(rows.contacts, lookups),
        "dats_chuong_trinh_dao_tao": _rows(rows.programs, lookups),
        "dats_ke_hoach_tuyen_sinh": _rows(rows.plans, lookups),
        "dats_phuong_thuc": _rows(rows.methods, lookups),
        "dats_phuong_thuc_to_hop": combos,
        "dats_nhan_su": _rows(rows.staff, lookups),
        "dats_co_so_vat_chat": _rows(rows.facilities, lookups),
        "dats_quy_mo_dao_tao": _rows(rows.scales, lookups),
        "dats_ty_le_viec_lam": _rows(rows.jobs, lookups),
        "dats_trinh_do_nganh": _rows(rows.levels, lookups),
        "dats_doi_tuong_du_tuyen": _rows(rows.audiences, lookups),
        "dats_dieu_kien_du_tuyen": _rows(rows.conditions, lookups),
        "dats_tieu_chi_xet_tuyen": _rows(rows.criteria, lookups),
        "dats_diem_cong": _rows(rows.bonuses, lookups),
        "dats_quy_tac_phan_bo": _rows(rows.allocations, lookups),
        "dats_ho_so_du_tuyen": _rows(rows.dossiers, lookups),
        "dats_quy_doi_nguong_dau_vao": _rows(rows.thresholds, lookups),
        "dats_quy_doi_diem_trung_tuyen": _rows(rows.conversions, lookups),
        "dats_chinh_sach_xet_tuyen_thang": _rows(rows.direct_admissions, lookups),
        "dats_chinh_sach_uu_tien_xet_tuyen": _rows(rows.priorities, lookups),
    }


def _all(db: Session, model, *criteria, order_by=None) -> list:
    stmt = select(model)
    if criteria:
        stmt = stmt.where(*criteria)
    if order_by is not None:
        stmt = stmt.order_by(*order_by)
    return list(db.scalars(stmt).all())


def _by_ids(db: Session, model, column, ids: list[int]) -> list:
    unique = list(dict.fromkeys(ids))
    if not unique:
        return []
    return list(db.scalars(select(model).where(column.in_(unique))).all())


def _ids(items, attr: str) -> list[int]:
    return [getattr(item, attr) for item in items if getattr(item, attr) is not None]


def load_de_an_bang(db: Session, de_an_id: int) -> dict[str, list[dict]]:
    """Tải mọi bảng con của đề án và đổi khóa ngoại thành nhãn."""
    programs = _all(
        db,
        DatsChuongTrinhDaoTao,
        DatsChuongTrinhDaoTao.de_an_id == de_an_id,
        order_by=(DatsChuongTrinhDaoTao.ma_xet_tuyen.asc(), DatsChuongTrinhDaoTao.id.asc()),
    )
    program_ids = [item.id for item in programs]
    methods = _by_ids(db, DatsPhuongThuc, DatsPhuongThuc.de_an_chuong_trinh_id, program_ids)
    methods.sort(key=lambda item: (item.thu_tu_uu_tien is None, item.thu_tu_uu_tien or 0, item.id))
    method_ids = [item.id for item in methods]
    combos = _by_ids(db, DatsPhuongThucToHop, DatsPhuongThucToHop.de_an_phuong_thuc_id, method_ids)
    combos.sort(
        key=lambda item: (
            item.thu_tu_hien_thi is None,
            item.thu_tu_hien_thi or 0,
            item.de_an_phuong_thuc_id,
            item.to_hop_id,
        )
    )

    rows = DeAnRows(
        campuses=_all(db, DatsTruSo, DatsTruSo.de_an_id == de_an_id, order_by=(DatsTruSo.id.asc(),)),
        websites=_all(db, DatsWebsite, DatsWebsite.de_an_id == de_an_id, order_by=(DatsWebsite.id.asc(),)),
        contacts=_all(
            db,
            DatsLienHeTuyenSinh,
            DatsLienHeTuyenSinh.de_an_id == de_an_id,
            order_by=(DatsLienHeTuyenSinh.id.asc(),),
        ),
        programs=programs,
        plans=_by_ids(db, DatsKeHoachTuyenSinh, DatsKeHoachTuyenSinh.de_an_chuong_trinh_id, program_ids),
        methods=methods,
        combos=combos,
        staff=_all(db, DatsNhanSu, DatsNhanSu.de_an_id == de_an_id, order_by=(DatsNhanSu.id.asc(),)),
        facilities=_all(
            db,
            DatsCoSoVatChat,
            DatsCoSoVatChat.de_an_id == de_an_id,
            order_by=(DatsCoSoVatChat.id.asc(),),
        ),
        scales=_all(
            db,
            DatsQuyMoDaoTao,
            DatsQuyMoDaoTao.de_an_id == de_an_id,
            order_by=(DatsQuyMoDaoTao.id.asc(),),
        ),
        jobs=_all(db, DatsTyLeViecLam, DatsTyLeViecLam.de_an_id == de_an_id, order_by=(DatsTyLeViecLam.id.asc(),)),
        levels=_by_ids(db, DatsTrinhDoNganh, DatsTrinhDoNganh.de_an_chuong_trinh_id, program_ids),
        audiences=_all(
            db,
            DatsDoiTuongDuTuyen,
            DatsDoiTuongDuTuyen.de_an_id == de_an_id,
            order_by=(DatsDoiTuongDuTuyen.id.asc(),),
        ),
        conditions=_all(
            db,
            DatsDieuKienDuTuyen,
            DatsDieuKienDuTuyen.de_an_id == de_an_id,
            order_by=(DatsDieuKienDuTuyen.id.asc(),),
        ),
        criteria=_all(
            db,
            DatsTieuChiXetTuyen,
            DatsTieuChiXetTuyen.de_an_id == de_an_id,
            order_by=(DatsTieuChiXetTuyen.id.asc(),),
        ),
        bonuses=_all(db, DatsDiemCong, DatsDiemCong.de_an_id == de_an_id, order_by=(DatsDiemCong.id.asc(),)),
        allocations=_all(
            db,
            DatsQuyTacPhanBo,
            DatsQuyTacPhanBo.de_an_id == de_an_id,
            order_by=(DatsQuyTacPhanBo.id.asc(),),
        ),
        dossiers=_all(
            db,
            DatsHoSoDuTuyen,
            DatsHoSoDuTuyen.de_an_id == de_an_id,
            order_by=(DatsHoSoDuTuyen.id.asc(),),
        ),
        thresholds=_all(
            db,
            DatsQuyDoiNguongDauVao,
            DatsQuyDoiNguongDauVao.de_an_id == de_an_id,
            order_by=(DatsQuyDoiNguongDauVao.id.asc(),),
        ),
        conversions=_all(
            db,
            DatsQuyDoiDiemTrungTuyen,
            DatsQuyDoiDiemTrungTuyen.de_an_id == de_an_id,
            order_by=(DatsQuyDoiDiemTrungTuyen.id.asc(),),
        ),
        direct_admissions=_all(
            db,
            DatsChinhSachXetTuyenThang,
            DatsChinhSachXetTuyenThang.de_an_id == de_an_id,
            order_by=(DatsChinhSachXetTuyenThang.id.asc(),),
        ),
        priorities=_all(
            db,
            DatsChinhSachUuTienXetTuyen,
            DatsChinhSachUuTienXetTuyen.de_an_id == de_an_id,
            order_by=(DatsChinhSachUuTienXetTuyen.id.asc(),),
        ),
    )
    rows.plans.sort(key=lambda item: item.id)
    rows.levels.sort(key=lambda item: item.id)

    program_labels = {
        item.id: code_name(item.ma_xet_tuyen, item.ten_chuong_trinh, item.id) for item in programs
    }
    method_labels = {}
    for item in methods:
        own = code_name(item.ma_phuong_thuc_cua_truong, item.ten_phuong_thuc_cua_truong, None)
        if not own:
            own = (item.ma_phuong_thuc_cua_bo or "").strip() or f"#{item.id}"
        program = program_labels.get(item.de_an_chuong_trinh_id)
        method_labels[item.id] = f"{program} / {own}" if program else own

    major_ids = _ids(programs, "nganh_dao_tao_id") + _ids(rows.jobs, "nganh_dao_tao_id")
    subject_ids = _ids(combos, "to_hop_id")
    for item in [*rows.thresholds, *rows.conversions]:
        subject_ids.extend(value for value in (item.to_hop_nguon_id, item.to_hop_dich_id) if value is not None)
    catalog_method_ids = []
    for item in [*rows.thresholds, *rows.conversions]:
        catalog_method_ids.extend(
            value for value in (item.phuong_thuc_nguon_id, item.phuong_thuc_dich_id) if value is not None
        )

    majors = {
        item.id: code_name(item.ma_nganh, item.ten_nganh, item.id)
        for item in _by_ids(db, DmNganhDaoTao, DmNganhDaoTao.id, major_ids)
    }
    subjects = {
        item.id: code_name(item.ma_to_hop, item.ten_to_hop, item.id)
        for item in _by_ids(db, DmToHopMonHoc, DmToHopMonHoc.id, subject_ids)
    }
    catalog_methods = {
        item.id: code_name(item.ma_phuong_thuc, item.ten_phuong_thuc, item.id)
        for item in _by_ids(db, DmPhuongThucTuyenSinh, DmPhuongThucTuyenSinh.id, catalog_method_ids)
    }
    lookups = DetailLookups(
        programs=program_labels,
        methods=method_labels,
        campuses={item.id: code_name(None, item.ten_co_so, item.id) for item in rows.campuses},
        audiences={
            item.id: code_name(item.ma_doi_tuong, item.ten_doi_tuong, item.id) for item in rows.audiences
        },
        majors=majors,
        subjects=subjects,
        catalog_methods=catalog_methods,
    )
    return assemble_bang(rows, lookups)
